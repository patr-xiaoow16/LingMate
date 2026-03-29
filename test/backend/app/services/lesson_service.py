from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import json
from collections import defaultdict
from uuid import uuid4
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.fixtures import (
    analysis_fixture,
    analysis_steps_fixture,
    modules_fixture,
    report_fixture,
    workspace_fixture,
)
from app.core.config import settings
from app.models import AIFeedback, AnalysisJob, Lesson, LessonEvent, Material, Submission, TranscriptSegment
from app.schemas.lesson import ImportMaterialRequest, ModuleActionRequest
from app.services.generation_service import generation_service
from app.services.pipeline_worker import pipeline_worker
from app.services.storage_service import storage_service


class LessonNotFoundError(RuntimeError):
    pass


@dataclass
class LessonService:
    def _is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _build_default_progress(self) -> dict:
        return {
            "currentModule": 1,
            "completedModules": [],
            "lastAction": "工作台已初始化，准备开始沉浸听力。",
        }

    def _next_lesson_id(self) -> str:
        return f"lesson-{uuid4().hex[:8]}"

    def _next_material_id(self) -> str:
        return f"material-{uuid4().hex[:8]}"

    def _next_submission_id(self) -> str:
        return f"submission-{uuid4().hex[:10]}"

    def _next_feedback_id(self) -> str:
        return f"feedback-{uuid4().hex[:10]}"

    def _get_lesson(self, db: Session, lesson_id: str) -> Lesson:
        lesson = db.execute(select(Lesson).where(Lesson.lesson_id == lesson_id)).scalar_one_or_none()
        if not lesson:
            raise LessonNotFoundError(f"Lesson not found: {lesson_id}")
        return lesson

    def _get_material(self, db: Session, material_id: str) -> Material:
        return db.execute(select(Material).where(Material.material_id == material_id)).scalar_one()

    def _record_event(self, db: Session, lesson_id: str, event_type: str, payload: dict | None = None) -> None:
        db.add(LessonEvent(lesson_id=lesson_id, event_type=event_type, payload_json=payload or {}))

    def import_material(self, db: Session, payload: ImportMaterialRequest) -> dict:
        source = payload.source
        url = source.url.strip()
        source_type = source.type
        is_upload = source_type == "upload"
        if not is_upload and not self._is_valid_url(url):
            return {"lessonId": None, "status": "error", "message": "请输入有效的 http/https 链接。"}

        material = Material(
            material_id=self._next_material_id(),
            source_type=source_type,
            source_url=url,
            file_name=source.fileName or "",
            mime_type=source.mimeType or "",
            title="Queued material",
            status="queued",
        )
        lesson = Lesson(
            lesson_id=self._next_lesson_id(),
            material_id=material.material_id,
            status="processing",
            provider=settings.analysis_provider,
            title="Queued lesson",
            analysis_json=self._build_queued_analysis(source_url=url),
            module_content_json={"modules": modules_fixture(), "llmMeta": {"provider": "queued", "mode": "pending"}},
            report_json=report_fixture(),
            progress_json=self._build_default_progress(),
        )
        db.add(material)
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "lesson_imported", {"source_url": url, "has_transcript": bool(source.transcript)})
        db.commit()
        pipeline_worker.enqueue_import_job(lesson.lesson_id)

        pending_job = db.execute(
            select(AnalysisJob).where(AnalysisJob.lesson_id == lesson.lesson_id).order_by(AnalysisJob.created_at.desc())
        ).scalar_one_or_none()
        if pending_job and source.transcript:
            pending_job.payload_json = {"transcript": source.transcript}
            db.add(pending_job)
            db.commit()

        return {
            "lessonId": lesson.lesson_id,
            "status": lesson.status,
            "redirect": f"/analysis/{lesson.lesson_id}",
            "provider": lesson.provider,
        }

    def import_uploaded_audio(
        self,
        db: Session,
        *,
        file_name: str,
        mime_type: str,
        content: bytes,
    ) -> dict:
        stored = storage_service.save_uploaded_file(file_name=file_name, content=content)
        payload = ImportMaterialRequest(
            mode="audio_upload",
            source={
                "type": "upload",
                "url": stored["path"],
                "fileName": stored["file_name"],
                "mimeType": mime_type,
            },
        )
        result = self.import_material(db, payload)
        lesson = self._get_lesson(db, result["lessonId"])
        material = self._get_material(db, lesson.material_id)
        material.source_url = stored["path"]
        material.file_name = stored["file_name"]
        material.mime_type = mime_type
        material.title = stored["file_name"] or material.title
        db.add(material)
        self._record_event(
            db,
            lesson.lesson_id,
            "audio_uploaded",
            {
                "file_name": stored["file_name"],
                "path": stored["path"],
                "mime_type": mime_type,
                "size_bytes": len(content),
            },
        )
        db.commit()
        return result

    def get_analysis(self, db: Session, lesson_id: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        payload = deepcopy(lesson.analysis_json or self._build_queued_analysis(""))
        material = self._get_material(db, lesson.material_id)
        pending_job = db.execute(
            select(AnalysisJob).where(AnalysisJob.lesson_id == lesson_id).order_by(AnalysisJob.created_at.desc())
        ).scalar_one_or_none()

        analysis_ready = lesson.status == "analysis_ready"
        payload["analysisReady"] = analysis_ready
        payload["status"] = "ready" if analysis_ready else lesson.status
        payload["lesson"]["badge"] = "Ready" if analysis_ready else "处理中"
        if lesson.status == "failed":
            payload["lesson"]["badge"] = "失败"
            payload["summary"]["title"] = "分析失败"
            payload["summary"]["description"] = lesson.error_message or payload["summary"]["description"]
            payload["pipeline"]["description"] = lesson.error_message or payload["pipeline"]["description"]
        payload["errorCode"] = payload.get("errorCode")
        payload["recoveryAction"] = payload.get("recoveryAction")
        payload["mockMeta"] = {
            "elapsedSeconds": 0,
            "totalDurationSeconds": 0,
            "currentStep": payload["pipeline"].get("activeStepTitle", "完成" if analysis_ready else "排队中"),
            "source": {"type": material.source_type, "url": material.source_url},
            "provider": lesson.provider,
            "jobStatus": pending_job.status if pending_job else "none",
        }
        return {"lessonId": lesson_id, **payload}

    def start_lesson(self, db: Session, lesson_id: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        analysis = self.get_analysis(db, lesson_id)
        if not analysis.get("analysisReady"):
            return {
                "lessonId": lesson_id,
                "status": "processing",
                "redirect": f"/analysis/{lesson_id}",
                "message": "AI 预处理尚未完成，请稍候。",
            }

        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        progress["currentModule"] = 1
        progress["completedModules"] = []
        progress["lastAction"] = "已进入沉浸听力，先从整体语感开始。"
        lesson.progress_json = progress
        lesson.status = "started"
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "lesson_started")
        db.commit()
        return {"lessonId": lesson_id, "status": "started", "redirect": f"/workspace/{lesson_id}?module=1&entry=analysis"}

    def get_workspace(self, db: Session, lesson_id: str, module_index: int | None = None) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        material = self._get_material(db, lesson.material_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        if module_index is not None and 1 <= module_index <= 8:
            progress["currentModule"] = module_index
            lesson.progress_json = progress
            db.add(lesson)
            db.commit()

        payload = workspace_fixture()
        payload["material"]["title"] = material.title
        payload["material"]["description"] = f"来源：{material.source_url}"
        payload["material"]["sourceLabel"] = f"来源：{material.source_url}"
        payload["material"]["audioUrl"] = storage_service.public_media_url(material.source_url) if material.source_type == "upload" else None
        payload["modules"] = generation_service.adapt_modules_for_workspace(
            (lesson.module_content_json or {}).get("modules", modules_fixture()),
            transcript=material.transcript_text or "",
            analysis=lesson.analysis_json or {},
        )
        payload["progress"]["current"] = progress["currentModule"]
        payload["progress"]["completed"] = len(progress["completedModules"])
        payload["completedModules"] = progress["completedModules"][:]
        payload["interaction"] = {"lastAction": progress["lastAction"]}
        payload["notePanel"] = {
            "title": "AI 随记",
            "subtitle": "像一位陪伴式听力老师一样，随时记下你的困惑、联想和感觉，AI 会继续接住并回应你。",
            "placeholder": "比如：这里我听不出 why / what hand you’re dealt 的感觉，像不像在说人生很随机？",
            "entries": self._build_note_entries(db, lesson.lesson_id),
        }
        return {"lessonId": lesson_id, **payload}

    def coach_module(self, db: Session, lesson_id: str, module_key: str, payload: ModuleActionRequest) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        message = payload.message or "请给我下一步建议"
        feedback = generation_service.generate_feedback(module_key=module_key, user_input=message, lesson_context=lesson.analysis_json or {})
        submission = Submission(
            submission_id=self._next_submission_id(),
            lesson_id=lesson.lesson_id,
            module_key=module_key,
            interaction_type="coach",
            user_input=message,
            meta_json={"label": payload.label},
        )
        ai_feedback = AIFeedback(
            feedback_id=self._next_feedback_id(),
            submission_id=submission.submission_id,
            provider=feedback.get("provider", settings.analysis_provider),
            model=feedback.get("model", settings.deepseek_model),
            feedback_json=feedback,
        )
        progress["lastAction"] = f"AI coach 已响应模块 {module_key}。"
        lesson.progress_json = progress
        db.add(submission)
        db.add(ai_feedback)
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "coach_module", {"module_key": module_key, "message": message})
        db.commit()
        print(
            "[LingMate][ai_feedback]",
            json.dumps(
                {
                    "lesson_id": lesson.lesson_id,
                    "module_key": module_key,
                    "submission_id": submission.submission_id,
                    "provider": ai_feedback.provider,
                    "model": ai_feedback.model,
                    "user_input": message,
                    "reply": feedback.get("reply", ""),
                    "suggestions": feedback.get("suggestions", []),
                },
                ensure_ascii=False,
            ),
        )
        return {
            "lessonId": lesson_id,
            "module": {"slug": module_key},
            "reply": feedback["reply"],
            "suggestions": feedback.get("suggestions", []),
            "submissionId": submission.submission_id,
        }

    def submit_note(self, db: Session, lesson_id: str, module_key: str, payload: ModuleActionRequest) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        message = (payload.message or "").strip()
        if not message:
            return {
                "lessonId": lesson_id,
                "moduleKey": module_key,
                "message": "随记内容为空，未保存。",
                "entries": self._build_note_entries(db, lesson_id),
            }

        feedback = generation_service.generate_note_feedback(
            module_key=module_key,
            user_input=message,
            lesson_context=lesson.analysis_json or {},
        )
        submission = Submission(
            submission_id=self._next_submission_id(),
            lesson_id=lesson.lesson_id,
            module_key=module_key,
            interaction_type="ai_note",
            user_input=message,
            meta_json={"label": payload.label or "AI随记"},
        )
        ai_feedback = AIFeedback(
            feedback_id=self._next_feedback_id(),
            submission_id=submission.submission_id,
            provider=feedback.get("provider", settings.analysis_provider),
            model=feedback.get("model", settings.deepseek_model),
            feedback_json=feedback,
        )
        progress["lastAction"] = f"已记录一条 AI 随记，当前模块 {module_key}。"
        lesson.progress_json = progress
        db.add(submission)
        db.add(ai_feedback)
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "ai_note_created", {"module_key": module_key})
        db.commit()
        print(
            "[LingMate][ai_note]",
            json.dumps(
                {
                    "lesson_id": lesson.lesson_id,
                    "module_key": module_key,
                    "submission_id": submission.submission_id,
                    "note": message,
                    "reply": feedback.get("reply", ""),
                },
                ensure_ascii=False,
            ),
        )
        return {
            "lessonId": lesson_id,
            "moduleKey": module_key,
            "message": "AI 随记已保存。",
            "entries": self._build_note_entries(db, lesson.lesson_id),
        }

    def delete_note(self, db: Session, lesson_id: str, submission_id: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        submission = db.execute(
            select(Submission).where(
                Submission.lesson_id == lesson.lesson_id,
                Submission.submission_id == submission_id,
                Submission.interaction_type == "ai_note",
            )
        ).scalar_one_or_none()
        if not submission:
            return {
                "lessonId": lesson_id,
                "submissionId": submission_id,
                "message": "这条 AI 随记不存在，可能已经被删除。",
                "entries": self._build_note_entries(db, lesson.lesson_id),
            }

        feedback_rows = db.execute(
            select(AIFeedback).where(AIFeedback.submission_id == submission.submission_id)
        ).scalars().all()
        for row in feedback_rows:
            db.delete(row)
        db.delete(submission)

        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        progress["lastAction"] = "已删除一条 AI 随记。"
        lesson.progress_json = progress
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "ai_note_deleted", {"submission_id": submission_id})
        db.commit()
        print(f"[LingMate][ai_note_deleted] lesson_id={lesson.lesson_id} submission_id={submission_id}")
        return {
            "lessonId": lesson_id,
            "submissionId": submission_id,
            "message": "AI 随记已删除。",
            "entries": self._build_note_entries(db, lesson.lesson_id),
        }

    def complete_module(self, db: Session, lesson_id: str, module_key: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        module_index = int(module_key)
        if module_index not in progress["completedModules"]:
            progress["completedModules"].append(module_index)
        next_module = min(8, module_index + 1)
        progress["currentModule"] = next_module
        progress["lastAction"] = f"已完成模块 {module_index}，继续进入下一步。"
        lesson.progress_json = progress
        if module_index >= 8:
            lesson.status = "completed"
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "module_completed", {"module_index": module_index})
        db.commit()
        return {
            "lessonId": lesson_id,
            "completed": module_key,
            "nextModule": next_module,
            "message": "模块已完成，进度已同步到本课学习记录。",
        }

    def perform_module_action(self, db: Session, lesson_id: str, module_key: str, payload: ModuleActionRequest) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        action = payload.action or "interact"
        label = payload.label or action
        current_module = progress["currentModule"]
        message = f"已执行操作：{label}"

        if action in {"module_select", "open_module"}:
            current_module = int(module_key)
            message = f"已切换到模块 {current_module}"
        elif action in {"play", "replay"}:
            message = "播放操作已记录，后续将接入真实音频播放追踪。"
        elif action in {"advance", "primary"}:
            if current_module not in progress["completedModules"]:
                progress["completedModules"].append(current_module)
            current_module = min(8, current_module + 1)
            message = f"流程已推进到模块 {current_module}。"

        progress["currentModule"] = current_module
        progress["lastAction"] = message
        lesson.progress_json = progress
        db.add(lesson)
        if payload.message:
            submission = Submission(
                submission_id=self._next_submission_id(),
                lesson_id=lesson.lesson_id,
                module_key=module_key,
                interaction_type=action,
                user_input=payload.message,
                meta_json={"label": label},
            )
            db.add(submission)
        self._record_event(db, lesson.lesson_id, "module_action", {"module_key": module_key, "action": action, "label": label})
        db.commit()
        return {
            "lessonId": lesson_id,
            "module": {"slug": module_key},
            "currentModule": current_module,
            "completedModules": progress["completedModules"][:],
            "message": message,
        }

    def get_report(self, db: Session, lesson_id: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        completed = len((lesson.progress_json or {}).get("completedModules", []))
        report = deepcopy(lesson.report_json or report_fixture())
        note_entries = self._build_note_entries(db, lesson.lesson_id)
        learning_journey = self._build_learning_journey(db, lesson.lesson_id, note_entries)
        total_minutes = sum(learning_journey["durationMinutes"])
        report["metrics"][0]["value"] = f"{total_minutes:.1f}m"
        report["metrics"][0]["note"] = "按 8 个模块的实际停留时长估算。"
        report["metrics"][2]["value"] = str(completed)
        report["metrics"][2]["note"] = f"本课共推进 {completed} / 8 个模块。"
        report["aiNotes"] = note_entries[-8:]
        report["learningJourney"] = learning_journey
        if note_entries:
            report["records"].append(
                {
                    "date": "本课过程",
                    "title": f"记录了 {len(note_entries)} 条 AI 随记",
                    "note": "这些随记会保留你的听感、困惑和 AI 的即时回应，帮助你在报告页回看整节课的思路变化。",
                }
            )
        return {"lessonId": lesson_id, **report}

    def get_review_payload(self, db: Session) -> dict:
        _ = db
        return deepcopy(report_fixture())

    def _build_queued_analysis(self, source_url: str) -> dict:
        analysis = deepcopy(analysis_fixture())
        analysis["summary"]["eyebrow"] = "Import queued"
        analysis["summary"]["title"] = "已接收材料，正在进入分析队列"
        analysis["summary"]["description"] = "后台任务会依次完成转写、分析与课程生成。"
        analysis["lesson"]["badge"] = "Queued"
        analysis["lesson"]["meta"] = "等待异步任务处理"
        analysis["lesson"]["transcript"] = ""
        analysis["pipeline"]["description"] = "等待后台任务开始。"
        analysis["pipeline"]["progress"] = 0
        analysis["pipeline"]["activeStepTitle"] = "排队中"
        steps = analysis_steps_fixture()
        analysis["pipeline"]["steps"] = [
            {"index": step["index"], "title": step["title"], "note": "等待前序步骤完成", "status": "todo", "stepProgress": 0}
            for step in steps
        ]
        analysis["analysisReady"] = False
        analysis["status"] = "processing"
        analysis["sourceUrl"] = source_url
        return analysis

    def _build_note_entries(self, db: Session, lesson_id: str) -> list[dict]:
        submissions = db.execute(
            select(Submission)
            .where(Submission.lesson_id == lesson_id, Submission.interaction_type == "ai_note")
            .order_by(Submission.created_at.asc())
        ).scalars().all()
        if not submissions:
            return []

        submission_ids = [submission.submission_id for submission in submissions]
        feedback_rows = db.execute(
            select(AIFeedback).where(AIFeedback.submission_id.in_(submission_ids)).order_by(AIFeedback.created_at.asc())
        ).scalars().all()
        feedback_map = {row.submission_id: row for row in feedback_rows}

        entries = []
        for submission in submissions:
            feedback = feedback_map.get(submission.submission_id)
            created_at = submission.created_at.strftime("%m-%d %H:%M") if submission.created_at else ""
            emotion = self._classify_note_emotion(submission.user_input)
            entries.append(
                {
                    "submissionId": submission.submission_id,
                    "moduleKey": submission.module_key,
                    "createdAt": created_at,
                    "emotion": emotion,
                    "user": {
                        "role": "我",
                        "content": submission.user_input,
                    },
                    "assistant": {
                        "role": "AI 老师",
                        "content": (feedback.feedback_json or {}).get("reply", "") if feedback else "",
                        "suggestions": (feedback.feedback_json or {}).get("suggestions", []) if feedback else [],
                    },
                }
            )
        return entries

    def _build_learning_journey(self, db: Session, lesson_id: str, note_entries: list[dict]) -> dict:
        duration_minutes = self._build_module_duration_minutes(db, lesson_id)
        emotion_by_module: dict[int, list[int]] = defaultdict(list)
        for entry in note_entries:
            module_index = self._safe_int(entry.get("moduleKey"), 1)
            emotion_by_module[module_index].append(entry.get("emotion", {}).get("score", 0))

        emotion_scores = []
        emotion_labels = []
        for module_index in range(1, 9):
            scores = emotion_by_module.get(module_index, [])
            avg = round(sum(scores) / len(scores), 2) if scores else 0.0
            emotion_scores.append(avg)
            emotion_labels.append(self._emotion_bucket_label(avg))

        efficiency_scores = self._build_efficiency_scores(
            duration_minutes=duration_minutes,
            emotion_scores=emotion_scores,
            note_entries=note_entries,
        )

        return {
            "labels": [f"M{index}" for index in range(1, 9)],
            "durationMinutes": duration_minutes,
            "emotionScores": emotion_scores,
            "emotionLabels": emotion_labels,
            "efficiencyScores": efficiency_scores,
            "efficiencyDefinition": "效率曲线 = 模块推进度 + 随记参与度 + 情绪恢复度 的综合分。分数越高，说明这一模块里你既有投入，也更快把困惑转成理解。",
        }

    def _build_module_duration_minutes(self, db: Session, lesson_id: str) -> list[float]:
        lesson = self._get_lesson(db, lesson_id)
        events = db.execute(
            select(LessonEvent).where(LessonEvent.lesson_id == lesson_id).order_by(LessonEvent.created_at.asc())
        ).scalars().all()

        durations_seconds = [0.0] * 8
        current_module = 1
        current_start = lesson.created_at
        timeline_started = False

        for event in events:
            if event.event_type == "lesson_started":
                current_module = 1
                current_start = event.created_at
                timeline_started = True
                continue

            if not timeline_started:
                continue

            if event.event_type == "module_completed":
                module_index = self._safe_int((event.payload_json or {}).get("module_index"), current_module)
                if current_start and 1 <= current_module <= 8:
                    durations_seconds[current_module - 1] += max(0.0, (event.created_at - current_start).total_seconds())
                current_module = min(8, module_index + 1)
                current_start = event.created_at
                continue

            if event.event_type == "module_action":
                payload = event.payload_json or {}
                action = payload.get("action")
                if action in {"module_select", "open_module"}:
                    target_module = self._safe_int(payload.get("module_key"), current_module)
                    if current_start and 1 <= current_module <= 8:
                        durations_seconds[current_module - 1] += max(0.0, (event.created_at - current_start).total_seconds())
                    current_module = max(1, min(8, target_module))
                    current_start = event.created_at

        if timeline_started and current_start and 1 <= current_module <= 8:
            end_time = lesson.updated_at or datetime.utcnow()
            durations_seconds[current_module - 1] += max(0.0, (end_time - current_start).total_seconds())

        duration_minutes = [round(seconds / 60, 1) for seconds in durations_seconds]
        if not any(duration_minutes):
            completed_modules = (lesson.progress_json or {}).get("completedModules", [])
            for index in range(8):
                duration_minutes[index] = 5.0 if (index + 1) in completed_modules else 0.0
        return duration_minutes

    def _build_efficiency_scores(self, duration_minutes: list[float], emotion_scores: list[float], note_entries: list[dict]) -> list[int]:
        note_count_by_module: dict[int, int] = defaultdict(int)
        for entry in note_entries:
            note_count_by_module[self._safe_int(entry.get("moduleKey"), 1)] += 1

        scores = []
        target_minutes = 6.0
        for module_index in range(1, 9):
            duration = duration_minutes[module_index - 1]
            notes = note_count_by_module.get(module_index, 0)
            emotion = emotion_scores[module_index - 1]

            engagement = min(notes / 2, 1.0)
            pace_fit = 1.0 - min(abs(duration - target_minutes) / target_minutes, 1.0) if duration > 0 else 0.0
            emotion_recovery = max(0.0, (emotion + 2) / 4)

            score = round((0.4 * engagement + 0.35 * pace_fit + 0.25 * emotion_recovery) * 100)
            scores.append(score)
        return scores

    def _classify_note_emotion(self, text: str) -> dict:
        content = (text or "").lower()
        rules = [
            ("挫败", -2, ["听不懂", "好难", "崩溃", "烦", "卡住", "完全不会", "蒙了"]),
            ("困惑", -1, ["不懂", "没听清", "什么意思", "为什么", " unsure", "confused", "?", "？"]),
            ("平稳", 0, ["先记一下", "我猜", "好像", "maybe", "感觉"]),
            ("投入", 1, ["懂了", "有点明白", "抓到了", "发现", "原来是", "哦"]),
            ("兴奋", 2, ["太好了", "会了", "好喜欢", "终于", "清楚了", "nice"]),
        ]
        for label, score, keywords in rules:
            if any(keyword in content for keyword in keywords):
                tone = "error" if score < 0 else "primary" if score > 0 else "secondary"
                return {"label": label, "score": score, "tone": tone}
        return {"label": "平稳", "score": 0, "tone": "secondary"}

    def _emotion_bucket_label(self, score: float) -> str:
        if score <= -1.5:
            return "挫败"
        if score < 0:
            return "困惑"
        if score == 0:
            return "平稳"
        if score < 1.5:
            return "投入"
        return "兴奋"

    def _safe_int(self, value, fallback: int) -> int:
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return fallback


lesson_service = LessonService()
