# Prompt Engineering Knowledge Base
## Comprehensive Guide for Agent & Todo List Prompt Generation

**Last Updated:** 2024
**Purpose:** Master knowledge base for generating effective prompts for AI agents and todo list systems

---

## Table of Contents
1. [Core Principles](#core-principles)
2. [Agent Prompt Patterns](#agent-prompt-patterns)
3. [Todo List Generation Patterns](#todo-list-generation-patterns)
4. [Advanced Techniques](#advanced-techniques)
5. [Structured Output Patterns](#structured-output-patterns)
6. [Best Practices Checklist](#best-practices-checklist)
7. [Prompt Templates Library](#prompt-templates-library)

---

## Core Principles

### 1. Clarity and Specificity
- **Rule:** Be explicit about what you want, not what you don't want
- **Bad:** "Don't make it too long"
- **Good:** "Provide a concise 3-paragraph summary"
- **Why:** Reduces ambiguity and guides AI toward desired output

### 2. Context Provision
- **Rule:** Include relevant background information
- **Components:**
  - Role/Persona assignment
  - Domain expertise level
  - Target audience
  - Constraints and requirements
- **Example:** "As a senior software architect with 10+ years in microservices, design a scalable API architecture for a fintech startup handling 1M+ transactions/day"

### 3. Iterative Refinement
- **Process:**
  1. Start with initial prompt
  2. Review output quality
  3. Identify gaps or issues
  4. Refine prompt with specific improvements
  5. Test and iterate

### 4. Positive Instructions
- **Rule:** Frame instructions positively
- **Bad:** "Don't use technical jargon"
- **Good:** "Use clear, simple language accessible to non-technical stakeholders"
- **Why:** AI models respond better to constructive guidance

### 5. Role/Persona Assignment
- **Benefits:**
  - Enhances relevance
  - Provides context frame
  - Guides decision-making
- **Format:** "You are a [role] with [expertise] specializing in [domain]"

---

## Agent Prompt Patterns

### Pattern 1: System Role Definition
```
You are a [SPECIFIC_ROLE] with expertise in [DOMAIN].
Your primary responsibilities include:
- [RESPONSIBILITY_1]
- [RESPONSIBILITY_2]
- [RESPONSIBILITY_3]

Your decision-making framework:
1. [CRITERIA_1]
2. [CRITERIA_2]
3. [CRITERIA_3]

When faced with ambiguity, you should:
- [BEHAVIOR_1]
- [BEHAVIOR_2]
```

### Pattern 2: ReAct (Reasoning + Acting)
```
You are an AI agent that uses the ReAct pattern:
1. **Think:** Analyze the situation and plan your approach
2. **Act:** Execute actions using available tools
3. **Observe:** Evaluate results and adjust strategy

Available tools:
- [TOOL_1]: [DESCRIPTION]
- [TOOL_2]: [DESCRIPTION]

Current task: [TASK_DESCRIPTION]
Context: [RELEVANT_CONTEXT]
```

### Pattern 3: Chain-of-Thought Agent
```
You are a [ROLE] agent that solves problems step-by-step.

For each task:
1. Break down the problem into sub-problems
2. Analyze each sub-problem independently
3. Synthesize solutions
4. Verify the complete solution
5. Reflect on the approach

Current objective: [OBJECTIVE]
Show your reasoning at each step.
```

### Pattern 4: Tool-Using Agent
```
You are a [ROLE] agent with access to the following tools:

Tools:
[TOOL_DEFINITIONS]

Workflow:
1. Understand the user's request
2. Determine which tools are needed
3. Execute tools in logical sequence
4. Combine results
5. Present final output

User request: [REQUEST]
```

### Pattern 5: Multi-Agent Collaboration
```
You are the [COORDINATOR_ROLE] managing a team of specialized agents:

Team:
- Agent 1: [ROLE_1] - [RESPONSIBILITY]
- Agent 2: [ROLE_2] - [RESPONSIBILITY]
- Agent 3: [ROLE_3] - [RESPONSIBILITY]

Your coordination strategy:
1. Decompose task into subtasks
2. Assign subtasks to appropriate agents
3. Monitor progress
4. Integrate results
5. Quality check final output

Current mission: [MISSION]
```

---

## Todo List Generation Patterns

### Pattern 1: Hierarchical Task Breakdown
```
Generate a comprehensive todo list for: [GOAL]

Structure:
- Main tasks (high-level objectives)
  - Subtasks (specific actions)
    - Sub-subtasks (detailed steps)

Requirements:
- Tasks should be actionable and specific
- Include dependencies between tasks
- Estimate complexity/duration if possible
- Prioritize tasks (High/Medium/Low)

Output format: [JSON/MARKDOWN/STRUCTURED]
```

### Pattern 2: SMART Task Generation
```
Create a todo list where each task follows SMART criteria:
- Specific: Clear and unambiguous
- Measurable: Can track progress
- Achievable: Realistic given constraints
- Relevant: Aligns with overall goal
- Time-bound: Has deadline or duration

Goal: [GOAL]
Constraints: [CONSTRAINTS]
Timeline: [TIMELINE]

For each task, include:
- Task description
- Success criteria
- Estimated effort
- Dependencies
- Priority
```

### Pattern 3: Context-Aware Todo Lists
```
You are a [ROLE] planning a [PROJECT_TYPE] project.

Context:
- Project goal: [GOAL]
- Team size: [SIZE]
- Timeline: [TIMELINE]
- Resources: [RESOURCES]
- Constraints: [CONSTRAINTS]
- Domain: [DOMAIN]

Generate a todo list that:
1. Accounts for all context factors
2. Breaks work into logical phases
3. Identifies critical path items
4. Includes risk mitigation tasks
5. Suggests parallel work opportunities

Output in [FORMAT] with [LEVEL_OF_DETAIL].
```

### Pattern 4: Progressive Refinement Todo
```
Generate an initial todo list for: [GOAL]

Then, for each high-level task:
1. Break it into 3-5 subtasks
2. Identify prerequisites
3. Suggest order of execution
4. Flag potential blockers

Format:
- [Task Name]
  - Prerequisites: [LIST]
  - Subtasks:
    1. [Subtask]
    2. [Subtask]
  - Estimated time: [TIME]
  - Priority: [PRIORITY]
  - Potential blockers: [LIST]
```

### Pattern 5: Agile/Scrum Todo Pattern
```
Create a todo list organized as an Agile sprint:

Sprint Goal: [GOAL]
Sprint Duration: [DURATION]

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

Output as: [FORMAT]
```

---

## Advanced Techniques

### 1. Chain-of-Thought (CoT) Prompting
```
Let's solve this step by step:

Problem: [PROBLEM]

Step 1: [ANALYSIS]
Step 2: [PLANNING]
Step 3: [EXECUTION]
Step 4: [VERIFICATION]

Show your reasoning at each step.
```

### 2. Few-Shot Learning
```
Here are examples of good [OUTPUT_TYPE]:

Example 1:
[INPUT_1] → [OUTPUT_1]

Example 2:
[INPUT_2] → [OUTPUT_2]

Example 3:
[INPUT_3] → [OUTPUT_3]

Now generate for:
[NEW_INPUT]
```

### 3. Self-Consistency
```
Generate [N] different approaches to: [TASK]

For each approach:
- Describe the strategy
- List pros and cons
- Estimate success probability

Then:
- Compare approaches
- Recommend the best one
- Explain why
```

### 4. Tree of Thoughts
```
For the task: [TASK]

Generate multiple solution paths:
- Path 1: [APPROACH_1]
- Path 2: [APPROACH_2]
- Path 3: [APPROACH_3]

Evaluate each path:
- Feasibility
- Effort required
- Expected outcome

Select the optimal path and elaborate.
```

### 5. Reflection and Refinement
```
Task: [TASK]

First attempt: [INITIAL_OUTPUT]

Now reflect:
1. What worked well?
2. What could be improved?
3. What was missing?

Generate an improved version incorporating your reflections.
```

---

## Structured Output Patterns

### JSON Schema Pattern
```
Generate output in JSON format following this schema:

{
  "task": "string",
  "subtasks": [
    {
      "id": "string",
      "description": "string",
      "priority": "high|medium|low",
      "estimated_time": "string",
      "dependencies": ["string"],
      "status": "pending|in_progress|completed"
    }
  ],
  "metadata": {
    "created_at": "ISO8601",
    "total_estimated_time": "string",
    "critical_path": ["string"]
  }
}

Task: [TASK_DESCRIPTION]
```

### Markdown Structured Pattern
```
Generate output in Markdown with this structure:

# [Main Goal]

## Phase 1: [Phase Name]
- [ ] Task 1.1: [Description]
  - [ ] Subtask 1.1.1
  - [ ] Subtask 1.1.2
- [ ] Task 1.2: [Description]

## Phase 2: [Phase Name]
...

### Summary
- Total tasks: [N]
- Estimated duration: [TIME]
- Critical path: [LIST]
```

### YAML Pattern
```
Generate output in YAML format:

project:
  name: "[NAME]"
  goal: "[GOAL]"
  timeline: "[TIMELINE]"

tasks:
  - id: "task-1"
    title: "[TITLE]"
    description: "[DESCRIPTION]"
    priority: "[PRIORITY]"
    estimated_time: "[TIME]"
    dependencies: []
    subtasks:
      - "[SUBTASK_1]"
      - "[SUBTASK_2]"
```

---

## Best Practices Checklist

### Pre-Generation Checklist
- [ ] Defined clear role/persona
- [ ] Specified output format
- [ ] Included relevant context
- [ ] Set constraints and requirements
- [ ] Identified success criteria
- [ ] Considered edge cases

### During Generation
- [ ] Use positive instructions
- [ ] Provide examples when helpful
- [ ] Break complex tasks into steps
- [ ] Include reasoning requirements
- [ ] Specify validation criteria

### Post-Generation
- [ ] Review output quality
- [ ] Check format compliance
- [ ] Verify completeness
- [ ] Test with edge cases
- [ ] Refine prompt if needed

---

## Prompt Templates Library

### Template 1: Generic Agent System Prompt
```
You are a [ROLE] specialized in [DOMAIN].

Capabilities:
- [CAPABILITY_1]
- [CAPABILITY_2]
- [CAPABILITY_3]

Working style:
- [STYLE_1]
- [STYLE_2]

Constraints:
- [CONSTRAINT_1]
- [CONSTRAINT_2]

When responding:
1. [STEP_1]
2. [STEP_2]
3. [STEP_3]
```

### Template 2: Task Decomposition Agent
```
You are a task decomposition specialist.

Your process:
1. Analyze the goal: [GOAL]
2. Identify major phases
3. Break each phase into actionable tasks
4. Identify dependencies
5. Prioritize tasks
6. Estimate effort

Output requirements:
- Format: [FORMAT]
- Detail level: [LEVEL]
- Include: [REQUIREMENTS]

Goal: [USER_GOAL]
```

### Template 3: Todo List Generator
```
Generate a comprehensive todo list for: [GOAL]

Context:
- Domain: [DOMAIN]
- Timeline: [TIMELINE]
- Resources: [RESOURCES]
- Constraints: [CONSTRAINTS]

Requirements:
- [REQUIREMENT_1]
- [REQUIREMENT_2]

Output format: [FORMAT]
Detail level: [LEVEL]
Include estimates: [YES/NO]
Include dependencies: [YES/NO]
```

### Template 4: Multi-Step Agent
```
You are a [ROLE] executing a multi-step process.

Process:
Step 1: [STEP_1_DESCRIPTION]
  - Input: [INPUT_1]
  - Output: [OUTPUT_1]
  - Validation: [VALIDATION_1]

Step 2: [STEP_2_DESCRIPTION]
  - Input: [INPUT_2]
  - Output: [OUTPUT_2]
  - Validation: [VALIDATION_2]

[Continue for all steps...]

Current request: [REQUEST]
Show progress at each step.
```

### Template 5: Quality-Focused Agent
```
You are a [ROLE] with a focus on quality.

Quality standards:
- Accuracy: [STANDARD]
- Completeness: [STANDARD]
- Clarity: [STANDARD]
- Efficiency: [STANDARD]

Quality checks:
1. [CHECK_1]
2. [CHECK_2]
3. [CHECK_3]

Task: [TASK]
Before finalizing, verify all quality standards are met.
```

---

## Key Resources

### Academic Papers
- "The Prompt Report: A Systematic Survey of Prompting Techniques" (arXiv:2406.06608)
- "The Prompt Canvas" (arXiv:2412.05127)

### Tools & Platforms
- OpenAI Playground
- PromptBase
- PromptChainer
- Helicone
- Agenta

### Guides
- OpenAI Prompt Engineering Guide
- AWS Prompt Engineering Resources Hub
- DigitalOcean Best Practices
- Prompt Engineering Library

---

## Usage Guidelines

1. **Start Simple:** Begin with basic patterns, then add complexity
2. **Iterate:** Refine prompts based on output quality
3. **Test:** Validate with multiple scenarios
4. **Document:** Keep track of what works
5. **Share:** Collaborate and learn from others

---

**Remember:** Effective prompt engineering is both art and science. Combine these patterns creatively based on your specific needs.

