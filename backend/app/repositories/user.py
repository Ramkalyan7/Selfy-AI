from typing import Any

from app.core.config import get_settings
from app.db.session import get_supabase
from app.models.user import User


settings = get_settings()


def _row_to_user(row: dict[str, Any] | None) -> User | None:
    if row is None:
        return None
    return User.model_validate(row)


def get_user_by_id(user_id: str) -> User | None:
    response = (
        get_supabase()
        .table(settings.supabase_users_table)
        .select("id, email, full_name, password_hash")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    return _row_to_user(response.data[0] if response.data else None)


def get_user_by_email(email: str) -> User | None:
    response = (
        get_supabase()
        .table(settings.supabase_users_table)
        .select("id, email, full_name, password_hash")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    return _row_to_user(response.data[0] if response.data else None)


def create_user(
    *,
    email: str,
    full_name: str,
    password_hash: str,
) -> User:
    response = (
        get_supabase()
        .table(settings.supabase_users_table)
        .insert(
            {
                "email": email,
                "full_name": full_name,
                "password_hash": password_hash,
            }
        )
        .execute()
    )
    return User.model_validate(response.data[0])
