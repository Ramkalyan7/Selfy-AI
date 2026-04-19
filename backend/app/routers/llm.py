import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.llm import LlmGenerateRequest, LlmGenerateResponse
from app.services.llm import generate_text_completion


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/generate", response_model=LlmGenerateResponse)
def generate_text(
    payload: LlmGenerateRequest,
    user: User = Depends(get_current_user),
) -> LlmGenerateResponse:
    try:
        _ = user
        model, text = generate_text_completion(
            prompt=payload.prompt,
            system_instruction=payload.system_instruction,
            model=payload.model,
        )
        return LlmGenerateResponse(model=model, text=text)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unhandled error reached llm generate route.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach the language model right now.",
        ) from exc
