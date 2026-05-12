from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


CommunicationStyle = Literal["casual", "formal", "mixed"]


class OnboardingProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    display_name: str
    occupation: str
    personality_description: str # How would you describe your personality? (e.g., funny, serious, chill, sarcastic)
    communication_style: CommunicationStyle #How do you usually talk? Casual Formal Mix of both
    top_values: list[str] # What are your top 3 values? (e.g., honesty, success, freedom, family)
    dislikes: str  # What do you dislike or avoid? (very important for realism)
    long_form_topics: str # What topics can you talk about for hours?
    current_goals: str # Whatare your current goals
    created_at: datetime
    updated_at: datetime
    completed_at: datetime
    primary_language: str        # especially important for non-English users
    secondary_language: str | None
    industry: str                # "tech", "finance", "creative" — changes vocab 
