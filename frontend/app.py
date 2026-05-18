"""
Optional Streamlit Frontend for ARDA Agent
Provides interactive UI for autonomous research
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ARDA - Autonomous Research Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuration")
api_endpoint = st.sidebar.text_input(
    "API Endpoint",
    value="http://localhost:8000",
    help="FastAPI server endpoint"
)

research_depth = st.sidebar.selectbox(
    "Research Depth",
    ["standard", "deep", "expert"],
    help="Deeper research = more tasks and longer execution"
)

depth_descriptions = {
    "standard": "3 tasks - Quick research (30-45s)",
    "deep": "5 tasks - Comprehensive research (50-75s)",
    "expert": "7 tasks - Expert-level analysis (80-120s)"
}

st.sidebar.info(f"📊 {depth_descriptions[research_depth]}")

# Main content
st.title("🤖 ARDA - Autonomous Research & Decision Agent")
st.markdown("""
**Production-ready agentic AI** for autonomous research and analysis.
Enter a complex query and ARDA will autonomously plan, execute, reflect, and synthesize findings.
""")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Research", "📊 Memory Stats", "📚 About", "⚡ API"])

# TAB 1: Research
with tab1:
    st.header("Research Query")

    col1, col2 = st.columns([4, 1])

    with col1:
        query = st.text_area(
            "Enter your research query:",
            placeholder="e.g., Should I invest in Tesla stock in 2026? What are the pros and cons?",
            height=100,
            label_visibility="collapsed"
        )

    with col2:
        st.markdown("### ")  # Spacing
        execute_btn = st.button("🚀 Execute Research", use_container_width=True)

    if execute_btn and query:
        st.divider()

        # Show progress
        with st.spinner("🔄 Executing research phases..."):
            progress_bar = st.progress(0)

            try:
                # Make API request
                response = requests.post(
                    f"{api_endpoint}/research",
                    json={"query": query, "depth": research_depth},
                    timeout=300
                )

                if response.status_code == 200:
                    result = response.json()
                    progress_bar.progress(100)

                    st.success("✅ Research Complete!")

                    # Show metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Execution Time",
                            f"{result['execution_time']:.1f}s"
                        )

                    with col2:
                        completed = result['phases']['execution']['tasks_completed']
                        total = result['phases']['execution']['tasks_total']
                        st.metric("Tasks", f"{completed}/{total}")

                    with col3:
                        st.metric(
                            "Success Rate",
                            f"{result['phases']['execution']['success_rate']:.0f}%"
                        )

                    with col4:
                        st.metric("Session", result['session_id'][:8] + "...")

                    st.divider()

                    # Tabs for results
                    res_col1, res_col2, res_col3, res_col4 = st.columns(4)

                    with res_col1:
                        if st.button("📋 Tasks", use_container_width=True):
                            st.session_state.show_tab = "tasks"

                    with res_col2:
                        if st.button("📊 Analyses", use_container_width=True):
                            st.session_state.show_tab = "analyses"

                    with res_col3:
                        if st.button("🔍 Reflection", use_container_width=True):
                            st.session_state.show_tab = "reflection"

                    with res_col4:
                        if st.button("📄 Report", use_container_width=True):
                            st.session_state.show_tab = "report"

                    st.divider()

                    # Show selected content
                    show_tab = st.session_state.get("show_tab", "report")

                    if show_tab == "tasks":
                        st.subheader("📋 Planned Tasks")
                        for i, task in enumerate(result['tasks'], 1):
                            with st.expander(f"Task {i}: {task.get('description', '')[:60]}"):
                                st.json(task)

                    elif show_tab == "analyses":
                        st.subheader("📊 Task Analyses")
                        for i, analysis in enumerate(result['analyses'], 1):
                            with st.expander(f"Analysis {i}: {analysis.get('task_id')}"):
                                st.write(analysis.get('analysis', 'No analysis'))
                                st.caption(f"Type: {analysis.get('type')}")

                    elif show_tab == "reflection":
                        st.subheader("🔍 Quality Reflection")
                        reflection = result['reflection']
                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric(
                                "Research Completeness",
                                reflection.get('completeness', 'N/A')
                            )

                        with col2:
                            tasks_info = reflection.get('tasks_status', {})
                            st.write(f"""
                            **Tasks Status:**
                            - Total: {tasks_info.get('total', 0)}
                            - Completed: {tasks_info.get('completed', 0)}
                            - Failed: {tasks_info.get('failed', 0)}
                            """)

                        st.write(reflection.get('assessment', 'No assessment'))

                    elif show_tab == "report":
                        st.subheader("📄 Final Report")
                        final = result['final_report']

                        st.subheader("📝 Synthesis")
                        st.write(final.get('synthesis', 'No synthesis'))

                        st.subheader("✅ Recommendation")
                        st.info(final.get('recommendation', 'No recommendation'))

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Research Quality",
                                final.get('research_quality', 'N/A')
                            )

                        with col2:
                            st.metric(
                                "Generated",
                                datetime.fromisoformat(final.get('generated_at', 0)).strftime("%H:%M:%S")
                            )

                    # Download results
                    st.divider()
                    col1, col2 = st.columns(2)

                    with col1:
                        st.download_button(
                            "📥 Download JSON",
                            json.dumps(result, indent=2),
                            "research_result.json",
                            use_container_width=True
                        )

                    with col2:
                        # Export as text
                        text_report = f"""
RESEARCH REPORT
===============

Query: {result['query']}
Date: {datetime.now().isoformat()}
Session: {result['session_id']}
Execution Time: {result['execution_time']}s

SUMMARY
-------
{result['final_report'].get('synthesis', '')}

RECOMMENDATION
--------------
{result['final_report'].get('recommendation', '')}

RESEARCH QUALITY: {result['final_report'].get('research_quality', '')}
"""
                        st.download_button(
                            "📄 Download Text",
                            text_report,
                            "research_report.txt",
                            use_container_width=True
                        )

                else:
                    st.error(f"API Error: {response.status_code}")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server")
                st.info(f"Make sure FastAPI server is running at {api_endpoint}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out")
                st.info("Try a shorter research depth")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# TAB 2: Memory Stats
with tab2:
    st.header("📊 Memory Statistics")

    try:
        response = requests.get(f"{api_endpoint}/memory/stats")

        if response.status_code == 200:
            stats = response.json()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🗄️ Database Memory")
                db_stats = stats.get('database', {})
                st.metric("Total Entries", db_stats.get('total_entries', 0))
                st.metric("Completed Sessions", db_stats.get('completed_sessions', 0))
                st.metric("Cached Queries", db_stats.get('cached_queries', 0))

            with col2:
                st.subheader("🔍 Vector Memory")
                vec_stats = stats.get('vector_memory', {})
                st.metric("Stored Entries", vec_stats.get('total_entries', 0))
                st.metric("Index Size", vec_stats.get('index_size', 0))

            st.divider()

            if st.button("🧹 Clear All Memory", use_container_width=True):
                clear_response = requests.post(f"{api_endpoint}/memory/clear")
                if clear_response.status_code == 200:
                    st.success("✅ Memory cleared")
                else:
                    st.error("❌ Failed to clear memory")

        else:
            st.error("Cannot fetch memory stats")

    except Exception as e:
        st.error(f"Error: {str(e)}")


# TAB 3: About
with tab3:
    st.header("ℹ️ About ARDA")

    st.markdown("""
    ### Autonomous Research & Decision Agent
    
    ARDA is a **production-ready agentic AI system** that demonstrates genuine autonomous capabilities:
    
    ✅ **Autonomous Planning** - Breaks down complex queries  
    ✅ **Tool Usage** - Dynamically selects and uses web search  
    ✅ **Multi-Step Reasoning** - Chains analysis across tasks  
    ✅ **Semantic Memory** - FAISS-based finding storage  
    ✅ **Reflection** - Evaluates work quality and identifies gaps  
    ✅ **Graph-Native** - Built on Jac/Jaseci architecture  
    
    ### Technology Stack
    - **Agent Framework**: Jac/Jaseci
    - **LLM**: Groq API + Llama 3.1 8b
    - **Search**: DuckDuckGo
    - **Vector Memory**: FAISS
    - **Persistent Memory**: SQLite
    - **API**: FastAPI
    
    ### Example Queries
    1. "Should I invest in Tesla stock in 2026?"
    2. "What are latest quantum computing developments?"
    3. "How is climate change affecting agriculture?"
    4. "Compare EV vs hydrogen fuel cell vehicles"
    
    ### How It Works
    1. **Planning**: Breaks query into tasks
    2. **Execution**: Performs search and reasoning
    3. **Reflection**: Evaluates quality
    4. **Memory**: Stores findings
    5. **Reporting**: Generates final report
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.link_button("📚 GitHub", "https://github.com/Jaseci-Labs/jac")

    with col2:
        st.link_button("📖 Docs", "https://docs.jaseci.org")

    with col3:
        st.link_button("🔑 Groq API", "https://console.groq.com")


# TAB 4: API
with tab4:
    st.header("⚡ FastAPI Endpoints")

    st.markdown("""
    ### Available Endpoints
    
    **POST /research**
    - Execute autonomous research
    - Request body: `{"query": "...", "depth": "standard|deep|expert"}`
    
    **GET /health**
    - Health check
    
    **GET /memory/stats**
    - Get memory statistics
    
    **POST /memory/clear**
    - Clear all memory
    
    **GET /sessions/{session_id}**
    - Get session details
    """)

    st.divider()

    st.code("""
# Example API Call
curl -X POST http://localhost:8000/research \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "Should I invest in Tesla stock?",
    "depth": "deep"
  }'
    """, language="bash")

    st.link_button(
        "📖 Interactive API Docs (Swagger)",
        f"{api_endpoint}/docs",
        use_container_width=True
    )


# Footer
st.divider()
st.markdown("""
---
**ARDA v1.0** | Built with ❤️ using Jac/Jaseci, Python, and Groq  
[GitHub](https://github.com) | [Docs](https://docs.jaseci.org)
""", help="Production-ready autonomous research agent")
