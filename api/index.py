"""
Vercel Serverless API for ARDA - Autonomous Research & Decision Agent
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

# Import ARDA components
from main import ARDAAgent

# Initialize FastAPI app
app = FastAPI(
    title="ARDA Research Agent API",
    description="Autonomous Research & Decision Agent",
    version="1.0.0"
)

# Enable CORS for Vercel
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

# Initialize ARDA agent (cached)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        try:
            _agent = ARDAAgent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    return _agent

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
        "github": "https://github.com/yourusername/arda-agent"
    }

# For Vercel
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Vercel serverless handler
from mangum import Mangum

handler = Mangum(app)
