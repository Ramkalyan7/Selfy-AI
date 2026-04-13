from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import get_supabase
from app.schemas.health import HealthResponse


router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    response = (
        get_supabase()
        .table(settings.supabase_users_table)
        .select("id")
        .limit(1)
        .execute()
    )
    _ = response.data

    return HealthResponse(status="ok", database="connected")
