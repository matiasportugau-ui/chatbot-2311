# Implementation Plan: Vercel System Environment Variables Integration

This plan outlines the steps to leverage Vercel's System Environment Variables in the BMC Chatbot project, improving deployment flexibility and automation.

## Objectives

1.  **Simplify URL Management**: Use `VERCEL_URL` and `VERCEL_ENV` to automatically determine the application's base URL and environment.
2.  **Enhance Deployment Experience**: Update documentation and preparation scripts to include the "Automatically expose System Environment Variables" feature.
3.  **Improve Reliability**: Reduce manual configuration of `NEXT_PUBLIC_APP_URL` and related redirection URIs.

## Proposed Changes

### 1. Update `prepare-vercel.js`

- Modify `createEnvTemplate()` to include instructions about enabling the "Automatically expose System Environment Variables" feature in Vercel settings.
- Update the template to suggest using `NEXT_PUBLIC_VERCEL_URL` as a fallback.

### 2. Update `VERCEL_DEPLOY_GUIDE.md`

- Add a section about Vercel System Environment Variables.
- Include a screenshot-like description of where to find the setting in Vercel Dashboard.

### 3. Update `src/lib/credentials-manager.ts`

- Modify `loadFromEnvironment()` to dynamically set the environment based on `VERCEL_ENV`.
- Add support for `NEXT_PUBLIC_VERCEL_URL` if `NEXT_PUBLIC_APP_URL` is missing.

### 4. Update `config.py` (Python)

- Detect if running on Vercel or similar (via `VERCEL` env var).
- Use `VERCEL_URL` to set `base_url` if applicable.

## Verification Plan

1.  Run `node prepare-vercel.js` and verify output files.
2.  Perform a test build locally setting `VERCEL=1` and `VERCEL_URL=test.vercel.app` to see if logic picks it up.
3.  Ensure no regressions in existing environment variable loading.

## User Notification Required

- [ ] Notify user about the new "Automatically expose System Environment Variables" setting requirement in Vercel.
