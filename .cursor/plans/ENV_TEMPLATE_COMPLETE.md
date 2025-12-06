# 🔑 Template para Completar Variables de Entorno

Completa este template con tus claves reales. Cada sección incluye instrucciones de dónde obtener cada valor.

## 📋 Instrucciones

1. Copia este template a un archivo `.env` en la raíz del proyecto
2. Reemplaza cada `your-...` o placeholder con tu valor real
3. Guarda el archivo como `.env` (no lo subas a Git)

---

## 🌐 API Configuration

```bash
# URLs de tus servicios locales o de producción
NEXT_PUBLIC_API_URL=http://localhost:3001/api
# O en producción: https://tu-dominio.com/api

NEXT_PUBLIC_WS_URL=ws://localhost:3001/ws
# O en producción: wss://tu-dominio.com/ws

PY_CHAT_SERVICE_URL=http://localhost:8000
# O en producción: https://tu-servicio-python.com
```

**Dónde obtener:**
- `NEXT_PUBLIC_API_URL`: URL de tu API Next.js
- `NEXT_PUBLIC_WS_URL`: URL del WebSocket server
- `PY_CHAT_SERVICE_URL`: URL de tu servicio Python de chat

---

## 🔐 Authentication

```bash
NEXTAUTH_URL=http://localhost:3000
# O en producción: https://tu-dominio.com

NEXTAUTH_SECRET=GENERA_UNA_CLAVE_SECRETA_AQUI
```

**Dónde obtener:**
- `NEXTAUTH_URL`: URL base de tu aplicación
- `NEXTAUTH_SECRET`: Genera una clave secreta con:
  ```bash
  openssl rand -base64 32
  ```

---

## 💾 Database

```bash
DATABASE_URL=postgresql://usuario:password@localhost:5432/bmc_dashboard
# Formato: postgresql://usuario:password@host:puerto/database

MONGODB_URI=mongodb://localhost:27017/bmc_chat
# O MongoDB Atlas: mongodb+srv://usuario:password@cluster.mongodb.net/database
```

**Dónde obtener:**
- `DATABASE_URL`: Credenciales de PostgreSQL (local o servicio cloud)
- `MONGODB_URI`: URI de conexión a MongoDB (local o MongoDB Atlas)

---

## 📱 WhatsApp Configuration

```bash
WHATSAPP_VERIFY_TOKEN=TU_TOKEN_DE_VERIFICACION_AQUI
WHATSAPP_ACCESS_TOKEN=TU_ACCESS_TOKEN_AQUI
WHATSAPP_PHONE_NUMBER_ID=TU_PHONE_NUMBER_ID_AQUI
WHATSAPP_BUSINESS_ID=TU_BUSINESS_ID_AQUI
WHATSAPP_APP_SECRET=TU_APP_SECRET_AQUI
N8N_WEBHOOK_URL_EXTERNAL=http://localhost:5678/webhook/whatsapp
```

**Dónde obtener:**
1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Crea una app de tipo "Business"
3. Agrega el producto "WhatsApp"
4. En "Getting Started" encontrarás:
   - `WHATSAPP_ACCESS_TOKEN`: Token temporal (cambia cada 24h) o permanente
   - `WHATSAPP_PHONE_NUMBER_ID`: ID del número de teléfono
   - `WHATSAPP_BUSINESS_ID`: ID de tu cuenta de negocio
   - `WHATSAPP_APP_SECRET`: En App Settings → Basic
   - `WHATSAPP_VERIFY_TOKEN`: Crea uno tú mismo (puede ser cualquier string)

---

## 🤖 OpenAI Configuration

```bash
OPENAI_API_KEY=sk-proj-TU_CLAVE_OPENAI_AQUI
OPENAI_MODEL=gpt-4o-mini
# Opciones: gpt-4o-mini, gpt-4o, gpt-4-turbo, gpt-3.5-turbo
```

**Dónde obtener:**
1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Inicia sesión o crea una cuenta
3. Ve a "API Keys" → "Create new secret key"
4. Copia la clave (empieza con `sk-`)
5. `OPENAI_MODEL`: Elige el modelo que quieras usar

---

## 🛒 Mercado Libre Configuration

```bash
# OAuth Credentials (obtener de https://developers.mercadolibre.com.ar/)
MERCADO_LIBRE_APP_ID=TU_APP_ID_AQUI
MERCADO_LIBRE_CLIENT_SECRET=TU_CLIENT_SECRET_AQUI
MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=TU_SELLER_ID_AQUI
MERCADO_LIBRE_WEBHOOK_SECRET=TU_WEBHOOK_SECRET_AQUI

# IMPORTANTE: MERCADO_LIBRE_AUTH_URL debe coincidir con la región donde registraste la app
# Argentina: https://auth.mercadolibre.com.ar
# México: https://auth.mercadolibre.com.mx
# Uruguay: https://auth.mercadolibre.com.uy
# Brasil: https://auth.mercadolibre.com.br
# Chile: https://auth.mercadolibre.com.cl
# Colombia: https://auth.mercadolibre.com.co
# Perú: https://auth.mercadolibre.com.pe
MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy
MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
MERCADO_LIBRE_SCOPES=offline_access read write
MERCADO_LIBRE_PKCE_ENABLED=true

# Tokens de acceso (se generan después de OAuth)
MELI_ACCESS_TOKEN=TU_ACCESS_TOKEN_AQUI
MELI_REFRESH_TOKEN=TU_REFRESH_TOKEN_AQUI
MELI_SELLER_ID=TU_SELLER_ID_AQUI
MELI_PAGE_SIZE=250
RUN_MELI_SYNC=true
```

**Dónde obtener:**
1. Ve a [Mercado Libre Developers](https://developers.mercadolibre.com.ar/)
2. Crea una aplicación
3. Obtén:
   - `MERCADO_LIBRE_APP_ID`: App ID de tu aplicación
   - `MERCADO_LIBRE_CLIENT_SECRET`: Client Secret
   - `MERCADO_LIBRE_SELLER_ID`: Tu ID de vendedor (se obtiene después de autenticar)
   - `MERCADO_LIBRE_WEBHOOK_SECRET`: Crea uno tú mismo para validar webhooks
4. Configura el redirect URI en tu app de ML
5. Los tokens `MELI_ACCESS_TOKEN` y `MELI_REFRESH_TOKEN` se generan automáticamente después de autenticar

---

## 📊 Knowledge Ingestion

```bash
SHOPIFY_PAGE_SIZE=250
RUN_SHOPIFY_SYNC=true
```

**Dónde obtener:**
- `SHOPIFY_PAGE_SIZE`: Tamaño de página para sincronización (ajusta según necesites)
- `RUN_SHOPIFY_SYNC`: `true` para activar sincronización automática

---

## 📈 External Services

```bash
GOOGLE_SHEETS_API_KEY=TU_GOOGLE_SHEETS_API_KEY_AQUI
```

**Dónde obtener:**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Habilita "Google Sheets API"
4. Ve a "Credentials" → "Create Credentials" → "API Key"
5. Copia la API Key

---

## 🔍 Monitoring

```bash
SENTRY_DSN=https://TU_DSN_AQUI@sentry.io/TU_PROJECT_ID
ANALYTICS_ID=TU_ANALYTICS_ID_AQUI
```

**Dónde obtener:**
- `SENTRY_DSN`: 
  1. Ve a [Sentry.io](https://sentry.io/)
  2. Crea un proyecto
  3. Copia el DSN de la configuración del proyecto
- `ANALYTICS_ID`: 
  - Google Analytics: GA_MEASUREMENT_ID (formato: G-XXXXXXXXXX)
  - O el ID de tu servicio de analytics

---

## 🎛️ Feature Flags

```bash
NEXT_PUBLIC_ENABLE_AI_INSIGHTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING=true
NEXT_PUBLIC_ENABLE_EXPORT_IMPORT=true
```

**Valores:**
- `true`: Habilita la funcionalidad
- `false`: Deshabilita la funcionalidad

---

## 🚀 XAI (Grok) Configuration

```bash
XAI_API_KEY=xai-TU_CLAVE_XAI_AQUI
XAI_MODEL=grok-4-latest,grok-beta
```

**Dónde obtener:**
1. Ve a [X.AI Console](https://console.x.ai/)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" → "Create API Key"
4. Copia la clave (empieza con `xai-`)
5. `XAI_MODEL`: Elige el modelo (grok-4-latest, grok-beta, etc.)

---

## 🔧 N8N Configuration

```bash
N8N_API_KEY=TU_N8N_API_KEY_AQUI
N8N_PUBLIC_KEY=TU_N8N_PUBLIC_KEY_AQUI
N8N_PRIVATE_KEY=TU_N8N_PRIVATE_KEY_AQUI
N8N_BASE_URL=http://localhost:5678
```

**Dónde obtener:**
1. Instala N8N o usa N8N Cloud
2. Ve a Settings → API
3. Genera las claves:
   - `N8N_API_KEY`: API Key para autenticación
   - `N8N_PUBLIC_KEY`: Clave pública (si usas encriptación)
   - `N8N_PRIVATE_KEY`: Clave privada (si usas encriptación)
4. `N8N_BASE_URL`: URL de tu instancia de N8N

---

## 🚀 Inicio Rápido

1. **Copia el template:**
   ```bash
   cp .env.example .env
   ```

2. **Genera NEXTAUTH_SECRET:**
   ```bash
   ./generate_env_secret.sh
   ```
   O manualmente:
   ```bash
   openssl rand -base64 32
   ```

3. **Edita `.env` y completa todos los placeholders con tus claves reales**

---

## 📝 Template Completo para Copiar

```bash
# Environment variables for the BMC Dashboard

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001/api
NEXT_PUBLIC_WS_URL=ws://localhost:3001/ws
PY_CHAT_SERVICE_URL=http://localhost:8000

# Authentication
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=GENERA_UNA_CLAVE_SECRETA_AQUI

# Database
DATABASE_URL=postgresql://usuario:password@localhost:5432/bmc_dashboard
MONGODB_URI=mongodb://localhost:27017/bmc_chat

# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=TU_TOKEN_DE_VERIFICACION_AQUI
WHATSAPP_ACCESS_TOKEN=TU_ACCESS_TOKEN_AQUI
WHATSAPP_PHONE_NUMBER_ID=TU_PHONE_NUMBER_ID_AQUI
WHATSAPP_BUSINESS_ID=TU_BUSINESS_ID_AQUI
WHATSAPP_APP_SECRET=TU_APP_SECRET_AQUI
N8N_WEBHOOK_URL_EXTERNAL=http://localhost:5678/webhook/whatsapp

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-TU_CLAVE_OPENAI_AQUI
OPENAI_MODEL=gpt-4o-mini

# XAI (Grok) Configuration
XAI_API_KEY=xai-TU_CLAVE_XAI_AQUI
XAI_MODEL=grok-4-latest,grok-beta

# Knowledge ingestion
SHOPIFY_PAGE_SIZE=250
RUN_SHOPIFY_SYNC=true

# Mercado Libre OAuth / API
MERCADO_LIBRE_APP_ID=TU_APP_ID_AQUI
MERCADO_LIBRE_CLIENT_SECRET=TU_CLIENT_SECRET_AQUI
MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
MERCADO_LIBRE_SELLER_ID=TU_SELLER_ID_AQUI
MERCADO_LIBRE_WEBHOOK_SECRET=TU_WEBHOOK_SECRET_AQUI
MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy
MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
MERCADO_LIBRE_SCOPES=offline_access read write
MERCADO_LIBRE_PKCE_ENABLED=true

# Mercado Libre ingestion
MELI_ACCESS_TOKEN=TU_ACCESS_TOKEN_AQUI
MELI_REFRESH_TOKEN=TU_REFRESH_TOKEN_AQUI
MELI_SELLER_ID=TU_SELLER_ID_AQUI
MELI_PAGE_SIZE=250
RUN_MELI_SYNC=true

# External Services
GOOGLE_SHEETS_API_KEY=TU_GOOGLE_SHEETS_API_KEY_AQUI

# Monitoring
SENTRY_DSN=TU_SENTRY_DSN_AQUI
ANALYTICS_ID=TU_ANALYTICS_ID_AQUI

# Feature Flags
NEXT_PUBLIC_ENABLE_AI_INSIGHTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME_MONITORING=true
NEXT_PUBLIC_ENABLE_EXPORT_IMPORT=true

# N8N Configuration
N8N_API_KEY=TU_N8N_API_KEY_AQUI
N8N_PUBLIC_KEY=TU_N8N_PUBLIC_KEY_AQUI
N8N_PRIVATE_KEY=TU_N8N_PRIVATE_KEY_AQUI
N8N_BASE_URL=http://localhost:5678
```

---

## ✅ Checklist de Completado

- [ ] API URLs configuradas
- [ ] NEXTAUTH_SECRET generado
- [ ] Base de datos configurada (PostgreSQL y MongoDB)
- [ ] Credenciales de WhatsApp configuradas
- [ ] OpenAI API Key configurada
- [ ] XAI API Key configurada (opcional)
- [ ] Mercado Libre OAuth configurado
- [ ] Google Sheets API Key configurada (opcional)
- [ ] Sentry DSN configurado (opcional)
- [ ] Analytics ID configurado (opcional)
- [ ] N8N configurado (opcional)
- [ ] Feature flags ajustados según necesidad

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:**
- Nunca subas el archivo `.env` a Git
- Verifica que `.env` esté en `.gitignore`
- No compartas tus claves públicamente
- Rota las claves periódicamente
- Usa diferentes claves para desarrollo y producción

---

## 📤 Después de Completar

Una vez que hayas completado todas las variables:

1. **Verifica que funciona:**
   ```bash
   # Carga las variables
   source .env
   
   # O ejecuta tu aplicación
   npm run dev
   ```

2. **Sube a GitHub Secrets (opcional):**
   ```bash
   python upload_secrets_to_github.py --env-file .env
   ```

---

**¿Necesitas ayuda con alguna variable específica?** Revisa la sección correspondiente arriba para instrucciones detalladas.

