from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .repository import LingMateRepository


class ImportLessonRequest(BaseModel):
    source_type: str = Field(default="link")
    source_value: str = Field(default="")
    goal: str | None = Field(default=None)


class CoachRequest(BaseModel):
    text: str = Field(default="")


app = FastAPI(
    title="LingMate Backend",
    version="0.1.0",
    description="Mock backend for the LingMate immersive listening web prototype.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = LingMateRepository()


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/api/home")
def get_home() -> dict:
    return repo.get_home()


@app.post("/api/import")
def import_lesson(payload: ImportLessonRequest) -> dict:
    return repo.import_lesson(payload.source_type, payload.source_value, payload.goal)


@app.get("/api/lessons/{lesson_id}/analysis")
def get_analysis(lesson_id: str) -> dict:
    try:
        return repo.get_analysis(lesson_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/lessons/{lesson_id}/start")
def start_lesson(lesson_id: str) -> dict:
    try:
        return repo.start_lesson(lesson_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/lessons/{lesson_id}/workspace")
def get_workspace(lesson_id: str, module: str | None = Query(default=None)) -> dict:
    try:
        return repo.get_workspace(lesson_id, module)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/lessons/{lesson_id}/modules/{module_key}/coach")
def coach_module(lesson_id: str, module_key: str, payload: CoachRequest) -> dict:
    try:
        return repo.coach_module(lesson_id, module_key, payload.text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/lessons/{lesson_id}/modules/{module_key}/complete")
def complete_module(lesson_id: str, module_key: str) -> dict:
    try:
        return repo.complete_module(lesson_id, module_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/lessons/{lesson_id}/report")
def get_report(lesson_id: str) -> dict:
    try:
        return repo.get_report(lesson_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/review")
def get_review(lesson_id: str | None = Query(default=None)) -> dict:
    try:
        return repo.get_review(lesson_id)
    except StopIteration as exc:
        raise HTTPException(status_code=404, detail="No active lesson found.") from exc
