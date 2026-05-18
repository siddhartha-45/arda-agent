"""
Planner Agent - Breaks down complex queries into executable tasks
"""

import:py from "tools.llm_tool", LLMTool;

walker PlanTasks {
    """
    Analyzes user query and creates a structured task plan
    """
    has query: str;
    has tasks: list = [];
    has task_count: int = 0;
    has llm_tool: any;

    can task_breakdown;
    can generate_execution_plan;
    can prioritize_tasks;

    :can:init {
        self.llm_tool = LLMTool();
    }

    :walker:activity {
        self.task_breakdown();
    }

    :can:task_breakdown {
        """
        Breaks down the query using LLM
        """
        prompt = f"""
Analyze this research query and break it down into 3-5 concrete, executable tasks.

Query: {self.query}

For each task, provide:
1. Task description
2. Required tool (search, reasoning, analysis)
3. Priority (1-5, with 5 being highest)
4. Success criteria

Format as JSON list with fields: description, tool, priority, criteria
""";
        
        response = self.llm_tool.call(prompt);
        
        try {
            tasks_data = json.loads(response);
            for i, task_data in enumerate(tasks_data) {
                task_obj = {
                    'task_id': f'task_{i+1}',
                    'description': task_data.get('description', ''),
                    'tool': task_data.get('tool', 'reasoning'),
                    'priority': int(task_data.get('priority', 3)),
                    'criteria': task_data.get('criteria', ''),
                    'status': 'pending'
                };
                self.tasks.append(task_obj);
            }
        } catch {
            self.tasks = [
                {
                    'task_id': 'task_1',
                    'description': f'Research and analyze: {self.query}',
                    'tool': 'search',
                    'priority': 5,
                    'criteria': 'Gather comprehensive information',
                    'status': 'pending'
                }
            ];
        }
    }

    :can:generate_execution_plan {
        """
        Generates sequential execution plan
        """
        self.prioritize_tasks();
        
        plan = {
            'total_tasks': len(self.tasks),
            'tasks': self.tasks,
            'execution_order': [t['task_id'] for t in sorted(self.tasks, key=lambda x: -x['priority'])]
        };
        
        report f"Plan generated: {len(self.tasks)} tasks";
    }

    :can:prioritize_tasks {
        """
        Sorts tasks by priority
        """
        self.tasks = sorted(self.tasks, key=lambda x: -x['priority']);
    }
}
