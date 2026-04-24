import json

from langchain_core.tools import BaseTool, StructuredTool

from app.integrations.github import GitHubClient


def get_github_tools(client: GitHubClient) -> list[BaseTool]:
    def github_get_authenticated_user() -> str:
        return json.dumps(client.get_authenticated_user())

    def github_list_repositories(
        visibility: str = "all",
        per_page: int = 30,
    ) -> str:
        return json.dumps(
            client.list_repositories(
                visibility=visibility,
                per_page=per_page,
            )
        )

    def github_get_repository(owner: str, repo: str) -> str:
        return json.dumps(client.get_repository(owner=owner, repo=repo))

    def github_create_issue(
        owner: str,
        repo: str,
        title: str,
        body: str = "",
    ) -> str:
        return json.dumps(
            client.create_issue(
                owner=owner,
                repo=repo,
                title=title,
                body=body,
            )
        )

    return [
        StructuredTool.from_function(
            func=github_get_authenticated_user,
            name="github_get_authenticated_user",
            description="Get the connected GitHub account profile for the current integration.",
        ),
        StructuredTool.from_function(
            func=github_list_repositories,
            name="github_list_repositories",
            description="List repositories visible to the connected GitHub account.",
        ),
        StructuredTool.from_function(
            func=github_get_repository,
            name="github_get_repository",
            description="Get repository details from GitHub using an owner and repository name.",
        ),
        StructuredTool.from_function(
            func=github_create_issue,
            name="github_create_issue",
            description="Create a GitHub issue in a repository the connected account can access.",
        ),
    ]
