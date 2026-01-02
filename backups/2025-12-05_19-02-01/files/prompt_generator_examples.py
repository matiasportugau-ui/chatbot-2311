#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examples of using the Prompt Generator
======================================

This file demonstrates how to use the PromptGenerator class
to create various types of prompts.
"""

from prompt_generator import PromptGenerator


def example_agent_system_role():
    """Example: Generate a system role agent prompt"""
    print("="*80)
    print("EXAMPLE 1: Agent System Role Prompt")
    print("="*80)
    
    generator = PromptGenerator()
    
    prompt = generator.generate_agent_prompt(
        role="Senior Software Architect",
        domain="microservices and cloud-native applications",
        pattern="system_role",
        responsibilities=[
            "Design scalable system architectures",
            "Evaluate technology choices",
            "Provide technical leadership",
            "Ensure best practices are followed"
        ],
        constraints=[
            "Must be cloud-agnostic",
            "Should support horizontal scaling",
            "Must follow 12-factor app principles",
            "Security must be built-in, not bolted-on"
        ],
        decision_framework="""1. Analyze requirements and constraints
2. Research available solutions
3. Evaluate trade-offs
4. Choose optimal solution
5. Document decision rationale""",
        working_style="""- Methodical and thorough analysis
- Evidence-based decision making
- Clear documentation
- Collaborative approach"""
    )
    
    print(prompt)
    print("\n")
    
    # Save it
    filepath = generator.save_prompt(
        prompt,
        filename="example_agent_system_role.txt",
        metadata={
            'type': 'agent',
            'role': 'Senior Software Architect',
            'pattern': 'system_role'
        }
    )
    print(f"✅ Saved to: {filepath}\n")


def example_agent_react():
    """Example: Generate a ReAct pattern agent prompt"""
    print("="*80)
    print("EXAMPLE 2: ReAct Pattern Agent Prompt")
    print("="*80)
    
    generator = PromptGenerator()
    
    prompt = generator.generate_agent_prompt(
        role="Code Review Assistant",
        domain="software development",
        pattern="react",
        task="Review a pull request and provide feedback",
        context="The PR adds a new authentication feature using OAuth2",
        tools=[
            "Code analysis tool: Analyze code quality and patterns",
            "Security scanner: Check for security vulnerabilities",
            "Documentation checker: Verify documentation completeness",
            "Test coverage analyzer: Check test coverage"
        ]
    )
    
    print(prompt)
    print("\n")


def example_todo_hierarchical():
    """Example: Generate a hierarchical todo list prompt"""
    print("="*80)
    print("EXAMPLE 3: Hierarchical Todo List Prompt")
    print("="*80)
    
    generator = PromptGenerator()
    
    prompt = generator.generate_todo_prompt(
        goal="Build a REST API for an e-commerce platform",
        pattern="hierarchical",
        format="markdown",
        domain="web development",
        timeline="6 weeks",
        resources="Team of 3 developers, 1 designer, 1 QA",
        constraints="Must use Python/FastAPI, PostgreSQL, Docker"
    )
    
    print(prompt)
    print("\n")
    
    # Save it
    filepath = generator.save_prompt(
        prompt,
        filename="example_todo_hierarchical.txt",
        metadata={
            'type': 'todo',
            'goal': 'Build REST API',
            'pattern': 'hierarchical'
        }
    )
    print(f"✅ Saved to: {filepath}\n")


def example_todo_smart():
    """Example: Generate a SMART criteria todo list prompt"""
    print("="*80)
    print("EXAMPLE 4: SMART Criteria Todo List Prompt")
    print("="*80)
    
    generator = PromptGenerator()
    
    prompt = generator.generate_todo_prompt(
        goal="Migrate legacy monolith to microservices architecture",
        pattern="smart",
        format="json",
        timeline="3 months",
        constraints="Zero downtime migration, maintain backward compatibility"
    )
    
    print(prompt)
    print("\n")


def example_todo_agile():
    """Example: Generate an Agile/Scrum todo list prompt"""
    print("="*80)
    print("EXAMPLE 5: Agile Sprint Todo List Prompt")
    print("="*80)
    
    generator = PromptGenerator()
    
    prompt = generator.generate_todo_prompt(
        goal="Implement user authentication and authorization system",
        pattern="agile",
        format="markdown",
        timeline="2 weeks",
        role="Scrum Master"
    )
    
    print(prompt)
    print("\n")


def example_custom_prompt():
    """Example: Generate a custom prompt using a template"""
    print("="*80)
    print("EXAMPLE 6: Custom Prompt Template")
    print("="*80)
    
    generator = PromptGenerator()
    
    custom_template = """You are a {role} working on a {project_type} project.

Your mission: {mission}

Key objectives:
{objectives}

Success criteria:
{success_criteria}

Current phase: {phase}
Next steps: {next_steps}"""
    
    prompt = generator.generate_custom_prompt(
        prompt_type="custom",
        custom_template=custom_template,
        role="DevOps Engineer",
        project_type="cloud migration",
        mission="Migrate on-premise infrastructure to AWS",
        objectives="""- Reduce infrastructure costs by 30%
- Improve deployment speed by 50%
- Achieve 99.9% uptime
- Implement CI/CD pipeline""",
        success_criteria="""- All services running on AWS
- Zero downtime during migration
- Automated deployment pipeline
- Monitoring and alerting in place""",
        phase="Planning and assessment",
        next_steps="""1. Audit current infrastructure
2. Design AWS architecture
3. Create migration plan
4. Set up CI/CD pipeline"""
    )
    
    print(prompt)
    print("\n")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("PROMPT GENERATOR EXAMPLES")
    print("="*80 + "\n")
    
    examples = [
        example_agent_system_role,
        example_agent_react,
        example_todo_hierarchical,
        example_todo_smart,
        example_todo_agile,
        example_custom_prompt
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            if i < len(examples):
                input("\nPress Enter to continue to next example...")
                print("\n")
        except Exception as e:
            print(f"❌ Error in example {i}: {e}\n")
    
    print("="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()

