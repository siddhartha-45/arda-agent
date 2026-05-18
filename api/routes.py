"""
FastAPI routes for ARDA agent system
"""

import json
import uuid
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from tools.llm_tool import LLMTool
from tools.search_tool import SearchTool
from tools.vector_memory import VectorMemory
from tools.db_memory import DatabaseMemory

# Initialize tools
llm = LLMTool()
search = SearchTool()
vector_mem = VectorMemory()
db_mem = DatabaseMemory()

router = APIRouter()


class ResearchQuery(BaseModel):
    """Input model for research endpoint"""
    query: str
    depth: str = "standard"  # standard, deep, expert


class ResearchResponse(BaseModel):
    """Output model for research endpoint"""
    query: str
    session_id: str
    tasks: list
    analyses: list
    reflection: dict
    final_report: dict
    execution_time: float


@router.post("/research", response_model=ResearchResponse)
async def research(input_data: ResearchQuery) -> ResearchResponse:
    """
    Execute autonomous research on a query

    Args:
        input_data: ResearchQuery with query string

    Returns:
        ResearchResponse with all findings and analysis
    """
    session_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        # Create session in database
        db_mem.create_session(session_id, input_data.query)

        # Phase 1: Planning
        tasks = _planning_phase(input_data.query, input_data.depth)

        # Phase 2: Execution
        results = _execution_phase(tasks, session_id)

        # Phase 3: Reflection
        reflection = _reflection_phase(input_data.query, tasks, results)

        # Phase 4: Memory Storage
        _memory_phase(session_id, results)

        # Phase 5: Report Generation
        final_report = _reporting_phase(input_data.query, tasks, results, reflection)

        execution_time = time.time() - start_time

        # Close session
        db_mem.close_session(session_id, json.dumps(final_report))

        return ResearchResponse(
            query=input_data.query,
            session_id=session_id,
            tasks=tasks,
            analyses=[r for r in results if r.get('status') == 'completed'],
            reflection=reflection,
            final_report=final_report,
            execution_time=execution_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


def _planning_phase(query: str, depth: str) -> list:
    """Phase 1: Break down query into tasks"""
    prompt = f"""
Analyze this research query and break it down into executable tasks.

Query: {query}
Depth: {depth}

Generate 3-5 tasks. For each, provide:
1. task_id (task_1, task_2, etc.)
2. description (what to research)
3. tool (search or reasoning)
4. priority (1-5)
5. criteria (success criteria)

Return valid JSON array only.
"""

    response = llm.call(prompt)

    try:
        if "```json" in response:
            tasks = json.loads(response.split("```json")[1].split("```")[0])
        elif "```" in response:
            tasks = json.loads(response.split("```")[1].split("```")[0])
        else:
            tasks = json.loads(response)

        for task in tasks:
            task['status'] = 'pending'

        return tasks
    except json.JSONDecodeError:
        # Fallback: create default task
        return [{
            'task_id': 'task_1',
            'description': f'Research: {query}',
            'tool': 'search',
            'priority': 5,
            'criteria': 'Comprehensive information gathering',
            'status': 'pending'
        }]


def _execution_phase(tasks: list, session_id: str) -> list:
    """Phase 2: Execute planned tasks"""
    results = []

    for task in tasks:
        task_id = task.get('task_id')
        description = task.get('description')
        tool = task.get('tool', 'reasoning')

        try:
            if tool == 'search':
                # Perform web search
                search_results = search.search(description, num_results=5)

                # Analyze search results
                analysis_prompt = f"""
Analyze these search results and provide insights.

Query: {description}

Results:
{json.dumps(search_results, indent=2)}

Provide:
1. Key findings
2. Relevant statistics
3. Main conclusions
4. Confidence (0-100%)

Be concise and analytical.
"""
                analysis = llm.call(analysis_prompt)

                result = {
                    'task_id': task_id,
                    'type': 'search',
                    'status': 'completed',
                    'description': description,
                    'search_count': len(search_results),
                    'analysis': analysis,
                    'timestamp': time.time()
                }
                results.append(result)

            else:  # reasoning
                # Perform reasoning task
                reasoning_prompt = f"""
Perform detailed analysis on this task.

Task: {description}

Provide:
1. Analysis
2. Key points
3. Considerations
4. Conclusions
5. Confidence (0-100%)
"""
                analysis = llm.call(reasoning_prompt)

                result = {
                    'task_id': task_id,
                    'type': 'reasoning',
                    'status': 'completed',
                    'description': description,
                    'analysis': analysis,
                    'timestamp': time.time()
                }
                results.append(result)

        except Exception as e:
            result = {
                'task_id': task_id,
                'type': tool,
                'status': 'failed',
                'error': str(e),
                'timestamp': time.time()
            }
            results.append(result)

    return results


def _reflection_phase(query: str, tasks: list, results: list) -> dict:
    """Phase 3: Reflect on results quality"""
    completed = len([r for r in results if r.get('status') == 'completed'])
    total = len(tasks)

    reflection_prompt = f"""
Evaluate the research quality.

Query: {query}
Tasks: {total}
Completed: {completed}

Results: {json.dumps(results[:2], indent=2, default=str)}

Assess:
1. Research completeness (0-100%)
2. Quality assessment
3. Gaps identified
4. Need more research? (yes/no)
5. Overall assessment

Provide valid JSON response.
"""

    response = llm.call(reflection_prompt)

    try:
        if "```json" in response:
            reflection = json.loads(response.split("```json")[1].split("```")[0])
        elif "```" in response:
            reflection = json.loads(response.split("```")[1].split("```")[0])
        else:
            reflection = json.loads(response)
    except json.JSONDecodeError:
        reflection = {
            'completeness': (completed / total) * 100 if total > 0 else 0,
            'quality': 'adequate',
            'gaps': 'May require deeper analysis',
            'needs_more_research': completed < total,
            'assessment': 'Research executed with mixed success'
        }

    return reflection


def _memory_phase(session_id: str, results: list) -> None:
    """Phase 4: Store findings in memory"""
    for result in results:
        # Store in database
        mem_entry = {
            'entry_id': f"{session_id}_{result.get('task_id')}",
            'session_id': session_id,
            'task_id': result.get('task_id'),
            'content': result.get('analysis', result.get('description', '')),
            'category': result.get('type', 'general'),
            'status': 'active',
            'type': result.get('type', 'result')
        }
        db_mem.insert(mem_entry)

        # Store in vector memory if has analysis
        if result.get('analysis'):
            vector_mem.add(
                entry_id=f"{session_id}_{result.get('task_id')}",
                text=result.get('analysis', ''),
                metadata={
                    'task_id': result.get('task_id'),
                    'session_id': session_id,
                    'type': result.get('type')
                }
            )


def _reporting_phase(
    query: str,
    tasks: list,
    results: list,
    reflection: dict
) -> dict:
    """Phase 5: Generate final report"""
    report_prompt = f"""
Generate a comprehensive research report.

Query: {query}

Completed Tasks: {len([r for r in results if r.get('status') == 'completed'])}/{len(tasks)}

Analyses Summary:
{json.dumps([r.get('analysis', '')[:200] for r in results if r.get('status') == 'completed'], indent=2)}

Reflection: {json.dumps(reflection, indent=2)}

Generate:
1. Executive summary
2. Key findings
3. Supporting evidence
4. Recommendations
5. Confidence and caveats

Provide comprehensive, professional report.
"""

    final_summary = llm.call(report_prompt)

    # Generate recommendation
    recommendation_prompt = f"""
Based on this research, provide a clear recommendation/conclusion.

Query: {query}
Summary: {final_summary}

Provide:
1. Clear recommendation
2. Supporting rationale
3. Risks/considerations
4. Confidence level (0-100%)

Be concise.
"""

    recommendation = llm.call(recommendation_prompt)

    return {
        'executive_summary': final_summary,
        'final_recommendation': recommendation,
        'tasks_completed': len([r for r in results if r.get('status') == 'completed']),
        'research_quality': reflection.get('quality', 'good'),
        'generated_at': time.time()
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "ARDA Research Agent"}


@router.get("/memory/stats")
async def memory_stats() -> Dict[str, Any]:
    """Get memory statistics"""
    return {
        'database': db_mem.get_stats(),
        'vector_memory': vector_mem.get_stats()
    }


@router.post("/memory/clear")
async def clear_memory() -> Dict[str, str]:
    """Clear all memory (use with caution)"""
    vector_mem.clear()
    return {"status": "success", "message": "Memory cleared"}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Retrieve research session details"""
    # This would query the database for session details
    # Simplified for now
    return {
        "session_id": session_id,
        "status": "completed",
        "message": "Session details would be retrieved from database"
    }
