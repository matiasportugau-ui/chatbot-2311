# Monitoreo y Persistencia Opcional

## 1. Persistencia con MongoDB

1. Levanta Mongo localmente (Docker recomendado):
   ```bash
   docker run -d --name bmc-mongodb -p 27017:27017 mongo:6
   ```
2. Actualiza `.env` o `config_conocimiento.json`:
   ```
   MONGODB_URI=mongodb://localhost:27017/bmc_chat
   ```
3. Vuelve a ejecutar `bash scripts/run_full_stack.sh` para que, si faltan archivos JSON, el bot recurra al fallback Mongo.

## 2. Automatizar refresco del conocimiento

1. Edita el cron de tu usuario:
   ```bash
   crontab -e
   ```
2. Programa el refresco nocturno (ejemplo a las 03:00):
   ```
   0 3 * * * cd /Users/matias/chatbot2511/chatbot-2311 && bash scripts/refresh_knowledge.sh >> logs/automation/cron_refresh.log 2>&1
   ```

## 3. Supervisión del API Server

- **macOS launchd**:
  - Crea `~/Library/LaunchAgents/com.bmc.chatbot.plist` que ejecute `scripts/run_full_stack.sh`.
  - Carga el servicio: `launchctl load ~/Library/LaunchAgents/com.bmc.chatbot.plist`.

- **Linux systemd**:
  - Crea `/etc/systemd/system/bmc-chatbot.service` con:
    ```
    [Service]
    WorkingDirectory=/Users/matias/chatbot2511/chatbot-2311
    ExecStart=/bin/bash scripts/run_full_stack.sh
    Restart=on-failure
    Environment="OPENAI_API_KEY=..."
    ```
  - Habilita: `sudo systemctl enable --now bmc-chatbot`.

## 4. Revisión de logs

- Los wrappers nuevos escriben en `logs/automation/`.
- Usa `tail -f logs/automation/run_*.log` para ver el estado en vivo.

## 5. Variables de entorno para ingesta y persistencia

- Define las credenciales de Mercado Libre en `.env` usando el nuevo flujo OAuth:
  - `MERCADO_LIBRE_APP_ID`, `MERCADO_LIBRE_CLIENT_SECRET`
  - `MERCADO_LIBRE_REDIRECT_URI` (debe coincidir con la app registrada)
  - `MERCADO_LIBRE_SELLER_ID` y `MERCADO_LIBRE_WEBHOOK_SECRET`
  - `MERCADO_LIBRE_SCOPES` y `MERCADO_LIBRE_PKCE_ENABLED` para ajustar permisos y seguridad.
  - Usa `npm run test` (ejecuta `test-mercado-libre.js`) para verificar que los endpoints de salud, listados y órdenes respondan antes de producción.
- Revisa los tokens persistidos en Mongo (`mercado_libre_grants`) si notas errores `invalid_grant`. El webhook `/api/mercado-libre/webhook` guardará eventos recientes en `mercado_libre_webhook_events` para diagnósticos.
- Controla la sincronización de Shopify con:
  - `SHOPIFY_PAGE_SIZE` (lote por request).
  - `SHOPIFY_SYNC_MAX_AGE_MINUTES` (se reutiliza el JSON si no superó ese tiempo).
  - `SHOPIFY_FORCE_SYNC=true` para ignorar el cache en ejecuciones puntuales.
- Mantén `MONGODB_URI` apuntando a tu instancia (local o externa). Si el archivo JSON no está disponible, el bot usará MongoDB como respaldo al iniciar `scripts/run_full_stack.sh`.


## 6. Ingestión automatizada de conocimiento

- `scripts/refresh_knowledge.sh` ejecuta los sincronizadores de Shopify y Mercado Libre antes de consolidar.
- Controla cada ingestor con variables de entorno:
  - `RUN_SHOPIFY_SYNC` (default `true`)
  - `RUN_MELI_SYNC` (default `true`, requiere la integración OAuth activa y tokens válidos en Mongo)
- Revisa [DATA_INGESTION.md](DATA_INGESTION.md) para formatos, logs y pasos manuales.
