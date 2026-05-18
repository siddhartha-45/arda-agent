"""
API_REFERENCE.md - Complete ARDA API Documentation
"""

# ARDA API Reference

## 🌐 Base URL

```
http://localhost:8000
```

## 📊 Endpoints

### 1. Health Check

**Endpoint:** `GET /`  
**Description:** Root endpoint with API info  
**Authorization:** None

**Request:**
```bash
curl http://localhost:8000/
```

**Response (200 OK):**
```json
{
  "name": "ARDA - Autonomous Research & Decision Agent",
  "version": "1.0.0",
  "description": "Production-ready agentic AI for autonomous research",
  "endpoints": {
    "POST /research": "Execute autonomous research",
    "GET /health": "Health check",
    "GET /memory/stats": "Memory statistics",
    "POST /memory/clear": "Clear memory",
    "GET /sessions/{session_id}": "Get session details"
  }
}
```

---

### 2. Execute Research

**Endpoint:** `POST /research`  
**Description:** Execute autonomous research on a query  
**Authorization:** None  
**Timeout:** 300 seconds

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "string (required)",
  "depth": "string (optional: 'standard', 'deep', 'expert')"
}
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | Yes | Research query (any length) |
| depth | string | No | Research depth level. Default: "standard" |

**Depth Levels:**
- `standard` - 3 tasks, ~30-45s
- `deep` - 5 tasks, ~50-75s
- `expert` - 7 tasks, ~80-120s

**Example Request:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in Tesla stock in 2026?",
    "depth": "deep"
  }'
```

**Response (200 OK):**
```json
{
  "query": "Should I invest in Tesla stock in 2026?",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "execution_time": 47.32,
  "tasks": [
    {
      "task_id": "task_1",
      "description": "Research Tesla's financial performance...",
      "tool": "search",
      "priority": 5,
      "status": "completed"
    },
    {
      "task_id": "task_2",
      "description": "Analyze market trends...",
      "tool": "reasoning",
      "priority": 4,
      "status": "completed"
    }
  ],
  "analyses": [
    {
      "task_id": "task_1",
      "type": "search",
      "status": "completed",
      "analysis": "Tesla's stock has shown...",
      "timestamp": 1716076820.5
    }
  ],
  "reflection": {
    "completeness": "100%",
    "assessment": "High-quality research completed",
    "tasks_status": {
      "total": 3,
      "completed": 3,
      "failed": 0
    }
  },
  "final_report": {
    "synthesis": "Based on comprehensive research...",
    "recommendation": "Consider investing in Tesla if your risk profile...",
    "research_quality": "100%",
    "tasks_completed": 3,
    "total_tasks": 3,
    "generated_at": "2024-05-18T14:20:47.32Z"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| query | string | Original research query |
| session_id | string | Unique session identifier |
| execution_time | number | Total execution time in seconds |
| tasks | array | Planned tasks with details |
| analyses | array | Task execution results |
| reflection | object | Quality assessment |
| final_report | object | Final synthesis and recommendation |

**Error Responses:**

```json
// 400 Bad Request
{
  "detail": "query field is required"
}

// 500 Internal Server Error
{
  "detail": "Research failed: API key invalid"
}

// 504 Gateway Timeout
{
  "detail": "Research timed out after 300 seconds"
}
```

---

### 3. Health Check

**Endpoint:** `GET /health`  
**Description:** Check API server health  
**Authorization:** None

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "ARDA Research Agent"
}
```

---

### 4. Memory Statistics

**Endpoint:** `GET /memory/stats`  
**Description:** Get memory system statistics  
**Authorization:** None

**Request:**
```bash
curl http://localhost:8000/memory/stats
```

**Response (200 OK):**
```json
{
  "database": {
    "total_entries": 145,
    "completed_sessions": 12,
    "cached_queries": 42
  },
  "vector_memory": {
    "total_entries": 145,
    "index_size": 145
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| database.total_entries | integer | Total memory entries in SQLite |
| database.completed_sessions | integer | Number of completed research sessions |
| database.cached_queries | integer | Number of cached query results |
| vector_memory.total_entries | integer | Embeddings stored in FAISS |
| vector_memory.index_size | integer | Size of FAISS index |

---

### 5. Clear Memory

**Endpoint:** `POST /memory/clear`  
**Description:** Clear all memory (vector and database)  
**Authorization:** None  
**Warning:** This action is irreversible!

**Request:**
```bash
curl -X POST http://localhost:8000/memory/clear
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Memory cleared"
}
```

---

### 6. Get Session Details

**Endpoint:** `GET /sessions/{session_id}`  
**Description:** Retrieve research session details  
**Authorization:** None

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| session_id | string (path) | Session ID from research response |

**Request:**
```bash
curl http://localhost:8000/sessions/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**Response (200 OK):**
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "query": "Should I invest in Tesla stock?",
  "created_at": 1716076800.0,
  "completed_at": 1716076847.32,
  "status": "completed",
  "results_summary": {
    "total_findings": 12,
    "quality_score": 0.85
  }
}
```

---

## 📝 Authentication

Currently, ARDA API has **no authentication** (development mode).

For production deployment:
```python
# Add in app.py
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/research", dependencies=[Depends(security)])
async def research(input_data: ResearchQuery):
    # Protected endpoint
    pass
```

---

## 🔄 Request/Response Workflow

### Typical Flow

```
1. CLIENT SENDS REQUEST
   POST /research
   {
     "query": "...",
     "depth": "deep"
   }
                ↓
2. SERVER RECEIVES & VALIDATES
   - Check query length
   - Validate depth parameter
   - Create session ID
                ↓
3. AGENT EXECUTES (Phase 1-5)
   - Planning phase
   - Execution phase
   - Reflection phase
   - Memory storage phase
   - Reporting phase
                ↓
4. SERVER RETURNS RESPONSE
   {
     "session_id": "...",
     "final_report": {...},
     "execution_time": 45.2
   }
                ↓
5. CLIENT RECEIVES & PROCESSES
   - Parse JSON
   - Extract recommendation
   - Store session ID for later retrieval
```

---

## ⏱️ Rate Limiting & Timeouts

**Current Behavior:**
- No built-in rate limiting
- Request timeout: 300 seconds (5 minutes)
- Concurrent requests: Limited by Groq API

**For Production:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/research")
@limiter.limit("10/minute")
async def research(request: Request, input_data: ResearchQuery):
    # Rate-limited endpoint
    pass
```

---

## 💾 Data Models

### ResearchQuery (Request)
```json
{
  "query": "string",
  "depth": "string"
}
```

### Task (Response Object)
```json
{
  "task_id": "string",
  "description": "string",
  "tool": "search|reasoning",
  "priority": "number",
  "success_criteria": "string",
  "status": "pending|completed|failed"
}
```

### Analysis (Response Object)
```json
{
  "task_id": "string",
  "type": "search|reasoning",
  "status": "completed|failed",
  "description": "string",
  "analysis": "string",
  "timestamp": "number"
}
```

### Reflection (Response Object)
```json
{
  "completeness": "string (percentage)",
  "assessment": "string",
  "tasks_status": {
    "total": "number",
    "completed": "number",
    "failed": "number"
  },
  "timestamp": "number"
}
```

### FinalReport (Response Object)
```json
{
  "synthesis": "string",
  "recommendation": "string",
  "research_quality": "string",
  "tasks_completed": "number",
  "total_tasks": "number",
  "generated_at": "string"
}
```

---

## 🔗 Integration Examples

### Python

```python
import requests
import json

def research(query, depth="standard"):
    """Execute research via API"""
    response = requests.post(
        "http://localhost:8000/research",
        json={
            "query": query,
            "depth": depth
        },
        timeout=300
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Usage
result = research("Should I invest in Tesla?", depth="deep")
print(result['final_report']['recommendation'])
```

### JavaScript/Node.js

```javascript
async function research(query, depth = "standard") {
  try {
    const response = await fetch("http://localhost:8000/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query, depth })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Research failed:", error);
    return null;
  }
}

// Usage
research("What is AI?", "deep").then(result => {
  console.log(result.final_report.recommendation);
});
```

### cURL Examples

**Simple Request:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'
```

**Advanced Request with Output Formatting:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare PyTorch vs TensorFlow",
    "depth": "deep"
  }' | jq '.final_report'
```

**Save Response to File:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest AI trends"}' \
  > research_result.json
```

---

## 🆘 Error Handling

### Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | Research completed |
| 400 | Bad Request | Check query format |
| 500 | Server Error | Check API key, logs |
| 504 | Timeout | Reduce depth or try again |

### Error Response Format

```json
{
  "detail": "Error description explaining what went wrong"
}
```

### Example Error Handling

```python
try:
    result = requests.post(
        "http://localhost:8000/research",
        json={"query": query},
        timeout=300
    )
    
    if result.status_code == 200:
        return result.json()
    elif result.status_code == 400:
        print("Bad request:", result.json()['detail'])
    elif result.status_code == 500:
        print("Server error:", result.json()['detail'])
    else:
        print(f"Unexpected error: {result.status_code}")
        
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Cannot connect to server")
```

---

## 📖 Interactive Documentation

When running the server, access interactive API docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

These provide:
- ✅ Endpoint documentation
- ✅ Try-it-out functionality
- ✅ Parameter validation
- ✅ Response examples

---

## 🚀 Production Deployment

For production use, consider:

1. **Authentication:** Add API keys or OAuth
2. **Rate Limiting:** Limit requests per client
3. **Logging:** Comprehensive request/response logging
4. **Monitoring:** Uptime, latency, error tracking
5. **Caching:** Redis for frequently asked queries
6. **Database:** PostgreSQL instead of SQLite
7. **Load Balancing:** Multiple instances behind reverse proxy

Example production setup:

```bash
# Run with Gunicorn + Uvicorn workers
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Behind Nginx for SSL and rate limiting
# With PostgreSQL for production database
# With Redis for caching
```

---

## 📊 Monitoring API Usage

Track API metrics:

```python
# In routes.py, add middleware
import time
from collections import defaultdict

request_times = defaultdict(list)

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    path = request.url.path
    request_times[path].append(duration)
    
    response.headers["X-Process-Time"] = str(duration)
    return response
```

---

**Version:** 1.0.0  
**Last Updated:** May 2024  
**Maintainer:** ARDA Development Team
