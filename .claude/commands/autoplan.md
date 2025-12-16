---
description: "Generate automated development plan for next phase with milestones, validation, and cost estimates"
---

# Automated Development Plan

Create a detailed implementation plan for the next development phase.

## What This Command Does

1. **Analyze current state:**
   - Read CLAUDE.md for project memory
   - Check completed phases
   - Identify next phase requirements

2. **Generate plan with:**
   - **Milestones:** Broken into 5-10 tasks
   - **Validation criteria:** Clear success metrics
   - **Token estimates:** Per milestone and total
   - **Cost estimates:** Economical/Balanced/Exhaustive
   - **Dependencies:** Blockers and prerequisites
   - **Risk assessment:** Potential issues and mitigations

3. **Output format:**
   ```
   Phase X: [Name]
   Estimated: X,XXX-X,XXX tokens | $X.XX-$X.XX USD

   Milestone 1: [Name] (X%)
   - Tasks: ...
   - Validation: ...
   - Tokens: X,XXX

   [Repeat for all milestones]

   Dependencies: ...
   Validation Criteria: ...
   Risks: ...
   ```

## Usage

Just say:
- "autoplan phase 6"
- "create automated plan for next phase"
- Or use this slash command

## Example Output

**Phase 6: CRM API & Google Sheets Integration**
- Milestone 1: Quote API Endpoints (30% - 5k tokens)
- Milestone 2: React Query Integration (20% - 4k tokens)
- Milestone 3: Quote Creation UI (25% - 6k tokens)
- Milestone 4: Quote Detail Modal (15% - 3k tokens)
- Milestone 5: Google Sheets Sync (10% - 7k tokens)

Total: 15k-25k tokens | $0.15-$0.25 USD (balanced)

**Benefits:**
- Clear roadmap before starting
- Cost predictability
- Measurable progress
- Risk mitigation upfront
