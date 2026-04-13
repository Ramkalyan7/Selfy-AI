import logging

from fastapi import APIRouter, Depends, HTTPException, status

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
def get_my_onboarding(user: User = Depends(get_current_user)) -> OnboardingStatusResponse:
    try:
        return get_onboarding_status(user.id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached onboarding read route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch onboarding right now.",
        ) from exc


@router.put("", response_model=OnboardingProfileResponse)
def save_my_onboarding(
    payload: OnboardingProfileUpsertRequest,
    user: User = Depends(get_current_user),
) -> OnboardingProfileResponse:
    try:
        return save_onboarding_profile(user_id=user.id, payload=payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached onboarding save route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save onboarding right now.",
        ) from exc
