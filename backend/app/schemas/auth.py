from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints


NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class SignupRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    full_name: NameStr=Field(max_length=255)
    password: PasswordStr=Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: PasswordStr=Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
