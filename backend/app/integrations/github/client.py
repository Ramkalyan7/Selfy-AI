from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


settings = get_settings()


@dataclass(frozen=True)
class GitHubClient:
    api_token: str
    base_url: str
    timeout_seconds: float = 20.0

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.api_token}",
            "User-Agent": "selfy-ai-backend",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        try:
            with httpx.Client(
                base_url=self.base_url,
                headers=self._headers(),
                timeout=self.timeout_seconds,
            ) as client:
                response = client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub is unavailable right now.",
            ) from exc

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub credentials are invalid.",
            )
        if response.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="GitHub rejected this action.",
            )
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="GitHub request failed.",
            )

        return response.json()

    def get_authenticated_user(self) -> dict[str, Any]:
        data = self._request(method="GET", path="/user")
        return {
            "login": data.get("login"),
            "name": data.get("name"),
            "html_url": data.get("html_url"),
        }

    def list_repositories(
        self,
        *,
        visibility: str = "all",
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        data = self._request(
            method="GET",
            path="/user/repos",
            params={
                "visibility": visibility,
                "per_page": per_page,
                "sort": "updated",
            },
        )
        return [
            {
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "private": item.get("private"),
                "html_url": item.get("html_url"),
                "description": item.get("description"),
            }
            for item in data
        ]

    def get_repository(self, *, owner: str, repo: str) -> dict[str, Any]:
        data = self._request(method="GET", path=f"/repos/{owner}/{repo}")
        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "private": data.get("private"),
            "default_branch": data.get("default_branch"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
        }

    def create_issue(
        self,
        *,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
    ) -> dict[str, Any]:
        data = self._request(
            method="POST",
            path=f"/repos/{owner}/{repo}/issues",
            payload={
                "title": title,
                "body": body or "",
            },
        )
        return {
            "number": data.get("number"),
            "title": data.get("title"),
            "state": data.get("state"),
            "html_url": data.get("html_url"),
        }


@lru_cache
def get_github_client() -> GitHubClient:
    if not settings.github_api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub is not configured.",
        )

    return GitHubClient(
        api_token=settings.github_api_token,
        base_url=settings.github_api_url.rstrip("/"),
    )
