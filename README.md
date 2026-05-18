# ARDA - Autonomous Research & Decision Agent

> **Production-ready agentic AI application** using Jac/Jaseci, Python, FastAPI, and Groq API
> 
> A complete, end-to-end autonomous agent system demonstrating **true agentic behavior** with planning, execution, reflection, memory management, and dynamic decision-making.

## 🎯 Overview

ARDA (Autonomous Research & Decision Agent) is a **production-ready AI agent system** that demonstrates genuine autonomous capabilities:

- ✅ **Autonomous Planning** - Breaks down complex queries into executable tasks
- ✅ **Tool Usage** - Dynamically selects and uses web search tools
- ✅ **Multi-Step Reasoning** - Chains reasoning across multiple tasks
- ✅ **Semantic Memory** - Stores and retrieves findings using FAISS
- ✅ **Reflection & Self-Correction** - Evaluates work quality and identifies gaps
- ✅ **Dynamic Execution** - Adapts based on intermediate results
- ✅ **Graph-Native Architecture** - Built on Jac nodes, edges, and walkers

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                            │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   PLANNER WALKER        │ → Task Decomposition
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────────────┐
        │   EXECUTOR WALKER             │ → Search + Reasoning
        │  - SearchTool                 │
        │  - LLMTool                    │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼────────────────────┐
        │   REFLECTION WALKER             │ → Quality Evaluation
        └────────────┬────────────────────┘
                     │
        ┌────────────▼─────────────────────┐
        │   MEMORY WALKER                  │ → Semantic Storage
        │  - VectorMemory (FAISS)          │
        │  - DatabaseMemory (SQLite)       │
        └────────────┬─────────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │   SUMMARIZER WALKER           │ → Report Generation
        └────────────┬──────────────────┘
                     │
        └────────────▼────────────────────┘
              Final Report & Recommendation
```

## 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Framework** | Jac/Jaseci | Graph-native agent orchestration |
| **Language** | Python 3.10+ | Core implementation |
| **LLM** | Groq API + Llama 3.1 8b | Free, fast inference |
| **Search** | DuckDuckGo API | Web research tool |
| **Vector Memory** | FAISS + Sentence Transformers | Semantic search & memory |
| **Persistent Memory** | SQLite | Session & historical storage |
| **REST API** | FastAPI | HTTP interface |
| **Server** | Uvicorn | ASGI server |

## 📋 Project Structure

```
arda-agent/
│
├── main.py                          # Main agent orchestration
├── app.py                           # FastAPI server
├── requirements.txt                 # Python dependencies
├── .env.example                     # Configuration template
├── README.md                        # This file
│
├── jac_app/
│   ├── graph.jac                   # Graph nodes & edges definition
│   ├── planner.jac                 # PlanTasks walker
│   ├── executor.jac                # ExecuteTasks walker
│   ├── reflection.jac              # ReflectOnResults walker
│   ├── memory.jac                  # Memory walkers
│   └── summarizer.jac              # GenerateReport walker
│
├── tools/
│   ├── llm_tool.py                 # Groq API wrapper
│   ├── search_tool.py              # DuckDuckGo search wrapper
│   ├── vector_memory.py            # FAISS semantic memory
│   └── db_memory.py                # SQLite persistent memory
│
├── api/
│   └── routes.py                   # FastAPI endpoints
│
└── database/
    └── memory.db                   # SQLite database (created at runtime)
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Groq API key (get free at https://console.groq.com)
- ~500MB disk space for FAISS indices and embeddings

### Step 1: Clone Repository

```bash
cd e:\jac\arda-agent
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Jaseci & Jac

```bash
pip install jaseci
jaseci -m jac --version
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy template
copy .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=gsk_your_key_here
```

Get your free Groq API key:
1. Visit https://console.groq.com
2. Sign up
3. Create API key
4. Add to `.env`

## ▶️ Running the Agent

### Option 1: Standalone Agent (CLI)

```bash
python main.py
```

**Example Query:**
```
Query: Should I invest in Tesla stock in 2026? What are the pros and cons?
```

**Output:**
```
============================================================
ARDA RESEARCH AGENT
============================================================
Query: Should I invest in Tesla stock in 2026? What are the pros and cons?
Session: 3fa85f64-5717-4562-b3fc-2c963f66afa6
Depth: standard
============================================================

[PHASE 1/5] PLANNING - Breaking down query into tasks...
  ✓ task_1: Research Tesla stock performance and current metrics
  ✓ task_2: Analyze market trends and competitive landscape
  ✓ task_3: Evaluate investment risks and opportunities

[PHASE 2/5] EXECUTION - Executing planned tasks...
  → task_1: Research Tesla stock performance...
  → task_2: Analyze market trends and competitive...
  → task_3: Evaluate investment risks and...

[PHASE 3/5] REFLECTION - Evaluating research quality...
  • completeness: 100%
  • assessment: Comprehensive research completed
  • timestamp: 1716076800.0

[PHASE 4/5] MEMORY - Storing findings in semantic memory...
✓ Findings stored in vector and database memory

[PHASE 5/5] REPORTING - Generating final report...
  • synthesis: Based on recent analysis...
  • recommendation: Investment in Tesla depends on...
  • research_quality: 100%

============================================================
RESEARCH COMPLETE
============================================================
Execution Time: 45.23s
Tasks: 3/3 completed
Success Rate: 100%
Recommendation: Consider Tesla investment based on...
============================================================
```

### Option 2: FastAPI Server

```bash
python app.py
```

Server runs at `http://localhost:8000`

Access documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ARDA Research Agent"
}
```

### Execute Research

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I invest in Tesla stock in 2026?",
    "depth": "deep"
  }'
```

**Request:**
```json
{
  "query": "Should I invest in Tesla stock in 2026?",
  "depth": "standard|deep|expert"
}
```

**Response:**
```json
{
  "query": "Should I invest in Tesla stock in 2026?",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "execution_time": 47.32,
  "tasks": [
    {
      "task_id": "task_1",
      "description": "Research Tesla's financial performance in 2024-2026",
      "tool": "search",
      "priority": 5,
      "status": "completed"
    }
  ],
  "analyses": [
    {
      "task_id": "task_1",
      "type": "search",
      "status": "completed",
      "analysis": "Tesla's stock performance shows..."
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
    "recommendation": "Consider investing in Tesla if...",
    "research_quality": "100%"
  }
}
```

### Get Memory Statistics

```bash
curl http://localhost:8000/memory/stats
```

**Response:**
```json
{
  "database": {
    "total_entries": 45,
    "completed_sessions": 12,
    "cached_queries": 23
  },
  "vector_memory": {
    "total_entries": 45,
    "index_size": 45
  }
}
```

### Clear Memory

```bash
curl -X POST http://localhost:8000/memory/clear
```

## 🤖 Agentic Behavior Explained

ARDA exhibits **genuine autonomous agent capabilities**:

### 1. Autonomous Planning
- Analyzes query complexity
- Breaks into 3-7 subtasks based on depth level
- Assigns appropriate tools (search vs. reasoning)
- Sets priorities and success criteria

**Example:**
```
Query: "Should I invest in Tesla?"

Generated Tasks:
├─ task_1: Research Tesla financials (tool: search, priority: 5)
├─ task_2: Analyze EV market trends (tool: search, priority: 4)
├─ task_3: Competitive analysis (tool: reasoning, priority: 4)
└─ task_4: Risk assessment (tool: reasoning, priority: 3)
```

### 2. Dynamic Tool Usage
- Selects appropriate tools per task
- Falls back gracefully on failures
- Retries failed tasks up to 3 times
- Adapts strategy based on results

**Tool Router Logic:**
```python
if task.tool == 'search':
    results = search_tool.search(description)
    analysis = llm.analyze(results)
else:  # reasoning
    analysis = llm.reason_deeply(description)
```

### 3. Multi-Step Reasoning
- Chains reasoning across tasks
- Builds on intermediate conclusions
- Validates findings against multiple sources
- Identifies contradictions

### 4. Semantic Memory
- Stores findings with embeddings
- Enables similarity search on historical queries
- Supports context retrieval for new queries
- Persistent across sessions

**Memory Flow:**
```
Findings → Embed with Sentence Transformers → 
Store in FAISS → Enable semantic retrieval
```

### 5. Reflection & Self-Correction
- Evaluates research completeness (0-100%)
- Checks confidence levels
- Identifies research gaps
- Decides if more research needed

**Reflection Metrics:**
```
Completeness = completed_tasks / total_tasks
Quality = avg(finding_confidence_scores)
Gap_identification = identifies areas needing more depth
```

### 6. Dynamic Execution
- Responds to task success/failure
- Adjusts strategy based on results
- Skips redundant analysis
- Prioritizes high-impact research

### 7. Graph-Native Architecture
Uses Jac's graph capabilities:
- **Nodes**: UserQuery, Task, SearchResult, Analysis, MemoryEntry, ReflectionRecord, FinalReport
- **Edges**: plannedTask, executionEdge, memoryLink, analysisLink, reflectionEdge, reportLink
- **Walkers**: PlanTasks, ExecuteTasks, ReflectOnResults, StoreMemory, MemoryRetrieval, GenerateReport

```jac
node Task {
    has task_id: str;
    has description: str;
    has status: str;  # pending, in_progress, completed, failed
}

walker ExecuteTasks {
    # Traverses task nodes, updates status
    # Performs actual execution
}
```

## 📊 Example Queries

Try these queries to see ARDA in action:

### 1. Investment Decision
```
"Should I invest in Tesla stock in 2026? What are the pros and cons?"
```
**Expected Behavior:** Searches for financial data, market analysis, competitive position, and risks

### 2. Technology Analysis
```
"What are the latest developments in quantum computing and their practical applications?"
```
**Expected Behavior:** Researches recent breakthroughs, challenges, and real-world use cases

### 3. Policy/Trend Analysis
```
"How is climate change affecting agricultural productivity and what solutions exist?"
```
**Expected Behavior:** Gathers scientific data, policy information, and solution approaches

### 4. Comparative Analysis
```
"Compare the benefits and drawbacks of electric vehicles versus hydrogen fuel cell vehicles"
```
**Expected Behavior:** Researches both technologies, environmental impact, and practicality

## 🔍 Advanced Features

### Memory Persistence

Research findings are stored in two systems:

**1. Vector Memory (FAISS)**
```python
vector_memory.add(
    entry_id="session_123_task_1",
    text="Tesla stock analysis showing...",
    metadata={"type": "financial", "confidence": 0.85}
)

# Later retrieval
results = vector_memory.search("Tesla investment", top_k=5)
```

**2. Database Memory (SQLite)**
```python
db_memory.insert({
    'session_id': 'session_123',
    'task_id': 'task_1',
    'content': '...',
    'category': 'financial_analysis',
    'type': 'search_result'
})

# Query by session
findings = db_memory.query_by_session('session_123')
```

### Retry Mechanism

Failed tasks are automatically retried:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = execute_task(task)
        break
    except Exception:
        if attempt < max_retries - 1:
            continue
        else:
            mark_as_failed(task)
```

### Confidence Scoring

Each finding includes confidence assessment:
```python
confidence = llm.score_relevance(
    text=finding,
    query=original_query
)  # Returns 0.0-1.0
```

### Session Tracking

All research sessions are tracked:
```json
{
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "query": "Should I invest in Tesla?",
  "created_at": 1716076800.0,
  "completed_at": 1716076847.32,
  "status": "completed",
  "results_summary": {...}
}
```

## 🛠️ Configuration

### Research Depth Levels

Edit `.env` to set default or customize per query:

```
# Light research - 3 tasks
depth: "standard"

# Comprehensive - 5 tasks  
depth: "deep"

# Expert-level - 7 tasks with specialist analysis
depth: "expert"
```

### LLM Parameters

Customize in `tools/llm_tool.py`:
```python
self.temperature = 0.7      # Creativity (0-1)
self.max_tokens = 2048      # Response length
self.model = "llama-3.1-8b-instant"  # Model selection
```

### Database Configuration

Change database path in `.env`:
```
DATABASE_PATH=database/memory.db
```

## 📈 Performance Metrics

### Typical Execution Times (by depth)

| Depth | Tasks | Search Calls | Reasoning Calls | Avg Time |
|-------|-------|-------------|-----------------|----------|
| Standard | 3 | 2 | 1 | 30-45s |
| Deep | 5 | 3 | 2 | 50-75s |
| Expert | 7 | 4 | 3 | 80-120s |

### Memory Usage

| Component | Typical Size |
|-----------|-------------|
| Vector Memory (FAISS) | 10-50MB (1000s entries) |
| Database (SQLite) | 1-5MB per 100 sessions |
| Model Embedding | 400MB (Sentence Transformers) |

## 🧪 Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Test

```python
from main import ARDAAgent

agent = ARDAAgent()
result = agent.research("Test query", depth="standard")
assert result['session_id'] is not None
assert result['execution_time'] > 0
assert len(result['final_report']) > 0
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10 -c 2 -p query.json http://localhost:8000/research
```

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Ensure `.env` file exists with valid key:
```bash
echo GROQ_API_KEY=gsk_your_key > .env
```

### Issue: "Module not found: groq"
**Solution:** Reinstall requirements:
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused" on memory operations
**Solution:** Ensure SQLite file permissions:
```bash
mkdir -p database
chmod 755 database
```

### Issue: Slow response times
**Solution:** 
1. Use "standard" depth instead of "deep"
2. Check network connectivity
3. Monitor Groq API quota

## 📚 Jac/Jaseci Integration

### Running Jac Files Directly

```bash
# Run individual walker
jaseci run planner.jac

# Debug walker
jaseci debug executor.jac

# View graph
jaseci view graph.jac
```

### Building Jac Modules

```bash
# Build for production
jac build jac_app/graph.jac

# Generate code
jac gen jac_app/graph.jac
```

### Extending the Graph

Add new walker:
```jac
walker NewAgent {
    has input_data: dict;
    
    :walker:activity {
        # Implementation
    }
}
```

## 📖 Documentation

### Internal Modules

- **`llm_tool.py`**: Groq API wrapper with streaming, caching
- **`search_tool.py`**: Multi-source web search wrapper
- **`vector_memory.py`**: FAISS semantic memory with batch operations
- **`db_memory.py`**: SQLite schema with session tracking
- **`routes.py`**: FastAPI endpoints with async support

### External Resources

- [Jac Documentation](https://github.com/Jaseci-Labs/jac)
- [Jaseci Docs](https://docs.jaseci.org)
- [Groq API Docs](https://console.groq.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [FAISS Documentation](https://faiss.ai)

## 🔐 Security Considerations

- **API Keys**: Never commit `.env` file; use `.env.example` template
- **Database**: SQLite file should not be world-readable
- **Memory Cleanup**: Regularly clean old entries with `cleanup_old_entries(days=30)`
- **Input Validation**: All inputs are validated with Pydantic

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

```bash
docker build -t arda-agent .
docker run -e GROQ_API_KEY=your_key -p 8000:8000 arda-agent
```

### Production Checklist

- [ ] Use Uvicorn with multiple workers: `uvicorn app:app --workers 4`
- [ ] Set up logging: `LOG_LEVEL=INFO`
- [ ] Configure database backups
- [ ] Monitor memory usage
- [ ] Set up error alerting
- [ ] Use reverse proxy (nginx) for rate limiting
- [ ] Enable HTTPS/TLS

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Additional tool integrations (Arxiv, Wikipedia, financial APIs)
- Advanced reflection mechanisms
- Multi-language support
- Distributed execution
- Advanced memory retrieval algorithms
- Custom LLM model support

## 📧 Support

For issues and questions:
1. Check `TROUBLESHOOTING` section
2. Review Jac documentation
3. Check Groq API status
4. Create GitHub issue with:
   - Full error message
   - Reproduction steps
   - Environment details

## 🎯 Roadmap

- [ ] Web UI dashboard for visualization
- [ ] Multi-agent collaboration
- [ ] Real-time streaming responses
- [ ] Advanced scheduling
- [ ] Cost optimization
- [ ] Custom reasoning engines
- [ ] Integration with other LLM providers

---

**Built with ❤️ using Jac/Jaseci, Python, and Groq**

**Version 1.0.0** | Production Ready | Fully Open Source
