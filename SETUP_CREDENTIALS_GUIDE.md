# 🔐 Guía de Configuración de Credenciales - Sistema BMC

**Tiempo estimado**: 25-30 minutos  
**Estado actual**: OpenAI API Key ✅ CONFIGURADA

---

## ✅ PASO 1: Crear archivo .env.local (2 minutos)

Crea un archivo llamado `.env.local` en la raíz del proyecto con este contenido:

```bash
# OpenAI API - YA CONFIGURADA ✅
OPENAI_API_KEY=***REMOVED***

# Google Sheets API - CONFIGURAR EN PASO 2
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=TU_EMAIL_AQUI
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nTU_CLAVE_AQUI\n-----END PRIVATE KEY-----\n"

# MongoDB Atlas - CONFIGURAR EN PASO 3
MONGODB_URI=mongodb+srv://TU_URI_AQUI

# URLs
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**⚠️ IMPORTANTE**: Este archivo NO se sube a GitHub (está en .gitignore)

---

## 📊 PASO 2: Configurar Google Service Account (15 minutos)

### 2.1 Acceder a Google Cloud Console

1. Ve a: https://console.cloud.google.com
2. Inicia sesión con tu cuenta de Google

### 2.2 Crear o seleccionar proyecto

**Opción A: Crear nuevo proyecto**
- Haz clic en el selector de proyectos (arriba a la izquierda)
- Click en "New Project"
- Nombre: "BMC Cotizaciones"
- Click "Create"

**Opción B: Usar proyecto existente**
- Selecciona el proyecto que quieras usar

### 2.3 Habilitar Google Sheets API

1. En el menú lateral: "APIs & Services" → "Library"
2. Buscar: "Google Sheets API"
3. Click en "Google Sheets API"
4. Click "Enable"

### 2.4 Crear Service Account

1. En el menú lateral: "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Llenar formulario:
   - **Service account name**: bmc-sheets-service
   - **Service account ID**: (se genera automáticamente)
   - **Description**: Service account para BMC Cotizaciones
4. Click "Create and Continue"
5. **Select a role**: 
   - Buscar "Editor" o "Basic" → "Editor"
   - Click "Continue"
6. Click "Done"

### 2.5 Crear clave JSON

1. En la lista de Service Accounts, encuentra "bmc-sheets-service"
2. Click en los 3 puntos (⋮) → "Manage keys"
3. Click "Add Key" → "Create new key"
4. Selecciona "JSON"
5. Click "Create"
6. **SE DESCARGARÁ UN ARCHIVO JSON** - Guárdalo en un lugar seguro

### 2.6 Extraer credenciales del JSON

Abre el archivo JSON descargado y copia:

**Email del Service Account**:
```json
{
  "client_email": "bmc-sheets-service@tu-proyecto.iam.gserviceaccount.com"
}
```
→ Copia este email y reemplaza `GOOGLE_SERVICE_ACCOUNT_EMAIL` en `.env.local`

**Private Key**:
```json
{
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n"
}
```
→ Copia TODA la clave (incluyendo BEGIN y END) y reemplaza `GOOGLE_PRIVATE_KEY` en `.env.local`

**⚠️ NOTA**: La clave debe incluir los `\n` (saltos de línea). Mantén las comillas dobles.

### 2.7 Compartir Google Sheet con el Service Account

1. Abre tu Google Sheet: 
   https://docs.google.com/spreadsheets/d/1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
2. Click en "Share" (arriba a la derecha)
3. Pega el email del Service Account (bmc-sheets-service@...)
4. Permisos: **Editor**
5. **DESMARCAR** "Notify people"
6. Click "Share"

✅ **GOOGLE SHEETS CONFIGURADO!**

---

## 🗄️ PASO 3: Configurar MongoDB Atlas (10 minutos)

### 3.1 Crear cuenta MongoDB Atlas

1. Ve a: https://www.mongodb.com/cloud/atlas/register
2. **Sign up** con tu email o cuenta de Google
3. Completa el registro

### 3.2 Crear cluster gratuito

1. Click "Build a Database"
2. Selecciona **M0 FREE** (Shared)
3. **Provider**: AWS
4. **Region**: Sao Paulo (sa-east-1) - más cercano a Uruguay
5. **Cluster Name**: bmc-cotizaciones
6. Click "Create"
7. **ESPERA 1-3 MINUTOS** mientras se crea el cluster

### 3.3 Crear usuario de base de datos

1. Aparecerá popup "Security Quickstart"
2. **Authentication Method**: Username and Password
3. **Username**: bmcadmin
4. **Password**: Click "Autogenerate Secure Password"
   - **⚠️ COPIA Y GUARDA ESTE PASSWORD**
5. Click "Create User"

### 3.4 Configurar acceso de red

1. En el mismo popup, sección "Where would you like to connect from?"
2. Click "Add My Current IP Address" 
3. **IMPORTANTE**: También agregar:
   - Click "Add a Different IP Address"
   - IP Address: `0.0.0.0/0`
   - Description: "Vercel and external access"
   - Click "Add Entry"
4. Click "Finish and Close"

### 3.5 Obtener Connection String

1. Click "Connect" en tu cluster
2. Selecciona "Drivers"
3. Driver: **Node.js**
4. Version: **5.5 or later**
5. Copia el **Connection String**:
   ```
   mongodb+srv://bmcadmin:<password>@bmc-cotizaciones.xxxxx.mongodb.net/
   ```

### 3.6 Actualizar .env.local con MongoDB URI

1. Toma el Connection String copiado
2. **REEMPLAZA** `<password>` con el password que generaste en el paso 3.3
3. Copia el URI completo y reemplaza `MONGODB_URI` en `.env.local`

**Ejemplo**:
```bash
MONGODB_URI=mongodb+srv://bmcadmin:Tu-Password-Aqui@bmc-cotizaciones.abc123.mongodb.net/
```

✅ **MONGODB CONFIGURADO!**

---

## 🛒 PASO 4: Conectar Mercado Libre (5 minutos)

El flujo OAuth usa la ruta `/api/mercado-libre/auth/callback`, por lo que la URL debe apuntar exactamente ahí.

1. En `.env.local` agrega o completa estas variables:
   ```bash
   # Mercado Libre OAuth / API
   MERCADO_LIBRE_APP_ID=tu-app-id
   MERCADO_LIBRE_CLIENT_SECRET=tu-client-secret
   MERCADO_LIBRE_SELLER_ID=tu-seller-id
   MERCADO_LIBRE_REDIRECT_URI=http://localhost:3000/api/mercado-libre/auth/callback
   # ⚠️ IMPORTANTE: MERCADO_LIBRE_AUTH_URL debe coincidir EXACTAMENTE con la región donde registraste la app
   # Si registraste en Argentina: https://auth.mercadolibre.com.ar
   # Si registraste en México: https://auth.mercadolibre.com.mx
   # Si registraste en Uruguay: https://auth.mercadolibre.com.uy
   # Si registraste en Brasil: https://auth.mercadolibre.com.br
   # Si registraste en Chile: https://auth.mercadolibre.com.cl
   # Si registraste en Colombia: https://auth.mercadolibre.com.co
   # Si registraste en Perú: https://auth.mercadolibre.com.pe
   MERCADO_LIBRE_AUTH_URL=https://auth.mercadolibre.com.uy  # ⚠️ CAMBIA ESTO según tu región
   MERCADO_LIBRE_API_URL=https://api.mercadolibre.com
   ```
2. Si tienes un entorno desplegado (Vercel, servidor propio, etc.), crea una segunda entrada con tu dominio público:
   ```
   MERCADO_LIBRE_REDIRECT_URI=https://tu-dominio.com/api/mercado-libre/auth/callback
   ```
3. Ve al portal de desarrolladores de Mercado Libre **de tu región** (ej: https://developers.mercadolibre.com.ar/apps/ para Argentina, https://developers.mercadolibre.com.uy/apps/ para Uruguay), abre tu aplicación y en **Redirect URIs** pega exactamente la URL anterior (incluye protocolo + dominio + `/api/mercado-libre/auth/callback`). El portal rechazará URLs genéricas como `https://www.mercadopago.com`.
4. Guarda y prueba desde el dashboard: el botón "Conectar Mercado Libre" iniciará el flujo, te enviará a Mercado Libre y volverá a `/dashboard?meli=connected` cuando acepte los permisos.

> ⚠️ **CRÍTICO**: Si `MERCADO_LIBRE_AUTH_URL` no coincide con la región donde registraste la app, el flujo OAuth fallará con errores de autenticación. Verifica en developers.mercadolibre.com.[tu-región] cuál es la región correcta.

---

## ✅ VERIFICACIÓN (2 minutos)

Una vez configurado todo, verifica que tu archivo `.env.local` se vea así:

```bash
# OpenAI API ✅
OPENAI_API_KEY=sk-proj-TU-KEY-AQUI

# Google Sheets API ✅
GOOGLE_SHEET_ID=1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=bmc-sheets-service@tu-proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgk...\n-----END PRIVATE KEY-----\n"

# MongoDB Atlas ✅
MONGODB_URI=mongodb+srv://bmcadmin:password@bmc-cotizaciones.xxxxx.mongodb.net/

# URLs
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## 🧪 TESTING

Después de configurar todo, ejecuta:

```bash
# 1. Limpiar caché
rm -rf .next

# 2. Iniciar servidor
npm run dev

# 3. Probar health check (en otra terminal)
curl http://localhost:3000/api/health
```

**Deberías ver**:
```json
{
  "status": "healthy",
  "services": {
    "openai": { "status": "ready" },
    "googleSheets": { "status": "ready" },
    "mongodb": { "status": "ready" }
  }
}
```

---

## 📝 CHECKLIST FINAL

- [ ] Archivo `.env.local` creado
- [ ] OpenAI API Key configurada ✅
- [ ] Google Service Account creado
- [ ] JSON descargado y credenciales copiadas a `.env.local`
- [ ] Google Sheet compartido con Service Account email
- [ ] MongoDB Atlas cluster creado (M0 Free)
- [ ] Usuario de base de datos creado
- [ ] IP 0.0.0.0/0 agregada a Network Access
- [ ] Connection String copiado a `.env.local`
- [ ] Health check ejecutado con éxito

---

## 🆘 PROBLEMAS COMUNES

### Google Sheets API error
- Verifica que compartiste el Sheet con el email del Service Account
- Asegúrate de que el Private Key incluye los `\n` y las comillas

### MongoDB connection error
- Verifica que reemplazaste `<password>` en el URI
- Asegúrate de que agregaste 0.0.0.0/0 a Network Access

### OpenAI API error
- Verifica que la key comienza con `sk-proj-` o `sk-`
- Revisa que no tenga espacios al inicio o final

---

## ✅ ¿LISTO?

Una vez completados todos los pasos, responde en el chat:

**"CREDENCIALES CONFIGURADAS"**

Y continuaremos con el BLOQUE 2: Testing Local y Deploy a Vercel. 🚀

