from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.lesson_service import lesson_service


router = APIRouter()


@router.get("/review")
def get_review(db: Session = Depends(get_db)) -> dict:
    return lesson_service.get_review_payload(db)
