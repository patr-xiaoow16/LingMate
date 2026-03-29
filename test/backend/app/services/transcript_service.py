from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover - optional until dependency is installed
    WhisperModel = None

try:
    import yt_dlp
except ImportError:  # pragma: no cover - optional until dependency is installed
    yt_dlp = None


class TranscriptUnavailableError(RuntimeError):
    def __init__(self, message: str, code: str = "transcript_unavailable", raw_error: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.raw_error = raw_error or message


@dataclass
class TranscriptService:
    def build_transcript_from_source(self, source_url: str, provided_transcript: str | None = None) -> dict:
        transcript = (provided_transcript or "").strip()
        if transcript:
            return {
                "title": "Imported transcript lesson",
                "transcript": transcript,
                "segments": self._split_segments(transcript),
                "meta": {"mode": "provided_transcript"},
            }

        if self._is_youtube_url(source_url):
            return self._build_from_youtube(source_url)

        lower_url = source_url.lower()
        if lower_url.startswith("upload://") or lower_url.endswith((".mp3", ".wav", ".m4a", ".mp4", ".aac", ".flac")):
            return self._build_from_uploaded_audio(source_url)
        if "podcast" in lower_url or "apple" in lower_url:
            transcript = (
                "I am not feeling great today, so I might need to take the afternoon off. "
                "I just wanted to give you a heads-up before the meeting starts. "
                "I should still be able to send the notes, but I may need a little extra time."
            )
            title = "Soft language at work"
        elif "ted" in lower_url:
            transcript = (
                "Small habits work because they lower the cost of starting. "
                "When a behavior feels easy, we repeat it more often, and repetition is what builds change."
            )
            title = "Tiny habits that actually stick"
        else:
            transcript = (
                "The speaker is explaining a situation in a calm and polite tone. "
                "The key point is not only the literal meaning, but also how the message is softened for the listener."
            )
            title = "Imported listening material"

        return {
            "title": title,
            "transcript": transcript,
            "segments": self._split_segments(transcript),
            "meta": {"mode": "seeded_from_url"},
        }

    def _build_from_uploaded_audio(self, source_url: str) -> dict:
        if WhisperModel is None:
            raise TranscriptUnavailableError("缺少 faster-whisper 依赖，当前无法转写本地音频。", code="missing_faster_whisper")

        audio_path = Path(source_url)
        if not audio_path.exists():
            raise TranscriptUnavailableError("上传的音频文件不存在或已丢失，请重新上传。", code="uploaded_audio_missing")

        print(
            f"[LingMate][Whisper] 准备加载 Whisper 模型：model={settings.whisper_model_size} "
            f"device={settings.whisper_device} compute={settings.whisper_compute_type}"
        )
        print("[LingMate][Whisper] 正在下载 Whisper 模型（如果本机已有缓存，会直接复用）")
        model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        print("[LingMate][Whisper] 模型下载完成 / 模型加载完成")
        print(f"[LingMate][Whisper] 开始转写音频：{audio_path.name}")
        segments, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
            language=settings.whisper_language or None,
        )
        raw_segments = list(segments)
        print(f"[LingMate][Whisper] 音频转写完成，原始分段数：{len(raw_segments)}")
        segment_rows = []
        for index, segment in enumerate(raw_segments, start=1):
            text = (segment.text or "").strip()
            if not text:
                continue
            segment_rows.append(
                {
                    "segment_index": index,
                    "start_ms": int(segment.start * 1000),
                    "end_ms": int(segment.end * 1000),
                    "text": text,
                    "speaker": "speaker_1",
                }
            )

        if not segment_rows:
            raise TranscriptUnavailableError(
                "音频转写完成，但没有识别出有效英文语音内容。请确认上传的是清晰的英文音频。",
                code="uploaded_audio_empty_transcript",
            )

        transcript = " ".join(segment["text"] for segment in segment_rows)
        print(f"[LingMate][Whisper] 已整理有效 transcript 分段：{len(segment_rows)}")
        return {
            "title": audio_path.stem or "Uploaded audio material",
            "transcript": transcript,
            "segments": segment_rows,
            "meta": {
                "mode": "uploaded_audio_asr",
                "language": getattr(info, "language", settings.whisper_language),
                "language_probability": getattr(info, "language_probability", None),
                "model_size": settings.whisper_model_size,
            },
        }

    def _build_from_youtube(self, source_url: str) -> dict:
        if yt_dlp is None:
            raise TranscriptUnavailableError("缺少 yt-dlp 依赖，无法解析 YouTube 字幕。", code="missing_ytdlp")

        info = self._extract_youtube_info(source_url)
        title = info.get("title") or "YouTube material"
        subtitles = info.get("subtitles") or {}
        automatic_captions = info.get("automatic_captions") or {}

        track = self._pick_caption_track(subtitles, "subtitles") or self._pick_caption_track(automatic_captions, "automatic_captions")
        if not track:
            raise TranscriptUnavailableError(
                "这个 YouTube 视频没有可用的英文字幕或自动字幕。当前版本暂不支持无字幕视频自动转写，请换一个带字幕的视频，或继续让我接入音频转写。",
                code="youtube_caption_missing",
            )

        caption_text = self._download_caption_text(track["url"])
        segments = self._parse_vtt(caption_text)
        if not segments:
            raise TranscriptUnavailableError("YouTube 字幕解析失败，未能提取出可用 transcript。", code="youtube_caption_parse_failed")

        transcript = " ".join(segment["text"] for segment in segments)
        return {
            "title": title,
            "transcript": transcript,
            "segments": segments,
            "meta": {
                "mode": "youtube_caption",
                "caption_language": track["language"],
                "caption_source": track["source"],
                "webpage_url": info.get("webpage_url", source_url),
            },
        }

    def _extract_youtube_info(self, source_url: str) -> dict:
        options = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "socket_timeout": 15,
            "retries": 1,
        }
        if settings.ytdlp_cookies_from_browser:
            options["cookiesfrombrowser"] = (settings.ytdlp_cookies_from_browser,)
        if settings.ytdlp_cookiefile:
            options["cookiefile"] = settings.ytdlp_cookiefile
        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                return ydl.extract_info(source_url, download=False)
            except Exception as exc:
                humanized = self._humanize_youtube_error(str(exc))
                raise TranscriptUnavailableError(
                    humanized["message"],
                    code=humanized["code"],
                    raw_error=str(exc),
                ) from exc

    def _pick_caption_track(self, tracks_by_lang: dict, source_name: str) -> dict | None:
        for language in settings.youtube_transcript_langs:
            candidates = tracks_by_lang.get(language) or []
            vtt = next((item for item in candidates if item.get("ext") == "vtt" and item.get("url")), None)
            if vtt:
                return {
                    "language": language,
                    "url": vtt["url"],
                    "source": source_name,
                }
            first = next((item for item in candidates if item.get("url")), None)
            if first:
                return {
                    "language": language,
                    "url": first["url"],
                    "source": source_name,
                }
        return None

    def _download_caption_text(self, caption_url: str) -> str:
        with httpx.Client(timeout=60.0) as client:
            response = client.get(caption_url)
            response.raise_for_status()
            return response.text

    def _parse_vtt(self, text: str) -> list[dict]:
        lines = text.splitlines()
        segments = []
        current_text: list[str] = []
        start_ms = 0
        end_ms = 0
        segment_index = 0

        for raw_line in lines:
            line = raw_line.strip("\ufeff").strip()
            if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
                if current_text:
                    cleaned = self._clean_caption_text(" ".join(current_text))
                    if cleaned:
                        segment_index += 1
                        segments.append(
                            {
                                "segment_index": segment_index,
                                "start_ms": start_ms,
                                "end_ms": end_ms,
                                "text": cleaned,
                                "speaker": "speaker_1",
                            }
                        )
                    current_text = []
                continue

            if "-->" in line:
                start_raw, end_raw = [part.strip() for part in line.split("-->", 1)]
                start_ms = self._parse_timestamp_ms(start_raw)
                end_ms = self._parse_timestamp_ms(end_raw.split(" ")[0])
                continue

            if line.isdigit():
                continue

            current_text.append(line)

        if current_text:
            cleaned = self._clean_caption_text(" ".join(current_text))
            if cleaned:
                segment_index += 1
                segments.append(
                    {
                        "segment_index": segment_index,
                        "start_ms": start_ms,
                        "end_ms": end_ms,
                        "text": cleaned,
                        "speaker": "speaker_1",
                    }
                )
        return self._dedupe_segments(segments)

    def _dedupe_segments(self, segments: list[dict]) -> list[dict]:
        deduped = []
        previous_text = None
        for segment in segments:
            if segment["text"] == previous_text:
                continue
            deduped.append(segment)
            previous_text = segment["text"]
        return deduped

    def _clean_caption_text(self, text: str) -> str:
        text = unescape(text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _parse_timestamp_ms(self, value: str) -> int:
        pieces = value.replace(",", ".").split(":")
        if len(pieces) == 3:
            hours, minutes, seconds = pieces
        elif len(pieces) == 2:
            hours = "0"
            minutes, seconds = pieces
        else:
            return 0
        sec_parts = seconds.split(".")
        whole_seconds = int(sec_parts[0])
        millis = int((sec_parts[1] if len(sec_parts) > 1 else "0").ljust(3, "0")[:3])
        return (int(hours) * 3600 + int(minutes) * 60 + whole_seconds) * 1000 + millis

    def _split_segments(self, transcript: str) -> list[dict]:
        parts = [part.strip() for part in transcript.replace("?", ".").replace("!", ".").split(".") if part.strip()]
        segments = []
        current_ms = 0
        for index, part in enumerate(parts, start=1):
            duration = max(2400, len(part.split()) * 450)
            segments.append(
                {
                    "segment_index": index,
                    "start_ms": current_ms,
                    "end_ms": current_ms + duration,
                    "text": part + ".",
                    "speaker": "speaker_1",
                }
            )
            current_ms += duration
        return segments

    def _is_youtube_url(self, source_url: str) -> bool:
        netloc = urlparse(source_url).netloc.lower()
        return "youtube.com" in netloc or "youtu.be" in netloc

    def _humanize_youtube_error(self, raw_error: str) -> dict:
        text = (raw_error or "").strip()
        lower = text.lower()

        if "sign in to confirm you’re not a bot" in lower or "sign in to confirm you're not a bot" in lower:
            return {
                "code": "youtube_auth_required",
                "message": "这个 YouTube 视频当前需要登录态才能读取字幕。请先登录 YouTube，再重试分析。",
            }

        if "video unavailable" in lower:
            return {"code": "youtube_video_unavailable", "message": "这个 YouTube 视频当前不可访问，可能已下架、私有或受地区限制。"}

        if "private video" in lower:
            return {"code": "youtube_private_video", "message": "这个 YouTube 视频是私有视频，当前无法分析。"}

        if "members-only" in lower or "members only" in lower:
            return {"code": "youtube_members_only", "message": "这个 YouTube 视频需要会员权限，当前无法分析。"}

        if "http error 403" in lower or "forbidden" in lower:
            return {
                "code": "youtube_forbidden",
                "message": "YouTube 拒绝了当前请求。请先登录 YouTube，或更换一个可公开访问并带字幕的视频。",
            }

        if "unable to download api page" in lower or "timed out" in lower or "network is unreachable" in lower:
            return {"code": "youtube_network_error", "message": "访问 YouTube 失败，请检查当前网络环境，或稍后重试。"}

        return {"code": "youtube_extract_failed", "message": f"YouTube 字幕提取失败：{text}"}


transcript_service = TranscriptService()
