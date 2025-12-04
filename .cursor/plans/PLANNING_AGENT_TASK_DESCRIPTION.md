# 🤖 Planning Agent Task Description
## Comprehensive Input Document for Planning AI Agent

**Version:** 1.0  
**Date:** 2025-01-12  
**Purpose:** Input document for Planning Agent (Planet Agent) to analyze PRs and generate implementation plans  
**Target System:** BMC Chatbot Ecosystem - Unified Consolidation & Production Plan

---

## 🎯 Agent Identity & Purpose

### Agent Name
**PlanningAgent** (also referred to as "Planet Agent" or "Planning AI Agent")

### Primary Responsibility
Analyze Pull Requests, code changes, and system state to generate comprehensive, actionable implementation plans that integrate seamlessly with the existing Unified Consolidation & Production Plan (16 phases).

### Core Capabilities
1. **PR Analysis:** Deep analysis of pull requests, including code changes, dependencies, and impact
2. **Plan Generation:** Create detailed task breakdowns following orchestrator phase structure
3. **Integration Planning:** Map changes to existing consolidation plan phases
4. **Risk Assessment:** Identify risks, blockers, and mitigation strategies
5. **Timeline Estimation:** Provide realistic time estimates for implementation

---

## 📋 Context & System State

### Current Workspace
- **Path:** `/Users/matias/chatbot2511/chatbot-2311`
- **Active Branch:** `cursor/design-data-recovery-implementation-plan-claude-4.5-sonnet-thinking-1fba`
- **Repository:** `chatbot-2311` (GitHub: `matiasportugau-ui/chatbot-2311`)

### Active Consolidation Plan
- **Plan Document:** `UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md`
- **Total Phases:** 16 (Phase 0 + Phases 1-15)
- **Current Status:** In progress
- **Orchestrator System:** Active with phase executors (phase_0 through phase_15)

### Key Components
1. **BMC Quotation Engine** - Product catalog, pricing by zone (Montevideo, Canelones, Maldonado, Rivera)
2. **WhatsApp Integration** - WhatsApp Business API integration
3. **n8n Workflows** - Orchestration workflows (WF_MAIN_orchestrator_v4.json, etc.)
4. **Qdrant Vector DB** - Product embeddings and knowledge base
5. **Chatwoot Integration** - Customer support platform
6. **Background Agents** - Autonomous agent system
7. **Dashboard** - Financial analytics and monitoring

### Agent Architecture
The system uses **12 specialized agents** (plus 2 optional domain agents) organized in 5 levels:

**Nivel 1: Core Agents (3)**
- OrchestratorAgent - Master coordinator
- RepositoryAgent - Git & workspace management
- DiscoveryAgent - Technical + BMC domain discovery

**Nivel 2: Consolidation Agents (2)**
- MergeAgent - Merge strategy & conflict resolution
- IntegrationAgent - Integration specialist (WhatsApp, n8n, Qdrant, Chatwoot)

**Nivel 3: Production Agents (4)**
- SecurityAgent - Security hardening
- InfrastructureAgent - Infrastructure as Code
- ObservabilityAgent - Monitoring & logging
- PerformanceAgent - Performance & load testing

**Nivel 4: Deployment Agents (3)**
- CICDAgent - CI/CD Pipeline
- DisasterRecoveryAgent - DR & Backup
- ValidationAgent - Final validation & QA

**Nivel 5: Domain Agents (2) - Optional**
- NLUAgent - NLP/Rasa specialist
- QuotationAgent - Quotation engine expert

**Total:** 12 specialized agents + 2 optional domain agents = 14 agents total

---

## 🔍 Task Analysis Framework

### Phase 1: PR/Change Analysis

#### Task 1.1: Extract PR Metadata
**Objective:** Gather all metadata about the pull request or change set

**Actions:**
1. Extract PR number, title, description, author
2. Identify base branch and head branch
3. Extract creation date, last update date
4. Determine PR status (open, merged, closed)
5. Identify review status and approvals
6. Extract labels and milestones

**Output Format:**
```json
{
  "pr_number": 35,
  "title": "Plan agent deployment and team instructions",
  "author": "matiasportugau-ui",
  "status": "merged",
  "base_branch": "new-branch",
  "head_branch": "cursor/plan-agent-deployment-and-team-instructions-claude-4.5-sonnet-thinking-56b8",
  "created_at": "2025-12-02T17:02:54Z",
  "updated_at": "2025-12-02T19:43:50Z",
  "files_changed": 5,
  "additions": 3501,
  "deletions": 0
}
```

#### Task 1.2: Analyze Changed Files
**Objective:** Categorize and understand all file changes

**Actions:**
1. List all files modified, added, or deleted
2. Categorize by type:
   - Configuration files (JSON, YAML, TOML)
   - Source code (Python, TypeScript, JavaScript)
   - Documentation (Markdown, MDX)
   - Tests (pytest, jest, etc.)
   - Scripts (Shell, Python automation)
   - Dependencies (requirements.txt, package.json)
3. Identify affected modules/components
4. Map files to BMC components (quotation engine, integrations, etc.)
5. Identify architectural impact (API changes, schema changes, etc.)

**Output Format:**
```json
{
  "files": [
    {
      "path": "AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md",
      "status": "added",
      "type": "documentation",
      "size": 1405,
      "affected_component": "orchestrator",
      "impact_level": "high"
    }
  ],
  "categories": {
    "documentation": 5,
    "configuration": 0,
    "source_code": 0,
    "tests": 0
  },
  "affected_modules": ["orchestrator", "deployment"]
}
```

#### Task 1.3: Understand PR Purpose & Objectives
**Objective:** Extract the primary goals and business context

**Actions:**
1. Parse PR description/body for objectives
2. Identify primary use case or feature
3. Map to consolidation plan phases
4. Identify business domain (BMC-specific or general)
5. Extract acceptance criteria
6. Identify related issues or dependencies

**Output Format:**
```json
{
  "primary_objective": "Create comprehensive multi-agent deployment plan",
  "business_domain": "deployment_orchestration",
  "related_phases": [0, 13, 15],
  "acceptance_criteria": [
    "Deployment plan document created",
    "Team instructions provided",
    "Orchestrator kickoff guide available"
  ],
  "dependencies": [],
  "related_issues": []
}
```

#### Task 1.4: Dependency Analysis
**Objective:** Identify all dependencies and potential conflicts

**Actions:**
1. Extract new dependencies (packages, libraries)
2. Check for conflicts with existing dependencies
3. Verify compatibility with current tech stack:
   - Python 3.10+
   - FastAPI
   - OpenAI GPT-4o-mini
   - n8n workflows
   - Qdrant
   - MongoDB
   - PostgreSQL
4. Identify required environment changes
5. Check for breaking changes
6. Identify migration requirements

**Output Format:**
```json
{
  "new_dependencies": [],
  "updated_dependencies": [],
  "conflicts": [],
  "compatibility": {
    "python": "3.10+",
    "compatible": true
  },
  "breaking_changes": false,
  "migration_required": false
}
```

---

### Phase 2: Impact Assessment

#### Task 2.1: Architecture Impact Analysis
**Objective:** Assess impact on system architecture

**Actions:**
1. Identify affected architectural components:
   - Service boundaries
   - API contracts
   - Data models
   - Integration points
2. Assess impact on:
   - WhatsApp Business API integration
   - n8n workflows
   - Qdrant vector database
   - Chatwoot integration
   - Quotation engine
   - Background agents
   - Dashboard
3. Determine alignment with monorepo consolidation goals
4. Identify required architectural changes

**Output Format:**
```json
{
  "affected_components": ["orchestrator", "deployment"],
  "service_boundaries": "no_change",
  "api_contracts": "no_change",
  "data_models": "no_change",
  "integration_points": {
    "whatsapp": "no_impact",
    "n8n": "no_impact",
    "qdrant": "no_impact",
    "chatwoot": "no_impact"
  },
  "consolidation_alignment": "high",
  "architectural_changes_required": false
}
```

#### Task 2.2: Consolidation Plan Alignment
**Objective:** Map changes to unified consolidation plan

**Actions:**
1. Map PR changes to UNIFIED_CONSOLIDATION_PRODUCTION_PLAN phases
2. Identify which phases need updates
3. Determine if new tasks need to be added
4. Check for conflicts with ongoing consolidation work
5. Identify phase dependencies
6. Determine if new phase is needed

**Output Format:**
```json
{
  "primary_phase": 0,
  "affected_phases": [0, 13, 15],
  "phase_updates_required": [
    {
      "phase": 0,
      "update_type": "documentation",
      "tasks_to_add": []
    }
  ],
  "new_phase_required": false,
  "conflicts": [],
  "dependencies": []
}
```

#### Task 2.3: BMC Domain Impact Assessment
**Objective:** Assess impact on BMC-specific components

**Actions:**
1. Assess impact on quotation engine:
   - Product catalog changes
   - Pricing logic changes
   - Zone-based pricing
2. Assess impact on integrations:
   - WhatsApp Business API
   - n8n workflows
   - Qdrant configuration
   - Chatwoot setup
3. Validate business logic preservation
4. Identify BMC-specific testing requirements

**Output Format:**
```json
{
  "quotation_engine_impact": "none",
  "integration_impact": {
    "whatsapp": "none",
    "n8n": "none",
    "qdrant": "none",
    "chatwoot": "none"
  },
  "business_logic_preserved": true,
  "bmc_testing_required": false
}
```

#### Task 2.4: Security & Production Readiness Impact
**Objective:** Assess security and production readiness implications

**Actions:**
1. Review security implications
2. Check for production readiness gaps
3. Identify required security hardening (Phase 9)
4. Assess impact on:
   - Webhook signature validation
   - Secrets management
   - Rate limiting
   - CORS configuration
   - API authentication

**Output Format:**
```json
{
  "security_impact": "low",
  "production_readiness_impact": "documentation_only",
  "security_hardening_required": false,
  "phase_9_updates": []
}
```

---

### Phase 3: Integration Strategy

#### Task 3.1: Merge Strategy Development
**Objective:** Determine optimal merge approach

**Actions:**
1. Determine merge approach:
   - Direct merge to target branch
   - Rebase and merge
   - Cherry-pick specific commits
   - Create integration branch
2. Identify potential conflicts
3. Plan conflict resolution approach
4. Determine testing strategy before merge
5. Identify rollback plan

**Output Format:**
```json
{
  "merge_strategy": "direct_merge",
  "target_branch": "new-branch",
  "conflicts_expected": false,
  "conflict_resolution": "not_required",
  "pre_merge_testing": ["documentation_review"],
  "rollback_plan": "git_revert"
}
```

#### Task 3.2: Testing Strategy
**Objective:** Define comprehensive testing approach

**Actions:**
1. Identify required test updates
2. Plan integration testing
3. Determine BMC-specific test scenarios
4. Plan regression testing scope
5. Identify performance testing needs
6. Plan UAT (User Acceptance Testing) if applicable

**Output Format:**
```json
{
  "test_updates_required": false,
  "integration_testing": {
    "required": false,
    "scenarios": []
  },
  "bmc_testing": {
    "required": false,
    "scenarios": []
  },
  "regression_testing": {
    "required": false,
    "scope": []
  },
  "performance_testing": {
    "required": false
  },
  "uat_required": false
}
```

#### Task 3.3: Documentation Updates
**Objective:** Identify documentation requirements

**Actions:**
1. Identify documentation that needs updates
2. Plan new documentation requirements
3. Update architecture diagrams if needed
4. Update consolidation plan if required
5. Update API documentation if applicable
6. Update deployment guides if applicable

**Output Format:**
```json
{
  "documentation_updates": [
    {
      "file": "UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md",
      "update_type": "reference",
      "priority": "low"
    }
  ],
  "new_documentation": [
    {
      "file": "AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md",
      "status": "added",
      "location": "root"
    }
  ],
  "diagram_updates": false
}
```

---

### Phase 4: Implementation Plan Generation

#### Task 4.1: Create Detailed Task Breakdown
**Objective:** Generate structured tasks following orchestrator format

**Task Format:**
```markdown
- [ ] **T[X].Y:** Task Name
  - **Script:** `path/to/script.py` (if applicable)
  - **Action:** Detailed description of what needs to be done
  - **Files:** List of files to be modified/created
  - **Dependencies:** List of prerequisite tasks
  - **Output:** Expected output location
  - **Priority:** P0 (Critical) / P1 (Important) / P2 (Medium)
  - **Agent:** Assigned agent (OrchestratorAgent, RepositoryAgent, etc.)
  - **Estimated Duration:** Time estimate (e.g., "2 hours", "1 day")
  - **BMC Context:** BMC-specific considerations (if applicable)
```

**Example Task:**
```markdown
- [ ] **T0.8:** Review and integrate agent deployment documentation
  - **Script:** `scripts/orchestrator/documentation/review_deployment_docs.py`
  - **Action:**
    - Review AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md
    - Review ORCHESTRATOR_KICKOFF_GUIDE.md
    - Review DEPLOYMENT_PACKAGE_SUMMARY.md
    - Integrate into Phase 0 documentation
    - Update orchestrator configuration if needed
  - **Files:**
    - `AGENT_DEPLOYMENT_PLAN_TEAM_INSTRUCTIONS.md`
    - `ORCHESTRATOR_KICKOFF_GUIDE.md`
    - `DEPLOYMENT_PACKAGE_SUMMARY.md`
    - `scripts/orchestrator/config/orchestrator_config.json`
  - **Dependencies:** None
  - **Output:** `consolidation/discovery/deployment_docs_integration.json`
  - **Priority:** P1 - Important
  - **Agent:** DiscoveryAgent
  - **Estimated Duration:** 2 hours
  - **BMC Context:** Ensure deployment plan aligns with BMC production requirements
```

#### Task 4.2: Phase Integration
**Objective:** Assign tasks to appropriate consolidation plan phases

**Actions:**
1. Map each task to a phase (0-15)
2. Update phase executors if needed
3. Create new phase if PR introduces major functionality
4. Update orchestrator configuration
5. Ensure phase dependencies are maintained
6. Validate phase sequence

**Output Format:**
```json
{
  "tasks_by_phase": {
    "0": [
      {
        "task_id": "T0.8",
        "task_name": "Review and integrate agent deployment documentation",
        "priority": "P1"
      }
    ],
    "13": [],
    "15": []
  },
  "phase_executor_updates": [],
  "new_phase_required": false,
  "orchestrator_config_updates": []
}
```

#### Task 4.3: Timeline Estimation
**Objective:** Provide realistic time estimates

**Actions:**
1. Estimate duration for each task
2. Identify critical path
3. Determine parallel execution opportunities
4. Set milestones and checkpoints
5. Account for dependencies
6. Include buffer time for unexpected issues

**Output Format:**
```json
{
  "total_estimated_duration": "2 hours",
  "critical_path": ["T0.8"],
  "parallel_opportunities": [],
  "milestones": [
    {
      "milestone": "Documentation Review Complete",
      "tasks": ["T0.8"],
      "estimated_completion": "2 hours from start"
    }
  ],
  "dependencies_resolved": true,
  "buffer_time": "30 minutes"
}
```

#### Task 4.4: Risk Assessment
**Objective:** Identify risks and mitigation strategies

**Actions:**
1. Identify potential risks:
   - Technical risks
   - Integration risks
   - Timeline risks
   - Resource risks
2. Plan mitigation strategies
3. Identify rollback procedures
4. Document assumptions and constraints
5. Identify blockers

**Output Format:**
```json
{
  "risks": [
    {
      "risk": "Documentation may conflict with existing plans",
      "probability": "low",
      "impact": "medium",
      "mitigation": "Review existing plans before integration",
      "owner": "DiscoveryAgent"
    }
  ],
  "blockers": [],
  "assumptions": [
    "PR changes are documentation-only",
    "No code changes required"
  ],
  "constraints": [
    "Must maintain compatibility with existing orchestrator system"
  ],
  "rollback_procedures": [
    "Revert documentation changes if conflicts arise"
  ]
}
```

---

## 📊 Output Requirements

### Required Deliverables

#### 1. PR Analysis Report
**File:** `consolidation/pr_analysis/pr_[NUMBER]_analysis.json`

**Structure:**
```json
{
  "pr_number": 35,
  "analysis_date": "2025-01-12T00:00:00Z",
  "metadata": {
    "title": "...",
    "author": "...",
    "status": "...",
    "base_branch": "...",
    "head_branch": "..."
  },
  "files_changed": [...],
  "purpose": "...",
  "dependencies": [...],
  "impact_assessment": {
    "architecture": {...},
    "consolidation_plan": {...},
    "bmc_domain": {...},
    "security": {...}
  },
  "integration_strategy": {
    "merge_strategy": "...",
    "testing_strategy": {...},
    "documentation_updates": [...]
  }
}
```

#### 2. Detailed Task List
**File:** `consolidation/pr_analysis/pr_[NUMBER]_tasks.md`

**Format:** Markdown with structured task breakdown following the format defined in Task 4.1

#### 3. Consolidation Plan Updates
**File:** `consolidation/pr_analysis/pr_[NUMBER]_plan_updates.md` (if needed)

**Content:**
- Modified phase descriptions
- New tasks added to existing phases
- New phase created (if major functionality)
- Updated phase dependencies

#### 4. Integration Checklist
**File:** `consolidation/pr_analysis/pr_[NUMBER]_integration_checklist.md`

**Structure:**
```markdown
# Integration Checklist for PR #35

## Pre-Merge Checks
- [ ] Documentation reviewed
- [ ] No conflicts with existing plans
- [ ] Dependencies verified

## Merge Steps
1. [ ] Review PR changes
2. [ ] Verify branch compatibility
3. [ ] Execute merge

## Post-Merge Validation
- [ ] Documentation accessible
- [ ] Links verified
- [ ] Integration complete

## Testing Requirements
- [ ] Documentation review
- [ ] Link validation
```

---

## 🤖 Agent Assignment Guidelines

### Primary Agent
**OrchestratorAgent** - Coordinates the planning process

### Supporting Agents (as needed)
- **RepositoryAgent** - If Git/workspace changes
- **DiscoveryAgent** - If new components discovered
- **MergeAgent** - If merge strategy needed
- **IntegrationAgent** - If integration changes
- **SecurityAgent** - If security implications
- **ValidationAgent** - For final validation

### Agent Selection Criteria
1. **RepositoryAgent:** Git operations, workspace changes, file analysis
2. **DiscoveryAgent:** New components, system discovery, documentation review
3. **MergeAgent:** Merge conflicts, branch management, integration strategy
4. **IntegrationAgent:** Integration changes, API updates, external service changes
5. **SecurityAgent:** Security implications, vulnerabilities, hardening needs
6. **ValidationAgent:** Testing requirements, quality assurance, UAT

---

## ✅ Acceptance Criteria

### Analysis Completeness
- [ ] PR #35 fully analyzed and documented
- [ ] All changed files categorized and impact assessed
- [ ] Integration strategy defined and validated
- [ ] Tasks created and assigned to appropriate phases
- [ ] Consolidation plan updated (if needed)
- [ ] Risk assessment completed
- [ ] Implementation timeline estimated
- [ ] All outputs generated in specified locations

### Quality Standards
- [ ] Tasks follow orchestrator format
- [ ] Tasks have clear priorities (P0/P1/P2)
- [ ] Tasks have assigned agents
- [ ] Tasks have time estimates
- [ ] Dependencies clearly identified
- [ ] BMC context considered where applicable
- [ ] Production readiness maintained or improved

### Documentation Standards
- [ ] All outputs use consistent format
- [ ] JSON outputs are valid and well-structured
- [ ] Markdown outputs are well-formatted
- [ ] Links are verified and working
- [ ] References to existing plans are accurate

---

## 🔄 Execution Workflow

### Step 1: Initialization
1. Load PR information (PR #35 or current changes)
2. Load current consolidation plan state
3. Load orchestrator configuration
4. Initialize context manager

### Step 2: Analysis Phase
1. Execute Phase 1: PR/Change Analysis (Tasks 1.1-1.4)
2. Execute Phase 2: Impact Assessment (Tasks 2.1-2.4)
3. Execute Phase 3: Integration Strategy (Tasks 3.1-3.3)

### Step 3: Plan Generation
1. Execute Phase 4: Implementation Plan Generation (Tasks 4.1-4.4)
2. Generate all required outputs
3. Validate outputs against acceptance criteria

### Step 4: Review & Validation
1. Review generated plan
2. Validate against existing consolidation plan
3. Check for conflicts or inconsistencies
4. Update consolidation plan if needed

### Step 5: Output Generation
1. Generate PR Analysis Report
2. Generate Detailed Task List
3. Generate Consolidation Plan Updates (if needed)
4. Generate Integration Checklist

---

## 📝 Special Considerations

### BMC Domain Context
- Always consider BMC-specific components (quotation engine, WhatsApp, n8n, Qdrant)
- Validate business logic preservation
- Consider zone-based pricing (Montevideo, Canelones, Maldonado, Rivera)
- Consider product catalog (Isodec, Isoroof, Isopanel, etc.)

### Production Readiness
- Maintain or improve production readiness
- Consider security implications
- Consider performance impact
- Consider observability needs

### Orchestrator Integration
- Tasks must follow orchestrator phase structure
- Tasks must be compatible with phase executors
- Tasks must integrate with state manager
- Tasks must support agent handoff if enabled

### Documentation Standards
- Preserve EXPORT_SEAL metadata blocks
- Use consistent formatting
- Include BMC context where applicable
- Link to related documentation

---

## 🎯 Success Metrics

### Analysis Quality
- **Completeness:** 100% of PR changes analyzed
- **Accuracy:** All impact assessments validated
- **Integration:** Seamless integration with consolidation plan

### Plan Quality
- **Actionability:** All tasks are clear and actionable
- **Prioritization:** Tasks properly prioritized
- **Estimates:** Time estimates are realistic

### Output Quality
- **Format:** All outputs follow specified formats
- **Completeness:** All required outputs generated
- **Validation:** All outputs pass validation

---

## 📚 Reference Documents

### Primary References
- `UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md` - Main consolidation plan
- `ENHANCED_MONOREPO_CONSOLIDATION_PLAN.md` - Enhanced plan details
- `scripts/orchestrator/phase_executors/phase_0_executor.py` - Phase executor example

### Supporting References
- `BMC_ARCHITECT_PROMPT.md` - BMC domain context
- `ARCHITECTURAL_REVIEW_PRODUCTION_READINESS.md` - Production readiness guidelines
- `scripts/orchestrator/main_orchestrator.py` - Orchestrator implementation

---

## 🔧 Technical Specifications

### Input Format
- **PR Information:** GitHub PR JSON or local changes
- **Plan State:** Current phase status from state manager
- **Configuration:** Orchestrator configuration JSON

### Output Format
- **JSON:** Structured data (analysis reports, configurations)
- **Markdown:** Documentation (task lists, checklists, updates)
- **Location:** `consolidation/pr_analysis/` directory

### Validation
- JSON outputs must be valid JSON
- Markdown outputs must be valid Markdown
- All file paths must be relative to workspace root
- All agent names must match orchestrator agent names

---

## 🚀 Quick Start Guide

### For Planning Agent

1. **Load Context:**
   ```python
   # Load PR information
   pr_info = load_pr_info(pr_number=35)
   
   # Load consolidation plan
   plan = load_consolidation_plan()
   
   # Load orchestrator config
   config = load_orchestrator_config()
   ```

2. **Execute Analysis:**
   ```python
   # Phase 1: PR Analysis
   analysis = analyze_pr(pr_info)
   
   # Phase 2: Impact Assessment
   impact = assess_impact(analysis, plan)
   
   # Phase 3: Integration Strategy
   strategy = develop_integration_strategy(analysis, impact)
   ```

3. **Generate Plan:**
   ```python
   # Phase 4: Implementation Plan
   tasks = generate_tasks(analysis, impact, strategy)
   plan_updates = integrate_to_plan(tasks, plan)
   ```

4. **Generate Outputs:**
   ```python
   # Generate all required outputs
   generate_analysis_report(analysis, impact, strategy)
   generate_task_list(tasks)
   generate_plan_updates(plan_updates)
   generate_integration_checklist(strategy)
   ```

---

## 📌 Notes

- This document serves as the **primary input** for the Planning Agent
- The Planning Agent should follow this structure when analyzing PRs or changes
- All outputs should maintain consistency with existing consolidation plan format
- BMC domain knowledge should be preserved throughout analysis
- Production readiness should be maintained or improved
- The Planning Agent should integrate seamlessly with the orchestrator system

---

**Export Seal:**
```json
{
  "export_seal": {
    "project": "chatbot-2311",
    "prompt_id": "planning-agent-task-description",
    "version": "1.0",
    "created_at": "2025-01-12T00:00:00Z",
    "author": "Planning Agent",
    "origin": "Unified Consolidation Plan"
  }
}
```

