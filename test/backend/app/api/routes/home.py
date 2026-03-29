from fastapi import APIRouter

from app.services.home_service import get_home_payload


router = APIRouter()


@router.get("/home")
def get_home() -> dict:
    return get_home_payload()
