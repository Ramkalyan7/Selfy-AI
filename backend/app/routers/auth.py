import logging

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth import login, signup


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_user(payload: SignupRequest) -> AuthResponse:
    try:
        return signup(payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached signup route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process signup right now.",
        ) from exc


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginRequest) -> AuthResponse:
    try:
        return login(payload)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached login route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process login right now.",
        ) from exc
