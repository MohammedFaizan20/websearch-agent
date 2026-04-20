from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Natural language search query")
    max_results: Optional[int] = Field(default=5, ge=1, le=10, description="Number of search results to retrieve")


class Source(BaseModel):
    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source]
    result_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None