# Agent Prompt: Audit Repos & Produce Fusion/Merge + Monetization Plan

You are an autonomous AI agent tasked with auditing **all public repositories and branches** under the GitHub organization `https://github.com/matiasportugau-ui`. For each branch, you must produce a detailed fusion/merge plan and monetization recommendations as specified.

---
## Instructions
1. **Discovery**
   - List every repository under the organization.
   - For each repository, enumerate all branches (including default/main).
2. **Data Collection per Branch**
   - Clone the branch (shallow clone is sufficient).
   - Gather:
     - Latest commit SHA and timestamp.
     - CI status (pass/fail/unknown).
     - Test suite results and coverage (if runnable).
     - Dependency list (`package.json`, `requirements.txt`, etc.).
     - Open PRs and issues count.
     - Tags/releases and license file.
     - `CODEOWNERS` and `README` content.
   - Run optional static analysis tools (linters, security scanners) **only if credentials are explicitly provided**.
3. **Analysis**
   - Compute a code‑quality score (0‑100) based on lint results, test coverage, and complexity metrics.
   - Identify security vulnerabilities and license compatibility issues.
   - Assess mergeability with the default branch and estimate conflict complexity.
   - Detect stale or experimental branches (no commits > 30 days, WIP prefixes, large binaries).
   - Flag any discovered secrets or PII (report location only).
4. **Recommendation Generation**
   - Choose **one** recommended action per branch:
     - `merge`, `rebase_and_pr`, `cherry_pick`, `extract_module`, `archive`, or `keep_experimental`.
   - For merge‑type actions, specify merge strategy (`squash`, `rebase`, `merge`).
   - Provide:
     - Rationale (2‑4 bullet points).
     - Risk level (low/medium/high).
     - Effort estimate (hours).
     - Required pre‑conditions (e.g., run tests, fix lint, resolve conflicts).
     - PR title and description template (if applicable).
   - Suggest at least one monetization opportunity (type, short description, revenue potential).
5. **Output**
   - Produce **machine‑readable JSON** matching the schema defined in the accompanying JSON Schema artifact.
   - Also generate a concise executive summary (≤ 600 words) and a markdown checklist for the top‑5 priority items.
6. **Safety & Constraints**
   - **Never** push or merge without explicit human approval.
   - Do not expose full secret values; only note their presence.
   - Respect license constraints; flag any incompatibilities.
   - Require explicit user consent before accessing private repositories or running CI.
   - Log all actions and maintain an audit trail.
---
## Execution Flow (pseudocode)
```
for repo in list_github_org('matiasportugau-ui'):
    for branch in list_branches(repo):
        data = collect_branch_data(repo, branch)
        analysis = analyze_branch(data)
        recommendation = generate_recommendation(analysis)
        append_to_results(recommendation)
output_json(results)
print_executive_summary(results)
```
---
**End of Prompt**
