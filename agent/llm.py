import os
import logging
from typing import List
import google.generativeai as genai
from agent.models import Source

logger = logging.getLogger(__name__)


GEMINI_MODEL = "gemini-2.5-flash"


def _build_prompt(query: str, sources: List[Source]) -> str:
    """
    Construct the prompt that instructs Gemini to synthesize search results.

    Design decision: sources are injected as numbered snippets so the model
    can reference them cleanly. The system instruction keeps the answer
    grounded - the model should not hallucinate beyond the provided content.
    """
    source_block = "\n\n".join(
        f"[{i+1}] Title: {s.title}\nURL: {s.url}\nSnippet: {s.snippet}"
        for i, s in enumerate(sources)
    )

    return f"""You are a helpful research assistant. Your task is to answer the user's query using ONLY the information from the search results provided below.

Rules:
- Be concise and factual. Aim for 3-5 sentences.
- Do not fabricate details that are not in the snippets.
- If the snippets do not contain enough information to answer the query, say so clearly.
- Do not mention source numbers in your answer. Write naturally.

User query: {query}

Search results:
{source_block}

Provide a clear, direct answer based on the above results."""


def generate_answer(query: str, sources: List[Source]) -> str:
    """
    Call Gemini 2.5 Flash to synthesize an answer from search result snippets.

    Args:
        query: The original user query
        sources: Retrieved search results to ground the answer

    Returns:
        A synthesized answer string
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,     
                max_output_tokens=512,
            ),
        )

        prompt = _build_prompt(query, sources)
        response = model.generate_content(prompt)

        answer = response.text.strip()
        logger.info(f"Gemini generated answer ({len(answer)} chars)")
        return answer

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise RuntimeError(f"LLM generation failed: {str(e)}") from e