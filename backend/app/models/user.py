from typing import Optional, TYPE_CHECKING
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .onboarding import OnboardingProfile


class User(SQLModel, table=True):
    model_config = {"extra": "ignore"}

    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    password_hash: str
    onboarding_profile: Optional["OnboardingProfile"] = Relationship(
        back_populates="user"
    )
