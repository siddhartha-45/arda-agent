"""
Lightweight ARDA API for Vercel - no heavy ML dependencies
Uses Groq LLM and DuckDuckGo search only
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from mangum import Mangum

# Import lightweight dependencies
try:
    from groq import Groq
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

def research_with_groq(query: str) -> Dict[str, Any]:
    """Use Groq LLM to research and analyze a query"""
    try:
        client = get_groq_client()
        
        # Research prompt
        research_prompt = f"""You are an expert research assistant. Provide comprehensive research findings for this query:

Query: {query}

Please provide:
1. Key Findings (3-5 main points)
2. Analysis (2-3 paragraphs of detailed analysis)
3. Recommendations (3-5 actionable recommendations)

Format your response as a structured research report."""
        
        message = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": research_prompt}
            ]
        )
        
        research_text = message.choices[0].message.content
        
        # Parse the response into sections
        sections = {
            "findings": [],
            "analysis": "",
            "recommendations": []
        }
        
        lines = research_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'findings' in line.lower():
                current_section = 'findings'
            elif 'analysis' in line.lower():
                current_section = 'analysis'
            elif 'recommendations' in line.lower():
                current_section = 'recommendations'
            elif current_section and line.startswith(('-', '•', '*')):
                clean_line = line.lstrip('-•* ').strip()
                if current_section in ['findings', 'recommendations']:
                    sections[current_section].append(clean_line)
            elif current_section == 'analysis' and line:
                sections['analysis'] += line + ' '
        
        # Create search result objects from findings
        search_results = []
        for idx, finding in enumerate(sections.get('findings', [])[:5], 1):
            search_results.append(SearchResult(
                title=f"Finding {idx}",
                link="#",
                snippet=finding[:300]
            ))
        
        return {
            "search_results": search_results,
            "analysis": sections['analysis'].strip() if sections['analysis'] else research_text[:500],
            "recommendations": ' '.join(sections.get('recommendations', []))
        }
    
    except Exception as e:
        return {
            "search_results": [],
            "analysis": f"Error during research: {str(e)}",
            "recommendations": ""
        }

# Root endpoint - serve web UI info
@app.get("/")
async def root():
    """Root endpoint - redirects to web UI"""
    return {
        "name": "ARDA Research Agent API",
        "status": "online",
        "version": "1.0.0",
        "deployment": "Vercel Serverless (Lightweight)",
        "note": "Open https://arda-research-agent.vercel.app/ in browser for web UI"
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
            "max_tokens": 1500
        }
    }

@app.get("/api/info")
async def get_info():
    """Get ARDA information"""
    return {
        "name": "ARDA - Autonomous Research & Decision Agent",
        "version": "1.0.0",
        "description": "Lightweight research agent powered by Groq LLM",
        "deployment": "Vercel Serverless",
        "note": "This is the lightweight Vercel version. Full Jaseci version available locally.",
        "github": "https://github.com/siddhartha-45/arda-agent"
    }

# Research endpoint
@app.post("/research")
async def research(query: ResearchQuery) -> ResearchResponse:
    """
    Execute research on a query using Groq LLM
    
    Args:
        query: ResearchQuery object with 'query' and optional 'depth'
        
    Returns:
        ResearchResponse with research findings and AI analysis
    """
    if not query.query or len(query.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    try:
        # Research using Groq
        research_results = research_with_groq(query.query)
        
        return ResearchResponse(
            query=query.query,
            status="completed",
            search_results=research_results.get('search_results', []),
            analysis=research_results.get('analysis', 'No analysis available')
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
