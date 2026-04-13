import logging

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import create_user, get_user_by_email
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse


logger = logging.getLogger(__name__)


def signup(payload: SignupRequest) -> AuthResponse:
    try:
        existing_user = get_user_by_email(str(payload.email))
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists.",
            )

        user = create_user(
            email=str(payload.email),
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )
        access_token = create_access_token(str(user.id))
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during signup.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process signup right now.",
        ) from exc


def login(payload: LoginRequest) -> AuthResponse:
    try:
        user = get_user_by_email(str(payload.email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        access_token = create_access_token(str(user.id))
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during login.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process login right now.",
        ) from exc
