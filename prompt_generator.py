#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Generator for AI Agents and Todo Lists
=============================================

A specialized tool for generating high-quality prompts based on best practices
and patterns from prompt engineering research.

Usage:
    python prompt_generator.py --type agent --role "Software Architect" --task "Design API"
    python prompt_generator.py --type todo --goal "Build web app" --format json
"""

import argparse
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class PromptGenerator:
    """Generates prompts for AI agents and todo lists using best practices"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load prompt templates"""
        return {
            'agent': {
                'system_role': """You are a {role} with expertise in {domain}.
Your primary responsibilities include:
{responsibilities}

Your decision-making framework:
{decision_framework}

When faced with ambiguity, you should:
{ambiguity_handling}

Working style:
{working_style}

Constraints:
{constraints}""",
                
                'react': """You are an AI agent that uses the ReAct pattern:
1. **Think:** Analyze the situation and plan your approach
2. **Act:** Execute actions using available tools
3. **Observe:** Evaluate results and adjust strategy

Available tools:
{tools}

Current task: {task}
Context: {context}

Show your reasoning at each step.""",
                
                'cot': """You are a {role} agent that solves problems step-by-step.

For each task:
1. Break down the problem into sub-problems
2. Analyze each sub-problem independently
3. Synthesize solutions
4. Verify the complete solution
5. Reflect on the approach

Current objective: {objective}
Show your reasoning at each step.""",
                
                'tool_using': """You are a {role} agent with access to the following tools:

Tools:
{tools}

Workflow:
1. Understand the user's request
2. Determine which tools are needed
3. Execute tools in logical sequence
4. Combine results
5. Present final output

User request: {request}"""
            },
            
            'todo': {
                'hierarchical': """Generate a comprehensive todo list for: {goal}

Structure:
- Main tasks (high-level objectives)
  - Subtasks (specific actions)
    - Sub-subtasks (detailed steps)

Requirements:
- Tasks should be actionable and specific
- Include dependencies between tasks
- Estimate complexity/duration if possible
- Prioritize tasks (High/Medium/Low)

Context:
- Domain: {domain}
- Timeline: {timeline}
- Resources: {resources}
- Constraints: {constraints}

Output format: {format}""",
                
                'smart': """Create a todo list where each task follows SMART criteria:
- Specific: Clear and unambiguous
- Measurable: Can track progress
- Achievable: Realistic given constraints
- Relevant: Aligns with overall goal
- Time-bound: Has deadline or duration

Goal: {goal}
Constraints: {constraints}
Timeline: {timeline}

For each task, include:
- Task description
- Success criteria
- Estimated effort
- Dependencies
- Priority

Output format: {format}""",
                
                'context_aware': """You are a {role} planning a {project_type} project.

Context:
- Project goal: {goal}
- Team size: {team_size}
- Timeline: {timeline}
- Resources: {resources}
- Constraints: {constraints}
- Domain: {domain}

Generate a todo list that:
1. Accounts for all context factors
2. Breaks work into logical phases
3. Identifies critical path items
4. Includes risk mitigation tasks
5. Suggests parallel work opportunities

Output in {format} with {detail_level} level of detail.""",
                
                'agile': """Create a todo list organized as an Agile sprint:

Sprint Goal: {goal}
Sprint Duration: {duration}

Organize tasks as:
- Epics (large features)
  - User Stories (user-facing features)
    - Tasks (implementation steps)
    - Acceptance Criteria

For each item, include:
- Story points or effort estimate
- Assignee (if applicable)
- Definition of Done
- Dependencies

Output as: {format}"""
            }
        }
    
    def generate_agent_prompt(
        self,
        role: str,
        domain: str = "general",
        pattern: str = "system_role",
        task: Optional[str] = None,
        context: Optional[str] = None,
        tools: Optional[List[str]] = None,
        responsibilities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate an agent prompt
        
        Args:
            role: Agent's role (e.g., "Software Architect")
            domain: Domain expertise (e.g., "microservices")
            pattern: Prompt pattern (system_role, react, cot, tool_using)
            task: Specific task description
            context: Additional context
            tools: List of available tools
            responsibilities: List of responsibilities
            constraints: List of constraints
            **kwargs: Additional parameters
        """
        template = self.templates['agent'].get(pattern, self.templates['agent']['system_role'])
        
        # Default values
        if responsibilities is None:
            responsibilities = [
                "Analyze requirements and constraints",
                "Design optimal solutions",
                "Provide clear recommendations"
            ]
        
        if constraints is None:
            constraints = [
                "Follow best practices",
                "Consider scalability and maintainability",
                "Ensure security and performance"
            ]
        
        if tools is None:
            tools = ["Analysis tools", "Design tools", "Validation tools"]
        
        # Format responsibilities and constraints
        resp_str = "\n".join(f"- {r}" for r in responsibilities)
        constr_str = "\n".join(f"- {c}" for c in constraints)
        tools_str = "\n".join(f"- {t}" for t in tools)
        
        # Build parameters dict
        params = {
            'role': role,
            'domain': domain,
            'responsibilities': resp_str,
            'decision_framework': kwargs.get('decision_framework', 
                "1. Gather all relevant information\n2. Evaluate options\n3. Choose optimal solution"),
            'ambiguity_handling': kwargs.get('ambiguity_handling',
                "- Ask clarifying questions\n- Make reasonable assumptions\n- Document assumptions"),
            'working_style': kwargs.get('working_style',
                "- Methodical and thorough\n- Evidence-based decisions\n- Clear communication"),
            'constraints': constr_str,
            'task': task or "Complete the assigned task",
            'context': context or "No additional context provided",
            'tools': tools_str,
            'objective': task or "Complete the objective",
            'request': task or "Process the user request"
        }
        
        # Merge with kwargs
        params.update(kwargs)
        
        return template.format(**params)
    
    def generate_todo_prompt(
        self,
        goal: str,
        pattern: str = "hierarchical",
        format: str = "markdown",
        domain: Optional[str] = None,
        timeline: Optional[str] = None,
        resources: Optional[str] = None,
        constraints: Optional[str] = None,
        role: Optional[str] = None,
        project_type: Optional[str] = None,
        team_size: Optional[str] = None,
        detail_level: str = "detailed",
        **kwargs
    ) -> str:
        """
        Generate a todo list prompt
        
        Args:
            goal: Main goal/objective
            pattern: Prompt pattern (hierarchical, smart, context_aware, agile)
            format: Output format (markdown, json, yaml)
            domain: Domain/industry
            timeline: Project timeline
            resources: Available resources
            constraints: Project constraints
            role: Planner's role
            project_type: Type of project
            team_size: Team size
            detail_level: Level of detail (brief, detailed, comprehensive)
            **kwargs: Additional parameters
        """
        template = self.templates['todo'].get(pattern, self.templates['todo']['hierarchical'])
        
        # Default values
        domain = domain or "general"
        timeline = timeline or "Not specified"
        resources = resources or "Standard resources"
        constraints = constraints or "None specified"
        role = role or "Project Manager"
        project_type = project_type or "general project"
        team_size = team_size or "Not specified"
        
        params = {
            'goal': goal,
            'domain': domain,
            'timeline': timeline,
            'resources': resources,
            'constraints': constraints,
            'format': format,
            'role': role,
            'project_type': project_type,
            'team_size': team_size,
            'detail_level': detail_level,
            'duration': timeline
        }
        
        # Merge with kwargs
        params.update(kwargs)
        
        return template.format(**params)
    
    def generate_custom_prompt(
        self,
        prompt_type: str,
        custom_template: str,
        **params
    ) -> str:
        """Generate prompt from custom template"""
        return custom_template.format(**params)
    
    def save_prompt(
        self,
        prompt: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Path:
        """Save generated prompt to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_prompt_{timestamp}.txt"
        
        filepath = Path(filename)
        
        # Prepare content
        content = f"# Generated Prompt\n"
        content += f"Generated: {datetime.now().isoformat()}\n\n"
        
        if metadata:
            content += "## Metadata\n"
            for key, value in metadata.items():
                content += f"- {key}: {value}\n"
            content += "\n"
        
        content += "## Prompt\n\n"
        content += prompt
        
        filepath.write_text(content, encoding='utf-8')
        return filepath


def main():
    """CLI interface for prompt generator"""
    parser = argparse.ArgumentParser(
        description="Generate prompts for AI agents and todo lists"
    )
    
    parser.add_argument(
        '--type',
        choices=['agent', 'todo'],
        required=True,
        help='Type of prompt to generate'
    )
    
    # Agent arguments
    parser.add_argument('--role', help='Agent role (e.g., "Software Architect")')
    parser.add_argument('--domain', default='general', help='Domain expertise')
    parser.add_argument(
        '--pattern',
        choices=['system_role', 'react', 'cot', 'tool_using'],
        default='system_role',
        help='Agent prompt pattern'
    )
    parser.add_argument('--task', help='Specific task description')
    parser.add_argument('--context', help='Additional context')
    parser.add_argument('--tools', nargs='+', help='Available tools')
    
    # Todo arguments
    parser.add_argument('--goal', help='Main goal/objective')
    parser.add_argument(
        '--todo-pattern',
        choices=['hierarchical', 'smart', 'context_aware', 'agile'],
        default='hierarchical',
        help='Todo list pattern'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'yaml'],
        default='markdown',
        help='Output format'
    )
    parser.add_argument('--timeline', help='Project timeline')
    parser.add_argument('--resources', help='Available resources')
    parser.add_argument('--constraints', help='Project constraints')
    
    # General arguments
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--save', action='store_true', help='Save prompt to file')
    parser.add_argument('--pretty', action='store_true', help='Pretty print output')
    
    args = parser.parse_args()
    
    generator = PromptGenerator()
    
    if args.type == 'agent':
        if not args.role:
            parser.error("--role is required for agent prompts")
        
        prompt = generator.generate_agent_prompt(
            role=args.role,
            domain=args.domain,
            pattern=args.pattern,
            task=args.task,
            context=args.context,
            tools=args.tools
        )
        
        metadata = {
            'type': 'agent',
            'role': args.role,
            'domain': args.domain,
            'pattern': args.pattern
        }
    
    elif args.type == 'todo':
        if not args.goal:
            parser.error("--goal is required for todo prompts")
        
        prompt = generator.generate_todo_prompt(
            goal=args.goal,
            pattern=args.todo_pattern,
            format=args.format,
            timeline=args.timeline,
            resources=args.resources,
            constraints=args.constraints
        )
        
        metadata = {
            'type': 'todo',
            'goal': args.goal,
            'pattern': args.todo_pattern,
            'format': args.format
        }
    
    # Output
    if args.pretty:
        print("\n" + "="*80)
        print("GENERATED PROMPT")
        print("="*80 + "\n")
    
    print(prompt)
    
    if args.save or args.output:
        filepath = generator.save_prompt(
            prompt,
            filename=args.output,
            metadata=metadata
        )
        print(f"\n✅ Prompt saved to: {filepath}", file=sys.stderr)


if __name__ == "__main__":
    import sys
    main()

