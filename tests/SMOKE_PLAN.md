## Smoke Test Plan

### Node / Next.js Stack
1. **Integrated Quote API**
   - `POST /api/integrated-quote` with `action=process`, sample consultation text, and a phone.
   - Expect `success: true`, populated `respuesta`, and a session id.  
   - Negative case: omit `consulta` → expect `400` with error message.
2. **Quote Engine API**
   - `POST /api/quote-engine` with `consulta` referencing a known product.  
   - Verify response `tipo === 'cotizacion'` and `cotizacion.total` > 0.
3. **Quote Parser API**
   - `POST /api/parse-quote` with realistic text; ensure `data.parsed.estado_info` reflects missing info.  
   - `GET /api/parse-quote?text=foo` should return `isValid: false`.
4. **Sheets Sync**
   - `GET /api/sheets/enhanced-sync?action=statistics` (stub credentials if needed).  
   - Expect summary payload or graceful degradation message when Google creds are absent.
5. **WhatsApp Webhook**
   - `POST /api/whatsapp/webhook` with a minimal mock message; verify `200` and log entry.
6. **UI Spot Checks**
   - `npm run dev` then load `/`, `/chat`, `/bmc-chat`, `/simulator`.  
   - Send a message through Chat + BMC Chat; confirm network calls succeed.

### Python / FastAPI Stack
1. **API Server Health**
   - `python api_server.py` and `curl http://localhost:8000/health` → expect `"status": "healthy"`.
2. **/chat/process**
   - `curl -X POST http://localhost:8000/chat/process -d '{"mensaje":"Hola","telefono":"+598..."}'`.  
   - Validate JSON schema: `tipo`, `confianza`, `sesion_id`.
3. **/quote/create**
   - Post sample client/spec payload; ensure response contains `id`, `precio_total`, and ISO timestamp.
4. **Insights Endpoint**
   - `GET /insights` after running a few simulated chats to ensure non-empty data.
5. **Simulator CLI**
   - `python simulate_chat_cli.py`, issue `/stats`, `/export`, and a few conversational turns.  
   - Confirm MongoDB warnings are harmless when DB is offline.
6. **run_simulation.sh**
   - Execute `./run_simulation.sh` to validate the one-click flow.  
   - Expected outcome: dependency check → env setup → verification report → chatbot launch.

Run the Node and Python suites independently whenever credentials change, and run both before cutting a release.***
