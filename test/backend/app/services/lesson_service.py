from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
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
from app.models.lesson import Lesson, LessonEvent
from app.schemas.lesson import ImportMaterialRequest, ModuleActionRequest


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

    def _get_lesson(self, db: Session, lesson_id: str) -> Lesson:
        lesson = db.execute(select(Lesson).where(Lesson.lesson_id == lesson_id)).scalar_one_or_none()
        if not lesson:
            raise LessonNotFoundError(f"Lesson not found: {lesson_id}")
        return lesson

    def _record_event(self, db: Session, lesson_id: str, event_type: str, payload: dict | None = None) -> None:
        db.add(LessonEvent(lesson_id=lesson_id, event_type=event_type, payload_json=payload or {}))

    def _created_seconds_ago(self, lesson: Lesson) -> float:
        created_at = lesson.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - created_at).total_seconds())

    def import_material(self, db: Session, payload: ImportMaterialRequest) -> dict:
        source = payload.source
        url = source.url.strip()
        if not self._is_valid_url(url):
            return {"lessonId": None, "status": "error", "message": "请输入有效的 http/https 链接。"}

        lesson = Lesson(
            lesson_id=self._next_lesson_id(),
            status="processing",
            source_type=source.type,
            source_url=url,
            provider=settings.analysis_provider,
            title="Why Saying “I’m not feeling great” Sounds Softer",
            analysis_json=analysis_fixture(),
            module_content_json={"modules": modules_fixture()},
            report_json=report_fixture(),
            progress_json=self._build_default_progress(),
        )
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "lesson_imported", {"source_url": url})
        db.commit()
        return {
            "lessonId": lesson.lesson_id,
            "status": lesson.status,
            "redirect": f"/analysis/{lesson.lesson_id}",
            "provider": lesson.provider,
        }

    def get_analysis(self, db: Session, lesson_id: str) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        payload = deepcopy(lesson.analysis_json or analysis_fixture())
        steps_blueprint = analysis_steps_fixture()

        elapsed = self._created_seconds_ago(lesson)
        total_duration = sum(step["duration"] for step in steps_blueprint)
        remaining = elapsed
        completed = 0
        active_step_title = None
        built_steps = []

        for step in steps_blueprint:
            built = {"index": step["index"], "title": step["title"], "etaSeconds": step["duration"]}
            if remaining >= step["duration"]:
                built["status"] = "done"
                built["note"] = step["done"]
                built["stepProgress"] = 100
                remaining -= step["duration"]
                completed += 1
            elif active_step_title is None:
                progress_ratio = 0 if step["duration"] == 0 else remaining / step["duration"]
                built["status"] = "active"
                built["note"] = step["pending"]
                built["stepProgress"] = max(6, min(96, int(progress_ratio * 100)))
                active_step_title = step["title"]
                remaining = 0
            else:
                built["status"] = "todo"
                built["note"] = "等待前序步骤完成"
                built["stepProgress"] = 0
            built_steps.append(built)

        analysis_ready = completed >= len(steps_blueprint)
        overall_progress = min(100, int((min(elapsed, total_duration) / total_duration) * 100))

        payload["pipeline"]["steps"] = built_steps
        payload["pipeline"]["progress"] = overall_progress
        payload["pipeline"]["activeStepTitle"] = active_step_title if not analysis_ready else "完成"
        payload["analysisReady"] = analysis_ready
        payload["status"] = "ready" if analysis_ready else "processing"
        payload["lesson"]["badge"] = "Ready" if analysis_ready else "处理中"
        payload["mockMeta"] = {
            "elapsedSeconds": round(elapsed, 1),
            "totalDurationSeconds": round(total_duration, 1),
            "currentStep": active_step_title if not analysis_ready else "完成",
            "source": {"type": lesson.source_type, "url": lesson.source_url},
            "provider": lesson.provider,
        }

        if analysis_ready and lesson.status == "processing":
            lesson.status = "analysis_ready"
            db.add(lesson)
            self._record_event(db, lesson.lesson_id, "analysis_ready")
            db.commit()

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
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        if module_index is not None and 1 <= module_index <= 8:
            progress["currentModule"] = module_index
            lesson.progress_json = progress
            db.add(lesson)
            db.commit()

        payload = workspace_fixture()
        payload["modules"] = deepcopy((lesson.module_content_json or {}).get("modules", modules_fixture()))
        payload["progress"]["current"] = progress["currentModule"]
        payload["progress"]["completed"] = len(progress["completedModules"])
        payload["completedModules"] = progress["completedModules"][:]
        payload["interaction"] = {"lastAction": progress["lastAction"]}
        return {"lessonId": lesson_id, **payload}

    def coach_module(self, db: Session, lesson_id: str, module_key: str, payload: ModuleActionRequest) -> dict:
        lesson = self._get_lesson(db, lesson_id)
        progress = deepcopy(lesson.progress_json or self._build_default_progress())
        message = payload.message or "请给我下一步建议"
        progress["lastAction"] = f"AI coach 已响应模块 {module_key}。"
        lesson.progress_json = progress
        db.add(lesson)
        self._record_event(db, lesson.lesson_id, "coach_module", {"module_key": module_key, "message": message})
        db.commit()
        return {
            "lessonId": lesson_id,
            "module": {"slug": module_key},
            "reply": f"围绕模块 {module_key} 继续：先保持当前节奏，再把你最不稳的一句重复 2 遍，最后迁移到自己的场景里。你的输入是：{message}",
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
        return {"lessonId": lesson_id, **deepcopy(lesson.report_json or report_fixture())}

    def get_review_payload(self, db: Session) -> dict:
        _ = db
        return deepcopy(report_fixture())


lesson_service = LessonService()
