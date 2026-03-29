from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import multiprocessing
import re

from app.core.config import settings
from app.content.fixtures import analysis_fixture, modules_fixture, report_fixture
from app.integrations.deepseek import deepseek_client


def _analysis_worker(queue, transcript: str, source_url: str, title: str) -> None:
    queue.put(deepseek_client.generate_analysis(transcript=transcript, source_url=source_url, title=title))


def _modules_worker(queue, transcript: str, analysis: dict) -> None:
    queue.put(deepseek_client.generate_modules(transcript=transcript, analysis=analysis))


def _feedback_worker(queue, module_key: str, user_input: str, lesson_context: dict) -> None:
    queue.put(
        deepseek_client.generate_feedback(
            module_key=module_key,
            user_input=user_input,
            lesson_context=lesson_context,
        )
    )


def _note_feedback_worker(queue, module_key: str, user_input: str, lesson_context: dict) -> None:
    queue.put(
        deepseek_client.generate_note_feedback(
            module_key=module_key,
            user_input=user_input,
            lesson_context=lesson_context,
        )
    )


@dataclass
class GenerationService:
    def generate_analysis(self, transcript: str, source_url: str, title: str) -> dict:
        response = self._run_with_timeout(
            _analysis_worker,
            transcript=transcript,
            source_url=source_url,
            title=title,
        )
        if response.get("ok") and response.get("analysis"):
            analysis = deepcopy(analysis_fixture())
            generated = response["analysis"]
            analysis["summary"]["pills"] = generated.get("summaryPills", analysis["summary"]["pills"])
            analysis["lesson"]["title"] = generated.get("lessonTitle", title)
            analysis["lesson"]["meta"] = generated.get("lessonMeta", analysis["lesson"]["meta"])
            analysis["lesson"]["transcript"] = transcript
            analysis["lesson"]["chips"] = generated.get("lessonChips", analysis["lesson"]["chips"])
            analysis["modulePlan"] = generated.get("modulePlan", analysis["modulePlan"])
            analysis["llmMeta"] = {
                "provider": response.get("provider"),
                "model": response.get("model"),
                "mode": "live",
            }
            return analysis

        analysis = deepcopy(analysis_fixture())
        analysis["lesson"]["title"] = title
        analysis["lesson"]["transcript"] = transcript
        analysis["llmMeta"] = {
            "provider": response.get("provider", "mock"),
            "model": response.get("model", "deepseek-chat"),
            "mode": "fallback",
        }
        return analysis

    def generate_modules(self, transcript: str, analysis: dict) -> dict:
        response = self._run_with_timeout(_modules_worker, transcript=transcript, analysis=analysis)
        modules = response.get("modules") if response.get("ok") else None
        if not modules:
            return {"modules": deepcopy(modules_fixture()), "llmMeta": response}
        return {
            "modules": self.adapt_modules_for_workspace(modules, transcript=transcript, analysis=analysis),
            "llmMeta": response,
        }

    def generate_feedback(self, module_key: str, user_input: str, lesson_context: dict) -> dict:
        response = self._run_with_timeout(
            _feedback_worker,
            module_key=module_key,
            user_input=user_input,
            lesson_context=lesson_context,
        )
        if response.get("ok") and response.get("feedback"):
            return response["feedback"] | {
                "provider": response.get("provider"),
                "model": response.get("model"),
            }
        return {
            "reply": f"围绕模块 {module_key} 继续：先保持当前节奏，再把你最不稳的一句重复 2 遍，最后迁移到自己的场景里。你的输入是：{user_input}",
            "suggestions": ["先保持原句骨架", "再替换一个场景元素", "最后读一遍检查语气"],
            "provider": response.get("provider", "mock"),
            "model": response.get("model", "deepseek-chat"),
        }

    def generate_note_feedback(self, module_key: str, user_input: str, lesson_context: dict) -> dict:
        response = self._run_with_timeout(
            _note_feedback_worker,
            module_key=module_key,
            user_input=user_input,
            lesson_context=lesson_context,
        )
        if response.get("ok") and response.get("feedback"):
            reply = str(response["feedback"].get("reply", "")).strip()
            return {
                "reply": reply[:60] or "我接住了，我们继续往下听。",
                "suggestions": [],
                "provider": response.get("provider"),
                "model": response.get("model"),
            }
        return {
            "reply": "我接住了。先继续听，等会儿我们再回来看这句。",
            "suggestions": [],
            "provider": response.get("provider", "mock"),
            "model": response.get("model", "deepseek-chat"),
        }

    def generate_report(self, completed_modules: int, expressions: list[str]) -> dict:
        report = deepcopy(report_fixture())
        report["shareCard"]["body"] = (
            f"本次材料：Soft language at work\n"
            f"掌握表达：{' / '.join(expressions[:3]) if expressions else 'not feeling great / heads-up / take the afternoon off'}\n"
            f"完成模块：{completed_modules} / 8"
        )
        report["metrics"][2]["value"] = f"{completed_modules:.1f}" if isinstance(completed_modules, float) else str(completed_modules)
        return report

    def adapt_modules_for_workspace(self, modules: list[dict] | None, transcript: str = "", analysis: dict | None = None) -> list[dict]:
        templates = deepcopy(modules_fixture())
        if not modules:
            return templates

        indexed_modules: dict[int, dict] = {}
        for position, module in enumerate(modules, start=1):
            if not isinstance(module, dict):
                continue
            module_index = self._normalize_index(module.get("index"), fallback=position)
            indexed_modules[module_index] = module

        lesson_chips = ((analysis or {}).get("lesson") or {}).get("chips") or []

        adapted_modules = []
        for template_index, template in enumerate(templates, start=1):
            generated = indexed_modules.get(template_index) or {}
            adapted_modules.append(
                self._adapt_module_by_index(
                    template_index=template_index,
                    template=template,
                    generated=generated,
                    lesson_chips=lesson_chips,
                    transcript=transcript,
                )
            )

        return adapted_modules

    def _adapt_module_by_index(
        self,
        *,
        template_index: int,
        template: dict,
        generated: dict,
        lesson_chips: list[str],
        transcript: str,
    ) -> dict:
        adapted = deepcopy(template)
        adapted["index"] = template_index
        adapted["slug"] = generated.get("slug", adapted["slug"])
        adapted["name"] = generated.get("name", adapted["name"])
        adapted["sidebar"] = generated.get("sidebar", adapted["sidebar"])
        adapted["headerTitle"] = generated.get("headerTitle", adapted["headerTitle"])
        adapted["headerDesc"] = generated.get("headerDesc", adapted["headerDesc"])
        adapted["coachCards"] = self._adapt_coach_cards(adapted.get("coachCards", []), generated.get("coachCards"))

        if template_index == 1:
            return self._map_immersive_listening(adapted, generated, lesson_chips, transcript)
        if template_index == 2:
            return self._map_vocabulary_module(adapted, generated, lesson_chips, transcript)
        if template_index == 3:
            return self._map_chinglish_module(adapted, generated)
        if template_index == 4:
            return self._map_scene_module(adapted, generated)
        if template_index == 5:
            return self._map_listening_decoder_module(adapted, generated, transcript)
        if template_index == 6:
            return self._map_subtext_module(adapted, generated)
        if template_index == 7:
            return self._map_pattern_module(adapted, generated)
        if template_index == 8:
            return self._map_output_module(adapted, generated)

        adapted["topCard"] = self._adapt_top_card(adapted["topCard"], generated.get("topCard"), lesson_chips, transcript)
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_immersive_listening(self, adapted: dict, generated: dict, lesson_chips: list[str], transcript: str) -> dict:
        top = adapted["topCard"]
        top["title"] = generated.get("topCard", {}).get("title", top["title"])
        intro = self._collapse_text(generated.get("topCard", {})) or top["subtitle"]
        top["subtitle"] = intro
        top["pills"] = lesson_chips[:2] if lesson_chips else top["pills"]
        top["sections"][1]["content"] = intro
        overview_questions = self._split_to_items(self._collapse_text(generated.get("rightCard", {})), limit=3)
        if overview_questions:
            top["sections"][2]["right"]["questions"] = overview_questions
        tone_hints = self._split_to_items(self._collapse_text(generated.get("leftCard", {})), limit=3)
        if tone_hints:
            top["sections"][2]["left"]["content"] = tone_hints[0]
            top["sections"][2]["left"]["chips"] = lesson_chips[:3] if lesson_chips else tone_hints[:3]
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        if transcript:
            adapted["leftCard"]["items"] = self._split_to_items(transcript, limit=3)
        return adapted

    def _map_vocabulary_module(self, adapted: dict, generated: dict, lesson_chips: list[str], transcript: str) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        generated_left = generated.get("leftCard", {})
        generated_right = generated.get("rightCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        phrases = self._extract_phrases(
            self._collapse_text(generated_top),
            self._collapse_text(generated_left),
            self._collapse_text(generated_right),
            transcript,
        )
        browser = next((section for section in top["sections"] if section.get("type") == "expression-browser"), None)
        if browser and phrases:
            browser["expressions"] = [
                {"phrase": phrase, "cefr": lesson_chips[min(idx, len(lesson_chips) - 1)] if lesson_chips else "B1", "selected": idx == 0}
                for idx, phrase in enumerate(phrases[:5])
            ]
            browser["detail"]["title"] = phrases[0]
            browser["detail"]["body"] = self._collapse_text(generated_left) or browser["detail"]["body"]
            browser["detail"]["chips"] = lesson_chips[:3] if lesson_chips else browser["detail"]["chips"]
            browser["detail"]["examples"] = self._split_to_items(transcript, limit=2)
        input_section = next((section for section in top["sections"] if section.get("type") == "input"), None)
        if input_section:
            input_section["content"] = self._first_sentence(transcript) or self._collapse_text(generated_right) or input_section["content"]
        banner = next((section for section in top["sections"] if section.get("type") == "banner"), None)
        if banner:
            banner["content"] = self._collapse_text(generated_right) or banner["content"]
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated_left)
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated_right)
        adapted["rightCard"]["rows"] = [
            {"label": "高频表达", "meta": str(len(phrases[:5])) if phrases else "3", "tone": "success"},
            {"label": "建议优先学", "meta": phrases[0] if phrases else "核心词块", "tone": "warning"},
            {"label": "例句迁移", "meta": "已生成", "tone": "default"},
        ]
        return adapted

    def _map_chinglish_module(self, adapted: dict, generated: dict) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        compare = next((section for section in top["sections"] if section.get("type") == "compare-list"), None)
        if compare:
            pairs = self._build_compare_pairs(
                self._collapse_text(generated_top),
                self._collapse_text(generated.get("leftCard", {})),
                self._collapse_text(generated.get("rightCard", {})),
            )
            if pairs:
                compare["pairs"] = pairs
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_scene_module(self, adapted: dict, generated: dict) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        scene_grid = next((section for section in top["sections"] if section.get("type") == "scene-grid"), None)
        scene_text = self._collapse_text(generated.get("rightCard", {})) or self._collapse_text(generated_top)
        if scene_grid and scene_text:
            scene_grid["right"]["content"] = scene_text
            scene_grid["left"]["rows"] = [
                {"label": item[:18], "meta": "AI 场景"}
                for item in self._split_to_items(self._collapse_text(generated.get("leftCard", {})), limit=3)
            ] or scene_grid["left"]["rows"]
        input_section = next((section for section in top["sections"] if section.get("type") == "input"), None)
        if input_section:
            input_section["content"] = self._collapse_text(generated.get("leftCard", {})) or input_section["content"]
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_listening_decoder_module(self, adapted: dict, generated: dict, transcript: str) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        panels = [section for section in top["sections"] if section.get("type") == "panel"]
        if panels:
            panels[0]["content"] = self._first_sentence(transcript) or panels[0]["content"]
        if len(panels) > 1:
            panels[1]["content"] = self._collapse_text(generated.get("rightCard", {})) or self._collapse_text(generated.get("leftCard", {})) or panels[1]["content"]
        chips = next((section for section in top["sections"] if section.get("type") == "chips"), None)
        if chips:
            chips["items"] = self._extract_phrases(self._collapse_text(generated.get("leftCard", {})), self._collapse_text(generated.get("rightCard", {})), limit=4)
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_subtext_module(self, adapted: dict, generated: dict) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        tone_section = next((section for section in top["sections"] if section.get("type") == "tone-insight"), None)
        if tone_section:
            tone_section["insightBody"] = self._collapse_text(generated.get("rightCard", {})) or tone_section["insightBody"]
            tone_section["rows"] = [
                {"label": item[:28], "meta": "tone", "tone": "success" if idx == 0 else "default"}
                for idx, item in enumerate(self._split_to_items(self._collapse_text(generated.get("leftCard", {})), limit=3))
            ] or tone_section["rows"]
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_pattern_module(self, adapted: dict, generated: dict) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        panel = next((section for section in top["sections"] if section.get("type") == "pattern-panel"), None)
        if panel:
            pattern_text = self._collapse_text(generated_top) or self._collapse_text(generated.get("rightCard", {}))
            if pattern_text:
                panel["title"] = pattern_text
                panel["chips"] = self._extract_phrases(self._collapse_text(generated.get("leftCard", {})), limit=3)
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _map_output_module(self, adapted: dict, generated: dict) -> dict:
        top = adapted["topCard"]
        generated_top = generated.get("topCard", {})
        top["title"] = generated_top.get("title", top["title"])
        top["subtitle"] = self._collapse_text(generated_top) or top["subtitle"]
        output_layout = next((section for section in top["sections"] if section.get("type") == "output-layout"), None)
        if output_layout:
            output_layout["inputContent"] = self._collapse_text(generated.get("rightCard", {})) or self._collapse_text(generated_top) or output_layout["inputContent"]
            task_items = self._split_to_items(self._collapse_text(generated.get("leftCard", {})), limit=3)
            if task_items:
                output_layout["tasks"] = [
                    {"label": item[:16], "meta": "AI 任务", "tone": "primary" if idx == 0 else "default"}
                    for idx, item in enumerate(task_items)
                ]
        adapted["leftCard"] = self._adapt_side_card(adapted["leftCard"], generated.get("leftCard"))
        adapted["rightCard"] = self._adapt_side_card(adapted["rightCard"], generated.get("rightCard"))
        return adapted

    def _adapt_top_card(self, template_card: dict, generated_card: dict | None, lesson_chips: list[str], transcript: str) -> dict:
        card = deepcopy(template_card)
        if not isinstance(generated_card, dict):
            return card

        card["title"] = generated_card.get("title", card.get("title"))
        if generated_card.get("subtitle"):
            card["subtitle"] = generated_card["subtitle"]
        elif generated_card.get("content"):
            card["subtitle"] = generated_card["content"]

        if lesson_chips and isinstance(card.get("pills"), list):
            card["pills"] = lesson_chips[: max(1, min(len(card["pills"]) or 2, len(lesson_chips)))]

        generated_sections = generated_card.get("sections")
        if isinstance(generated_sections, list) and generated_sections:
            card["sections"] = generated_sections
        elif generated_card.get("content"):
            card["sections"] = self._inject_text_into_sections(card.get("sections", []), generated_card["content"], transcript)

        if isinstance(generated_card.get("actions"), list) and generated_card["actions"]:
            card["actions"] = generated_card["actions"]

        return card

    def _adapt_side_card(self, template_card: dict, generated_card: dict | None) -> dict:
        card = deepcopy(template_card)
        if not isinstance(generated_card, dict):
            return card

        card["title"] = generated_card.get("title", card.get("title"))
        content = self._collapse_text(generated_card)
        items = self._split_to_items(content)

        if content:
            if "body" in card:
                card["body"] = content
            if "panel" in card:
                card["panel"] = content
            if "inputContent" in card:
                card["inputContent"] = content
            if "banner" in card and not card.get("score"):
                card["banner"] = content

        if items and "items" in card:
            card["items"] = items
        if items and "rows" in card:
            card["rows"] = [
                {"label": item[:18], "meta": "AI 提炼", "tone": "default"}
                for item in items[: max(1, len(card["rows"]) if isinstance(card.get("rows"), list) and card["rows"] else 3)]
            ]

        return card

    def _adapt_coach_cards(self, template_cards: list[dict], generated_cards: list[dict] | None) -> list[dict]:
        cards = deepcopy(template_cards)
        if not isinstance(generated_cards, list) or not generated_cards:
            return cards

        if not cards:
            cards = [{"title": "AI Coach", "body": "", "tags": []}]

        for index, generated in enumerate(generated_cards):
            if not isinstance(generated, dict):
                continue
            if index >= len(cards):
                cards.append({"title": "AI Coach", "body": "", "tags": []})
            cards[index]["title"] = generated.get("title", cards[index].get("title"))
            cards[index]["body"] = generated.get("body") or generated.get("content") or cards[index].get("body", "")
            cards[index]["tags"] = generated.get("tags") or cards[index].get("tags", [])
        return cards

    def _inject_text_into_sections(self, sections: list[dict], content: str, transcript: str) -> list[dict]:
        injected = deepcopy(sections)
        if not injected:
            return [{"type": "panel", "label": "AI 解析内容", "tone": "secondary", "content": content}]

        for section in injected:
            if section.get("type") == "panel":
                section["content"] = content
                return injected
            if section.get("type") == "banner":
                section["content"] = content
                return injected
            if section.get("type") == "pattern-panel":
                section["title"] = content
                return injected
            if section.get("type") == "input":
                section["content"] = content
                return injected
            if section.get("type") == "compare-list":
                items = self._split_to_items(content)
                if items:
                    section["pairs"] = [{"wrong": items[0], "right": items[1] if len(items) > 1 else content, "note": "AI 已根据本课材料生成对照提示。"}]
                return injected
            if section.get("type") == "output-layout":
                section["inputContent"] = content
                return injected
            if section.get("type") == "expression-browser":
                expressions = self._split_to_items(content)
                if expressions:
                    section["expressions"] = [
                        {"phrase": item, "cefr": "B1", "selected": idx == 0}
                        for idx, item in enumerate(expressions[:5])
                    ]
                    section["detail"]["title"] = expressions[0]
                    section["detail"]["body"] = content
                    section["detail"]["examples"] = self._split_to_items(transcript)[:2]
                return injected
            if section.get("type") == "scene-grid":
                section["right"]["content"] = content
                return injected
            if section.get("type") == "tone-insight":
                section["insightBody"] = content
                return injected

        injected.insert(0, {"type": "panel", "label": "AI 解析内容", "tone": "secondary", "content": content})
        return injected

    def _split_to_items(self, text: str, limit: int = 4) -> list[str]:
        normalized = re.sub(r"\s+", " ", (text or "")).strip()
        if not normalized:
            return []
        chunks = [piece.strip(" -") for piece in re.split(r"[。\n]|(?<=[.!?])\s+", normalized) if piece.strip(" -")]
        return chunks[:limit] if chunks else [normalized]

    def _first_sentence(self, text: str) -> str:
        items = self._split_to_items(text, limit=1)
        return items[0] if items else ""

    def _extract_phrases(self, *texts: str, limit: int = 5) -> list[str]:
        phrases: list[str] = []
        seen: set[str] = set()
        for text in texts:
            for piece in self._split_to_items(text, limit=limit * 2):
                cleaned = piece.strip().strip(".,;:!?")
                if not cleaned:
                    continue
                lowered = cleaned.lower()
                if lowered in seen:
                    continue
                seen.add(lowered)
                phrases.append(cleaned)
                if len(phrases) >= limit:
                    return phrases
        return phrases

    def _build_compare_pairs(self, *texts: str) -> list[dict]:
        items = self._extract_phrases(*texts, limit=4)
        if len(items) < 2:
            return []
        pairs = []
        for idx in range(0, len(items) - 1, 2):
            wrong = items[idx]
            right = items[idx + 1]
            pairs.append(
                {
                    "wrong": wrong,
                    "right": right,
                    "note": "AI 已把不够自然的表达和更地道的说法放在一起，方便直接对照。",
                }
            )
        return pairs[:3]

    def _collapse_text(self, generated_card: dict) -> str:
        for key in ("body", "content", "subtitle", "panel", "inputContent"):
            value = generated_card.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _normalize_index(self, value, fallback: int) -> int:
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return fallback

    def _run_with_timeout(self, worker, **kwargs) -> dict:
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        process = ctx.Process(target=worker, args=(queue, *kwargs.values()))
        process.start()
        process.join(timeout=settings.deepseek_generation_timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join(timeout=2)
            return {
                "ok": False,
                "provider": "deepseek",
                "model": settings.deepseek_model,
                "error": f"DeepSeek 调用超时（>{settings.deepseek_generation_timeout_seconds}s）",
            }

        if queue.empty():
            return {
                "ok": False,
                "provider": "deepseek",
                "model": settings.deepseek_model,
                "error": "DeepSeek 没有返回可用结果。",
            }

        return queue.get()


generation_service = GenerationService()
