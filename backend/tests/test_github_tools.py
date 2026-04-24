import json

from app.agent.tools.github import get_github_tools
from app.agent.tools.registry import get_agent_tools


class _FakeGitHubClient:
    def get_authenticated_user(self) -> dict[str, str]:
        return {
            "login": "ram",
            "name": "Ram Kumar",
            "html_url": "https://github.com/ram",
        }

    def list_repositories(
        self,
        *,
        visibility: str = "all",
        per_page: int = 30,
    ) -> list[dict[str, str | bool | None]]:
        return [
            {
                "name": "selfy-ai",
                "full_name": "ram/selfy-ai",
                "private": False,
                "html_url": "https://github.com/ram/selfy-ai",
                "description": "Selfy AI backend",
            }
        ]

    def get_repository(self, *, owner: str, repo: str) -> dict[str, str | bool | None]:
        return {
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "private": False,
            "default_branch": "main",
            "description": "Repository details",
            "html_url": f"https://github.com/{owner}/{repo}",
        }

    def create_issue(
        self,
        *,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
    ) -> dict[str, str | int]:
        return {
            "number": 1,
            "title": title,
            "state": "open",
            "html_url": f"https://github.com/{owner}/{repo}/issues/1",
        }


def test_get_github_tools_exposes_expected_names() -> None:
    tools = get_github_tools(_FakeGitHubClient())
    names = {tool.name for tool in tools}

    assert names == {
        "github_get_authenticated_user",
        "github_list_repositories",
        "github_get_repository",
        "github_create_issue",
    }


def test_github_create_issue_tool_invokes_client() -> None:
    tools = {tool.name: tool for tool in get_github_tools(_FakeGitHubClient())}

    result = tools["github_create_issue"].invoke(
        {
            "owner": "ram",
            "repo": "selfy-ai",
            "title": "Bug report",
            "body": "Something broke",
        }
    )

    assert json.loads(result) == {
        "number": 1,
        "title": "Bug report",
        "state": "open",
        "html_url": "https://github.com/ram/selfy-ai/issues/1",
    }


def test_get_agent_tools_returns_empty_when_github_not_configured(monkeypatch) -> None:
    monkeypatch.setattr("app.agent.tools.registry.settings.github_api_token", "")

    assert get_agent_tools() == []
