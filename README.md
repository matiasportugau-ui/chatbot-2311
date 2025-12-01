# Sistema de Chatbot Conversacional BMC Uruguay

Sistema completo de asistente virtual inteligente con capacidades de cotización automática para BMC Uruguay. Integra IA conversacional (OpenAI), gestión de cotizaciones, dashboard de métricas, y múltiples canales de comunicación (WhatsApp, Web).

## 🎯 Características Principales

### 🤖 Chatbot Inteligente
- **IA Conversacional** con OpenAI GPT-4 para comprensión natural del lenguaje
- **Procesamiento contextual** que mantiene el hilo de conversación
- **Fallback inteligente** a pattern matching cuando IA no está disponible
- **Validación automática de datos** - solicita información faltante de forma natural
- **Múltiples interfaces**: CLI, Web UI, WhatsApp Business

### 💼 Sistema de Cotizaciones
- **Generación automática** de cotizaciones desde consultas en lenguaje natural
- **Cálculo de precios** basado en especificaciones técnicas y matriz de precios
- **Integración Google Sheets** para gestión colaborativa
- **Seguimiento de estados** (Pendiente, Enviado, Confirmado, etc.)
- **Base de conocimiento** de productos BMC (Isodec, Poliestireno, Lana de Roca, etc.)

### 📊 Dashboard de Gestión
- **Monitoreo en tiempo real** de conversaciones y cotizaciones
- **Analytics y métricas** de rendimiento del chatbot
- **Gestión de contexto** de conversaciones
- **Exportación/importación** de datos
- **Tendencias y patrones** de consultas

### 🔌 Integraciones
- **WhatsApp Business API** para atención automatizada
- **MercadoLibre API** para gestión de órdenes y productos
- **Google Sheets** para sincronización de cotizaciones
- **MongoDB** para persistencia de datos
- **n8n** para automatización de workflows

## Validación Inteligente de Datos (Bot)

El sistema incluye validación centralizada que garantiza que toda la información requerida esté completa antes de generar una cotización. El bot conversacional detecta automáticamente datos faltantes y los solicita al cliente de manera natural y amigable.

### Campos Obligatorios

Para generar una cotización, el sistema requiere los siguientes datos mínimos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **nombre** | Nombre del cliente | Juan |
| **apellido** | Apellido del cliente | Pérez |
| **telefono** | Teléfono de contacto | 099123456 |
| **producto** | Tipo de producto | isodec, poliestireno, lana_roca |
| **espesor** | Espesor del producto | 50mm, 75mm, 100mm, 125mm, 150mm |
| **largo** | Largo en metros | 10 |
| **ancho** | Ancho en metros | 5 |

### Comportamiento del Bot

**Solicitud Automática de Datos:**
- El bot detecta automáticamente qué datos faltan
- Solicita la información de forma clara y específica
- Adapta el mensaje según la cantidad de datos faltantes
- No genera cotización hasta tener todos los datos requeridos

**Ejemplos de Mensajes del Bot:**

Cuando falta un solo dato:
```
Bot: "Para poder cotizar necesito que me indiques qué producto te interesa 
(Isodec, Poliestireno o Lana de Roca). ¿Cuál te interesa?"
```

Cuando faltan varios datos:
```
Bot: "Para poder cotizar necesito los siguientes datos: tu apellido, 
el espesor que necesitas (50mm, 75mm, 100mm, 125mm o 150mm) y las dimensiones 
(largo x ancho en metros, por ejemplo: 10m x 5m). ¿Podrías indicarme esa información?"
```

Cuando faltan las dimensiones:
```
Bot: "Para poder cotizar necesito las dimensiones (largo x ancho en metros, 
por ejemplo: 10m x 5m). ¿Cuáles son las dimensiones?"
```

### Flujo de Validación

1. **Cliente inicia conversación** - El bot saluda y ofrece ayuda
2. **Cliente solicita cotización** - El bot explica qué datos necesita
3. **Cliente proporciona información** - El bot extrae los datos del mensaje
4. **Validación automática** - El sistema verifica si faltan datos obligatorios
5. **Solicitud de datos faltantes** - Si falta algo, el bot lo solicita específicamente
6. **Generación de cotización** - Solo cuando todos los datos están completos

### Ventajas del Sistema de Validación

✅ **Cotizaciones completas:** Garantiza que ninguna cotización se genere sin información crítica  
✅ **Experiencia natural:** El bot solicita datos de forma conversacional y amigable  
✅ **Mensajes contextuales:** Los mensajes se adaptan a qué específicamente falta  
✅ **Mantenibilidad:** La lógica de validación está centralizada en `utils_cotizaciones.py`  
✅ **Extensible:** Fácil agregar nuevos campos obligatorios en el futuro

### Uso en el Código

```python
from utils_cotizaciones import obtener_datos_faltantes, formatear_mensaje_faltantes

# Construir contexto con datos actuales
contexto = {
    "nombre": "Juan",
    "apellido": "",  # Faltante
    "telefono": "099123456",
    "producto": "isodec",
    "espesor": "100mm",
    "largo": 10,
    "ancho": 5
}

# Detectar datos faltantes
faltantes = obtener_datos_faltantes(contexto)  
# Resultado: ['apellido']

# Generar mensaje amigable
mensaje = formatear_mensaje_faltantes(faltantes)
# Resultado: "Para poder cotizar necesito tu apellido. ¿Cómo te llamas?"
```

## 🏗️ Arquitectura del Sistema

```
bmc-chatbot-system/
├── Backend (Python)
│   ├── api_server.py                      # FastAPI server con endpoints REST
│   ├── ia_conversacional_integrada.py     # Motor de IA conversacional
│   ├── sistema_cotizaciones.py            # Lógica de cotizaciones
│   ├── chat_interactivo.py                # Interfaz CLI del chatbot
│   ├── simulate_chat_cli.py               # Simulador para testing
│   ├── background_agent_followup.py       # Agente de seguimiento automático
│   └── python-scripts/                    # Scripts auxiliares
│
├── Frontend (Next.js + TypeScript)
│   └── src/
│       ├── app/
│       │   ├── page.tsx                   # Dashboard principal
│       │   ├── chat/                      # Interfaz de chat web
│       │   ├── simulator/                 # Simulador de conversaciones
│       │   └── api/                       # API routes de Next.js
│       ├── components/
│       │   ├── dashboard/                 # Componentes del dashboard
│       │   └── chat/                      # Componentes de chat
│       └── models/                        # Modelos TypeScript
│
├── Legacy/Secondary App
│   └── nextjs-app/                        # App Next.js básica (bootstrap)
│
├── Workflows & Automation
│   ├── n8n_workflows/                     # Workflows de n8n
│   │   ├── workflow-whatsapp-complete.json
│   │   ├── workflow-chat.json
│   │   └── workflow-sheets-sync.json
│   └── docker-compose.yml                 # Servicios: n8n, MongoDB, API
│
├── Scripts & Utilities
│   ├── scripts/
│   │   ├── setup_chatbot_env.sh          # Setup del entorno
│   │   ├── run_full_stack.sh             # Lanzar sistema completo
│   │   ├── refresh_knowledge.sh          # Actualizar base de conocimiento
│   │   └── test-e2e-whatsapp.sh          # Tests E2E
│   ├── launch.sh                         # Launcher unificado (Unix)
│   └── unified_launcher.py               # Launcher con menú interactivo
│
├── Data & Configuration
│   ├── data/                             # Datos de productos y conversaciones
│   ├── conocimiento_completo.json        # Base de conocimiento consolidada
│   ├── requirements.txt                  # Dependencias Python
│   └── .env                             # Variables de entorno (crear desde env.example)
│
└── Documentation
    ├── README.md                         # Este archivo
    ├── HOW_TO_RUN.md                    # Guía de ejecución
    ├── SETUP_WHATSAPP.md                # Setup de WhatsApp
    ├── BMC_SYSTEM_GUIDE.md              # Guía completa del sistema
    └── IMPLEMENTATION_SUMMARY.md         # Resumen de implementación
```

## 💻 Stack Tecnológico

### Backend
- **Python 3.11+** - Lenguaje principal del backend
- **FastAPI** - Framework API REST moderno y rápido
- **OpenAI API** - Motor de IA conversacional (GPT-4)
- **PyMongo** - Cliente de MongoDB
- **Uvicorn** - Servidor ASGI de alto rendimiento

### Frontend
- **Next.js 16** - Framework React con SSR/SSG
- **React 19** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework CSS utility-first
- **shadcn/ui** - Componentes UI reutilizables

### Bases de Datos & Storage
- **MongoDB** - Base de datos NoSQL para conversaciones y cotizaciones
- **Google Sheets** - Storage y sincronización de cotizaciones

### Integrations & APIs
- **WhatsApp Business API** - Canal de mensajería
- **MercadoLibre API** - Integración e-commerce
- **Google Sheets API** - Sincronización de datos
- **n8n** - Orquestador de workflows

### DevOps & Tools
- **Docker & Docker Compose** - Containerización
- **Git & GitHub** - Control de versiones
- **Dev Containers** - Entornos de desarrollo reproducibles

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Python 3.11 o superior**
- **Node.js 20 o superior** (para el dashboard)
- **Docker & Docker Compose** (opcional, para servicios completos)
- **Git** para clonar el repositorio

### Instalación Paso a Paso

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-org/bmc-chatbot-system.git
cd bmc-chatbot-system
```

#### 2. Configurar Variables de Entorno

```bash
# Copiar template de variables de entorno
cp env.example .env

# Editar .env con tus credenciales
nano .env  # o usa tu editor preferido
```

**Variables mínimas requeridas:**
```env
# OpenAI (REQUERIDO para IA conversacional)
OPENAI_API_KEY=sk-...

# MongoDB (REQUERIDO)
MONGODB_URI=mongodb://localhost:27017/bmc_chat
# O usa MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/bmc_chat

# Google Sheets (OPCIONAL, pero recomendado)
GOOGLE_SHEET_ID=tu-sheet-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=tu-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# WhatsApp (OPCIONAL)
WHATSAPP_ACCESS_TOKEN=tu-token
WHATSAPP_PHONE_NUMBER_ID=tu-phone-id
WHATSAPP_VERIFY_TOKEN=tu-verify-token
```

**Para obtener credenciales:**
- OpenAI: https://platform.openai.com/api-keys
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- Google Sheets: Ver `SETUP_CREDENTIALS_GUIDE.md`
- WhatsApp: Ver `SETUP_WHATSAPP.md`

#### 3. Instalación Backend (Python)

```bash
# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### 4. Instalación Frontend (Next.js)

```bash
# Instalar dependencias del dashboard principal
npm install

# O si prefieres usar el app secundario
cd nextjs-app && npm install
```

#### 5. Iniciar Servicios con Docker (Opcional)

Si quieres MongoDB, n8n y el API todo en contenedores:

```bash
docker-compose up -d
```

Esto iniciará:
- MongoDB en `localhost:27017`
- API Python en `localhost:8000`
- n8n en `localhost:5678`

## 🎬 Cómo Ejecutar el Sistema

### Opción 1: Launcher Unificado (Recomendado)

El sistema incluye un launcher interactivo que facilita la ejecución:

```bash
# Linux/Mac
./launch.sh

# O directamente con Python
python unified_launcher.py
```

El launcher te mostrará un menú con opciones:
1. **Chat Interactivo** - CLI conversacional
2. **API Server** - Backend FastAPI
3. **Simulador** - Testing de conversaciones
4. **Full Stack** - API + Dashboard completo
5. **Setup Only** - Solo configurar sin ejecutar

### Opción 2: Componentes Individuales

#### Backend API (FastAPI)

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar API server
python api_server.py

# La API estará disponible en http://localhost:8000
# Documentación interactiva en http://localhost:8000/docs
```

#### Dashboard (Next.js)

```bash
# Desde la raíz del proyecto
npm run dev

# El dashboard estará en http://localhost:3000
```

#### Chat CLI Interactivo

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar chat interactivo
python chat_interactivo.py
```

#### Simulador de Chat

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar simulador
python simulate_chat_cli.py

# O usa el script
./start_simulator.sh
```

### Opción 3: Stack Completo con Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

Servicios disponibles:
- API: http://localhost:8000
- n8n: http://localhost:5678 (admin/bmc2024)
- MongoDB: localhost:27017

### Opción 4: Script de Ejecución Completa

```bash
# Ejecuta setup, validación e inicia servicios
bash scripts/run_full_stack.sh
```

## 🧪 Testing y Validación

### Tests Automatizados

```bash
# Test E2E de WhatsApp
bash scripts/test-e2e-whatsapp.sh

# Test de integración completa
python test_sistema_automatico.py

# Validar configuración e integraciones
python validar_integracion.py
```

### Simulador para Testing

El simulador permite probar conversaciones sin necesidad de WhatsApp:

```bash
# Iniciar simulador CLI
python simulate_chat_cli.py

# O desde el dashboard web
# http://localhost:3000/simulator
```

**Comandos del simulador:**
- `/help` - Ayuda
- `/new` - Nueva sesión
- `/phone <number>` - Cambiar teléfono
- `/history` - Ver historial
- `/export` - Exportar conversación
- `/stats` - Estadísticas
- `/exit` - Salir

### Poblar Base de Conocimiento

Para entrenar el sistema con escenarios de prueba:

```bash
# Ejecutar escenarios de prueba
python populate_kb.py

# Ver escenarios disponibles
ls test_scenarios/
```

## 🔄 Actualizar Base de Conocimiento

### Sincronización de Datos

```bash
# Script completo de actualización
bash scripts/refresh_knowledge.sh
```

Este script:
1. Sincroniza productos desde fuentes externas (Shopify, MercadoLibre)
2. Consolida archivos JSON de conocimiento
3. Valida integraciones
4. Genera reportes de actualización

### Sincronización Manual

```bash
source .venv/bin/activate

# Sincronizar productos Shopify
python python-scripts/fetch_shopify_products.py

# Sincronizar MercadoLibre (requiere tokens)
python python-scripts/fetch_mercadolibre_questions.py

# Consolidar conocimiento
python consolidar_conocimiento.py

# Validar todo
python validar_integracion.py
```

### Configurar Tokens de MercadoLibre

```bash
# Helper para obtener/refrescar tokens OAuth
python python-scripts/mercadolibre_oauth_helper.py
```

## 💬 Uso del Sistema

### Interfaz de Chat (Múltiples Opciones)

#### 1. Chat CLI Interactivo

```bash
python chat_interactivo.py
```

Conversación en terminal con el bot. Ideal para testing rápido y desarrollo.

**Ejemplo de conversación:**
```
👤 Tú: Hola, necesito cotizar Isodec para un galpón

🤖 Bot: ¡Hola! Con gusto te ayudo con la cotización de Isodec.
       ¿Podrías indicarme las dimensiones del galpón?

👤 Tú: 10 metros por 15 metros, con altura de 5 metros

🤖 Bot: Perfecto. ¿Qué espesor de panel necesitas?
       Tenemos: 50mm, 100mm, 150mm, 200mm

👤 Tú: 100mm

🤖 Bot: 🎉 COTIZACIÓN LISTA
       Producto: Isodec EPS 100mm
       Dimensiones: 10m x 15m x 5m
       Precio estimado: $2,750 USD
       Código: BMC-20241201-001
```

#### 2. Dashboard Web

```bash
npm run dev
```

Accede a http://localhost:3000

**Páginas disponibles:**
- `/` - Dashboard principal con métricas
- `/chat` - Interfaz de chat web
- `/simulator` - Simulador de conversaciones
- `/bmc-chat` - Chat BMC mejorado

**Características del dashboard:**
- 📊 **Métricas en tiempo real** - Conversiones, tiempo de respuesta
- 💬 **Gestión de conversaciones** - Ver historial, contexto
- 📈 **Analytics** - Tendencias, productos más consultados
- 🔍 **Búsqueda avanzada** - Por cliente, producto, fecha
- 📤 **Exportar/Importar** - Datos en JSON, CSV

#### 3. WhatsApp Business

Una vez configurado el webhook (ver `SETUP_WHATSAPP.md`):

1. Los clientes envían mensajes a tu número de WhatsApp Business
2. El sistema procesa automáticamente con IA
3. Genera cotizaciones y responde en tiempo real
4. Guarda conversación en MongoDB
5. Sincroniza con Google Sheets

### API Endpoints

El sistema expone una API REST completa:

```bash
# Health check
GET http://localhost:8000/health

# Procesar mensaje de chat
POST http://localhost:8000/chat/process
{
  "mensaje": "Necesito cotizar Isodec 100mm",
  "telefono": "+59891234567",
  "sesion_id": "session-123"
}

# Crear cotización
POST http://localhost:8000/quote/create
{
  "cliente": {...},
  "especificaciones": {...}
}

# Obtener insights
GET http://localhost:8000/insights

# Ver documentación completa
GET http://localhost:8000/docs
```

### Flujo Típico de Uso

1. **Cliente inicia conversación** (WhatsApp, Web, o CLI)
2. **IA procesa el mensaje** y extrae información estructurada
3. **Sistema valida datos** y solicita información faltante si es necesario
4. **Genera cotización** con cálculos automáticos de precios
5. **Envía respuesta** al cliente con detalles de la cotización
6. **Guarda en MongoDB** para seguimiento
7. **Sincroniza con Google Sheets** para gestión del equipo
8. **Dashboard muestra métricas** en tiempo real

## 📱 Integración WhatsApp Business

### Configuración

Ver la guía completa en `SETUP_WHATSAPP.md`

**Pasos resumidos:**

1. Crear app en Meta for Developers
2. Obtener credenciales (Access Token, Phone Number ID)
3. Configurar webhook con n8n o API directa
4. Importar workflow de n8n desde `n8n_workflows/workflow-whatsapp-complete.json`
5. Activar workflow

### Flujo de WhatsApp

```
Cliente (WhatsApp) 
    ↓
Meta Webhook → n8n → Python API → OpenAI
    ↓             ↓         ↓
Respuesta ← MongoDB ← Sistema Cotización
```

### n8n Workflows

El sistema incluye varios workflows predefinidos:

- **workflow-whatsapp-complete.json** - Flujo completo de WhatsApp
- **workflow-chat.json** - Procesamiento de mensajes
- **workflow-sheets-sync.json** - Sincronización Google Sheets
- **workflow-analytics.json** - Analytics y reportes

**Acceder a n8n:**
```bash
# Si usas Docker
docker-compose up -d n8n
# Acceder en http://localhost:5678
# Usuario: admin / Contraseña: bmc2024
```

### Agente de Seguimiento Automático

El sistema incluye un agente que detecta conversaciones pendientes y envía seguimientos:

```bash
# Ejecutar una vez
python background_agent_followup.py

# Ejecutar en modo continuo
python background_agent_followup.py --continuous

# Programar con cron (Linux/Mac)
0 */2 * * * cd /path/to/project && python background_agent_followup.py
```

## 📦 Productos y Servicios

### Productos Principales

#### Paneles Isodec
- **Descripción:** Paneles aislantes térmicos con núcleo de EPS
- **Espesores disponibles:** 50mm, 75mm, 100mm, 125mm, 150mm, 200mm
- **Rellenos:** EPS (estándar), Poliuretano, Lana de roca
- **Colores:** Blanco, Gris, Beige, Personalizado
- **Aplicaciones:** Techos, paredes, galpones completos
- **Terminaciones:** Gotero, Hormigón, Aluminio, PVC

#### Otros Productos
- **Poliestireno Expandido (EPS)** - Placas aislantes (25-100mm)
- **Lana de Roca** - Aislante térmico y acústico (50-100mm)
- **Chapas Galvanizadas** - Acero galvanizado (0.30-0.50mm)
- **Calamería** - Estructura metálica (1.5-2.5mm)
- **Accesorios** - Babetas, goteros, remates, juntas, tornillería

### Servicios Adicionales
- **Instalación** - Precio base + costo por m²
- **Flete** - Según zona geográfica (Montevideo, Canelones, Interior)
- **Asesoramiento técnico** - Incluido sin cargo
- **Mediciones en obra** - Coordinación previa

## 💰 Cálculo de Precios

El sistema calcula automáticamente precios considerando:

### Factores de Cotización

1. **Producto y especificaciones**
   - Tipo de material (Isodec, EPS, Lana de Roca)
   - Espesor del panel
   - Color y terminaciones

2. **Dimensiones**
   - Área total (m²)
   - Largo y ancho
   - Altura (para galpones completos)

3. **Servicios adicionales**
   - Instalación (opcional)
   - Flete según zona
   - Accesorios necesarios

4. **Factores de ajuste**
   - Espesor: 0.8x (50mm) a 1.3x (200mm)
   - Color: 1.0x (Blanco) a 1.15x (Personalizado)
   - Terminaciones: +5% a +15% según tipo
   - Volumen: Descuentos por cantidad

### Fórmula General

```
Precio Total = (Área × Precio_base × Factor_espesor × Factor_color) 
               + Costo_terminaciones 
               + Costo_instalación 
               + Costo_flete 
               + Accesorios
```

El sistema aplica automáticamente estos cálculos cuando genera cotizaciones.

## 📊 Integración Google Sheets

### Sincronización Bidireccional

El sistema sincroniza automáticamente con Google Sheets para:

1. **Importar cotizaciones existentes** desde la planilla compartida
2. **Exportar nuevas cotizaciones** generadas por el chatbot
3. **Actualizar estados** cuando cambian en el sheet
4. **Notificar al equipo** de nuevas consultas

### Configuración

**Sheet ID:** Configurar en `.env` como `GOOGLE_SHEET_ID`

**Pestañas del Sheet:**
- `Admin.` - Cotizaciones pendientes
- `Enviados` - Presupuestos enviados
- `Confirmado` - Ventas confirmadas

### Campos Sincronizados

| Campo Sheet | Sistema | Descripción |
|-------------|---------|-------------|
| Arg | codigo | Código único de cotización |
| Estado | estado | Pendiente, Enviado, Confirmado, etc. |
| Fecha | fecha | Fecha de la consulta |
| Cliente | cliente.nombre | Nombre del cliente |
| Telefono | cliente.telefono | Número de contacto |
| Direccion | cliente.direccion | Ubicación del proyecto |
| Consulta | mensaje_original | Texto completo para análisis IA |
| Producto | especificaciones.producto | Producto solicitado |
| Precio | cotizacion.total | Precio calculado |

### API de Sincronización

```typescript
// Endpoint Next.js para sincronización
POST /api/sheets/sync
{
  "action": "add_quote" | "update_status" | "move_to_enviados",
  "data": { ... }
}

GET /api/sheets/sync  // Leer todas las cotizaciones
```

### Scripts de Sincronización

```bash
# Sincronización manual
python integracion_google_sheets.py

# Sincronización automática (con n8n)
# El workflow workflow-sheets-sync.json corre cada 5 minutos
```

## 🔧 Configuración Avanzada

### Variables de Entorno

Las principales variables de configuración en `.env`:

```env
# === OpenAI Configuration ===
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# === MongoDB ===
MONGODB_URI=mongodb://localhost:27017/bmc_chat

# === Google Sheets ===
GOOGLE_SHEET_ID=tu-sheet-id
GOOGLE_SERVICE_ACCOUNT_EMAIL=tu-email@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# === WhatsApp Business ===
WHATSAPP_ACCESS_TOKEN=tu-token
WHATSAPP_PHONE_NUMBER_ID=tu-phone-id
WHATSAPP_VERIFY_TOKEN=tu-verify-token
WHATSAPP_BUSINESS_ID=tu-business-id

# === MercadoLibre (Opcional) ===
MELI_ACCESS_TOKEN=tu-meli-token
MELI_REFRESH_TOKEN=tu-refresh-token
MELI_CLIENT_ID=tu-client-id
MELI_CLIENT_SECRET=tu-client-secret
MELI_SELLER_ID=tu-seller-id

# === API Configuration ===
PY_CHAT_SERVICE_URL=http://localhost:8000
N8N_WEBHOOK_URL_EXTERNAL=https://tu-n8n-url.com

# === Chat Configuration ===
CHAT_USE_FULL_IA=true  # true para usar OpenAI, false para pattern matching
```

### Base de Conocimiento

El sistema usa archivos JSON para almacenar conocimiento de productos:

- `conocimiento_completo.json` - Base consolidada
- `data/shopify/shopify_products_raw.json` - Productos de Shopify
- `data/mercadolibre/mercadolibre_questions_raw.json` - Preguntas frecuentes de ML
- `config_conocimiento.json` - Configuración de conocimiento

### Estados de Cotización

| Estado | Descripción |
|--------|-------------|
| **Pendiente** | Cotización creada, pendiente de revisión |
| **Asignado** | Asignada a vendedor específico |
| **Adjunto** | Con archivo de cotización adjunto |
| **Listo** | Lista para enviar al cliente |
| **Enviado** | Presupuesto enviado al cliente |
| **Confirmado** | Cliente confirmó la compra |
| **Rechazado** | Cliente rechazó la cotización |

### Zonas de Flete

```python
ZONAS_FLETE = {
    "montevideo": {"base": 50, "factor": 1.0},
    "canelones": {"base": 80, "factor": 1.2},
    "maldonado": {"base": 120, "factor": 1.5},
    "colonia": {"base": 150, "factor": 1.8},
    "interior": {"base": 200, "factor": 2.0}
}
```

## 🛠️ Desarrollo y Personalización

### Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente (Usuario)                     │
│          (WhatsApp, Web UI, CLI, API directa)           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                    │
│  • Endpoints REST                                        │
│  • Request validation                                    │
│  • Response formatting                                   │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              IA Conversacional (OpenAI)                  │
│  • Natural language processing                           │
│  • Intent classification                                 │
│  • Entity extraction                                     │
│  • Context management                                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│             Sistema de Cotizaciones                      │
│  • Price calculation                                     │
│  • Quote generation                                      │
│  • Validation logic                                      │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                  Persistencia & Sync                     │
│  • MongoDB (conversaciones, cotizaciones)                │
│  • Google Sheets (equipo de ventas)                      │
│  • n8n (workflows automatizados)                         │
└─────────────────────────────────────────────────────────┘
```

### Agregar Nuevos Productos

1. Editar base de conocimiento en `conocimiento_completo.json`:

```json
{
  "productos": [
    {
      "nombre": "Producto Nuevo",
      "categoria": "categoria",
      "descripcion": "Descripción detallada",
      "especificaciones": {
        "espesores": ["50mm", "100mm"],
        "colores": ["Blanco", "Gris"],
        "precios": {
          "50mm": 100.00,
          "100mm": 150.00
        }
      }
    }
  ]
}
```

2. Actualizar sistema:
```bash
python consolidar_conocimiento.py
python validar_integracion.py
```

### Personalizar Prompts de IA

Editar `ia_conversacional_integrada.py`:

```python
SYSTEM_PROMPT = """
Eres un asistente de ventas experto de BMC Uruguay.
Tu objetivo es ayudar a los clientes a obtener cotizaciones...
[Personalizar según necesidad]
"""
```

### Agregar Nuevos Endpoints API

En `api_server.py`:

```python
@app.post("/mi-nuevo-endpoint")
async def mi_nuevo_endpoint(request: MiRequest):
    """Descripción del endpoint"""
    # Lógica aquí
    return {"success": True, "data": resultado}
```

### Extender Dashboard

En `src/app/` crear nuevas rutas y componentes:

```typescript
// src/app/mi-nueva-pagina/page.tsx
export default function MiNuevaPagina() {
  return <div>Mi nuevo componente</div>
}
```

## 🔍 Solución de Problemas

### Problemas Comunes

#### ❌ Error: "OpenAI API key not found"
**Solución:**
```bash
# Verificar que existe .env
ls -la .env

# Verificar variable de entorno
cat .env | grep OPENAI_API_KEY

# O exportar temporalmente
export OPENAI_API_KEY=sk-tu-api-key
```

#### ❌ Error: "MongoDB connection failed"
**Solución:**
```bash
# Si usas Docker
docker-compose up -d mongodb

# Verificar que está corriendo
docker ps | grep mongodb

# Si usas MongoDB Atlas, verifica la connection string
# Debe incluir username, password y cluster correcto
```

#### ❌ Error: "Module not found"
**Solución:**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt

# Para el frontend
npm install
```

#### ❌ Bot no responde o respuestas genéricas
**Solución:**
```bash
# 1. Verificar API key de OpenAI
echo $OPENAI_API_KEY

# 2. Verificar conocimiento actualizado
python validar_integracion.py

# 3. Refrescar base de conocimiento
bash scripts/refresh_knowledge.sh

# 4. Ver logs del API server
tail -f logs/api_server.log  # si existe
```

#### ❌ Error: "Permission denied" en scripts
**Solución:**
```bash
# Dar permisos de ejecución a todos los scripts
chmod +x *.sh
chmod +x scripts/*.sh
```

#### ❌ WhatsApp webhook no funciona
**Solución:**
1. Verificar que el `WHATSAPP_VERIFY_TOKEN` coincide en Meta y en `.env`
2. Usar ngrok para desarrollo local: `ngrok http 5678`
3. Verificar logs de n8n: http://localhost:5678/executions
4. Ver `SETUP_WHATSAPP.md` para configuración completa

#### ❌ Google Sheets no sincroniza
**Solución:**
1. Verificar Service Account tiene permisos en el Sheet
2. Verificar `GOOGLE_SHEET_ID` correcto en `.env`
3. Verificar formato del `GOOGLE_PRIVATE_KEY` (debe tener `\n`)
4. Ejecutar test: `python integracion_google_sheets.py`

### Logs y Debugging

```bash
# Ver logs del API server
python api_server.py  # logs en consola

# Ver logs de Docker
docker-compose logs -f chat-api
docker-compose logs -f mongodb
docker-compose logs -f n8n

# Ver logs de n8n workflows
# Acceder a http://localhost:5678/executions

# Verificar estado del sistema
python validar_integracion.py

# Test de integración completa
python test_sistema_automatico.py
```

### Obtener Ayuda

Si sigues teniendo problemas:

1. **Revisa la documentación completa:**
   - `HOW_TO_RUN.md` - Guía de ejecución
   - `SETUP_WHATSAPP.md` - Configuración WhatsApp
   - `SETUP_CREDENTIALS_GUIDE.md` - Credenciales
   - `BMC_SYSTEM_GUIDE.md` - Guía completa

2. **Ejecuta diagnósticos:**
   ```bash
   python validar_integracion.py
   bash scripts/test-e2e-whatsapp.sh
   ```

3. **Revisa issues conocidos:**
   - Ver `IMPLEMENTATION_SUMMARY.md` para limitaciones conocidas
   - Ver `DETAILED_BRANCH_COMPARISON.md` para cambios recientes

## 📚 Documentación Adicional

El proyecto incluye documentación completa en varios archivos:

### Guías de Configuración
- **[SETUP_CREDENTIALS_GUIDE.md](./SETUP_CREDENTIALS_GUIDE.md)** - Obtener y configurar credenciales
- **[SETUP_WHATSAPP.md](./SETUP_WHATSAPP.md)** - Configuración de WhatsApp Business API
- **[BMC_SYSTEM_GUIDE.md](./BMC_SYSTEM_GUIDE.md)** - Guía completa del sistema
- **[SETUP_COMPLETE_GUIDE.md](./SETUP_COMPLETE_GUIDE.md)** - Setup completo paso a paso

### Guías de Uso
- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Cómo ejecutar el sistema
- **[QUICK_START_SIMULATOR.md](./QUICK_START_SIMULATOR.md)** - Inicio rápido del simulador
- **[START_CHATBOT_NOW.md](./START_CHATBOT_NOW.md)** - Inicio rápido del chatbot
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Referencia rápida de comandos

### Documentación Técnica
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Resumen de implementación
- **[DETAILED_BRANCH_COMPARISON.md](./DETAILED_BRANCH_COMPARISON.md)** - Comparación detallada de cambios
- **[PLAN_IMPLEMENTATION_STATUS.md](./PLAN_IMPLEMENTATION_STATUS.md)** - Estado de implementación
- **[N8N_WORKFLOW_GUIDE.md](./N8N_WORKFLOW_GUIDE.md)** - Guía de workflows n8n
- **[VERCEL_DEPLOY_GUIDE.md](./VERCEL_DEPLOY_GUIDE.md)** - Deployment a Vercel

### Guías de Desarrollo
- **[CPANEL_HOSTING_GUIDE.md](./CPANEL_HOSTING_GUIDE.md)** - Hosting en cPanel
- **[.devcontainer/](./.devcontainer/)** - Configuración de Dev Containers
- **[AUTOMATED_AGENT_GUIDE.md](./AUTOMATED_AGENT_GUIDE.md)** - Guía de agente automatizado

## 🚀 Deployment

### Desarrollo Local

```bash
# Backend
python api_server.py

# Frontend
npm run dev
```

### Docker Compose (Recomendado)

```bash
# Iniciar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Vercel (Frontend)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Configurar variables de entorno
vercel env add MONGODB_URI
vercel env add OPENAI_API_KEY
# ... etc
```

Ver guía completa en `VERCEL_DEPLOY_GUIDE.md`

### Railway/Render (Backend + DB)

Opciones para deployment del backend Python:
- **Railway** - Deploy con Docker
- **Render** - Deploy con Dockerfile
- **Heroku** - Con Procfile

## 🤝 Contribución

### Workflow de Desarrollo

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer cambios y commit: `git commit -m "feat: descripción"`
3. Push: `git push origin feature/nueva-funcionalidad`
4. Crear Pull Request en GitHub
5. Esperar revisión y merge

### Convenciones de Código

- **Python:** Seguir PEP 8
- **TypeScript:** Seguir guía de estilo de Airbnb
- **Commits:** Usar Conventional Commits (feat, fix, docs, etc.)
- **Tests:** Escribir tests para nuevas funcionalidades

## 📞 Contacto y Soporte

### BMC Uruguay
- **Web:** https://bmcuruguay.com.uy
- **Email:** info@bmcuruguay.com.uy
- **Teléfono:** Consultar en sitio web

### Soporte Técnico
Para problemas técnicos:
1. Revisar sección "Solución de Problemas" arriba
2. Consultar documentación específica en carpeta `docs/`
3. Revisar issues conocidos en `IMPLEMENTATION_SUMMARY.md`

---

## 📄 Licencia

Sistema desarrollado específicamente para BMC Uruguay.  
Todos los derechos reservados © 2024 BMC Uruguay

---

**Versión:** 2.0  
**Última actualización:** Diciembre 2024  
**Desarrollado para:** BMC Uruguay  
**Stack:** Python 3.11+ • FastAPI • Next.js 16 • OpenAI GPT-4 • MongoDB • n8n
