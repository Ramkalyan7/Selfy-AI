from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings


settings = get_settings()


@dataclass(frozen=True)
class LlmRequest:
    prompt: str
    system_instruction: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class LlmResponse:
    provider: str
    model: str
    text: str


class LlmProvider(Protocol):
    provider_name: str

    def generate(self, request: LlmRequest) -> LlmResponse:
        ...


class GeminiLangChainProvider:
    provider_name = "gemini"

    def __init__(self, *, api_key: str, default_model: str):
        self._api_key = api_key
        self._default_model = default_model

    @property
    def default_model(self) -> str:
        return self._default_model

    def generate(self, request: LlmRequest) -> LlmResponse:
        if not self._api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini is not configured.",
            )

        chosen_model = request.model or self.default_model
        messages = []
        if request.system_instruction:
            messages.append(SystemMessage(content=request.system_instruction))
        messages.append(HumanMessage(content=request.prompt))

        try:
            llm = ChatGoogleGenerativeAI(
                model=chosen_model,
                google_api_key=self._api_key,
            )
            response = llm.invoke(messages)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini request failed.",
            ) from exc

        text = _extract_response_text(response)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned an empty response.",
            )

        return LlmResponse(
            provider=self.provider_name,
            model=chosen_model,
            text=text,
        )


def _extract_response_text(response: object) -> str:
    content = getattr(response, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part.strip())
    return ""


@lru_cache
def get_llm_provider(provider_name: str | None = None) -> LlmProvider:
    chosen_provider = (provider_name or settings.llm_provider).strip().lower()
    if chosen_provider == "gemini":
        return GeminiLangChainProvider(
            api_key=settings.gemini_api_key,
            default_model=settings.gemini_model,
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Unsupported LLM provider: {chosen_provider}.",
    )


def generate_text_completion(
    *,
    prompt: str,
    system_instruction: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> tuple[str, str, str]:
    llm_provider = get_llm_provider(provider)
    response = llm_provider.generate(
        LlmRequest(
            prompt=prompt,
            system_instruction=system_instruction,
            model=model,
        )
    )
    return response.provider, response.model, response.text
