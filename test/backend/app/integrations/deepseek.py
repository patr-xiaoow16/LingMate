from app.core.config import settings


class DeepSeekClient:
    def __init__(self) -> None:
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.api_key = settings.deepseek_api_key

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_course_structure(self, transcript: str) -> dict:
        return {
            "provider": "deepseek" if self.is_configured() else "mock",
            "model": self.model,
            "configured": self.is_configured(),
            "transcriptPreview": transcript[:160],
        }


deepseek_client = DeepSeekClient()
