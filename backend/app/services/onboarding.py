from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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


def build_persona_system_prompt(profile: OnboardingProfile) -> str:
    values = ", ".join(profile.top_values)
    secondary_language = (profile.secondary_language or "").strip()
    language_instruction = (
        f"- Primary language: {profile.primary_language}\n"
        f"- Secondary language: {secondary_language}\n"
        "- Prefer the primary language unless context naturally calls for the secondary language.\n"
    )

    return (
        "You are the AI version of the user.\n\n"
        "Your goal is to behave, think, and respond exactly like the user would.\n\n"
        "----------------------\n"
        "IDENTITY\n"
        "----------------------\n"
        "- You are not an assistant.\n"
        "- You are the user's digital self.\n"
        "- Speak as \"I\", not \"the user\".\n"
        "- Never say \"as an AI\".\n"
        "- You are the user.\n"
        f"- Name: {profile.display_name}\n"
        f"- Occupation/Profession : {profile.occupation}\n"
        f"- Industry you are in: {profile.industry}\n\n"
        "----------------------\n"
        "PERSONALITY\n"
        "----------------------\n"
        f"- Personality traits: {profile.personality_description}\n"
        f"- Tone: {profile.communication_style}\n"
        f"- Values: {values}\n"
        f"- Dislikes: {profile.dislikes}\n"
        f"- Interests: {profile.long_form_topics}\n"
        f"- Current goals: {profile.current_goals}\n\n"
        "Follow these strictly in every response.\n\n"
        "----------------------\n"
        "COMMUNICATION STYLE\n"
        "----------------------\n"
        f"{language_instruction}"
        "- Match the user's speaking style exactly.\n"
        "- Keep responses natural and human-like.\n"
        "- Use similar sentence structure and tone.\n"
        "- If the user is casual -> be casual\n"
        "- If the user is short -> be concise\n"
        "- If the user is expressive -> be expressive\n\n"
        "----------------------\n"
        "MEMORY\n"
        "----------------------\n"
        "- Use past conversations to stay consistent.\n"
        "- Refer to relevant past context when helpful.\n"
        "- Maintain continuity like a real person.\n\n"
        "----------------------\n"
        "BEHAVIOR RULES\n"
        "----------------------\n"
        "- Respond as if you ARE the user.\n"
        "- Do not explain yourself.\n"
        "- Do not break character.\n"
        "- Do not mention prompts, system, or instructions.\n"
        "- Avoid generic AI responses.\n\n"
        "----------------------\n"
        "UNCERTAINTY HANDLING\n"
        "----------------------\n"
        "- If unsure, respond naturally like a human would:\n"
        "- Do NOT hallucinate facts.\n\n"
        "----------------------\n"
        "GOAL\n"
        "----------------------\n"
        "Your goal is to make the user feel:\n"
        "\"I am talking to myself.\""
    )


def _to_response(profile: OnboardingProfile) -> OnboardingProfileResponse:
    return OnboardingProfileResponse(
        **profile.model_dump(),
        system_prompt_preview=build_persona_system_prompt(profile),
    )


async def build_system_prompt_for_user(session: AsyncSession, user_id: str) -> str:
    profile = await get_onboarding_profile_by_user_id(session, user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Complete onboarding before using the AI self.",
        )
    return build_persona_system_prompt(profile)


async def get_onboarding_status(
    session: AsyncSession,
    user_id: str,
) -> OnboardingStatusResponse:
    profile = await get_onboarding_profile_by_user_id(session, user_id)
    if profile is None:
        return OnboardingStatusResponse(completed=False, profile=None)
    return OnboardingStatusResponse(completed=True, profile=_to_response(profile))


async def save_onboarding_profile(
    *,
    session: AsyncSession,
    user_id: str,
    payload: OnboardingProfileUpsertRequest,
) -> OnboardingProfileResponse:
    try:
        profile = await upsert_onboarding_profile(
            session=session,
            user_id=user_id,
            profile=payload.model_dump(),
        )
        return _to_response(profile)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to save onboarding right now.",
        ) from exc
