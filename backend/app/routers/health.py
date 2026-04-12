from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine
from app.schemas.health import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return HealthResponse(status="ok", database="connected")
