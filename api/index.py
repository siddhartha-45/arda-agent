"""
Lightweight ARDA API for Vercel.

The deployed app uses this file directly. Keep it free of the local FAISS,
SQLite, and Jac/Jaseci dependencies so the serverless function starts quickly.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from mangum import Mangum
except ImportError:
    Mangum = None

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

try:
    from groq import Groq
except ImportError:
    Groq = None


app = FastAPI(
    title="ARDA Research Agent API",
    description="Lightweight Autonomous Research & Decision Agent",
    version="1.0.0",
)

API_BUILD = "structured-analysis-2026-05-19"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchQuery(BaseModel):
    query: str
    depth: str = "standard"


class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str


class ResearchResponse(BaseModel):
    query: str
    status: str
    search_results: List[SearchResult]
    analysis: Optional[str] = None


def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Run a lightweight DuckDuckGo search and normalize the result shape."""
    if DDGS is None:
        raise HTTPException(
            status_code=503,
            detail="duckduckgo-search is not installed on this deployment",
        )

    try:
        with DDGS() as ddgs:
            raw_results = ddgs.text(
                query,
                region="us-en",
                safesearch="moderate",
                max_results=num_results,
            )

        results = []
        for result in raw_results or []:
            title = result.get("title") or "Untitled result"
            link = result.get("href") or result.get("url") or ""
            snippet = result.get("body") or result.get("snippet") or ""

            if title or link or snippet:
                results.append(
                    {
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                    }
                )

        return results[:num_results]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Search failed: {exc}")


def get_groq_client() -> Optional[Any]:
    """Return a Groq client when configured, otherwise let search still work."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or Groq is None:
        return None
    return Groq(api_key=api_key)


def analyze_search_results(query: str, search_results: List[Dict[str, str]]) -> str:
    """Generate an analysis from search results, with a deterministic fallback."""
    client = get_groq_client()

    if client is None:
        return (
            "Search completed. Add GROQ_API_KEY in Vercel environment variables "
            "to enable AI analysis of these results."
        )

    context = "\n\n".join(
        (
            f"{idx}. {result['title']}\n"
            f"URL: {result['link']}\n"
            f"Summary: {result['snippet']}"
        )
        for idx, result in enumerate(search_results, 1)
    )

    prompt = f"""You are ARDA, a concise research assistant.

Research query: {query}

Search results:
{context}

Write the answer in this exact structured format:

## Summary
- 2 to 3 bullets explaining what the search results indicate.

## Companies Mentioned
| Company or list source | Why it matters | Source |
| --- | --- | --- |

## Caveats
- 2 to 4 bullets about freshness, missing data, market risk, or source limits.

## Next Steps
- 3 practical bullets the user can take next.

Rules:
- Do not write placeholders like "[insert company names]".
- If the search snippets do not include specific company names, say that the available snippets point to ranked gainers pages rather than naming companies directly.
- Do not invent stock tickers, prices, returns, or company names that are not present in the search results.
- Keep it concise and skimmable.

Ground the brief only in the search results above."""

    try:
        message = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            max_tokens=900,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.choices[0].message.content or "Analysis completed."
    except Exception as exc:
        return (
            "Search completed, but AI analysis failed. "
            f"Groq error: {exc}"
        )


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "name": "ARDA Research Agent API",
        "status": "online",
        "version": "1.0.0",
        "build": API_BUILD,
        "deployment": "Vercel Serverless (Lightweight)",
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/models")
async def get_models() -> Dict[str, Dict[str, Any]]:
    return {
        "api": {
            "build": API_BUILD,
        },
        "llm": {
            "provider": "Groq",
            "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            "temperature": 0.3,
            "max_tokens": 900,
            "configured": bool(os.getenv("GROQ_API_KEY")),
        },
        "search": {
            "provider": "DuckDuckGo",
            "results_per_query": 5,
            "configured": DDGS is not None,
        },
    }


@app.get("/api/info")
async def get_info() -> Dict[str, str]:
    return {
        "name": "ARDA - Autonomous Research & Decision Agent",
        "version": "1.0.0",
        "description": "Lightweight research agent with web search and Groq analysis",
        "deployment": "Vercel Serverless",
        "github": "https://github.com/siddhartha-45/arda-agent",
    }


@app.post("/research")
async def research(input_data: ResearchQuery) -> ResearchResponse:
    query = input_data.query.strip()
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    search_results = search_web(query, num_results=5)
    analysis = (
        analyze_search_results(query, search_results)
        if search_results
        else "No search results found for this query."
    )

    return ResearchResponse(
        query=query,
        status="completed",
        search_results=[SearchResult(**result) for result in search_results],
        analysis=analysis,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": str(exc)})


handler = Mangum(app) if Mangum is not None else app
