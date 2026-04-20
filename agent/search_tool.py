import os
import logging
from typing import List
from tavily import TavilyClient
from agent.models import Source

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = 5) -> List[Source]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise EnvironmentError("TAVILY_API_KEY is not set in .env")

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
    )

    sources = []
    for result in response.get("results", []):
        sources.append(
            Source(
                title=result.get("title", "No title"),
                url=result.get("url", ""),
                snippet=result.get("content", "No description available."),
            )
        )

    if not sources:
        raise RuntimeError("No search results returned.")

    return sources