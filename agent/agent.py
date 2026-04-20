import logging
from agent.models import SearchResponse, SearchRequest
from agent.search_tool import search_web
from agent.llm import generate_answer

logger = logging.getLogger(__name__)


def run_agent(request: SearchRequest) -> SearchResponse:
    """
    Core agent pipeline:
      1. Run web search for the user query
      2. Pass retrieved snippets to Gemini to generate a grounded answer
      3. Return a structured response with the answer and all sources

    Any exception from search or LLM propagates up to the FastAPI layer,
    which maps it to an appropriate HTTP error response.

    Args:
        request: Validated SearchRequest with query and max_results

    Returns:
        SearchResponse with answer, sources, and metadata
    """
    logger.info(f"Agent received query: '{request.query}' (max_results={request.max_results})")

   
    sources = search_web(query=request.query, max_results=request.max_results)
    logger.info(f"Retrieved {len(sources)} sources")

   
    answer = generate_answer(query=request.query, sources=sources)

    return SearchResponse(
        query=request.query,
        answer=answer,
        sources=sources,
        result_count=len(sources),
    )