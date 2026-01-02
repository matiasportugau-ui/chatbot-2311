# Codebase Analysis Plan: Chatbot Platform with CRM Dashboard

## System Definition

**Target System:** Chatbot Platform with Integrated Dashboard for Google Sheets CRM
- **Core Functions:**
  - Chatbot interface and conversation handling
  - Google Sheets CRM integration for lead management
  - Lead ingestion and processing
  - Automatic quote generation
  - Dashboard for monitoring and analytics

**Project Type:** Enterprise Chatbot Platform with CRM Integration

**Repository Scope:** All workspace folders + All GitHub repositories and branches
- `/Users/matias/chatbot2511/chatbot-2311/` (main chatbot repo)
- `/Users/matias/Projects/` (additional projects)
- `/Users/matias/Master_TEMP/` (temporary/master files)
- `/Users/matias/Documents/GitHub/` (GitHub repositories)
- `/Users/matias/Documents/GitHub/master-knowledge-analysis/` (knowledge base)
- **All GitHub repositories** under `matiasportugau-ui` namespace/organization
- **All branches** within each repository (local and remote branches)
- **GitHub Actions** workflows and configurations
- **Pull Requests** (open and closed) for context and changes

**GitHub API Authentication:** ✅ Configured (token provided, will be used securely)

**Keywords for Relevance:**
- Primary: `chatbot`, `chat`, `conversation`, `message`, `whatsapp`, `lead`, `crm`, `sheets`, `google`, `quote`, `quotation`, `cotizacion`, `dashboard`, `ingest`, `ingestion`
- Secondary: `agent`, `ai`, `model`, `integration`, `webhook`, `n8n`, `workflow`, `pricing`, `product`, `client`, `customer`, `analytics`, `insights`

## Analysis Tasks

### Phase 1: GitHub Repository and Branch Discovery

**Task 1.1: Discover GitHub Repositories**
- Use GitHub API with provided token to list all repositories under `matiasportugau-ui` namespace
- For each repository, collect:
  - Repository name, description, language
  - Default branch
  - Repository visibility (public/private)
  - Last updated date
  - Star count, fork count
  - Topics/tags
- Mark inaccessible repos as `#ZonaDesconocida`
- Document repository relationships and dependencies

**Task 1.2: Enumerate All Branches**
- For each GitHub repository:
  - List all branches via GitHub API (`GET /repos/{owner}/{repo}/branches`)
  - Identify branch types:
    - Main/master branches
    - Development branches (develop, dev)
    - Feature branches (feature/*)
    - Hotfix branches (hotfix/*)
    - Release branches (release/*)
    - Stale/archived branches
  - Get branch protection rules
  - Track branch relationships (merged status, ahead/behind)
- For local repositories:
  - List local branches (`git branch`)
  - List remote branches (`git branch -r`)
  - Map local to remote branches

**Task 1.3: Discover GitHub Actions**
- For each repository:
  - List all workflow files (`.github/workflows/*.yml`)
  - Extract workflow definitions:
    - Workflow name and triggers
    - Jobs and steps
    - Dependencies between workflows
    - Secrets and environment variables used
  - Analyze workflow purposes:
    - CI/CD pipelines
    - Automated testing
    - Deployment workflows
    - Scheduled tasks
  - Document workflow relationships to system components

**Task 1.4: Analyze Pull Requests**
- For each repository:
  - Fetch open pull requests (`GET /repos/{owner}/{repo}/pulls?state=open`)
  - Fetch recently closed PRs (last 100)
  - For each PR, extract:
    - Title, description, labels
    - Files changed
    - Author and reviewers
    - Status (open, merged, closed)
    - Associated branches
    - Comments and discussions
  - Identify PRs relevant to target system (keyword matching)
  - Map PR changes to modules and components
  - Note pending changes not yet merged

**Task 1.5: Local Repository Discovery**
- Scan workspace root directories for local git repositories
- Find all `.git` directories
- Extract repository metadata:
  - Remote URLs (identify GitHub repos)
  - Current branch
  - Commit history
- Map local repos to GitHub repos
- Document repository structure and relationships

### Phase 2: Module Discovery Across Branches

**Task 2.1: Language and File Type Inventory (Per Branch)**
- For each repository and branch:
  - Checkout or analyze branch content (via GitHub API or git)
  - Identify JavaScript/TypeScript files
  - Identify Python backend scripts
  - Identify configuration files (JSON, YAML, ENV)
  - Identify documentation (MD, TXT)
  - Count files by type per repository and branch
  - Track differences between branches (what's unique to each branch)

**Task 2.2: Module Discovery (Cross-Branch Analysis)**
- For each repository and branch:
  - Traverse all folders recursively
  - Identify modules by naming patterns:
    - Components: `*.tsx`, `*.jsx`, `Component.*`
    - Services: `*Service.*`, `*service.*`, `*api.*`
    - Hooks: `use*.ts`, `use*.js`
    - Stores: `*Store.*`, `*store.*`, `*state.*`
    - Utilities: `*util.*`, `*helper.*`, `*utils.*`
    - Domain models: `*model.*`, `*entity.*`, `*type.*`
    - Integrations: `*integration.*`, `*integrate.*`
    - Config: `config.*`, `*.config.*`
    - Actions: `.github/workflows/*.yml`
- Track module versions across branches:
  - Modules that exist in multiple branches
  - Branch-specific modules
  - Modules with different implementations per branch
  - Merge conflicts or divergent implementations
- Map modules to pull requests (which PRs introduced/modified them)

### Phase 3: Relevance Filtering and Classification

**Task 3.1: Keyword-Based Filtering**
- Scan module names for keyword matches
- Scan file contents for keyword occurrences
- Scan PR descriptions and titles for relevance
- Score relevance: High/Medium/Low/None
- Tag modules with matched keywords
- Tag PRs relevant to target system

**Task 3.2: Module Classification**
- Classify each module by type:
  - **UI**: React components, pages, views
  - **Service**: API clients, business logic services
  - **Domain**: Data models, entities, types
  - **Store**: State management (Redux, Zustand, etc.)
  - **Integration**: External service integrations (Google Sheets, WhatsApp, n8n)
  - **Hook**: React hooks, custom hooks
  - **Utility**: Helper functions, formatters, validators
  - **Workflow**: GitHub Actions workflows
  - **Other**: Configs, tests, scripts

**Task 3.3: System Component Mapping**
- Map modules to system functions:
  - Chatbot: conversation handling, message processing, AI integration
  - CRM Dashboard: UI components, data visualization, analytics
  - Google Sheets: integration modules, sync logic, data mapping
  - Lead Ingestion: data import, validation, processing
  - Quote Generation: pricing logic, calculation, template generation
- Map GitHub Actions to system functions:
  - CI/CD for chatbot deployment
  - Automated testing workflows
  - Data sync workflows
  - Scheduled tasks

### Phase 4: Semantic Analysis

**Task 4.1: Purpose and Function Analysis**
- For each relevant module:
  - Describe purpose and responsibility
  - Identify inputs and outputs
  - Document dependencies (imports/exports)
  - Note data flow and relationships
  - Link to related PRs and branches

**Task 4.2: Contribution Assessment**
- Determine direct vs indirect contribution to target system
- Identify modules that:
  - Directly implement system features
  - Support system operations (utilities, configs)
  - Integrate with external services
  - Provide infrastructure (routing, state management)
- Assess PR impact on system:
  - Which PRs add/modify system features
  - Which PRs are pending and could affect system

**Task 4.3: Code Quality Indicators**
- Flag potential issues:
  - Duplicate code patterns across branches
  - Deprecated/unused modules
  - Areas needing refactoring
  - Missing documentation
  - Circular dependencies
  - Failed CI/CD workflows
  - PRs with unresolved conflicts

### Phase 5: Unified Module Map Generation

**Task 5.1: Structured Module List**
- Build JSON structure with:
  - Repository name and GitHub URL
  - Branch name (if branch-specific)
  - Relative path from repo root
  - Module name
  - Type classification
  - Description (purpose and function)
  - Relevance score (High/Medium/Low/None)
  - Justification (why relevant or not)
  - Suggested action (integrate/refactor/document/review/discard)
  - Related PRs (if any)
  - Notes (uncertainties, #ZonaDesconocida markers)

**Task 5.2: GitHub Actions Documentation**
- Document each workflow:
  - Workflow name and file path
  - Triggers and schedule
  - Jobs and steps
  - Purpose and relation to system
  - Dependencies on other workflows
  - Status (active/inactive)

**Task 5.3: Pull Request Summary**
- For relevant PRs:
  - PR number, title, status
  - Files changed
  - Modules affected
  - Relevance to target system
  - Recommendation (merge, review, close)

**Task 5.4: Action Recommendations**
- **Integrate**: Modules ready to use, well-structured
- **Refactor**: Modules needing cleanup but valuable
- **Document**: Modules functional but lacking docs
- **Review**: Modules with unclear purpose or quality concerns
- **Discard**: Deprecated, unused, or obsolete code
- **Merge**: PRs ready to be merged
- **Update**: PRs needing updates before merge

### Phase 6: Global Analysis and Reporting

**Task 6.1: Statistics Compilation**
- Total modules discovered (across all repos and branches)
- Relevant modules count (High + Medium relevance)
- Distribution by type
- Distribution by repository
- Distribution by branch
- Distribution by action recommendation
- Total PRs analyzed
- Active workflows count

**Task 6.2: Functional Gap Analysis**
- Identify missing capabilities:
  - Required features not implemented
  - Incomplete integrations
  - Missing error handling
  - Lack of monitoring/analytics
  - Security gaps
  - Missing CI/CD workflows

**Task 6.3: Integration Opportunities**
- Identify modules that could be:
  - Combined for better cohesion
  - Refactored for reuse
  - Integrated with existing system
  - Enhanced with additional features
- Identify PRs that could be merged to complete features
- Identify workflows that could be consolidated

**Task 6.4: Risk Assessment**
- **Accessibility Risks**: Inaccessible repos, permission issues, private repos
- **Technical Debt**: Code quality issues, outdated dependencies, stale branches
- **Ambiguity**: Unclear purpose, missing context, undocumented PRs
- **Dependencies**: Circular deps, fragile integrations, workflow dependencies
- **Security**: Exposed keys, unsafe practices, unmerged security PRs
- **Branch Management**: Stale branches, merge conflicts, divergent code

## Expected Output Structure

```json
{
  "system_info": {
    "name": "Chatbot Platform with Integrated Google Sheets CRM Dashboard",
    "core_functions": [
      "Chatbot interface and conversation handling",
      "Google Sheets CRM integration",
      "Lead ingestion and processing",
      "Automatic quote generation",
      "Dashboard for monitoring and analytics"
    ],
    "keywords": ["chatbot", "chat", "crm", "sheets", "lead", "quote", "dashboard", "ingest"]
  },
  "repositories": [
    {
      "name": "<repo_name>",
      "owner": "matiasportugau-ui",
      "url": "<github_url>",
      "default_branch": "<branch_name>",
      "branches": ["<branch1>", "<branch2>"],
      "workflows": ["<workflow1>", "<workflow2>"],
      "open_prs": 0,
      "recent_prs": 0
    }
  ],
  "modules": [
    {
      "repo": "<repository_name>",
      "branch": "<branch_name>",
      "path": "<relative_path>",
      "name": "<module_name>",
      "type": "UI|Service|Domain|Store|Integration|Hook|Utility|Workflow|Other",
      "description": "<purpose and function>",
      "relevance": "High|Medium|Low|None",
      "justification": "<why relevant to system>",
      "action": "integrate|refactor|document|review|discard",
      "related_prs": [<pr_number>],
      "notes": "<uncertainties or #ZonaDesconocida>"
    }
  ],
  "workflows": [
    {
      "repo": "<repository_name>",
      "name": "<workflow_name>",
      "file": ".github/workflows/<file>.yml",
      "triggers": ["push", "pull_request"],
      "purpose": "<description>",
      "relevance": "High|Medium|Low|None",
      "status": "active|inactive"
    }
  ],
  "pull_requests": [
    {
      "repo": "<repository_name>",
      "number": <pr_number>,
      "title": "<pr_title>",
      "state": "open|closed|merged",
      "branch": "<source_branch>",
      "files_changed": [<file_paths>],
      "modules_affected": [<module_names>],
      "relevance": "High|Medium|Low|None",
      "recommendation": "merge|review|update|close"
    }
  ],
  "global_report": {
    "total_modules": 0,
    "relevant_modules": 0,
    "total_repositories": 0,
    "total_branches": 0,
    "total_workflows": 0,
    "total_prs": 0,
    "by_type": {
      "UI": 0,
      "Service": 0,
      "Domain": 0,
      "Store": 0,
      "Integration": 0,
      "Hook": 0,
      "Utility": 0,
      "Workflow": 0,
      "Other": 0
    },
    "by_repo": {},
    "by_branch": {},
    "functional_gaps": [],
    "integration_opportunities": [
      {
        "module": "<repo.path.module>",
        "reason": "<explanation>",
        "recommendation": "<action>"
      }
    ],
    "risks": [
      {
        "type": "accessibility|technical_debt|ambiguity|dependencies|security|branch_management",
        "severity": "High|Medium|Low",
        "detail": "<description>",
        "affected_modules": []
      }
    ]
  }
}
```

## Risk Signals

- 🟢 **Green**: Clear structure, coherent naming, well-separated modules, good documentation, active CI/CD
- 🟡 **Yellow**: Ambiguous naming, mixed concerns, potential duplicates, missing docs, stale branches
- 🔴 **Red**: Inaccessible repos, circular dependencies, obsolete code, security issues, merge conflicts

## Success Criteria

1. **Scan Completeness**: All accessible repositories and branches explored
2. **Module Map Clarity**: Clear classification and description of all modules
3. **System Alignment**: Accurate relevance scoring for target system
4. **Actionable Insights**: Clear recommendations for each module, PR, and workflow
5. **Risk Identification**: All risks documented with severity
6. **GitHub Integration**: All repos, branches, actions, and PRs discovered and analyzed

## Next Steps After Analysis

1. Review modules tagged `#ZonaDesconocida` manually
2. Prioritize integration opportunities
3. Review and merge relevant open PRs
4. Consolidate or update GitHub Actions workflows
5. Create technical roadmap based on findings
6. Address high-severity risks first
7. Document system architecture based on module map
8. Clean up stale branches and resolve conflicts

## Security Note

GitHub Personal Access Token provided. Token will be:
- Used only for API authentication during analysis
- Stored securely in environment variables (not in files)
- Never committed to version control
- Revoked after analysis if needed

