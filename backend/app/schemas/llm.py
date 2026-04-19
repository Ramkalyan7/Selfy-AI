from pydantic import BaseModel, Field


class LlmGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    system_instruction: str | None = Field(default=None, max_length=10_000)
    model: str | None = Field(default=None, max_length=255)


class LlmGenerateResponse(BaseModel):
    model: str
    text: str
