from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BASE_DIR / "lingmate_app.db"
DEFAULT_UPLOADS_DIR = BASE_DIR / "storage" / "uploads"


class Settings(BaseSettings):
    app_name: str = "LingMate Backend"
    app_version: str = "0.1.0"
    app_env: str = "development"
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    analysis_provider: str = "mock"
    task_worker_poll_interval_seconds: float = 1.0
    task_worker_enabled: bool = True
    youtube_transcript_langs: list[str] = ["en", "en-US", "en-GB"]
    ytdlp_cookies_from_browser: str = ""
    ytdlp_cookiefile: str = ""
    transcript_extract_timeout_seconds: int = 0
    deepseek_generation_timeout_seconds: int = 90
    uploads_dir: str = str(DEFAULT_UPLOADS_DIR)
    whisper_model_size: str = "tiny"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_language: str = "en"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
