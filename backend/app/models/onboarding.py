from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


CommunicationStyle = Literal["casual", "formal", "mixed"]


class OnboardingProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: str
    display_name: str
    occupation: str
    personality_description: str
    communication_style: CommunicationStyle
    conflict_response_style: str
    top_values: list[str]
    dislikes: str
    reply_to_invite: str
    reply_to_low_mood: str
    reply_to_help_request: str
    long_form_topics: str
    current_goals: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime
