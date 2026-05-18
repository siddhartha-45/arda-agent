"""
ARDA Agent - Autonomous Research & Decision Agent
Main application entry point
"""

import os
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

from tools.llm_tool import LLMTool
from tools.search_tool import SearchTool
from tools.vector_memory import VectorMemory
from tools.db_memory import DatabaseMemory

# Load environment variables
load_dotenv()


class ARDAAgent:
    """
    Autonomous Research & Decision Agent
    Orchestrates multi-agent workflow for research tasks
    """

    def __init__(self):
        """Initialize ARDA agent system"""
        self.llm = LLMTool()
        self.search = SearchTool()
        self.vector_memory = VectorMemory()
        self.db_memory = DatabaseMemory()
        self.session_id = None
        self.execution_history = []

    def research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Execute autonomous research on a query

        Args:
            query: Research query
            depth: Research depth (standard, deep, expert)

        Returns:
            Comprehensive research report
        """
        self.session_id = str(uuid.uuid4())
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"ARDA RESEARCH AGENT")
        print(f"{'='*60}")
        print(f"Query: {query}")
        print(f"Session: {self.session_id}")
        print(f"Depth: {depth}")
        print(f"{'='*60}\n")

        try:
            # Create session
            self.db_memory.create_session(self.session_id, query)

            # Phase 1: Planning
            print("[PHASE 1/5] PLANNING - Breaking down query into tasks...")
            tasks = self._planning_phase(query, depth)
            self._print_phase_results("Tasks", tasks)

            # Phase 2: Execution
            print("\n[PHASE 2/5] EXECUTION - Executing planned tasks...")
            results = self._execution_phase(tasks)
            self._print_phase_results("Results", results)

            # Phase 3: Reflection
            print("\n[PHASE 3/5] REFLECTION - Evaluating research quality...")
            reflection = self._reflection_phase(query, tasks, results)
            self._print_phase_results("Reflection", reflection)

            # Phase 4: Memory
            print("\n[PHASE 4/5] MEMORY - Storing findings in semantic memory...")
            self._memory_phase(results)
            print("✓ Findings stored in vector and database memory")

            # Phase 5: Reporting
            print("\n[PHASE 5/5] REPORTING - Generating final report...")
            final_report = self._reporting_phase(query, tasks, results, reflection)
            self._print_phase_results("Final Report", final_report)

            # Calculate metrics
            execution_time = time.time() - start_time
            completed_tasks = len([r for r in results if r.get('status') == 'completed'])

            # Close session
            self.db_memory.close_session(self.session_id, json.dumps(final_report))

            # Return comprehensive result
            research_result = {
                'query': query,
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'execution_time': round(execution_time, 2),
                'depth': depth,
                'phases': {
                    'planning': {'tasks_generated': len(tasks)},
                    'execution': {
                        'tasks_completed': completed_tasks,
                        'tasks_total': len(tasks),
                        'success_rate': (completed_tasks / len(tasks) * 100) if tasks else 0
                    },
                    'reflection': reflection,
                    'memory': {'entries_stored': len(results)},
                    'reporting': final_report
                },
                'tasks': tasks,
                'analyses': [r for r in results if r.get('status') == 'completed'],
                'reflection': reflection,
                'final_report': final_report
            }

            self._print_summary(research_result)
            return research_result

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            raise

    def _planning_phase(self, query: str, depth: str) -> list:
        """Break down query into executable tasks"""
        prompt = f"""
You are an expert research planner. Analyze this query and break it down into concrete, executable tasks.

Query: "{query}"
Research Depth: {depth}

Generate {3 if depth == 'standard' else 5 if depth == 'deep' else 7} tasks.

For each task, provide:
- task_id (e.g., "task_1")
- description (what to research)
- tool ("search" for web research, "reasoning" for analysis)
- priority (1-5, where 5 is highest)
- success_criteria (how to know task succeeded)

Return ONLY valid JSON array, no markdown formatting:
[
  {{"task_id": "...", "description": "...", "tool": "...", "priority": 5, "success_criteria": "..."}},
  ...
]
"""

        response = self.llm.call(prompt)

        try:
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()
            if response.endswith("```"):
                response = response[:-3].strip()

            tasks = json.loads(response)

            for task in tasks:
                task['status'] = 'pending'

            return tasks

        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse tasks, using default: {e}")
            return [{
                'task_id': 'task_1',
                'description': f'Comprehensive research on: {query}',
                'tool': 'search',
                'priority': 5,
                'success_criteria': 'Gather relevant information',
                'status': 'pending'
            }]

    def _execution_phase(self, tasks: list) -> list:
        """Execute planned tasks"""
        results = []
        retry_count = {}

        for task in tasks:
            task_id = task.get('task_id')
            description = task.get('description')
            tool = task.get('tool', 'reasoning')

            print(f"  → {task_id}: {description[:60]}...")

            try:
                if tool == 'search':
                    result = self._execute_search_task(task)
                else:
                    result = self._execute_reasoning_task(task)

                results.append(result)

            except Exception as e:
                # Retry logic
                if task_id not in retry_count:
                    retry_count[task_id] = 0

                if retry_count[task_id] < 2:
                    retry_count[task_id] += 1
                    print(f"    Retrying {task_id}...")
                    try:
                        result = self._execute_reasoning_task(task) if tool == 'search' else self._execute_search_task(task)
                        results.append(result)
                    except Exception as retry_e:
                        results.append({
                            'task_id': task_id,
                            'type': tool,
                            'status': 'failed',
                            'error': str(retry_e),
                            'timestamp': time.time()
                        })
                else:
                    results.append({
                        'task_id': task_id,
                        'type': tool,
                        'status': 'failed',
                        'error': f'Task failed after retries: {str(e)}',
                        'timestamp': time.time()
                    })

        return results

    def _execute_search_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search task"""
        task_id = task.get('task_id')
        description = task.get('description')

        # Search
        search_results = self.search.search(description, num_results=5)

        # Analyze results
        analysis_prompt = f"""
Analyze these web search results and provide key insights.

Query: "{description}"

Results:
{json.dumps(search_results, indent=2)}

Provide analysis with:
1. Key findings (2-3 sentences)
2. Important statistics or facts
3. Expert perspectives found
4. Gaps or limitations
5. Confidence level (0-100%)

Be concise and factual.
"""

        analysis = self.llm.call(analysis_prompt)

        return {
            'task_id': task_id,
            'type': 'search',
            'status': 'completed',
            'description': description,
            'search_results_count': len(search_results),
            'analysis': analysis,
            'timestamp': time.time()
        }

    def _execute_reasoning_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reasoning/analysis task"""
        task_id = task.get('task_id')
        description = task.get('description')

        reasoning_prompt = f"""
Perform detailed analysis on this research task.

Task: "{description}"

Provide:
1. Analysis and findings
2. Key considerations
3. Different perspectives
4. Main conclusions
5. Confidence assessment (0-100%)

Be thorough and analytical.
"""

        analysis = self.llm.call(reasoning_prompt)

        return {
            'task_id': task_id,
            'type': 'reasoning',
            'status': 'completed',
            'description': description,
            'analysis': analysis,
            'timestamp': time.time()
        }

    def _reflection_phase(self, query: str, tasks: list, results: list) -> Dict[str, Any]:
        """Reflect on research quality"""
        completed = len([r for r in results if r.get('status') == 'completed'])
        total = len(tasks)

        reflection_prompt = f"""
Evaluate the quality and completeness of this research effort.

Original Query: "{query}"
Tasks Planned: {total}
Tasks Completed: {completed}
Success Rate: {(completed/total*100):.0f}%

Sample Results:
{json.dumps([r.get('analysis', '')[:300] for r in results[:2]], indent=2)}

Assess:
1. Research completeness (0-100%)
2. Quality of findings (poor/fair/good/excellent)
3. Key gaps or limitations
4. Need for additional research? (yes/no)
5. Confidence in final recommendation (0-100%)

Provide concise assessment.
"""

        response = self.llm.call(reflection_prompt)

        return {
            'completeness': f"{(completed/total*100):.0f}%" if total > 0 else "0%",
            'assessment': response,
            'tasks_status': {
                'total': total,
                'completed': completed,
                'failed': total - completed
            },
            'timestamp': time.time()
        }

    def _memory_phase(self, results: list) -> None:
        """Store findings in semantic memory"""
        for result in results:
            if result.get('status') == 'completed':
                # Database storage
                mem_entry = {
                    'entry_id': f"{self.session_id}_{result.get('task_id')}",
                    'session_id': self.session_id,
                    'task_id': result.get('task_id'),
                    'content': result.get('analysis', ''),
                    'category': result.get('type', 'research'),
                    'status': 'active',
                    'type': result.get('type', 'finding')
                }
                self.db_memory.insert(mem_entry)

                # Vector memory (semantic search)
                if result.get('analysis'):
                    self.vector_memory.add(
                        entry_id=f"{self.session_id}_{result.get('task_id')}",
                        text=result.get('analysis', ''),
                        metadata={
                            'task_id': result.get('task_id'),
                            'session_id': self.session_id,
                            'type': result.get('type'),
                            'created_at': time.time()
                        }
                    )

        # Build optimized index
        self.vector_memory.build_index()

    def _reporting_phase(
        self,
        query: str,
        tasks: list,
        results: list,
        reflection: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final report and recommendations"""
        completed_analyses = [r.get('analysis', '') for r in results if r.get('status') == 'completed']

        synthesis_prompt = f"""
Create a comprehensive research synthesis and report.

Original Query: "{query}"

Research Summary:
- Tasks: {len(tasks)} planned, {len([r for r in results if r.get('status') == 'completed'])} completed
- Quality Assessment: {reflection.get('assessment', 'Good')}

Key Findings:
{json.dumps(completed_analyses[:3], indent=2)}

Generate:
1. Executive Summary (2-3 sentences)
2. Key Findings (main points)
3. Supporting Evidence
4. Recommendations or Conclusions
5. Confidence and Caveats

Be professional and actionable.
"""

        synthesis = self.llm.call(synthesis_prompt)

        recommendation_prompt = f"""
Based on this research, provide a final clear recommendation.

Query: "{query}"

Research Summary: {synthesis[:500]}

Provide:
1. Final Recommendation
2. Supporting Logic
3. Risks/Considerations
4. Confidence Level (0-100%)

Be concise and decisive.
"""

        recommendation = self.llm.call(recommendation_prompt)

        return {
            'synthesis': synthesis,
            'recommendation': recommendation,
            'research_quality': reflection.get('completeness'),
            'tasks_completed': len([r for r in results if r.get('status') == 'completed']),
            'total_tasks': len(tasks),
            'generated_at': datetime.now().isoformat()
        }

    @staticmethod
    def _print_phase_results(phase: str, data: Any) -> None:
        """Print formatted phase results"""
        if isinstance(data, list):
            for item in data[:3]:
                if isinstance(item, dict):
                    summary = item.get('description') or item.get('task_id') or item.get('status')
                    print(f"  ✓ {summary}")
        elif isinstance(data, dict):
            for key, value in list(data.items())[:3]:
                print(f"  • {key}: {str(value)[:60]}")

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Print execution summary"""
        print(f"\n{'='*60}")
        print("RESEARCH COMPLETE")
        print(f"{'='*60}")
        print(f"Execution Time: {result['execution_time']}s")
        print(f"Tasks: {result['phases']['execution']['tasks_completed']}/{result['phases']['execution']['tasks_total']} completed")
        print(f"Success Rate: {result['phases']['execution']['success_rate']:.0f}%")
        print(f"Recommendation: {result['final_report']['recommendation'][:100]}...")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    # Example usage
    agent = ARDAAgent()

    queries = [
        "Should I invest in Tesla stock in 2026? What are the pros and cons?",
        "What are the latest developments in quantum computing?",
        "How is climate change affecting agricultural productivity?"
    ]

    for query in queries:
        try:
            result = agent.research(query, depth="deep")
            print(json.dumps(result, indent=2, default=str))
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
