from __future__ import annotations

from copy import deepcopy

from .mock_data import build_base_lesson, build_home_payload, build_imported_lesson, build_review_payload


class LingMateRepository:
    def __init__(self) -> None:
        self._lessons: dict[str, dict] = {}
        base = build_base_lesson()
        self._lessons[base["id"]] = base
        self._sequence = 1

    def list_lessons(self) -> list[dict]:
        return list(self._lessons.values())

    def get_home(self) -> dict:
        return build_home_payload(self.list_lessons())

    def import_lesson(self, source_type: str, source_value: str, goal: str | None = None) -> dict:
        self._sequence += 1
        lesson_id = f"lesson-imported-{self._sequence}"
        lesson = build_imported_lesson(lesson_id, source_type, source_value, goal)
        self._lessons[lesson_id] = lesson
        return {
            "message": "材料已完成预处理，正在进入 AI 分析页。",
            "lesson_id": lesson_id,
            "analysis_url": f"/analysis/{lesson_id}",
        }

    def get_analysis(self, lesson_id: str) -> dict:
        lesson = self._get_lesson(lesson_id)
        analysis = lesson["analysis"]
        return {
            "lesson": self._lesson_summary(lesson),
            "headline": analysis["headline"],
            "summary_cards": deepcopy(analysis["summary_cards"]),
            "processing_steps": deepcopy(analysis["processing_steps"]),
            "transcript": deepcopy(analysis["transcript"]),
            "voice_signals": deepcopy(analysis["voice_signals"]),
            "recommendations": deepcopy(analysis["recommendations"]),
            "plan": deepcopy(analysis["plan"]),
        }

    def start_lesson(self, lesson_id: str) -> dict:
        lesson = self._get_lesson(lesson_id)
        lesson["status"] = "learning"
        lesson["workspace"]["modules"][0]["status"] = "current"
        return {
            "message": "学习工作台已准备好。",
            "workspace_url": f"/workspace/{lesson_id}/immersive-listening",
        }

    def get_workspace(self, lesson_id: str, module_key: str | None = None) -> dict:
        lesson = self._get_lesson(lesson_id)
        modules = lesson["workspace"]["modules"]
        active_module = next((module for module in modules if module["key"] == module_key), None) if module_key else None
        if active_module is None:
            active_module = next((module for module in modules if module["status"] == "current"), modules[0])

        sidebar_modules = []
        completed_count = lesson["completed_modules"]
        for module in modules:
            state = module["status"]
            if module["key"] == active_module["key"]:
                state = "current"
            sidebar_modules.append(
                {
                    "key": module["key"],
                    "step": module["step"],
                    "title": module["title"],
                    "duration": module["duration"],
                    "status": state,
                }
            )

        return {
            "lesson": self._lesson_summary(lesson),
            "shell": {
                "eyebrow": lesson["workspace"]["eyebrow"],
                "heading": lesson["workspace"]["heading"],
                "subheading": lesson["workspace"]["subheading"],
                "stats": deepcopy(lesson["workspace"]["stats"]),
                "completion": {"completed": completed_count, "total": len(modules)},
            },
            "sidebar": {
                "lesson_card": deepcopy(lesson["workspace"]["lesson_card"]),
                "modules": sidebar_modules,
            },
            "active_module": deepcopy(active_module),
        }

    def coach_module(self, lesson_id: str, module_key: str, user_input: str) -> dict:
        lesson = self._get_lesson(lesson_id)
        module = self._get_module(lesson, module_key)
        clean_input = (user_input or "").strip()

        if not clean_input:
            summary = "先写一个最直觉的答案也没关系，AI 会根据你的版本继续往自然表达上推。"
            bullets = [
                "先说状态，再说需求，再补一个负责的后续动作。",
                "保持句子短而清楚，比堆复杂词更重要。",
            ]
            score = 68
        else:
            score = min(96, 72 + len(clean_input) // 6)
            bullets = [
                f"你已经开始围绕“{module['title'][:6]}”这个目标组织语言。",
                "如果想更像真实口语，可以再加入一个缓冲词或补偿动作。",
                "试着把句子压缩到 2-3 句，会更像即时沟通场景。",
            ]
            summary = f"你的输入“{clean_input[:48]}”已经抓住了核心信息，下一步重点是让语气更自然、结构更清晰。"

        return {
            "response": {
                "headline": f"AI 教练反馈 · {module['english_title']}",
                "score": score,
                "summary": summary,
                "bullets": bullets,
                "next_step": module["primary_action"],
            }
        }

    def complete_module(self, lesson_id: str, module_key: str) -> dict:
        lesson = self._get_lesson(lesson_id)
        modules = lesson["workspace"]["modules"]
        active_index = next(index for index, module in enumerate(modules) if module["key"] == module_key)
        modules[active_index]["status"] = "completed"
        modules[active_index]["progress"] = 100
        lesson["completed_modules"] = len([module for module in modules if module["status"] == "completed"])

        next_module = None
        if active_index + 1 < len(modules):
            next_module = modules[active_index + 1]["key"]
            if modules[active_index + 1]["status"] != "completed":
                modules[active_index + 1]["status"] = "current"
        lesson["status"] = "review_ready" if next_module is None else "learning"

        return {
            "message": "模块进度已保存。",
            "next_module": next_module,
            "completed": lesson["completed_modules"],
            "total": len(modules),
        }

    def get_report(self, lesson_id: str) -> dict:
        lesson = self._get_lesson(lesson_id)
        report = lesson["report"]
        return {
            "lesson": self._lesson_summary(lesson),
            "hero": deepcopy(report["hero"]),
            "metrics": deepcopy(report["metrics"]),
            "weaknesses": deepcopy(report["weaknesses"]),
            "weekly_hours": deepcopy(report["weekly_hours"]),
            "journal": deepcopy(report["journal"]),
            "note_card": deepcopy(report["note_card"]),
        }

    def get_review(self, lesson_id: str | None = None) -> dict:
        active_id = lesson_id or self.list_lessons()[-1]["id"]
        return build_review_payload(self.list_lessons(), active_id)

    def _lesson_summary(self, lesson: dict) -> dict:
        return {
            "id": lesson["id"],
            "title": lesson["title"],
            "topic_cn": lesson["topic_cn"],
            "source_label": lesson["source_label"],
            "level": lesson["level"],
            "length": lesson["length"],
            "goal": lesson["goal"],
            "status": lesson["status"],
        }

    def _get_module(self, lesson: dict, module_key: str) -> dict:
        for module in lesson["workspace"]["modules"]:
            if module["key"] == module_key:
                return module
        raise KeyError(f"Unknown module key: {module_key}")

    def _get_lesson(self, lesson_id: str) -> dict:
        try:
            return self._lessons[lesson_id]
        except KeyError as exc:
            raise KeyError(f"Unknown lesson id: {lesson_id}") from exc
