"""
ARCHITECTURE.md - System Design and Jac/Jaseci Integration
"""

# ARDA System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Layer                             │
│  CLI / FastAPI REST / Streamlit UI / Python Integration      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Orchestration Layer                         │
│  main.py / ARDAAgent - Coordinates research phases           │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──┐  ┌──────▼──┐  ┌─────▼──────┐
│  Jac     │  │  Tools  │  │  Memory    │
│  Walkers │  │  Modules│  │  Systems   │
│          │  │         │  │            │
└────┬─────┘  └────┬────┘  └─────┬──────┘
     │             │             │
     │      ┌──────┴─────┐       │
     │      │            │       │
     │   ┌──▼──┐  ┌──────▼──┐   │
     │   │LLM  │  │ Search  │   │
     │   │Tool │  │  Tool   │   │
     │   └─────┘  └─────────┘   │
     │                           │
     └───────────────┬───────────┘
                     │
        ┌────────────┼──────────────┐
        │            │              │
    ┌───▼─────┐ ┌────▼────┐ ┌──────▼───┐
    │FAISS    │ │SQLite   │ │Groq API  │
    │Vector   │ │Database │ │External  │
    │Memory   │ │         │ │Services  │
    └─────────┘ └─────────┘ └──────────┘
```

---

## 🔄 5-Phase Execution Model

### Phase 1: Planning
```
INPUT: User query
↓
[PLANNER WALKER]
- Parse query complexity
- Determine task count based on depth
- Generate 3-7 tasks
↓
OUTPUT: Task list with priorities
```

**Example:**
```
Query: "Should I invest in Tesla stock?"

Generated Tasks:
├─ task_1: Research Tesla's financial performance (priority: 5, tool: search)
├─ task_2: Analyze EV market trends (priority: 4, tool: search)
├─ task_3: Competitive analysis (priority: 4, tool: reasoning)
└─ task_4: Investment risk assessment (priority: 3, tool: reasoning)
```

---

### Phase 2: Execution
```
INPUT: Task list
↓
For each task:
  [EXECUTOR WALKER]
  ├─ If tool == "search"
  │  ├─ Call SearchTool (DuckDuckGo)
  │  ├─ Get 5 web results
  │  └─ Call LLMTool to analyze
  │
  └─ If tool == "reasoning"
     ├─ Call LLMTool with prompt
     └─ Get detailed analysis
     
  On failure: Retry up to 3 times
↓
OUTPUT: Task results with analyses
```

**Example:**
```
task_1: Research Tesla's financial performance
├─ Search: "Tesla financial results 2024 2025"
├─ Results: 5 articles found
├─ Analysis by LLM:
│  "Tesla Q3 2024 revenue reached $25B, up 10% YoY...
│   Current PE ratio: 45x, below historical average...
│   Profitability margins strong at 13%..."
└─ Status: COMPLETED ✓
```

---

### Phase 3: Reflection
```
INPUT: Task results
↓
[REFLECTION WALKER]
- Evaluate completion rate
- Score confidence of each finding (0-100%)
- Identify gaps
- Determine need for more research
↓
OUTPUT: Quality assessment
```

**Example:**
```
Reflection Assessment:
├─ Completeness: 90%
├─ Average Confidence: 78%
├─ Gaps: Limited analyst predictions for 2026
├─ Additional Research Needed: Maybe
└─ Ready for Final Report: Yes
```

---

### Phase 4: Memory Storage
```
INPUT: All findings
↓
[MEMORY WALKERS]
├─ Store in Vector Memory (FAISS)
│  ├─ Encode text with Sentence Transformers
│  ├─ Create embeddings
│  └─ Build searchable index
│
└─ Store in Database Memory (SQLite)
   ├─ Create session record
   ├─ Insert all entries
   └─ Create indices for queries
↓
OUTPUT: Stored for future retrieval
```

**Example:**
```
Session: 3fa85f64...
├─ 4 entries stored in FAISS vector index
├─ 4 entries stored in SQLite database
├─ Semantically searchable by:
│  ├─ "Tesla financial analysis"
│  ├─ "EV market trends"
│  ├─ "Investment risks"
│  └─ Any similarity query
```

---

### Phase 5: Reporting
```
INPUT: All findings + reflection
↓
[SUMMARIZER WALKER]
- Synthesize all findings
- Generate executive summary
- Provide clear recommendation
- Include confidence scores
↓
OUTPUT: Final professional report
```

**Example:**
```
SYNTHESIS:
"Based on comprehensive research of Tesla's financials,
market position, and competitive landscape, the company
represents a viable but volatile investment opportunity..."

RECOMMENDATION:
"Suitable for investors with moderate-to-high risk tolerance.
Consider 5+ year horizon. Average dollar-cost approach
recommended to reduce timing risk. Tesla confidence: 78%."
```

---

## 🔗 Jac/Jaseci Integration

### Jac Graph Structure

```jac
node UserQuery {
    has query: str;
    has timestamp: float;
}

node Task {
    has task_id: str;
    has status: str;  # pending, in_progress, completed, failed
}

walker PlanTasks {
    has query: str;
    has tasks: list;
    
    :walker:activity {
        # Planning logic
    }
}
```

### Jac Advantages for ARDA

1. **Native Graph Semantics**
   - Nodes represent data/state
   - Edges represent relationships
   - Walkers traverse and transform

2. **Declarative Agent Definition**
   - Clear node types
   - Explicit relationships
   - Easy to understand flow

3. **Scalability**
   - Multi-node traversal
   - Parallel walker execution
   - Distributed graph processing

4. **Type Safety**
   - Strongly typed nodes
   - Field validation
   - Runtime checking

### Example Jac Walker

```jac
walker ExecuteTasks {
    has tasks: list;
    has results: list;
    
    can execute_all;
    can route_task;
    can handle_failure;
    
    :walker:activity {
        self.execute_all();
    }
    
    :can:execute_all {
        for task in self.tasks {
            self.route_task(task);
        }
    }
    
    :can:route_task {
        has task: dict;
        
        if task.get('tool') == 'search' {
            # Execute search
            results = search_tool.search(task['description']);
            analysis = llm.call(results);
        } else {
            # Execute reasoning
            analysis = llm.reason(task['description']);
        }
        
        self.results.append({
            'task_id': task.get('task_id'),
            'analysis': analysis,
            'status': 'completed'
        });
    }
}
```

---

## 🧠 Memory Systems

### Vector Memory (FAISS)

```
Text Input
    ↓
Sentence Transformers Embedding
    ↓
384-dimensional Vector
    ↓
FAISS Index Storage
    ↓
Later: Semantic Search
(Find similar findings by meaning, not just keywords)
```

**Operations:**
```python
# Add entry
vector_memory.add(
    entry_id="session_123_task_1",
    text="Tesla stock analysis showing...",
    metadata={"type": "financial"}
)

# Search semantically
results = vector_memory.search(
    "Tesla investment opportunity",
    top_k=5
)
# Returns 5 most similar findings regardless of exact keywords
```

### Database Memory (SQLite)

```
Session 1 ──┐
Session 2 ──┤
Session 3 ──┼─► SQLite DB (memory.db)
Session 4 ──┤
...       ──┘

Features:
├─ Session tracking
├─ Task associations
├─ Query caching
├─ Historical search
└─ Performance indices
```

**Schema:**
```sql
memory_entries:
  entry_id (PK)
  session_id (FK, indexed)
  task_id
  content
  category
  status
  created_at

sessions:
  session_id (PK)
  query
  created_at
  completed_at
  status
  results_summary

query_cache:
  query_hash (PK)
  query
  results
  created_at
  access_count
```

---

## 🛠️ Tool Integration

### LLM Tool (Groq API)

```
User Prompt
    ↓
[LLMTool.call()]
    ├─ Create messages array
    ├─ Add system context
    ├─ Call Groq API
    ├─ Handle streaming
    └─ Parse response
    ↓
LLM Response
```

**Features:**
- Temperature control (creativity)
- Token limits
- JSON parsing
- Error handling
- Retry logic

### Search Tool (DuckDuckGo)

```
Search Query
    ↓
[SearchTool.search()]
    ├─ Call DuckDuckGo API
    ├─ Get 5 results
    ├─ Extract: title, body, href
    └─ Score relevance
    ↓
Web Results + Analysis
```

**Capabilities:**
- Text search
- News search
- Deep search (multi-source)
- Source comparison

---

## 🔀 Agentic Decision Flow

```
START
│
├─ Query received
│
├─ PLANNING PHASE
│  └─ If query complex? → more tasks
│  └─ Assign tools dynamically
│
├─ EXECUTION PHASE
│  ├─ For each task:
│  │  ├─ Execute with assigned tool
│  │  ├─ On failure? → Retry (max 3)
│  │  └─ On success? → Store result
│  │
│  └─ Continue if tasks remaining
│
├─ REFLECTION PHASE
│  ├─ Calculate completion rate
│  ├─ Score confidence
│  └─ Need more research?
│     ├─ If YES → Consider additional tasks
│     └─ If NO → Proceed to memory
│
├─ MEMORY PHASE
│  ├─ Embed findings
│  ├─ Store in vector DB
│  └─ Store in SQL DB
│
├─ REPORTING PHASE
│  ├─ Synthesize findings
│  ├─ Generate recommendation
│  └─ Score confidence
│
└─ RETURN RESULT
```

---

## 📊 Data Flow

```
CLIENT REQUEST
   │
   ├─ /research endpoint receives
   ├─ Create session_id
   │
   PLANNING
   │  
   ├─ Query → LLMTool → Tasks (3-7 per depth)
   │
   EXECUTION
   │
   ├─ task_1 → SearchTool → web results → LLMTool → analysis
   ├─ task_2 → LLMTool → reasoning → analysis
   ├─ task_3 → SearchTool + LLMTool → analysis
   │
   REFLECTION
   │
   ├─ Results → LLMTool → quality assessment
   │
   MEMORY
   │
   ├─ Analyses → Sentence Transformers → FAISS
   ├─ Analyses → SQLite
   │
   REPORTING
   │
   ├─ All findings → LLMTool → synthesis
   ├─ Synthesis → LLMTool → recommendation
   │
   RESPONSE
   │
   └─ JSON with all phases → CLIENT
```

---

## ⚙️ Configuration & Extensibility

### Adding New Walkers

```jac
walker NewSpecialistAgent {
    has input_data: dict;
    has expertise: str = "domain";
    
    can analyze;
    can generate_insights;
    
    :walker:activity {
        self.analyze();
        self.generate_insights();
    }
    
    :can:analyze {
        # Domain-specific analysis logic
    }
    
    :can:generate_insights {
        # Generate specialized insights
    }
}
```

### Adding New Tools

```python
# Create new tool
class CustomTool:
    def execute(self, task):
        # Tool implementation
        return results
    
# Use in executor
if tool == "custom":
    result = custom_tool.execute(task)
```

### Extending Memory Systems

```python
# Add custom memory backend
class GraphMemory:
    def __init__(self):
        self.graph = {}  # Neo4j or similar
    
    def store_relationships(self, entity1, relationship, entity2):
        # Store entity relationships
        pass
    
    def query_relationships(self, entity):
        # Query related entities
        pass

# Integrate into memory phase
self.graph_memory.store_relationships(
    "Tesla", "competes_with", "Ford"
)
```

---

## 🚀 Performance Characteristics

### Execution Time Breakdown (Standard Depth)

```
Planning Phase:      2-3 seconds
  └─ LLM task breakdown

Execution Phase:     25-30 seconds
  ├─ task_1 (search):    5-7s (search + analysis)
  ├─ task_2 (search):    5-7s (search + analysis)
  └─ task_3 (reason):    5-8s (reasoning)

Reflection Phase:    3-5 seconds
  └─ LLM quality evaluation

Memory Phase:        2-3 seconds
  ├─ Embedding generation
  └─ Database storage

Reporting Phase:     5-10 seconds
  ├─ LLM synthesis
  └─ LLM recommendation

Total:              ~40-50 seconds
```

### Scalability Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Max concurrent queries | 10 | Groq API limit |
| Memory per session | 1-5MB | Depends on findings |
| Total index size | Scales linear | ~50KB per 10 tasks |
| Query latency | 40-120s | Depends on depth |
| Throughput | 0.5-1.5 queries/min | Limited by LLM API |

---

## 🔐 Security Architecture

```
API Request
    ↓
Input Validation (Pydantic)
    ↓
Session Creation
    ↓
Agent Execution
    │
    ├─ LLM: API key protected
    ├─ Search: Public API (no auth needed)
    ├─ Memory: Local storage
    │
    ├─ Error handling
    └─ Logging
    ↓
Response Validation
    ↓
Client Response
```

**Security Measures:**
- Input validation with Pydantic
- API key environment variables
- SQLite file permissions
- FAISS index protection
- Error message sanitization
- Request timeout protection

---

## 📈 Deployment Architecture

### Development
```
Single Machine
├─ Python venv
├─ FastAPI dev server
├─ SQLite local DB
└─ FAISS local index
```

### Production
```
Load Balancer (nginx)
    ↓
├─ API Instance 1 (Gunicorn + Uvicorn)
├─ API Instance 2
└─ API Instance 3
    ↓
├─ PostgreSQL (shared DB)
├─ Redis (caching)
└─ S3 (vector index backups)
```

---

## 🔮 Future Architecture Enhancements

1. **Multi-LLM Support**
   - OpenAI, Claude, local models
   - Dynamic model selection

2. **Distributed Walkers**
   - Multi-machine Jac execution
   - Distributed task execution

3. **Advanced Memory**
   - Graph databases (Neo4j)
   - Knowledge graphs
   - Entity linking

4. **Real-time Streaming**
   - WebSocket connections
   - Streaming responses
   - Live progress updates

5. **Agent Collaboration**
   - Multi-agent systems
   - Sub-agent delegation
   - Consensus mechanisms

---

**Architecture Version:** 1.0  
**Last Updated:** May 2024  
**Status:** Production Ready
