# 📋 Prompt Template for Complete Workspace Mapping

Use this prompt to generate a comprehensive, 100% complete workspace mapping for any project.

---

## 🎯 Main Prompt (Complete Evaluation)

```
Generate a comprehensive workspace mapping document that provides 100% complete evaluation:

1. **Maps ALL files** in the workspace (no exceptions)
2. **Groups files into logical modules** based on functionality and architecture
3. **Determines the functionality** of each file with detailed descriptions
4. **Shows complete integration status** - how files are connected or not connected
5. **Creates visual status** showing where we are in the project
6. **Includes all API endpoints** with methods, functionality, and dependencies
7. **Documents all database collections** with schemas and purposes
8. **Maps all dependencies** between files and modules
9. **Identifies entry points** for production, development, and testing
10. **Provides actionable recommendations** prioritized by importance

The output should include:

### Structure:
- Executive Summary (tech stack, purpose, overview, file count)
- Complete Module Organization (grouped by functionality)
  - For each module:
    - Complete file listing with functionality description
    - Integration status (Active/Partial/Legacy/Unused)
    - Dependencies and relationships
    - Critical files highlighted
- Complete Integration Map (visual diagrams showing how modules connect)
- Database Architecture (all collections, schemas, relationships)
- API Endpoints Complete List (all routes, methods, functionality)
- Module Status Summary (table with status indicators)
- Key Entry Points (main files to start/run the system)
- Complete File Dependencies (critical dependency chains)
- Integration Status by Feature (feature-level integration matrix)
- Recommendations (prioritized improvements)
- File Count Summary (statistics)

### Format:
- Use tables for file listings
- Use ASCII diagrams for visual representations
- Use status indicators (✅ ⚠️ ❌) for quick scanning
- Include file paths and brief descriptions
- Show integration relationships clearly
- Highlight critical files with ⭐
- Use color coding (🔴 🟡 🟢) for priority/status

### Visual Elements:
- Architecture diagrams (complete system)
- Data flow diagrams (end-to-end)
- Module dependency graphs
- Integration status matrices
- Database schema diagrams
- API endpoint tree
- Docker services diagram

Generate this as a markdown document that serves as both a reference guide and a visual map of the entire codebase. Ensure 100% coverage - no file should be unaccounted for.
```

---

## 🔍 Enhanced Prompt (Deep Analysis)

```
Create a comprehensive workspace mapping and architecture analysis document that provides:

### 1. Complete File Inventory
- List ALL files in the workspace (including hidden, config, data files)
- Categorize by type (code, config, docs, data, scripts, tests)
- Identify duplicates or similar files
- Note file sizes and complexity indicators
- Mark files as: Core, Active, Partial, Legacy, Unused

### 2. Module Identification
- Group files into logical modules (e.g., Frontend, Backend, API, Database, Tests)
- For each module:
  - Purpose and responsibility
  - Key files and their roles (mark with ⭐)
  - Entry points and exit points
  - Dependencies (what it needs)
  - Dependents (what depends on it)
  - Integration level (High/Medium/Low)

### 3. Functionality Analysis
- For each significant file:
  - What it does (primary function)
  - What it depends on (dependencies)
  - What depends on it (dependents)
  - Integration level (Core/Active/Partial/Legacy/Unused)
  - Last modified date (if available)
  - Test coverage (if available)
  - Criticality (Critical/Important/Normal/Low)

### 4. Integration Mapping
- Create visual diagrams showing:
  - How modules interact
  - Data flow between components
  - API contracts and interfaces
  - External dependencies
  - Integration points with third-party services
  - Database relationships
  - Service dependencies

### 5. Status Assessment
- Current state of each module:
  - ✅ Active and integrated
  - 🟡 Partially integrated
  - ⚠️ Legacy but functional
  - ❌ Unused or deprecated
- Health indicators:
  - Code quality signals
  - Documentation completeness
  - Test coverage
  - Maintenance status
  - Update frequency

### 6. API Endpoints Complete Documentation
- List ALL API endpoints:
  - Route path
  - HTTP methods (GET, POST, PUT, DELETE, etc.)
  - Functionality description
  - Request/response schemas
  - Dependencies
  - Integration status
  - Usage examples

### 7. Database Architecture
- All collections/tables:
  - Collection name
  - Purpose
  - Schema/structure
  - Relationships
  - Indexes
  - Integration status

### 8. Visual Representations
- System architecture diagram (complete)
- Module dependency graph (all modules)
- Data flow diagram (end-to-end)
- Integration status matrix (all features)
- File organization tree (complete structure)
- Quick reference tables
- API endpoint tree
- Database schema diagram

### 9. Actionable Insights
- Identify:
  - Dead code or unused files
  - Duplicate functionality
  - Missing integrations
  - Broken dependencies
  - Documentation gaps
  - Security concerns
  - Performance bottlenecks
- Provide recommendations:
  - High priority fixes (this week)
  - Medium priority improvements (this month)
  - Low priority cleanup (this quarter)
  - Future enhancements (this year)

### 10. Quick Reference
- Entry points for common tasks
- File location guide (where to find X)
- Dependency lookup (what needs Y)
- Integration checklist (what connects to Z)
- API endpoint quick reference
- Database collection quick reference

Format the output as a well-structured markdown document with:
- Clear section headers
- Tables for structured data
- ASCII diagrams for visual elements
- Status indicators for quick scanning
- Cross-references between sections
- Index or table of contents
- File count statistics
```

---

## 🎨 Visual-Focused Prompt

```
Generate a visual workspace map that shows:

1. **Complete Architecture Diagram**
   - High-level system architecture (all components)
   - Component relationships (all connections)
   - Data flow directions (complete paths)
   - Integration points (all external services)
   - Service ports and protocols

2. **Module Dependency Graph**
   - Which modules depend on which (all dependencies)
   - Dependency direction (arrows)
   - Critical paths highlighted
   - Circular dependency warnings
   - Dependency depth visualization

3. **File Organization Tree**
   - Complete directory structure
   - File counts per directory
   - Module boundaries (clear separation)
   - Key files highlighted (⭐)
   - File types color-coded

4. **Integration Status Dashboard**
   - Visual status indicators (all features)
   - Integration completeness (percentage)
   - Health metrics (all services)
   - Warning flags (all issues)
   - Priority indicators

5. **Data Flow Map**
   - How data moves through the system (complete flow)
   - Transformation points (all transformations)
   - Storage locations (all databases/files)
   - External integrations (all APIs)
   - Backup and recovery paths

6. **API Endpoint Tree**
   - All endpoints organized by category
   - Methods for each endpoint
   - Dependencies for each endpoint
   - Integration status

7. **Database Schema Diagram**
   - All collections/tables
   - Relationships between collections
   - Indexes and constraints
   - Data flow between collections

Use ASCII art, Unicode symbols, and color coding (via markdown) to make it visually clear and scannable. Ensure 100% coverage of all components.
```

---

## 📊 Analysis-Focused Prompt

```
Perform a deep analysis of the workspace and generate:

1. **Codebase Health Report**
   - File count and distribution (complete statistics)
   - Code vs documentation ratio
   - Configuration complexity
   - Test coverage assessment
   - Code quality metrics
   - Technical debt indicators

2. **Integration Analysis**
   - Integration completeness score (percentage)
   - Missing integration points (all gaps)
   - Redundant integrations (all duplicates)
   - Integration quality metrics
   - Integration health status

3. **Architecture Assessment**
   - Adherence to patterns (all patterns)
   - Separation of concerns (all modules)
   - Coupling analysis (all dependencies)
   - Cohesion metrics (all modules)
   - Scalability assessment

4. **Maintenance Status**
   - Active vs legacy code ratio
   - Documentation completeness (all files)
   - Update frequency indicators (all files)
   - Abandoned components (all unused)
   - Maintenance priority

5. **Risk Assessment**
   - Single points of failure (all identified)
   - Unused dependencies (all listed)
   - Security concerns (all issues)
   - Technical debt indicators (all debt)
   - Performance bottlenecks (all identified)

6. **Improvement Roadmap**
   - Immediate actions (this week) - prioritized
   - Short-term improvements (this month) - prioritized
   - Long-term refactoring (this quarter) - prioritized
   - Strategic enhancements (this year) - prioritized

7. **Statistics Summary**
   - Total files by type
   - Total files by module
   - Total API endpoints
   - Total database collections
   - Total dependencies
   - Integration coverage percentage
```

---

## 🚀 Quick Mapping Prompt (Simplified)

```
Create a quick workspace map that shows:

1. **File List by Module** (table format)
   - Module name
   - Files in module (complete list)
   - Status (Active/Legacy/Unused)
   - Key functionality (brief)
   - Critical files (⭐)

2. **Integration Status** (matrix format)
   - Module names as rows/columns
   - Integration indicators in cells
   - Status legend
   - Integration strength

3. **Entry Points** (list)
   - Main files to start the system
   - Development entry points
   - Testing entry points
   - Production entry points

4. **Quick Reference** (table)
   - "I need to modify X" → "Go to file Y"
   - Common tasks and file locations
   - API endpoints by category
   - Database collections by purpose

Keep it concise but comprehensive enough to navigate the codebase quickly. Include file counts and statistics.
```

---

## 💡 Usage Tips

1. **Start with the main prompt** to get a comprehensive overview
2. **Use enhanced prompt** if you need deeper analysis
3. **Use visual-focused prompt** for presentations or documentation
4. **Use analysis-focused prompt** for code reviews or audits
5. **Use quick mapping prompt** for rapid onboarding

### Customization:
- Add project-specific requirements
- Include technology stack details
- Specify output format preferences
- Request specific diagrams or analyses
- Request statistics and metrics

### Example Customization:
```
[Use main prompt] + 
"Focus on Python backend modules" +
"Include code complexity metrics" +
"Show API endpoint mapping" +
"Highlight security-related files" +
"Include all database collections" +
"Show complete dependency graph"
```

---

## 📝 Output Format Template

The generated document should follow this structure:

```markdown
# Complete Workspace Mapping

## Executive Summary
[Overview, tech stack, purpose, file count, statistics]

## Complete Module Organization
### Module 1: [Name]
[Complete file table with functionality, status, dependencies, criticality]

### Module 2: [Name]
[Complete file table with functionality, status, dependencies, criticality]

## Database Architecture
[All collections, schemas, relationships, indexes]

## API Endpoints Complete List
[All routes, methods, functionality, dependencies, integration status]

## Complete Integration Map
[Visual diagrams - architecture, data flow, dependencies]

## Module Status Summary
[Tables and matrices with complete status]

## Complete File Dependencies
[All dependency chains, critical paths]

## Integration Status by Feature
[Complete feature matrix with all integrations]

## Recommendations
[Prioritized actions - High/Medium/Low]

## File Count Summary
[Statistics - total files, by type, by module, by status]
```

---

## ✅ Completeness Checklist

When generating the mapping, ensure:

- [ ] All files are listed (no file left behind)
- [ ] All modules are documented
- [ ] All API endpoints are listed
- [ ] All database collections are documented
- [ ] All dependencies are mapped
- [ ] All integration points are identified
- [ ] All entry points are documented
- [ ] All critical files are highlighted
- [ ] All status indicators are accurate
- [ ] All visual diagrams are complete
- [ ] All recommendations are prioritized
- [ ] Statistics are accurate and complete

---

**Note:** Adjust the prompt based on:
- Project size (smaller projects need less detail, but still 100% coverage)
- Team needs (developers vs managers need different views)
- Purpose (onboarding vs audit vs refactoring)
- Time available (quick scan vs deep dive - but always complete)

**Key Principle:** Always aim for 100% file coverage, even if some files get less detail. Every file should be accounted for in the mapping.

