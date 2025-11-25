## n8n Workflow Alignment Review

| Workflow / Client Call | Expected Endpoint | In-Repo Source | Current Status |
| --- | --- | --- | --- |
| Chat webhook (`sendChatMessage`) | `POST ${N8N_BASE_URL}/webhook/chat` | `n8n-client.ts` lines 68-93 | ✅ Matches the documented chat workflow in `n8n_workflows/workflow-chat.json`. Requires n8n to forward the payload to either FastAPI (`/chat/process`) or the Next route (`/api/chat`). |
| WhatsApp webhook (`processWhatsAppMessage`) | `POST ${N8N_BASE_URL}/webhook/whatsapp` | `n8n-client.ts` lines 101-142 | ✅ Mirrors the webhook handled locally by `src/app/api/whatsapp/webhook/route.ts`. Ensure the WhatsApp Business credentials (`WHATSAPP_*`) are set either in n8n or Next; both expect the same structure. |
| Sheets sync (`syncSheetRow`) | `POST ${N8N_BASE_URL}/webhook/sheets-sync` | `n8n-client.ts` lines 144-172 | ✅ Matches `n8n_workflows/workflow-sheets-sync.json`. Locally, the equivalent functionality resides in `src/app/api/sheets/enhanced-sync/route.ts`. |
| Analytics / Insights (`getInsights`, `getConversions`) | `POST ${N8N_BASE_URL}/webhook/analytics` | `n8n-client.ts` lines 175-233 | ✅ n8n workflow handles `action: obtener_insights` / `analisis_conversiones`. Our FastAPI `/insights` endpoint offers the same data when running without n8n. |

### Notes
- All client helpers point to configurable `N8N_BASE_URL` / `N8N_API_KEY`. No repo changes required beyond setting those env vars.
- Local fallbacks exist for each workflow (FastAPI + Next API routes), which means development can proceed even if n8n is offline.
- When deploying, ensure that n8n forwards webhook payloads to the Python engine or use the Node quoting engine directly through `/api/integrated-quote`.

This review confirms that every documented n8n workflow has a matching handler or fallback in the codebase. No endpoint mismatches were found.***
