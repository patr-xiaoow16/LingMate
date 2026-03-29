from __future__ import annotations

import multiprocessing
import threading
import time
from datetime import datetime, timezone
import json
from uuid import uuid4

from sqlalchemy import select

from app.content.fixtures import analysis_fixture, report_fixture
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import AnalysisJob, Lesson, LessonEvent, Material, TranscriptSegment
from app.services.generation_service import generation_service
from app.services.transcript_service import TranscriptUnavailableError, transcript_service


def _transcript_worker(queue, source_url: str, provided_transcript: str | None) -> None:
    try:
        result = transcript_service.build_transcript_from_source(
            source_url=source_url,
            provided_transcript=provided_transcript,
        )
        queue.put({"ok": True, "result": result})
    except Exception as exc:  # pragma: no cover
        if isinstance(exc, TranscriptUnavailableError):
            queue.put(
                {
                    "ok": False,
                    "message": exc.message,
                    "code": exc.code,
                    "raw_error": exc.raw_error,
                }
            )
        else:
            queue.put(
                {
                    "ok": False,
                    "message": str(exc),
                    "code": "transcript_extract_failed",
                    "raw_error": str(exc),
                }
            )


class PipelineWorker:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if not settings.task_worker_enabled:
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="lingmate-pipeline-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def enqueue_import_job(self, lesson_id: str) -> None:
        db = SessionLocal()
        try:
            job = AnalysisJob(
                job_id=f"job-{uuid4().hex[:10]}",
                lesson_id=lesson_id,
                job_type="process_import",
                status="pending",
                payload_json={},
            )
            db.add(job)
            db.add(LessonEvent(lesson_id=lesson_id, event_type="job_enqueued", payload_json={"job_id": job.job_id}))
            db.commit()
        finally:
            db.close()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            handled = self._process_once()
            if not handled:
                time.sleep(settings.task_worker_poll_interval_seconds)

    def _process_once(self) -> bool:
        db = SessionLocal()
        try:
            job = db.execute(
                select(AnalysisJob)
                .where(AnalysisJob.status == "pending")
                .order_by(AnalysisJob.created_at.asc())
                .limit(1)
            ).scalar_one_or_none()
            if not job:
                return False

            lesson = db.execute(select(Lesson).where(Lesson.lesson_id == job.lesson_id)).scalar_one_or_none()
            if not lesson:
                job.status = "failed"
                job.error_message = "Lesson not found"
                db.add(job)
                db.commit()
                return True

            material = db.execute(select(Material).where(Material.material_id == lesson.material_id)).scalar_one()
            self._mark_job_started(db, job)
            self._process_import_job(db, lesson, material, job)
            return True
        finally:
            db.close()

    def _mark_job_started(self, db, job: AnalysisJob) -> None:
        job.status = "running"
        job.attempts += 1
        job.started_at = datetime.now(timezone.utc)
        db.add(job)
        db.commit()

    def _set_pipeline_state(self, db, lesson: Lesson, step_index: int, active_note: str) -> None:
        analysis = lesson.analysis_json or analysis_fixture()
        steps = analysis["pipeline"]["steps"]
        active_title = steps[step_index]["title"]
        for idx, step in enumerate(steps):
            if idx < step_index:
                step["status"] = "done"
            elif idx == step_index:
                step["status"] = "active"
                step["note"] = active_note
            else:
                step["status"] = "todo"
                step["note"] = "等待前序步骤完成"
        analysis["pipeline"]["activeStepTitle"] = active_title
        analysis["pipeline"]["progress"] = int(((step_index) / max(len(steps), 1)) * 100)
        analysis["analysisReady"] = False
        analysis["status"] = "processing"
        lesson.analysis_json = analysis
        lesson.status = "processing"
        db.add(lesson)
        db.commit()
        print(f"[LingMate][步骤] lesson_id={lesson.lesson_id} -> {active_title}：{active_note}")

    def _process_import_job(self, db, lesson: Lesson, material: Material, job: AnalysisJob) -> None:
        try:
            print(f"[LingMate][任务开始] lesson_id={lesson.lesson_id}，开始处理导入材料：{material.source_url}")
            self._set_pipeline_state(db, lesson, 0, "正在生成 transcript")
            transcript_bundle = self._build_transcript_with_timeout(
                source_url=material.source_url,
                provided_transcript=job.payload_json.get("transcript"),
            )
            material.title = transcript_bundle["title"]
            material.status = "transcribed"
            material.transcript_text = transcript_bundle["transcript"]
            material.transcript_meta_json = transcript_bundle["meta"]
            lesson.title = transcript_bundle["title"]
            db.add(material)
            db.add(lesson)
            db.commit()
            print(f"[LingMate][步骤完成] lesson_id={lesson.lesson_id}，已生成 transcript，共 {len(transcript_bundle['segments'])} 段。")

            db.query(TranscriptSegment).filter(TranscriptSegment.lesson_id == lesson.lesson_id).delete()
            for segment in transcript_bundle["segments"]:
                db.add(
                    TranscriptSegment(
                        lesson_id=lesson.lesson_id,
                        material_id=material.material_id,
                        segment_index=segment["segment_index"],
                        start_ms=segment["start_ms"],
                        end_ms=segment["end_ms"],
                        text=segment["text"],
                        speaker=segment["speaker"],
                    )
                )
            db.commit()

            self._set_pipeline_state(db, lesson, 1, "正在调用 DeepSeek 生成 transcript 分析")
            analysis = generation_service.generate_analysis(
                transcript=material.transcript_text,
                source_url=material.source_url,
                title=material.title,
            )
            print(f"[LingMate][步骤完成] lesson_id={lesson.lesson_id}，DeepSeek transcript 分析已生成。")

            self._set_pipeline_state(db, lesson, 5, "正在生成 8 模块课程内容")
            modules = generation_service.generate_modules(
                transcript=material.transcript_text,
                analysis=analysis,
            )
            print(f"[LingMate][步骤完成] lesson_id={lesson.lesson_id}，8 模块课程内容已生成。")
            expressions = analysis.get("lesson", {}).get("chips", [])
            completed_modules = len((lesson.progress_json or {}).get("completedModules", []))
            report = generation_service.generate_report(completed_modules=completed_modules, expressions=expressions)
            print(f"[LingMate][步骤完成] lesson_id={lesson.lesson_id}，学习报告已生成。")

            analysis["lesson"]["transcript"] = material.transcript_text
            analysis["pipeline"]["steps"] = [
                {"index": "01", "title": "Whisper 转写", "note": "transcript 已生成", "status": "done"},
                {"index": "02", "title": "难度分级", "note": "DeepSeek 已完成难度分析", "status": "done"},
                {"index": "03", "title": "关键表达", "note": "DeepSeek 已提取关键表达", "status": "done"},
                {"index": "04", "title": "场景识别", "note": "DeepSeek 已识别场景", "status": "done"},
                {"index": "05", "title": "语音现象", "note": "DeepSeek 已生成听力分析", "status": "done"},
                {"index": "06", "title": "课程编排", "note": "8 模块课程内容已生成", "status": "done"},
            ]
            analysis["pipeline"]["activeStepTitle"] = "完成"
            analysis["pipeline"]["progress"] = 100
            analysis["analysisReady"] = True
            analysis["status"] = "ready"

            lesson.analysis_json = analysis
            lesson.module_content_json = modules
            lesson.report_json = report
            lesson.status = "analysis_ready"
            lesson.provider = analysis.get("llmMeta", {}).get("provider", settings.analysis_provider)
            db.add(lesson)
            db.add(LessonEvent(lesson_id=lesson.lesson_id, event_type="analysis_ready", payload_json={"job_id": job.job_id}))

            job.status = "completed"
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()

            print(
                "[LingMate][analysis_ready]",
                json.dumps(
                    {
                        "lesson_id": lesson.lesson_id,
                        "title": lesson.title,
                        "provider": lesson.provider,
                        "material_url": material.source_url,
                        "transcript_preview": material.transcript_text[:180],
                        "lesson_chips": analysis.get("lesson", {}).get("chips", []),
                        "module_count": len(modules.get("modules", [])),
                    },
                    ensure_ascii=False,
                ),
            )
        except TranscriptUnavailableError as exc:
            lesson.status = "failed"
            lesson.error_message = str(exc)
            lesson.analysis_json = lesson.analysis_json or analysis_fixture()
            lesson.analysis_json["status"] = "failed"
            lesson.analysis_json["analysisReady"] = False
            lesson.analysis_json["summary"]["title"] = "材料导入失败"
            lesson.analysis_json["summary"]["description"] = str(exc)
            lesson.analysis_json["pipeline"]["description"] = str(exc)
            lesson.analysis_json["pipeline"]["activeStepTitle"] = "失败"
            lesson.analysis_json["errorCode"] = exc.code
            lesson.analysis_json["recoveryAction"] = self._build_recovery_action(exc.code)
            db.add(lesson)
            db.add(LessonEvent(lesson_id=lesson.lesson_id, event_type="analysis_failed", payload_json={"error": str(exc)}))
            job.status = "failed"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()
            print(f"[LingMate][analysis_failed] lesson_id={lesson.lesson_id} message={exc}")
            print(f"[LingMate][analysis_failed_raw] lesson_id={lesson.lesson_id} raw_error={exc.raw_error}")
        except Exception as exc:
            lesson.status = "failed"
            lesson.error_message = str(exc)
            lesson.analysis_json = lesson.analysis_json or analysis_fixture()
            lesson.analysis_json["status"] = "failed"
            lesson.analysis_json["analysisReady"] = False
            lesson.analysis_json["pipeline"]["description"] = f"处理失败：{exc}"
            lesson.analysis_json["errorCode"] = "analysis_failed"
            db.add(lesson)
            db.add(LessonEvent(lesson_id=lesson.lesson_id, event_type="analysis_failed", payload_json={"error": str(exc)}))
            job.status = "failed"
            job.error_message = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()
            print(f"[LingMate][analysis_failed] lesson_id={lesson.lesson_id} message=处理失败，请查看详细日志")
            print(f"[LingMate][analysis_failed_raw] lesson_id={lesson.lesson_id} error={exc}")

    def _build_recovery_action(self, error_code: str) -> dict | None:
        if error_code == "youtube_auth_required":
            return {
                "type": "open_url",
                "label": "打开 YouTube 登录",
                "url": "https://accounts.google.com/ServiceLogin?service=youtube",
                "note": "登录后请回到当前页面重新导入链接。",
            }
        if error_code == "transcript_timeout":
            return {
                "type": "retry_hint",
                "label": "请重新导入更短视频",
                "note": "建议先尝试 3-10 分钟、公开且带英文字幕的视频。",
            }
        return None

    def _build_transcript_with_timeout(self, source_url: str, provided_transcript: str | None) -> dict:
        if settings.transcript_extract_timeout_seconds <= 0:
            print("[LingMate][转写] 当前未设置 transcript 超时限制，将等待转写完成。")
            return transcript_service.build_transcript_from_source(
                source_url=source_url,
                provided_transcript=provided_transcript,
            )

        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        process = ctx.Process(target=_transcript_worker, args=(queue, source_url, provided_transcript))
        process.start()
        process.join(timeout=settings.transcript_extract_timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
            raise TranscriptUnavailableError(
                f"转写提取超时，已超过 {settings.transcript_extract_timeout_seconds} 秒。请稍后重试，或更换更短、更公开的视频链接。",
                code="transcript_timeout",
                raw_error="transcript extraction timeout",
            )

        if queue.empty():
            raise TranscriptUnavailableError(
                "转写提取失败，后台没有返回可用结果。请稍后重试。",
                code="transcript_extract_failed",
                raw_error="empty transcript result",
            )

        payload = queue.get()
        if payload.get("ok"):
            return payload["result"]

        raise TranscriptUnavailableError(
            payload.get("message", "转写提取失败。"),
            code=payload.get("code", "transcript_extract_failed"),
            raw_error=payload.get("raw_error"),
        )


pipeline_worker = PipelineWorker()
