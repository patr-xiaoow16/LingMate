import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.migrations import run_lightweight_migrations
from app.db.session import Base, engine
from app.models import AIFeedback, AnalysisJob, Lesson, LessonEvent, Material, Submission, TranscriptSegment
from app.services.pipeline_worker import pipeline_worker

_startup_lock = threading.Lock()
_db_initialized = False


def create_application() -> FastAPI:
    _ = (Material, Lesson, LessonEvent, TranscriptSegment, Submission, AIFeedback, AnalysisJob)
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        global _db_initialized
        with _startup_lock:
            if not _db_initialized:
                Base.metadata.create_all(bind=engine)
                run_lightweight_migrations()
                _db_initialized = True
        pipeline_worker.start()

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        pipeline_worker.stop()

    app.include_router(api_router, prefix=settings.api_prefix)
    app.mount("/media", StaticFiles(directory=settings.uploads_dir), name="media")
    return app


app = create_application()
