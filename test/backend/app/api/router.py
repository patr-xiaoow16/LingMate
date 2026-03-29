from fastapi import APIRouter

from app.api.routes import health, home, lessons, review


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(home.router, tags=["home"])
api_router.include_router(lessons.router, tags=["lessons"])
api_router.include_router(review.router, tags=["review"])
