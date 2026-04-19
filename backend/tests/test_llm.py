from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.repositories import user as user_repository
from app.routers import llm as llm_router


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

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, field: str, value: str):
        self._filters.append((field, value))
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    def execute(self):
        rows = self._client.select(self._table_name, self._filters, self._limit)
        return _FakeResponse(rows)


class _FakeSupabaseClient:
    def __init__(self):
        self.tables = {"users": {}}

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


def _auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def test_generate_text_endpoint(monkeypatch) -> None:
    fake_supabase = _FakeSupabaseClient()
    fake_supabase.seed_user(
        {
            "id": "user-llm-1",
            "email": "ram@example.com",
            "full_name": "Ram Kumar",
            "password_hash": "hashed-password",
        }
    )
    monkeypatch.setattr(user_repository, "get_supabase", lambda: fake_supabase)
    monkeypatch.setattr(
        llm_router,
        "generate_text_completion",
        lambda **_kwargs: ("gemini", "gemini-2.5-flash", "Hello from Gemini"),
    )

    response = client.post(
        "/llm/generate",
        json={
            "prompt": "Say hello",
            "system_instruction": "Be concise.",
        },
        headers=_auth_headers("user-llm-1"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "text": "Hello from Gemini",
    }


def test_generate_text_requires_auth() -> None:
    response = client.post(
        "/llm/generate",
        json={
            "prompt": "Say hello",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication is required."}
