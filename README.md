# SloozeAI - Web Search Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange?style=flat-square&logo=google)
![Tavily](https://img.shields.io/badge/Search-Tavily-purple?style=flat-square)


**An AI-powered web search agent that retrieves live search results and synthesizes grounded answers using Gemini 2.5 Flash.**

[Live Demo](https://websearch-agent.onrender.com) · [API Docs](https://websearch-agent.onrender.com/docs) 

</div>

---

## Overview

SloozeAI is a full-stack AI agent that accepts a natural language query, searches the live web via Tavily, and uses Google Gemini 2.5 Flash to synthesize a concise, grounded answer — along with the source URLs used to generate it.

---

## Demo

> **Query:** What are the latest specs in MacBook this year?

**Answer:**
> Recent MacBook Pro models feature Apple's M5 Pro and M5 Max processors along with Apple's N1 wireless chip for Wi-Fi 7. Storage starts at 1TB for M5 Pro and 2TB for M5 Max configurations...

**Sources:**
- [Best MacBooks We've Tested – CNET](https://www.cnet.com/tech/computing/best-macbook/)
- [Apple introduces MacBook Pro with M5 Pro and M5 Max](https://www.apple.com/newsroom/...)
- [Which Apple MacBook Should You Buy? – WIRED](https://www.wired.com/story/which-macbook-should-you-buy/)

---

## Features

- Natural language query input via a clean Google-style UI
- Live web search powered by Tavily Search API
- AI-generated answers grounded in retrieved content using Gemini 2.5 Flash
- Source attribution with title, URL and snippet for every result
- REST API with auto-generated Swagger docs at `/docs`
- Error handling for search failures, LLM quota limits and missing config
- Fully deployed on Render with a static frontend served from FastAPI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| LLM | Gemini 2.5 Flash (Google AI Studio) |
| Web search | Tavily Search API |
| Data validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Deployment | Render |

---

## Project Structure

```
websearch-agent/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # Orchestration - ties search and LLM together
│   ├── search_tool.py    # Tavily search integration
│   ├── llm.py            # Gemini 2.5 Flash integration
│   └── models.py         # Pydantic request/response models
├── static/
│   └── index.html        # Frontend UI (search page)
├── main.py               # FastAPI app, routes, middleware
├── requirements.txt
├── runtime.txt           # Python version pin for Render
├── .env.example
└── README.md
```

---

## Architecture

```
User Query (Browser UI)
        │
        ▼
POST /search  ←─ FastAPI (main.py)
        │         Pydantic validates request
        ▼
Agent Core (agent/agent.py)
        │
        ├──► Search Tool (agent/search_tool.py)
        │       Tavily API → top 5 results
        │       Returns: title, URL, snippet per result
        │
        └──► LLM (agent/llm.py)
                Gemini 2.5 Flash
                Prompt = query + numbered snippets
                Returns: grounded, synthesized answer
        │
        ▼
JSON Response
  { query, answer, sources[], result_count }
        │
        ▼
Frontend renders answer card + source cards
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/app/apikey) API key (free)
- A [Tavily](https://tavily.com) API key (free tier: 1000 searches/month)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/MohammedFaizan20/websearch-agent.git
cd websearch-agent
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

```bash
cp .env
```

Open `.env` and add your keys:

```
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**5. Run the server**

```bash
python -m uvicorn main:app --reload
```

The server starts at `http://localhost:8000`.

---

## Usage

### Browser UI

Open `http://localhost:8000` in your browser for the full search interface.

### Swagger UI

Open `http://localhost:8000/docs` to explore and test the API interactively.

### cURL

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest AI models in 2025?", "max_results": 5}'
```


### Response Format

```json
{
  "query": "What are the latest AI models in 2025?",
  "answer": "In 2025, several major AI labs released flagship models...",
  "sources": [
    {
      "title": "Article title",
      "url": "https://example.com/article",
      "snippet": "Brief excerpt from the page..."
    }
  ],
  "result_count": 5
}
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend UI |
| `GET` | `/health` | Health check |
| `POST` | `/search` | Run the agent pipeline |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

### POST /search

**Request body:**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | Yes | — | Natural language search query (3–500 chars) |
| `max_results` | integer | No | 5 | Number of search results to retrieve (1–10) |

---

## Design Decisions

### Tavily over DuckDuckGo

Tavily is purpose-built for AI agents and returns clean, structured results without bot detection issues. DuckDuckGo's unofficial library frequently returns `202 Ratelimit` errors in automated environments regardless of usage frequency. Tavily's free tier (1000 searches/month) is sufficient for demo and evaluation use.

### Snippet-based retrieval over full page content

The agent uses search result snippets rather than fetching and parsing full web pages. This keeps latency low (single network hop vs. N parallel fetches) and avoids HTML parsing complexity. The trade-off is shallower context for queries that need in-depth page content. A future improvement would be adding a selective fetch step for the top 1–2 results.

### Gemini temperature set to 0.3

Low temperature keeps answers factual and grounded in the retrieved snippets rather than allowing the model to extrapolate. The prompt explicitly instructs the model not to fabricate details beyond the provided content.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `TAVILY_API_KEY` | Yes | Tavily Search API key |

---
