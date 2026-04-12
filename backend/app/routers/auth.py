import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from app.services.auth import login, signup


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup_user(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        return signup(db, payload)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Unhandled database error reached signup route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process signup right now.",
        ) from exc
    except Exception as exc:
        logger.exception("Unhandled error reached signup route.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process signup right now.",
        ) from exc


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        return login(db, payload)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.exception("Unhandled database error reached login route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process login right now.",
        ) from exc
    except Exception as exc:
        logger.exception("Unhandled error reached login route.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process login right now.",
        ) from exc
