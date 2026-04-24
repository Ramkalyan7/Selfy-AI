from langchain_core.tools import BaseTool

from app.agent.tools.github import get_github_tools
from app.core.config import get_settings
from app.integrations.github import get_github_client


settings = get_settings()


def get_agent_tools() -> list[BaseTool]:
    tools: list[BaseTool] = []
    if settings.github_api_token:
        tools.extend(get_github_tools(get_github_client()))
    return tools
