from functools import lru_cache

from supabase import Client, create_client
from app.core.config import get_settings


settings = get_settings()


@lru_cache
def get_supabase() -> Client:
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be configured before starting the backend."
        )
    return create_client(settings.supabase_url, settings.supabase_key)
