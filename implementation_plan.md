# Implementation Plan: Unified Vercel Environment File

## Objective

Create a single, comprehensive `vercel-env-template.txt` that includes **all** environment variables, API keys, and tokens referenced across the codebase, validate their presence, and prune any that are unused or non‑functional.

## Steps

1. **Discover Variables**
   - Use `grep` to find patterns `process.env.*`, `os.getenv(`, and literal `*_KEY`, `*_TOKEN`, `*_SECRET` in the entire monorepo (`/Users/matias/chatbot2511`).
   - Collect variable names and the files where they appear.
2. **Aggregate & De‑duplicate**
   - Merge results into a unique list, preserving ordering (frontend first, then backend).
3. **Generate Preliminary Template**
   - Write each variable as `NAME=` (empty placeholder) with a comment indicating its source file(s).
4. **Validate Functionality**
   - Run a lightweight Node script that loads the generated file via `dotenv` and attempts to import modules that depend on each variable.
   - Capture any errors (missing required values) and mark those variables as _required_.
   - For Python, run a short script that imports `config.py` and checks `os.getenv` usage.
5. **Prune Non‑working Variables**
   - Remove entries that cause runtime errors when left empty (e.g., mandatory API keys).
   - Keep optional variables with a comment `# optional`.
6. **Finalize `vercel-env-template.txt`**
   - Replace the existing file with the cleaned list.
   - Add a header explaining the purpose and the Vercel System Variables tip.
7. **Verification**
   - Execute `node prepare-vercel.js` to ensure the deploy guide reflects the new template.
   - Run the project's test suite (`npm test` and any Python tests) to confirm no missing env vars.

## Deliverables

- Updated `vercel-env-template.txt` (final unified env file).
- Short report (`env-generation-report.md`) summarizing discovered variables, removed ones, and any manual values the user must fill.

## Timeline

- Discovery & aggregation: ~1 min.
- Validation scripts: ~2 min.
- Generation & verification: ~1 min.

**Next Action:** Await user approval to execute the plan.
