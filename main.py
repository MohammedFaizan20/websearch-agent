import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from agent.agent import run_agent
from agent.models import ErrorResponse, SearchRequest, SearchResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: validate required env vars early so the error is obvious
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY is not set — /search requests will fail until it is configured.")
    logger.info("Slooze AI Web Search Agent is running.")
    yield
    logger.info("Agent shutting down.")


app = FastAPI(
    title="Slooze AI Web Search Agent",
    description=(
        "An AI agent that accepts natural language queries, searches the web via DuckDuckGo, "
        "and uses Gemini 2.5 Flash to synthesize a grounded answer with cited sources."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Health"])
def root():
    return FileResponse("static/index.html")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.post(
    "/search",
    response_model=SearchResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Agent"],
    summary="Search the web and get an AI-generated answer",
)
def search(request: SearchRequest) -> SearchResponse:
    """
    Accepts a natural language query, retrieves live web results via DuckDuckGo,
    and returns a Gemini-synthesized answer alongside the source URLs used.

    **Example request body:**
    ```json
    {
      "query": "What are the latest specs in MacBook this year?",
      "max_results": 5
    }
    ```
    """
    try:
        result = run_agent(request)
        return result

    except EnvironmentError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except RuntimeError as e:
        logger.error(f"Agent runtime error: {e}")
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")