from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    material_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(32), default="url")
    source_url: Mapped[str] = mapped_column(Text)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    mime_type: Mapped[str] = mapped_column(String(128), default="")
    title: Mapped[str] = mapped_column(String(255), default="Untitled material")
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    transcript_text: Mapped[str] = mapped_column(Text, default="")
    transcript_meta_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lesson_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    material_id: Mapped[str] = mapped_column(String(64), ForeignKey("materials.material_id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="processing", index=True)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    title: Mapped[str] = mapped_column(String(255), default="Untitled lesson")
    error_message: Mapped[str] = mapped_column(Text, default="")
    analysis_json: Mapped[dict] = mapped_column(JSON, default=dict)
    module_content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    report_json: Mapped[dict] = mapped_column(JSON, default=dict)
    progress_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class LessonEvent(Base):
    __tablename__ = "lesson_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lesson_id: Mapped[str] = mapped_column(String(64), ForeignKey("lessons.lesson_id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lesson_id: Mapped[str] = mapped_column(String(64), ForeignKey("lessons.lesson_id"), index=True)
    material_id: Mapped[str] = mapped_column(String(64), ForeignKey("materials.material_id"), index=True)
    segment_index: Mapped[int] = mapped_column(Integer)
    start_ms: Mapped[int] = mapped_column(Integer, default=0)
    end_ms: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    speaker: Mapped[str] = mapped_column(String(64), default="speaker_1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    submission_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    lesson_id: Mapped[str] = mapped_column(String(64), ForeignKey("lessons.lesson_id"), index=True)
    module_key: Mapped[str] = mapped_column(String(64), index=True)
    interaction_type: Mapped[str] = mapped_column(String(64), index=True)
    user_input: Mapped[str] = mapped_column(Text, default="")
    meta_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="submitted", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    feedback_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    submission_id: Mapped[str] = mapped_column(String(64), ForeignKey("submissions.submission_id"), index=True)
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    model: Mapped[str] = mapped_column(String(64), default="deepseek-chat")
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1")
    feedback_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    lesson_id: Mapped[str] = mapped_column(String(64), ForeignKey("lessons.lesson_id"), index=True)
    job_type: Mapped[str] = mapped_column(String(64), default="process_import", index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
