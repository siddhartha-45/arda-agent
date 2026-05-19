"""
Vercel Serverless API for ARDA - Autonomous Research & Decision Agent
Optimized for serverless deployment (minimal imports on startup)
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from mangum import Mangum

# Initialize FastAPI app
app = FastAPI(
    title="ARDA Research Agent API",
    description="Autonomous Research & Decision Agent",
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

class ResearchResponse(BaseModel):
    session_id: str
    query: str
    status: str
    findings: Dict[str, Any]
    recommendations: Optional[str] = None

# Lazy-load agent only when needed
_agent = None
_import_error = None

def get_agent():
    """Lazy-load ARDA agent - only import when first API call is made"""
    global _agent, _import_error
    
    if _import_error:
        raise HTTPException(
            status_code=503, 
            detail=f"Agent initialization failed: {_import_error}"
        )
    
    if _agent is None:
        try:
            import sys
            from pathlib import Path
            # Add parent directory to path for imports
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from main import ARDAAgent
            _agent = ARDAAgent()
        except Exception as e:
            _import_error = str(e)
            raise HTTPException(
                status_code=503,
                detail=f"Failed to initialize agent: {str(e)}"
            )
    return _agent


# Health endpoints (no dependencies)
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "ARDA Research Agent API",
        "status": "online",
        "version": "1.0.0",
        "deployment": "Vercel Serverless"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

# API Info endpoints (no dependencies)
@app.get("/api/models")
async def get_models():
    """Get available models and configuration"""
    return {
        "llm": {
            "provider": "Groq",
            "model": "llama-3.1-8b-instant",
            "temperature": 0.7,
            "max_tokens": 2048
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
        "description": "Production-ready agentic AI with Jac/Jaseci",
        "capabilities": [
            "Autonomous planning and task decomposition",
            "Multi-tool execution with retry logic",
            "Reflection and self-correction",
            "Semantic memory with FAISS",
            "Research synthesis and recommendations"
        ],
        "deployment": "Vercel Serverless",
        "github": "https://github.com/siddhartha-45/arda-agent"
    }

# Research endpoint (loads agent on first call)
@app.post("/research")
async def research(query: ResearchQuery) -> ResearchResponse:
    """
    Execute autonomous research on a query
    
    Args:
        query: ResearchQuery object with 'query' and optional 'depth'
        
    Returns:
        ResearchResponse with findings and recommendations
    """
    try:
        agent = get_agent()
        
        # Execute research
        result = agent.research(query.query, depth=query.depth)
        
        return ResearchResponse(
            session_id=result.get('session_id', 'unknown'),
            query=result.get('query', query.query),
            status="completed",
            findings=result.get('findings', {}),
            recommendations=result.get('recommendations')
        )
    
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
