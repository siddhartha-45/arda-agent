"""
FastAPI application server for ARDA
Provides REST API for autonomous research
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import routes
from api.routes import router

# Create app
app = FastAPI(
    title="ARDA - Autonomous Research & Decision Agent",
    description="Production-ready agentic AI system for autonomous research",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "ARDA - Autonomous Research & Decision Agent",
        "version": "1.0.0",
        "description": "Production-ready agentic AI for autonomous research",
        "endpoints": {
            "POST /research": "Execute autonomous research on a query",
            "GET /health": "Health check",
            "GET /memory/stats": "Memory statistics",
            "POST /memory/clear": "Clear memory",
            "GET /sessions/{session_id}": "Get session details"
        },
        "documentation": "/docs",
        "openapi_schema": "/openapi.json"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
