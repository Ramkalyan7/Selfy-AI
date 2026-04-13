from fastapi.testclient import TestClient

from app.main import app
from app.routers import health


client = TestClient(app)


class _FakeSupabaseQuery:
    def select(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def execute(self):
        return type("Response", (), {"data": []})()


class _FakeSupabaseClient:
    def table(self, _name: str):
        return _FakeSupabaseQuery()


def test_health_endpoint() -> None:
    health.get_supabase = lambda: _FakeSupabaseClient()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
