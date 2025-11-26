# 🚀 Guía de Hosting para tu Chatbot BMC

## Tu Situación Actual

Tu hosting cPanel en **grow-importa.com.uy** es hosting compartido con estas características:
- ✅ 100 GB disco (70.62 GB usado)
- ✅ 100 GB ancho de banda
- ✅ 15 bases de datos MySQL
- ❌ **No soporta Node.js** (tu chatbot usa Next.js)
- ❌ **No tiene MongoDB** (tu chatbot lo necesita)
- ❌ **No puede ejecutar Docker**

---

## 🎯 Solución Recomendada: Vercel + MongoDB Atlas (GRATIS)

### Arquitectura Final
```
                    ┌──────────────────────────┐
                    │   Tu dominio cPanel      │
                    │  grow-importa.com.uy     │
                    └───────────┬──────────────┘
                                │ DNS CNAME
                                ▼
┌───────────────────────────────────────────────────────┐
│                    VERCEL (Gratis)                     │
│  ┌─────────────────┐    ┌─────────────────────────┐   │
│  │   Next.js App   │    │    API Routes           │   │
│  │   (Dashboard)   │    │  /api/chat              │   │
│  │                 │    │  /api/quotes            │   │
│  └─────────────────┘    │  /api/whatsapp/webhook  │   │
│                         └───────────┬─────────────┘   │
└─────────────────────────────────────┼─────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │  MongoDB Atlas  │    │   OpenAI API    │    │  Google Sheets  │
    │    (Gratis)     │    │                 │    │                 │
    │   512 MB free   │    │                 │    │                 │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📋 Paso a Paso: Deploy Completo

### Paso 1: Crear cuenta en MongoDB Atlas (5 min)

1. Ve a [mongodb.com/atlas](https://mongodb.com/atlas)
2. Crea cuenta gratuita
3. Crea un **Cluster** gratis (M0 - 512MB)
4. En "Database Access": crea usuario con password
5. En "Network Access": agrega IP `0.0.0.0/0` (permite todas)
6. Copia tu **Connection String**:
   ```
   mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/bmc_chat
   ```

### Paso 2: Subir código a GitHub (5 min)

1. Crea repositorio en [github.com](https://github.com)
2. Sube tu código:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/bmc-chatbot.git
   git push -u origin main
   ```

### Paso 3: Deploy en Vercel (5 min)

1. Ve a [vercel.com](https://vercel.com)
2. "Sign up" con GitHub
3. "New Project" → Selecciona tu repositorio
4. **Framework:** Next.js (detectado automático)
5. Click **Deploy**

### Paso 4: Configurar Variables de Entorno (3 min)

En Vercel Dashboard → Settings → Environment Variables, agrega:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `sk-xxx...` | Tu API key de OpenAI |
| `MONGODB_URI` | `mongodb+srv://...` | Connection string de Atlas |
| `GOOGLE_SHEET_ID` | `1ABC...xyz` | ID de tu Google Sheet |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | `xxx@xxx.iam.gserviceaccount.com` | Email del service account |
| `GOOGLE_PRIVATE_KEY` | `-----BEGIN PRIVATE...` | Private key (escapar \n) |

### Paso 5: Conectar tu Dominio (5 min)

#### Opción A: Subdominio (Recomendado)
En tu **cPanel** → Zone Editor → Agregar registro:
```
Tipo: CNAME
Nombre: chatbot
Destino: cname.vercel-dns.com
```
Resultado: `chatbot.grow-importa.com.uy`

#### Opción B: Dominio completo
En **Vercel** Dashboard → Settings → Domains:
1. Agrega `grow-importa.com.uy`
2. Vercel te dará instrucciones de DNS
3. Configura en cPanel los registros que indica

---

## 🧪 Verificar que Funciona

Después del deploy, prueba estas URLs:

```bash
# Health check
https://TU-APP.vercel.app/api/health

# Dashboard
https://TU-APP.vercel.app

# Con tu dominio (después de configurar DNS)
https://chatbot.grow-importa.com.uy
```

---

## 💰 Costos Estimados

| Servicio | Tier Gratis | Tier Pago (si necesitas más) |
|----------|-------------|------------------------------|
| **Vercel** | 100GB bandwidth/mes | $20/mes (Pro) |
| **MongoDB Atlas** | 512MB storage | $57/mes (M10) |
| **OpenAI API** | Pay per use | ~$5-20/mes típico |
| **Tu cPanel** | Ya lo tienes | $X/mes actual |

**Total inicial: $0-5/mes** (solo OpenAI usage)

---

## 🔄 Alternativa: VPS con Docker (Control Total)

Si prefieres control total o necesitas más recursos:

### Opción: DigitalOcean Droplet ($6/mes)

1. Crea cuenta en [digitalocean.com](https://digitalocean.com)
2. Crea Droplet Ubuntu 22.04 ($6/mes)
3. Conecta por SSH:
   ```bash
   ssh root@TU_IP
   ```
4. Instala Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
5. Clona y ejecuta:
   ```bash
   git clone https://github.com/TU_USUARIO/bmc-chatbot.git
   cd bmc-chatbot
   cp .env.example .env
   # Edita .env con tus credenciales
   docker-compose up -d
   ```

---

## 📱 Integración WhatsApp

Una vez deployado, configura WhatsApp Business:

1. **Webhook URL:** `https://chatbot.grow-importa.com.uy/api/whatsapp/webhook`
2. **Verify Token:** El que configures en variables de entorno
3. En Meta Business → WhatsApp → Webhooks → Configurar URL

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar mi cPanel actual?
No directamente para el chatbot. Pero puedes:
- Usar cPanel para tu sitio web principal
- Usar Vercel para el chatbot
- Conectar ambos con subdominios

### ¿Es seguro Vercel?
Sí, Vercel es usado por Netflix, TikTok, y miles de empresas. Tiene SSL automático.

### ¿Qué pasa si excedo los límites gratis?
Vercel te avisa antes. Puedes:
- Optimizar tu código
- Upgrade a plan Pro ($20/mes)
- Mover a VPS

### ¿Puedo migrar después?
Sí, tu código es portable. Puedes mover de Vercel a VPS en cualquier momento.

---

## 🆘 Soporte

Si tienes problemas:
1. Revisa logs en Vercel Dashboard → Deployments → View Logs
2. Verifica variables de entorno
3. Prueba localmente: `npm run build && npm run start`

---

**¿Listo para deployar?** 

Ejecuta estos comandos para preparar tu proyecto:

```bash
# Verificar que todo compila
npm run build

# Ver que no hay archivos sensibles
git status

# Subir a GitHub
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

Luego sigue los pasos de Vercel arriba. ¡Tu chatbot estará online en minutos!
