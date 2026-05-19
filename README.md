# ARDA-agent

ARDA-agent is a lightweight AI research assistant that searches the web, collects relevant sources, and turns them into a structured research brief. It is designed for quick exploratory research on current topics such as market trends, technology updates, company news, and general decision-making questions.

The deployed version focuses on fast web research and clean summaries. The broader repository also includes experimental agentic modules for planning, execution, reflection, and memory.

## Tagline

AI-powered research that searches, analyzes, and summarizes insights in seconds.

## Project Status

The live Vercel app is a lightweight research assistant. It uses web search plus Groq analysis and is optimized for fast serverless deployment.

The repository also contains experimental local agent modules for planning, execution, reflection, and memory. Those local modules show the broader ARDA-agent direction, but the deployed website intentionally uses a smaller production path.

## Inspiration

Research often starts with a simple question but quickly turns into a messy workflow: opening many tabs, comparing sources, reading long pages, and manually writing notes. ARDA-agent was inspired by the idea of making that first research pass faster and more organized.

Instead of giving only a chatbot-style answer, ARDA-agent uses live web search results and then creates a structured analysis from those sources. This makes it useful for topics that change often, including stocks, market movers, AI developments, product comparisons, and recent news.

## What It Does

ARDA-agent lets a user enter a research query and returns:

- Relevant web search results
- A concise AI-generated analysis
- Structured sections such as summary, caveats, and next steps
- Source links for further reading

For example, a query like "latest stock rising companies in previous week" returns market-related search results and a structured brief based on those sources.

## Built With

### Deployed Web App

| Category | Technology | Purpose |
| --- | --- | --- |
| Backend Language | Python | Runs the research API |
| API Framework | FastAPI | Handles `/research`, health, and info endpoints |
| Validation | Pydantic | Validates request and response data |
| Serverless Adapter | Mangum | Adapts FastAPI for Vercel Python functions |
| Frontend | HTML, CSS, JavaScript | Provides the browser research interface |
| Hosting | Vercel | Serves the static UI and serverless API |
| Search | ddgs | Retrieves web search results |
| LLM API | Groq API | Generates structured analysis from search results |
| Model | Llama 3.1 8B Instant | Fast LLM used through Groq |
| Version Control | Git and GitHub | Tracks code and triggers deployment |

### Local / Experimental Agent Components

| Category | Technology | Purpose |
| --- | --- | --- |
| Agent Framework Experiments | Jac/Jaseci | Explores graph-native planning and execution workflows |
| Local Database | SQLite | Prototype session and memory storage |
| Vector Search | FAISS | Prototype semantic memory retrieval |
| Embeddings | Sentence Transformers | Prototype vector-memory embeddings |

## How It Works

1. The user submits a research query from the web interface.
2. The frontend sends the query to the FastAPI endpoint at `/research`.
3. The backend searches the web using `ddgs`.
4. Search results are normalized into title, link, and snippet fields.
5. If `GROQ_API_KEY` is configured, Groq generates a structured research brief.
6. If Groq is unavailable, the app still returns search results instead of failing completely.
7. The frontend displays the analysis and source links in a readable format.

The deployed API is intentionally lightweight so it can run well on Vercel. Heavy local components such as FAISS and SQLite are kept out of the serverless path.

## Challenges We Ran Into

One major challenge was deployment. The original project explored a fuller agent architecture with memory and heavier dependencies, but serverless deployment works best with a smaller dependency set. The Vercel API was simplified to focus on search and LLM analysis.

Another challenge was error handling. If the Groq API key is missing or invalid, the app should not completely fail. The current version can still return search results and explains when AI analysis is unavailable.

We also had to improve response quality. Early analysis could be too vague or include placeholder text. The prompt now asks for a fixed structure and tells the model not to invent company names, stock tickers, prices, or returns that are not present in the search results.

## Accomplishments

- Built a working research assistant with live web search
- Deployed a Python FastAPI app on Vercel
- Added graceful fallback behavior for API failures
- Improved the UI so analysis is shown as sections, bullets, and tables
- Kept the deployed version lightweight while preserving room for deeper local agent experiments

## What We Learned

Building useful AI applications is not just about calling an LLM. The quality of the result depends on search, prompts, validation, error handling, frontend formatting, and deployment constraints.

We also learned that structured prompts produce more reliable output. A clear format helps the model return information that users can scan quickly and trust more easily.

## What's Next

Future improvements could include:

- Better source ranking and deduplication
- Financial data APIs for stock-specific queries
- Inline citations inside the generated analysis
- Saved research history
- Export to Markdown or PDF
- A richer dashboard for comparing results
- Deeper agent workflows using planning, reflection, and memory

## Local Setup

```bash
cd arda-agent
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install uvicorn
```

Create a `.env` file or set the environment variable:

```bash
GROQ_API_KEY=your_groq_api_key
```

Run the lightweight Vercel-style API locally:

```bash
uvicorn api.index:app --reload
```

Then open `public/index.html` in a browser or call `http://127.0.0.1:8000/research` directly.

The fuller local agent path in `app.py` and `api/routes.py` uses the experimental memory modules and may require additional dependencies such as FAISS, Sentence Transformers, and Jac/Jaseci.

## Deployment Notes

The Vercel deployment uses:

- `api/index.py` for the serverless API
- `public/index.html` for the frontend
- `requirements.txt` for Python dependencies
- `vercel.json` for routing

Set `GROQ_API_KEY` in Vercel project environment variables to enable AI analysis.
