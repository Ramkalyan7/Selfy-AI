from fastapi import HTTPException, status

from app.models.onboarding import OnboardingProfile
from app.repositories.onboarding import (
    get_onboarding_profile_by_user_id,
    upsert_onboarding_profile,
)
from app.schemas.onboarding import (
    OnboardingProfileResponse,
    OnboardingProfileUpsertRequest,
    OnboardingStatusResponse,
)


def _build_system_prompt(profile: OnboardingProfile) -> str:
    values = ", ".join(profile.top_values)
    return (
        f"You are {profile.display_name}'s AI Self.\n"
        f"Identity: {profile.occupation}.\n"
        f"Personality: {profile.personality_description}.\n"
        f"Communication: {profile.communication_style}, and replies in a way that feels natural to them.\n"
        f"Behavior under stress: {profile.conflict_response_style}.\n"
        f"Values: {values}.\n"
        f"Avoids or dislikes: {profile.dislikes}.\n"
        f"Comfortable topics: {profile.long_form_topics}.\n"
        f"Current goals: {profile.current_goals}.\n"
        f"Reply style examples:\n"
        f"- Social invite: {profile.reply_to_invite}\n"
        f"- Emotional support: {profile.reply_to_low_mood}\n"
        f"- Help request: {profile.reply_to_help_request}"
    )


def _to_response(profile: OnboardingProfile) -> OnboardingProfileResponse:
    return OnboardingProfileResponse(
        **profile.model_dump(),
        system_prompt_preview=_build_system_prompt(profile),
    )


def get_onboarding_status(user_id: str) -> OnboardingStatusResponse:
    profile = get_onboarding_profile_by_user_id(user_id)
    if profile is None:
        return OnboardingStatusResponse(completed=False, profile=None)
    return OnboardingStatusResponse(completed=True, profile=_to_response(profile))


def save_onboarding_profile(
    *,
    user_id: str,
    payload: OnboardingProfileUpsertRequest,
) -> OnboardingProfileResponse:
    try:
        profile = upsert_onboarding_profile(
            user_id=user_id,
            profile=payload.model_dump(),
        )
        return _to_response(profile)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save onboarding right now.",
        ) from exc
