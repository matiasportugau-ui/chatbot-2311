# User Test Plan

## 1. Overview

This document outlines the user testing strategy for the BMC Chatbot ecosystem, covering the Shopify App, Mercado Libre integration, and the Simulator/Dashboard components.

## 2. Test Environments

| Component             | Path                                      | Status                          |
| --------------------- | ----------------------------------------- | ------------------------------- |
| **Shopify App**       | `2026_Mono_rep/apps/shopify-app`          | Ready for UI/Functional testing |
| **Mercado Libre Bot** | `chatbot-2311` (Next.js) + Python Backend | Partial (OAuth pending)         |
| **Simulator**         | `chatbot-2311/src/app/simulator`          | Ready (Requires backend)        |
| **Dashboard**         | `chatbot-2311/src/components/dashboard`   | UI Ready (Export/Import mocked) |

## 3. Test Scenarios

### 3.1 Mercado Libre Integration

- [ ] **OAuth Flow**:
  - Generate Auth URL.
  - **Action**: Click the link, authorize with a test ML account.
  - **Expected**: Redirect to app with valid token exchange.
- [ ] **Automated Answers**:
  - Run `npm run mercado-auto` (or Python equivalent).
  - **Expected**: System fetches unanswered questions, generates drafts, and (if live mode) answers them.
  - **Validation**: Check `MERCADO_LIBRE_DRAFT_ANSWERS.md` or logs.

### 3.2 Shopify App

- [ ] **Dashboard Access**:
  - Load `app._index.tsx`.
  - **Expected**: View stats, recent activity.
- [ ] **Character Creator**:
  - Route: `/app/character`
  - **Action**: Generate a new avatar/persona.
  - **Expected**: AI generates image, saves to Shopify Files/Metafields.
- [ ] **Training Center**:
  - Route: `/app/training`
  - **Action**: Upload a PDF or text snippet.
  - **Expected**: Knowledge base updates (Vector DB ingestion).
- [ ] **Chat Widget**:
  - **Action**: Interact with chat bubble on storefront.
  - **Expected**: Responses match the configured persona.

### 3.3 Simulator & Dashboard

- [ ] **Simulator**:
  - **Action**: Send "Hola, tienen stock?"
  - **Expected**: Bot replies with context-aware answer from inventory.
- [ ] **Export/Import**:
  - **Action**: Click "Export CSV".
  - **Expected**: Visual feedback (Success toast). _Note: Logic is currently mocked._

## 4. Execution Steps

1.  Start Backend Services (Python/Node).
2.  Start Frontend Apps (Remix/Next.js).
3.  Perform manual walkthrough of Scenarios 3.1 - 3.3.
4.  Log defects in `defect_log.md` (to be created).

## 5. Current Gaps

- Mercado Libre OAuth flow needs completion (Token exchange logic).
- Export/Import is mocked (needs backend hookup).
- Simulator requires running Python backend (`http://localhost:8000`).
