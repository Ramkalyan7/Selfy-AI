from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.repositories import onboarding as onboarding_repository
from app.repositories import user as user_repository


client = TestClient(app)


class _FakeResponse:
    def __init__(self, data):
        self.data = data


class _FakeSupabaseQuery:
    def __init__(self, client, table_name: str):
        self._client = client
        self._table_name = table_name
        self._filters: list[tuple[str, str]] = []
        self._limit: int | None = None
        self._operation = "select"
        self._payload = None
        self._on_conflict = None

    def select(self, *_args, **_kwargs):
        self._operation = "select"
        return self

    def eq(self, field: str, value: str):
        self._filters.append((field, value))
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    def upsert(self, payload, on_conflict: str | None = None):
        self._operation = "upsert"
        self._payload = payload
        self._on_conflict = on_conflict
        return self

    def execute(self):
        if self._operation == "upsert":
            return _FakeResponse([self._client.upsert(self._table_name, self._payload, self._on_conflict)])

        rows = self._client.select(self._table_name, self._filters, self._limit)
        return _FakeResponse(rows)


class _FakeSupabaseClient:
    def __init__(self):
        self.tables = {
            "users": {},
            "user_onboarding_profiles": {},
        }

    def table(self, table_name: str):
        return _FakeSupabaseQuery(self, table_name)

    def seed_user(self, row: dict):
        self.tables["users"][row["id"]] = row

    def select(self, table_name: str, filters: list[tuple[str, str]], limit: int | None):
        rows = list(self.tables[table_name].values())
        for field, value in filters:
            rows = [row for row in rows if row.get(field) == value]
        if limit is not None:
            rows = rows[:limit]
        return rows

    def upsert(self, table_name: str, payload: dict, on_conflict: str | None):
        conflict_key = on_conflict or "id"
        row_id = payload[conflict_key]
        existing = self.tables[table_name].get(row_id, {})
        timestamp = datetime.now(UTC).isoformat()
        row = {
            **existing,
            **payload,
            "created_at": existing.get("created_at", timestamp),
            "updated_at": timestamp,
            "completed_at": timestamp,
        }
        self.tables[table_name][row_id] = row
        return row


def _auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def _payload() -> dict:
    return {
        "display_name": "Ram",
        "occupation": "Developer",
        "personality_description": "Funny, calm, slightly sarcastic.",
        "communication_style": "casual",
        "conflict_response_style": "Usually stays calm and solves the problem directly.",
        "top_values": ["Honesty", "Freedom", "Growth"],
        "dislikes": "Fake behavior and wasting time.",
        "reply_to_invite": "Yeah bro, I should be there tonight.",
        "reply_to_low_mood": "I am here for you. Want to talk through what is going on?",
        "reply_to_help_request": "Of course, tell me what you need help with.",
        "long_form_topics": "Tech, startups, and AI products.",
        "current_goals": "Build Selfy AI and grow as a founder.",
    }


def test_get_onboarding_returns_incomplete_when_missing(monkeypatch) -> None:
    fake_supabase = _FakeSupabaseClient()
    fake_supabase.seed_user(
        {
            "id": "user-1",
            "email": "ram@example.com",
            "full_name": "Ram Kumar",
            "password_hash": "hashed-password",
        }
    )
    monkeypatch.setattr(user_repository, "get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(onboarding_repository, "get_supabase", lambda: fake_supabase)

    response = client.get("/onboarding", headers=_auth_headers("user-1"))

    assert response.status_code == 200
    assert response.json() == {"completed": False, "profile": None}


def test_put_onboarding_saves_and_returns_profile(monkeypatch) -> None:
    fake_supabase = _FakeSupabaseClient()
    fake_supabase.seed_user(
        {
            "id": "user-2",
            "email": "ram2@example.com",
            "full_name": "Ram Verma",
            "password_hash": "hashed-password",
        }
    )
    monkeypatch.setattr(user_repository, "get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(onboarding_repository, "get_supabase", lambda: fake_supabase)

    put_response = client.put("/onboarding", json=_payload(), headers=_auth_headers("user-2"))

    assert put_response.status_code == 200
    body = put_response.json()
    assert body["user_id"] == "user-2"
    assert body["display_name"] == "Ram"
    assert body["communication_style"] == "casual"
    assert body["top_values"] == ["Honesty", "Freedom", "Growth"]
    assert "You are Ram's AI Self." in body["system_prompt_preview"]

    get_response = client.get("/onboarding", headers=_auth_headers("user-2"))

    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["completed"] is True
    assert fetched["profile"]["reply_to_help_request"] == _payload()["reply_to_help_request"]
