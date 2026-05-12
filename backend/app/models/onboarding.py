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
    conflict_response_style: str #How do you react when something goes wrong? (calm / emotional /problem-solving / ignore)
    top_values: list[str] # What are your top 3 values? (e.g., honesty, success, freedom, family)
    dislikes: str  # What do you dislike or avoid? (very important for realism)
    
    
#     How would you reply to this message?
# 👉 “Hey bro, are you coming tonight?”
# How would you reply to this?
# 👉 “I’m feeling really low today.”
# How would you reply to this?
# 👉 “Can you help me with something?”

    reply_to_invite: str
    reply_to_low_mood: str
    reply_to_help_request: str
    long_form_topics: str # What topics can you talk about for hours?
    current_goals: str # Whatare your current goals
    created_at: datetime
    updated_at: datetime
    completed_at: datetime
