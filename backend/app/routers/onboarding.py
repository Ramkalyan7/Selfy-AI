import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingProfileResponse,
    OnboardingProfileUpsertRequest,
    OnboardingStatusResponse,
)
from app.services.onboarding import get_onboarding_status, save_onboarding_profile


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("", response_model=OnboardingStatusResponse)
async def get_my_onboarding(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OnboardingStatusResponse:
    try:
        return await get_onboarding_status(session, user.id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached onboarding read route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch onboarding right now.",
        ) from exc


@router.put("", response_model=OnboardingProfileResponse)
async def save_my_onboarding(
    payload: OnboardingProfileUpsertRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OnboardingProfileResponse:
    try:
        return await save_onboarding_profile(
            session=session,
            user_id=user.id,
            payload=payload,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached onboarding save route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save onboarding right now.",
        ) from exc
