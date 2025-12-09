# Prompt Generator for AI Agents & Todo Lists

A comprehensive prompt engineering system based on research and best practices for generating high-quality prompts for AI agents and todo list generation.

## Overview

This system provides:
1. **Knowledge Base**: Comprehensive guide to prompt engineering (`PROMPT_ENGINEERING_KNOWLEDGE_BASE.md`)
2. **Generator Tool**: Python tool for generating prompts (`prompt_generator.py`)
3. **Examples**: Usage examples (`prompt_generator_examples.py`)

## Quick Start

### Installation

No additional dependencies required (uses standard library).

### Basic Usage

#### Generate an Agent Prompt

```bash
python prompt_generator.py --type agent \
    --role "Software Architect" \
    --domain "microservices" \
    --pattern system_role \
    --task "Design a scalable API architecture"
```

#### Generate a Todo List Prompt

```bash
python prompt_generator.py --type todo \
    --goal "Build a web application" \
    --pattern hierarchical \
    --format markdown \
    --timeline "6 weeks"
```

### Python API Usage

```python
from prompt_generator import PromptGenerator

generator = PromptGenerator()

# Generate agent prompt
agent_prompt = generator.generate_agent_prompt(
    role="Senior Developer",
    domain="Python/FastAPI",
    pattern="react",
    task="Review code and suggest improvements"
)

# Generate todo prompt
todo_prompt = generator.generate_todo_prompt(
    goal="Implement authentication system",
    pattern="smart",
    format="json",
    timeline="2 weeks"
)

# Save prompts
generator.save_prompt(agent_prompt, filename="agent_prompt.txt")
generator.save_prompt(todo_prompt, filename="todo_prompt.txt")
```

## Available Patterns

### Agent Patterns

1. **system_role**: Standard system role definition with responsibilities
2. **react**: ReAct pattern (Reasoning + Acting) for tool-using agents
3. **cot**: Chain-of-Thought pattern for step-by-step reasoning
4. **tool_using**: Agent with specific tools and workflow

### Todo List Patterns

1. **hierarchical**: Multi-level task breakdown (main tasks → subtasks → sub-subtasks)
2. **smart**: Tasks following SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
3. **context_aware**: Context-aware planning with phases and critical path
4. **agile**: Agile/Scrum sprint organization (Epics → User Stories → Tasks)

## Command Line Options

### Agent Options

```
--type agent              Type of prompt (required)
--role ROLE              Agent role (required)
--domain DOMAIN          Domain expertise (default: "general")
--pattern PATTERN        Pattern: system_role, react, cot, tool_using
--task TASK             Specific task description
--context CONTEXT       Additional context
--tools TOOL [TOOL ...]  Available tools
```

### Todo Options

```
--type todo              Type of prompt (required)
--goal GOAL              Main goal/objective (required)
--todo-pattern PATTERN   Pattern: hierarchical, smart, context_aware, agile
--format FORMAT          Output format: markdown, json, yaml
--timeline TIMELINE      Project timeline
--resources RESOURCES    Available resources
--constraints CONSTRAINTS Project constraints
```

### General Options

```
--output, -o FILE        Output file path
--save                   Save prompt to file
--pretty                 Pretty print output
```

## Examples

### Example 1: Software Architect Agent

```python
from prompt_generator import PromptGenerator

generator = PromptGenerator()

prompt = generator.generate_agent_prompt(
    role="Senior Software Architect",
    domain="microservices and cloud-native applications",
    pattern="system_role",
    responsibilities=[
        "Design scalable system architectures",
        "Evaluate technology choices",
        "Provide technical leadership"
    ],
    constraints=[
        "Must be cloud-agnostic",
        "Should support horizontal scaling",
        "Security must be built-in"
    ]
)
```

### Example 2: ReAct Agent

```python
prompt = generator.generate_agent_prompt(
    role="Code Review Assistant",
    domain="software development",
    pattern="react",
    task="Review a pull request and provide feedback",
    context="The PR adds a new authentication feature",
    tools=[
        "Code analysis tool",
        "Security scanner",
        "Documentation checker"
    ]
)
```

### Example 3: Hierarchical Todo List

```python
prompt = generator.generate_todo_prompt(
    goal="Build a REST API for an e-commerce platform",
    pattern="hierarchical",
    format="markdown",
    domain="web development",
    timeline="6 weeks",
    resources="Team of 3 developers",
    constraints="Must use Python/FastAPI, PostgreSQL"
)
```

### Example 4: SMART Todo List

```python
prompt = generator.generate_todo_prompt(
    goal="Migrate legacy monolith to microservices",
    pattern="smart",
    format="json",
    timeline="3 months",
    constraints="Zero downtime migration"
)
```

## Best Practices

Based on research and industry best practices:

1. **Be Specific**: Clearly define roles, tasks, and expected outputs
2. **Provide Context**: Include relevant background information
3. **Use Positive Instructions**: Frame what to do, not what to avoid
4. **Iterate**: Refine prompts based on output quality
5. **Assign Roles**: Give the AI a clear persona/role
6. **Specify Format**: Clearly define expected output format
7. **Include Constraints**: Set boundaries and limitations
8. **Add Examples**: Use few-shot learning when helpful

## Knowledge Base

See `PROMPT_ENGINEERING_KNOWLEDGE_BASE.md` for:
- Comprehensive prompt engineering principles
- Detailed pattern explanations
- Advanced techniques (CoT, few-shot, self-consistency)
- Structured output patterns
- Best practices checklist
- Template library

## Research Sources

This system is based on:
- OpenAI's Prompt Engineering Guide
- "The Prompt Report: A Systematic Survey of Prompting Techniques" (arXiv:2406.06608)
- "The Prompt Canvas" (arXiv:2412.05127)
- Industry best practices from AWS, DigitalOcean, and others
- ReAct, Chain-of-Thought, and other proven patterns

## Contributing

To add new patterns or improve existing ones:

1. Add template to `PromptGenerator._load_templates()`
2. Update documentation in knowledge base
3. Add examples to `prompt_generator_examples.py`
4. Test with various scenarios

## License

This tool is provided as-is for prompt engineering purposes.

## Support

For questions or issues:
1. Check the knowledge base for patterns and best practices
2. Review examples in `prompt_generator_examples.py`
3. Experiment with different patterns and parameters

---

**Remember**: Effective prompt engineering is iterative. Start simple, test, refine, and improve!

