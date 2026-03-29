from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


@dataclass
class StorageService:
    def save_uploaded_file(self, file_name: str, content: bytes) -> dict:
        uploads_dir = Path(settings.uploads_dir)
        uploads_dir.mkdir(parents=True, exist_ok=True)

        safe_name = self._sanitize_name(file_name or "audio.bin")
        stored_name = f"{uuid4().hex[:12]}-{safe_name}"
        file_path = uploads_dir / stored_name
        file_path.write_bytes(content)

        return {
            "file_name": safe_name,
            "stored_name": stored_name,
            "path": str(file_path),
            "upload_url": f"upload://{stored_name}",
        }

    def public_media_url(self, file_path: str) -> str | None:
        if not file_path:
            return None
        path = Path(file_path)
        uploads_dir = Path(settings.uploads_dir).resolve()
        try:
            resolved = path.resolve()
        except FileNotFoundError:
            resolved = path
        if uploads_dir not in resolved.parents and resolved != uploads_dir:
            return None
        return f"/media/{resolved.name}"

    def _sanitize_name(self, file_name: str) -> str:
        return "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in file_name)


storage_service = StorageService()
