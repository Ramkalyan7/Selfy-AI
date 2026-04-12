from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator


NameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
PasswordStr = Annotated[str, StringConstraints(min_length=8, max_length=128)]


class SignupRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    full_name: NameStr
    password: PasswordStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if len(value.split()) < 2:
            raise ValueError("Full name must include at least first and last name.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if " " in value:
            raise ValueError("Password must not contain spaces.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: PasswordStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("Password must not start or end with spaces.")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
