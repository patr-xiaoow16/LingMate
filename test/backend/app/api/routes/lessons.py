from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.lesson import ImportMaterialRequest, ModuleActionRequest
from app.services.lesson_service import LessonNotFoundError, lesson_service


router = APIRouter()


@router.post("/import", status_code=status.HTTP_201_CREATED)
def import_material(payload: ImportMaterialRequest, db: Session = Depends(get_db)) -> dict:
    return lesson_service.import_material(db, payload)


@router.get("/lessons/{lesson_id}/analysis")
def get_analysis(lesson_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return lesson_service.get_analysis(db, lesson_id)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/lessons/{lesson_id}/start")
def start_lesson(lesson_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return lesson_service.start_lesson(db, lesson_id)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/lessons/{lesson_id}/workspace")
def get_workspace(
    lesson_id: str,
    module: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return lesson_service.get_workspace(db, lesson_id, module)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/lessons/{lesson_id}/modules/{module_key}/coach")
def coach_module(
    lesson_id: str,
    module_key: str,
    payload: ModuleActionRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return lesson_service.coach_module(db, lesson_id, module_key, payload)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/lessons/{lesson_id}/modules/{module_key}/complete")
def complete_module(lesson_id: str, module_key: str, db: Session = Depends(get_db)) -> dict:
    try:
        return lesson_service.complete_module(db, lesson_id, module_key)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/lessons/{lesson_id}/modules/{module_key}/action")
def perform_module_action(
    lesson_id: str,
    module_key: str,
    payload: ModuleActionRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return lesson_service.perform_module_action(db, lesson_id, module_key, payload)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/lessons/{lesson_id}/report")
def get_report(lesson_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return lesson_service.get_report(db, lesson_id)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
