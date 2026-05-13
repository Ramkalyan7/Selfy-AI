from typing import Any

from app.core.config import get_settings
from app.db.session import get_supabase
from app.models.onboarding import OnboardingProfile


settings = get_settings()


def _row_to_onboarding_profile(row: dict[str, Any] | None) -> OnboardingProfile | None:
    if row is None:
        return None
    return OnboardingProfile.model_validate(row)


def get_onboarding_profile_by_user_id(user_id: str) -> OnboardingProfile | None:
    response = (
        get_supabase()
        .table(settings.supabase_onboarding_table)
        .select(
            "user_id, display_name, occupation, personality_description, "
            "communication_style, top_values, dislikes, long_form_topics, "
            "current_goals, primary_language, secondary_language, industry, "
            "created_at, updated_at, completed_at"
        )
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return _row_to_onboarding_profile(response.data[0] if response.data else None)


def upsert_onboarding_profile(*, user_id: str, profile: dict[str, Any]) -> OnboardingProfile:
    response = (
        get_supabase()
        .table(settings.supabase_onboarding_table)
        .upsert(
            {
                "user_id": user_id,
                **profile,
            },
            on_conflict="user_id",
        )
        .execute()
    )
    return OnboardingProfile.model_validate(response.data[0])
