from functools import lru_cache

from fastapi import HTTPException, status

from app.core.config import get_settings


settings = get_settings()


@lru_cache
def get_gemini_client():
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini is not configured.",
        )

    try:
        from google import genai
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini SDK is not installed.",
        ) from exc

    return genai.Client(api_key=settings.gemini_api_key)


def generate_text_completion(
    *,
    prompt: str,
    system_instruction: str | None = None,
    model: str | None = None,
) -> tuple[str, str]:
    client = get_gemini_client()
    chosen_model = model or settings.gemini_model
    request: dict[str, object] = {
        "model": chosen_model,
        "contents": prompt,
    }

    if system_instruction:
        from google.genai import types

        request["config"] = types.GenerateContentConfig(
            system_instruction=system_instruction,
        )

    try:
        response = client.models.generate_content(**request)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini request failed.",
        ) from exc

    text = getattr(response, "text", None)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned an empty response.",
        )

    return chosen_model, text
