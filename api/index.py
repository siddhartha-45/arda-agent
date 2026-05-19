"""
Lightweight ARDA API for Vercel - no heavy ML dependencies
Uses Groq LLM and DuckDuckGo search only
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from mangum import Mangum
from pathlib import Path

# Import lightweight dependencies
try:
    from groq import Groq
    from duckduckgo_search import DDGS
except ImportError as e:
    raise RuntimeError(f"Missing required package: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="ARDA Research Agent API",
    description="Lightweight Autonomous Research & Decision Agent",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
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

# Initialize clients
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")
    return Groq(api_key=api_key)

def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """Search the web using DuckDuckGo"""
    try:
        results = []
        ddgs = DDGS()
        for result in ddgs.text(query, max_results=num_results):
            results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("body", "")[:500]
            })
        return results
    except Exception as e:
        return []

def analyze_search_results(query: str, results: List[Dict[str, Any]]) -> str:
    """Use Groq to analyze search results"""
    if not results:
        return "No search results found."
    
    try:
        client = get_groq_client()
        
        # Format search results for LLM
        formatted_results = "\n".join([
            f"- {r['title']}: {r['snippet']}"
            for r in results[:3]
        ])
        
        prompt = f"""Based on the following search results, provide a brief analysis (2-3 sentences) for the query: "{query}"

Search Results:
{formatted_results}

Analysis:"""
        
        message = client.messages.create(
            model="llama-3.1-8b-instant",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"Analysis unavailable: {str(e)}"

# Root endpoint - serve web UI
@app.get("/")
async def root():
    """Serve the web UI"""
    try:
        public_dir = Path(__file__).parent.parent / "public"
        index_file = public_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")
    except:
        pass
    # Fallback to JSON if HTML not found
    return {
        "name": "ARDA Research Agent API",
        "status": "online",
        "version": "1.0.0",
        "deployment": "Vercel Serverless (Lightweight)"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

# API Info endpoints
@app.get("/api/models")
async def get_models():
    """Get available models and configuration"""
    return {
        "llm": {
            "provider": "Groq",
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
            "max_tokens": 500
        },
        "search": {
            "provider": "DuckDuckGo",
            "results_per_query": 5
        }
    }

@app.get("/api/info")
async def get_info():
    """Get ARDA information"""
    return {
        "name": "ARDA - Autonomous Research & Decision Agent",
        "version": "1.0.0",
        "description": "Lightweight research agent with Groq LLM and web search",
        "deployment": "Vercel Serverless",
        "note": "This is the lightweight Vercel version. Full Jaseci version available locally.",
        "github": "https://github.com/siddhartha-45/arda-agent"
    }

# Research endpoint
@app.post("/research")
async def research(query: ResearchQuery) -> ResearchResponse:
    """
    Execute research on a query using web search and LLM analysis
    
    Args:
        query: ResearchQuery object with 'query' and optional 'depth'
        
    Returns:
        ResearchResponse with search results and AI analysis
    """
    if not query.query or len(query.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    try:
        # Search the web
        search_results = search_web(query.query, num_results=5)
        
        if not search_results:
            return ResearchResponse(
                query=query.query,
                status="completed",
                search_results=[],
                analysis="No search results found for this query."
            )
        
        # Analyze results with LLM
        analysis = analyze_search_results(query.query, search_results)
        
        # Convert to response model
        results_formatted = [
            SearchResult(
                title=r["title"],
                link=r["link"],
                snippet=r["snippet"]
            )
            for r in search_results
        ]
        
        return ResearchResponse(
            query=query.query,
            status="completed",
            search_results=results_formatted,
            analysis=analysis
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Vercel serverless handler
handler = Mangum(app)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

# API Info endpoints
@app.get("/api/models")
async def get_models():
    """Get available models and configuration"""
    return {
        "llm": {
            "provider": "Groq",
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
            "max_tokens": 500
        },
        "search": {
            "provider": "DuckDuckGo",
            "results_per_query": 5
        }
    }

@app.get("/api/info")
async def get_info():
    """Get ARDA information"""
    return {
        "name": "ARDA - Autonomous Research & Decision Agent",
        "version": "1.0.0",
        "description": "Lightweight research agent with Groq LLM and web search",
        "deployment": "Vercel Serverless",
        "note": "This is the lightweight Vercel version. Full Jaseci version available locally.",
        "github": "https://github.com/siddhartha-45/arda-agent"
    }

# Research endpoint
@app.post("/research")
async def research(query: ResearchQuery) -> ResearchResponse:
    """
    Execute research on a query using web search and LLM analysis
    
    Args:
        query: ResearchQuery object with 'query' and optional 'depth'
        
    Returns:
        ResearchResponse with search results and AI analysis
    """
    if not query.query or len(query.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    try:
        # Search the web
        search_results = search_web(query.query, num_results=5)
        
        if not search_results:
            return ResearchResponse(
                query=query.query,
                status="completed",
                search_results=[],
                analysis="No search results found for this query."
            )
        
        # Analyze results with LLM
        analysis = analyze_search_results(query.query, search_results)
        
        # Convert to response model
        results_formatted = [
            SearchResult(
                title=r["title"],
                link=r["link"],
                snippet=r["snippet"]
            )
            for r in search_results
        ]
        
        return ResearchResponse(
            query=query.query,
            status="completed",
            search_results=results_formatted,
            analysis=analysis
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Vercel serverless handler
handler = Mangum(app)
