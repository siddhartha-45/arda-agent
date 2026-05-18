"""
INSTALL.md - Complete Installation Guide for ARDA Agent
"""

# ARDA - Complete Installation Guide

## 📋 Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed
- **pip** package manager
- **Git** (optional, for cloning)
- **~500MB** free disk space
- **Internet connection** (for downloads and API calls)
- **Groq API key** (free at https://console.groq.com)

## 🔑 Step 1: Get Groq API Key

ARDA uses the **Groq API** with Llama 3.1 8b model - completely FREE!

1. Visit https://console.groq.com
2. Sign up with email
3. Create new API key
4. Keep it safe - you'll need it in .env

⏱️ **Time: 5 minutes**

## 📁 Step 2: Project Setup

### Windows

```bash
# Navigate to project
cd e:\jac\arda-agent

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate
```

### macOS/Linux

```bash
cd ~/jac/arda-agent
python3 -m venv venv
source venv/bin/activate
```

## 📦 Step 3: Install Jac/Jaseci

```bash
# Install Jaseci framework
pip install jaseci

# Verify installation
jaseci --version

# Install Jac VSCode extension (optional but recommended)
# In VSCode: Extensions → Search "Jac" → Install Jac from Striveworks
```

## 🔧 Step 4: Install Project Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This installs:
- **groq** - LLM API client
- **duckduckgo-search** - Web search
- **fastapi** - REST API framework
- **sentence-transformers** - Embeddings for semantic memory
- **faiss-cpu** - Vector search
- **uvicorn** - ASGI server
- Plus utilities

⏱️ **Time: 3-5 minutes** (depending on internet)

## 🔐 Step 5: Configure Environment

```bash
# Copy template
copy .env.example .env          # Windows
# OR
cp .env.example .env           # macOS/Linux

# Edit .env with your favorite editor
# Windows: notepad .env
# macOS/Linux: nano .env
```

Add your Groq API key:

```env
GROQ_API_KEY=gsk_your_actual_key_here_1234567890abcdef
PORT=8000
DEBUG=false
```

✅ **Save the file!**

## ✅ Step 6: Verify Installation

```bash
# Test Python imports
python -c "from tools.llm_tool import LLMTool; print('✅ LLMTool OK')"
python -c "from tools.search_tool import SearchTool; print('✅ SearchTool OK')"
python -c "from tools.vector_memory import VectorMemory; print('✅ VectorMemory OK')"
python -c "from tools.db_memory import DatabaseMemory; print('✅ DatabaseMemory OK')"

# Test Jac
jaseci run jac_app/graph.jac --help
```

## 🚀 Step 7: Run ARDA

### Option A: Quick Start Demo (Recommended First)

```bash
python quickstart.py
```

- Runs a complete 5-minute demo
- Shows all agent phases
- Tests all components
- Output includes next steps

### Option B: Interactive CLI Mode

```bash
python main.py
```

- Enter custom queries
- See full research process
- Get detailed analysis
- Can run multiple queries

### Option C: FastAPI Server

```bash
python app.py
```

- Starts REST API at http://localhost:8000
- Access Swagger UI: http://localhost:8000/docs
- Use for programmatic access
- Keep running for API calls

### Option D: Streamlit Web UI (Most User-Friendly)

```bash
# Install Streamlit (if not in requirements)
pip install streamlit

# Run UI
streamlit run frontend/app.py
```

- Beautiful interactive interface
- Upload research queries
- Visualize results
- Download reports

## 📊 Testing the Installation

After starting any mode, test with these queries:

### Test 1: Simple Research
```
Query: "What is artificial intelligence?"
Time: ~30 seconds
Expected: Basic information with definitions
```

### Test 2: Investment Analysis
```
Query: "Should I invest in Tesla stock?"
Time: ~45 seconds
Expected: Financial analysis with pros/cons
```

### Test 3: Technical Comparison
```
Query: "Compare Python vs Go for backend development"
Time: ~50 seconds
Expected: Technical comparison of languages
```

## 🐛 Troubleshooting Installation

### Problem: "GROQ_API_KEY not found"

**Solution:**
```bash
# Check .env file exists
dir .env              # Windows: should show .env

# Check key is set
type .env             # Windows
cat .env              # macOS/Linux

# Should contain: GROQ_API_KEY=gsk_xxxxx
```

### Problem: "No module named 'groq'"

**Solution:**
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or specific package
pip install groq==0.4.1
```

### Problem: "Port 8000 already in use"

**Solution:**
```bash
# Change port in .env
PORT=8001

# Or kill process using port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Problem: "SSL Certificate Error"

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or disable SSL (not recommended for production)
# Add to .env: SSL_VERIFY=false
```

### Problem: FAISS installation fails

**Solution:**
```bash
# Use CPU version specifically
pip install faiss-cpu

# If that fails, try older version
pip install faiss-cpu==1.7.3
```

## 📈 Performance Verification

After installation, verify performance:

```bash
# Check execution time
time python quickstart.py    # macOS/Linux
# or
python -m timeit "import main"  # Windows
```

Expected:
- **Standard depth**: 30-45 seconds
- **Deep research**: 50-75 seconds
- **Expert analysis**: 80-120 seconds

## 📚 Directory Structure After Installation

```
arda-agent/
├── venv/                 # Virtual environment (created)
├── database/
│   └── memory.db        # SQLite (created on first run)
├── .env                 # Config (created from template)
├── vector_memory.pkl    # FAISS index (created on first run)
├── main.py
├── app.py
├── quickstart.py
├── requirements.txt
├── README.md
├── jac_app/
│   ├── graph.jac
│   ├── planner.jac
│   ├── executor.jac
│   ├── reflection.jac
│   ├── memory.jac
│   └── summarizer.jac
├── tools/
│   ├── llm_tool.py
│   ├── search_tool.py
│   ├── vector_memory.py
│   └── db_memory.py
├── api/
│   └── routes.py
└── frontend/
    └── app.py
```

## 🎯 Next Steps After Installation

1. **Try the Demo:**
   ```bash
   python quickstart.py
   ```

2. **Read Documentation:**
   - Open README.md
   - Review Jac examples in jac_app/

3. **Experiment with Queries:**
   ```bash
   python main.py
   ```
   - Try different query types
   - Test different research depths
   - Observe agent behavior

4. **Explore the Code:**
   - Read tools/* modules
   - Review agent logic in main.py
   - Understand Jac walkers

5. **Deploy as Service:**
   - Run app.py for REST API
   - Integrate with frontend
   - Build custom applications

## 🔄 Updating Installation

To update to latest version:

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update Jaseci
pip install --upgrade jaseci
```

## 📞 Getting Help

### If installation fails:

1. **Check prerequisites:**
   - Python 3.10+ installed
   - pip working
   - Internet connection active

2. **Review errors:**
   - Read error messages carefully
   - Search error in README.md
   - Check Groq status page

3. **Common issues:**
   - .env file not found → copy from .env.example
   - API key invalid → check console.groq.com
   - Port in use → change PORT in .env
   - Network error → check internet connection

4. **Get support:**
   - Review README.md Troubleshooting
   - Check GitHub issues
   - Review Jac documentation

## ✨ You're Ready!

Congratulations! 🎉

Your ARDA installation is complete. You now have:

✅ Autonomous research agent  
✅ REST API interface  
✅ Web UI frontend  
✅ Semantic memory system  
✅ Complete documentation  

Start with: `python quickstart.py`

Happy researching! 🚀
