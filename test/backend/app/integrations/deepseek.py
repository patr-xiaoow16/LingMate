from __future__ import annotations

import json
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class DeepSeekClient:
    def is_configured(self) -> bool:
        return bool(settings.deepseek_api_key)

    def _chat_completion(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.is_configured():
            return {"ok": False, "provider": "mock", "model": settings.deepseek_model, "error": "DEEPSEEK_API_KEY not configured"}

        url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": settings.deepseek_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=90.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except Exception as exc:
            return {"ok": False, "provider": "deepseek", "model": settings.deepseek_model, "error": str(exc)}

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "provider": "deepseek",
                "model": settings.deepseek_model,
                "error": "Invalid JSON returned by DeepSeek",
                "raw": content,
            }
        return {"ok": True, "provider": "deepseek", "model": settings.deepseek_model, "data": parsed}

    def generate_analysis(self, transcript: str, source_url: str, title: str) -> dict:
        system_prompt = (
            "You are generating structured analysis for an English listening lesson product. "
            "Return strict JSON only."
        )
        user_prompt = f"""
Generate listening-analysis JSON for this lesson.

Title: {title}
Source URL: {source_url}
Transcript:
{transcript}

Return JSON with keys:
- lessonTitle: string
- lessonMeta: string
- summaryPills: string[]
- lessonChips: string[]
- modulePlan: array of 7 objects with label, desc, tone
"""
        result = self._chat_completion(system_prompt, user_prompt)
        if not result.get("ok"):
            return result
        return {
            "ok": True,
            "provider": result["provider"],
            "model": result["model"],
            "analysis": result["data"],
        }

    def generate_modules(self, transcript: str, analysis: dict) -> dict:
        system_prompt = (
            "You are generating structured module JSON for an English listening product. "
            "Return strict JSON only. Keep the shape concise but compatible with an 8-module workspace."
        )
        user_prompt = f"""
Transcript:
{transcript}

Analysis summary:
{json.dumps(analysis, ensure_ascii=False)}

Return JSON with key:
- modules: array of 8 module objects

Each module must include:
- index
- slug
- name
- sidebar
- headerTitle
- headerDesc
- topCard
- leftCard
- rightCard
- coachCards

The structure should be compatible with a Vue renderer expecting arrays/strings/objects similar to a learning workspace.
"""
        result = self._chat_completion(system_prompt, user_prompt)
        if not result.get("ok"):
            return result
        return {
            "ok": True,
            "provider": result["provider"],
            "model": result["model"],
            "modules": result["data"].get("modules"),
        }

    def generate_feedback(self, module_key: str, user_input: str, lesson_context: dict) -> dict:
        system_prompt = "You are an English learning AI coach. Return strict JSON only."
        user_prompt = f"""
Module: {module_key}
User input: {user_input}
Lesson context: {json.dumps(lesson_context, ensure_ascii=False)}

Return JSON with:
- reply: string
- suggestions: string[]
"""
        result = self._chat_completion(system_prompt, user_prompt)
        if not result.get("ok"):
            return result
        return {
            "ok": True,
            "provider": result["provider"],
            "model": result["model"],
            "feedback": result["data"],
        }

    def generate_note_feedback(self, module_key: str, user_input: str, lesson_context: dict) -> dict:
        system_prompt = (
            "你是一位陪伴式听力老师。"
            "用户会写下自己的听力随记、猜测、困惑或感受。"
            "你只做简短中文回应，像聊天，不要写成长段分析。"
            "回复控制在 1-2 句，总字数尽量少于 45 个中文字符。"
            "语气温和、接住用户，但不要啰嗦。"
            "Return strict JSON only."
        )
        user_prompt = f"""
当前模块: {module_key}
用户随记: {user_input}
课程上下文: {json.dumps(lesson_context, ensure_ascii=False)}

返回 JSON:
- reply: string
- suggestions: string[]  // 对于随记这里默认返回空数组
"""
        result = self._chat_completion(system_prompt, user_prompt)
        if not result.get("ok"):
            return result
        return {
            "ok": True,
            "provider": result["provider"],
            "model": result["model"],
            "feedback": result["data"],
        }


deepseek_client = DeepSeekClient()
