from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import OnboardingProfile


async def get_onboarding_profile_by_user_id(
    session: AsyncSession,
    user_id: str,
) -> OnboardingProfile | None:
    return await session.get(OnboardingProfile, user_id)


async def upsert_onboarding_profile(
    *,
    session: AsyncSession,
    user_id: str,
    profile: dict[str, Any],
) -> OnboardingProfile:
    now = datetime.now(timezone.utc)
    existing_profile = await get_onboarding_profile_by_user_id(session, user_id)

    if existing_profile is None:
        existing_profile = OnboardingProfile(
            user_id=user_id,
            **profile,
            completed_at=now,
        )
        session.add(existing_profile)
    else:
        for field_name, value in profile.items():
            setattr(existing_profile, field_name, value)
        existing_profile.completed_at = now
        existing_profile.updated_at = now

    await session.commit()
    await session.refresh(existing_profile)
    return existing_profile
