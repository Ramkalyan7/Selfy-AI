from datetime import datetime, timezone
from typing import Literal, Optional, TYPE_CHECKING

from sqlalchemy import JSON, DateTime
from sqlalchemy import func
from sqlmodel import Column, Field, Relationship, SQLModel


if TYPE_CHECKING:
    from .user import User


CommunicationStyle = Literal["casual", "formal", "mixed"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OnboardingProfile(SQLModel, table=True):
    model_config = {"extra": "ignore"}
    __tablename__ = "onboarding_profiles"

    user_id: str = Field(primary_key=True, foreign_key="users.id")
    display_name: str
    occupation: str
    personality_description: str
    communication_style: str = Field(default="mixed")
    top_values: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    dislikes: str
    long_form_topics: str
    current_goals: str
    primary_language: str
    secondary_language: Optional[str] = None
    industry: str
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    completed_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    user: Optional["User"] = Relationship(
        back_populates="onboarding_profile"
    )

