# Sistema de Cotizaciones BMC Uruguay

Sistema completo de chatbot conversacional para la gestión de cotizaciones de productos de aislamiento térmico, desarrollado específicamente para BMC Uruguay. Integra IA conversacional, gestión de cotizaciones, integración con WhatsApp, y un dashboard web moderno.

## 🚀 Características Principales

### Backend (Python/FastAPI)
- **API REST completa** con FastAPI para procesamiento de mensajes y cotizaciones
- **IA Conversacional Integrada** con OpenAI para interacciones naturales
- **Gestión completa de cotizaciones** con seguimiento de estados
- **Cálculo automático de precios** basado en especificaciones técnicas
- **Integración con matriz de precios** actualizable desde bmcuruguay.com.uy
- **Validación inteligente de datos** - El bot solicita automáticamente información faltante
- **Integración con MongoDB** para persistencia de conversaciones
- **Sincronización con Google Sheets** del Administrador de Cotizaciones II
- **Integración con MercadoLibre** para sincronización de preguntas y productos
- **Sincronización con Shopify** para catálogo de productos

### Frontend (Next.js)
- **Dashboard web moderno** con interfaz React/Next.js
- **Chat interactivo** con UI similar a WhatsApp
- **Simulador de conversaciones** para testing
- **Visualización de cotizaciones** y análisis de datos
- **Gestión de contexto compartido** entre sesiones

### Infraestructura
- **Unified Launcher** - Punto de entrada único para todos los modos del sistema
- **Integración con n8n** para automatización de workflows
- **Integración con WhatsApp** para comunicación con clientes
- **Sistema de monitoreo** y logging automatizado
- **Deployment en Vercel** con configuración optimizada

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

## Estructura del Sistema

```
sistema-cotizaciones-bmc/
├── api_server.py                # Servidor FastAPI principal
├── unified_launcher.py          # Launcher unificado (punto de entrada)
├── sistema_cotizaciones.py     # Lógica principal del sistema de cotizaciones
├── utils_cotizaciones.py        # Utilidades de validación centralizada
├── ia_conversacional_integrada.py # IA conversacional con validación
├── chat_interactivo.py          # Chat interactivo con validación
├── simulate_chat_cli.py         # Simulador CLI mejorado
├── simulacion_agente.py         # Simulación de agente con validación
├── main.py                      # Sistema interactivo completo
├── config.py                    # Configuración centralizada
├── matriz_precios.json          # Matriz de precios y productos
│
├── python-scripts/              # Scripts Python organizados
│   ├── sistema_cotizaciones.py
│   ├── importar_datos_planilla.py
│   ├── generador_plantillas.py
│   ├── fetch_shopify_products.py
│   ├── fetch_mercadolibre_questions.py
│   └── ...
│
├── src/app/                     # Next.js Frontend (App Router)
│   ├── api/                     # API Routes (Next.js)
│   │   ├── chat/               # Endpoints de chat
│   │   ├── quote-engine/       # Motor de cotizaciones
│   │   ├── whatsapp/           # Webhooks de WhatsApp
│   │   └── ...
│   ├── chat/                   # Página de chat
│   ├── simulator/              # Simulador web
│   └── ...
│
├── nextjs-app/                  # Next.js App (legacy/alternativa)
│   ├── package.json
│   └── ...
│
├── scripts/                     # Scripts de automatización
│   ├── setup_chatbot_env.sh
│   ├── refresh_knowledge.sh
│   ├── run_full_stack.sh
│   └── ...
│
├── n8n_workflows/               # Workflows de n8n
│   └── ...
│
├── .devcontainer/              # Configuración de Dev Container
│   ├── devcontainer.json
│   └── post-create.sh
│
├── requirements.txt             # Dependencias Python
├── vercel.json                  # Configuración de Vercel
└── README.md                    # Este archivo
```

## 🌐 Trabajo en la Nube (Codespaces / Cursor Cloud)

### Configuración Inicial

1. **Sincroniza el repositorio:**
   ```bash
   git push origin <rama>
   ```
   Esto asegura que el workspace cloud arranque con la última versión.

2. **Crea el workspace remoto:**
   - **GitHub Codespaces:** En la página del repo → `Code → Create codespace on main`
   - **Cursor Cloud:** Abre Cursor → `New Cloud Workspace` → Pega la URL del repositorio

3. **Dev Container automático:**
   Al iniciar, `.devcontainer/devcontainer.json` cargará:
   - Contenedor `python:3.11` con Node.js 20
   - Ejecutará `.devcontainer/post-create.sh` para instalar:
     - Dependencias Python (`requirements.txt`)
     - Dependencias Node.js (`nextjs-app`)

4. **Variables y secretos:**
   Usa estos archivos para configurar credenciales:
   - `SETUP_CREDENTIALS_GUIDE.md` - Configuración general
   - `SETUP_WHATSAPP.md` - Configuración de WhatsApp
   
   Puedes usar Secrets de GitHub/Cursor para almacenar API keys de forma segura.

5. **Ciclo local ↔ nube:**
   - Antes de cambiar de entorno: `git pull`
   - Al terminar en la nube: `git commit && git push`

### Verificación Rápida

Dentro del workspace cloud:

```bash
# Validar flujo principal
python unified_launcher.py --mode api

# Probar UI
cd nextjs-app && npm run dev
# Accede en http://localhost:3000

# Ejecutar scripts específicos
python python-scripts/fetch_shopify_products.py
```

### Deployment Automático

Una vez que el workspace funcione, considera activar:
- **GitHub Actions** - CI/CD automático
- **Vercel** - Deployment automático del frontend
- Consulta `DEPLOYMENT_GUIDE.md` y `VERCEL_DEPLOY_GUIDE.md` para más detalles

## Instalación

### Instalación Automática (Recomendada)

El **Unified Launcher** maneja automáticamente toda la instalación y configuración.

1. **Requisitos del sistema:**
   - Python 3.11 o superior (recomendado)
   - Node.js 18+ (opcional, para frontend Next.js)
   - Git (para clonar el repositorio)

2. **Clonar el repositorio:**
   ```bash
   git clone [url-del-repositorio]
   cd sistema-cotizaciones-bmc
   ```

3. **Ejecutar el Unified Launcher:**
   
   **Windows:**
   ```batch
   launch.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./launch.sh
   ```
   
   **O directamente:**
   ```bash
   python unified_launcher.py
   ```

   El launcher automáticamente:
   - ✅ Verifica Python 3.11+
   - ✅ Crea entorno virtual (`.venv`)
   - ✅ Instala dependencias Python (`requirements.txt`)
   - ✅ Configura Node.js (si está disponible)
   - ✅ Crea archivo `.env` si no existe
   - ✅ Muestra menú interactivo con todos los modos

4. **Configurar variables de entorno:**
   
   Edita el archivo `.env` creado y agrega tus credenciales:
   ```bash
   OPENAI_API_KEY=tu_api_key_aqui
   MONGODB_URI=tu_mongodb_uri_aqui
   MELI_ACCESS_TOKEN=tu_token_meli  # Opcional
   MELI_SELLER_ID=tu_seller_id      # Opcional
   ```

   Consulta `SETUP_CREDENTIALS_GUIDE.md` para más detalles.

### Instalación Manual (Avanzada)

Si prefieres instalar manualmente:

1. **Configurar entorno virtual:**
   ```bash
   bash scripts/setup_chatbot_env.sh
   source .venv/bin/activate  # Linux/Mac
   # o
   .venv\Scripts\activate     # Windows
   ```

2. **Instalar dependencias Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar dependencias Node.js (opcional, para frontend):**
   ```bash
   cd nextjs-app
   npm install
   cd ..
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

## Actualizar conocimiento entrenado

Cada vez que recibas nuevos datos de conversaciones o quieras sincronizar el catálogo:

1. (Opcional) Lanza manualmente los ingesters:
   ```bash
   source .venv/bin/activate
   python python-scripts/fetch_shopify_products.py
   python python-scripts/fetch_mercadolibre_questions.py  # requiere MELI_ACCESS_TOKEN/MELI_SELLER_ID
   # o usa un CSV exportado:
   # python python-scripts/fetch_mercadolibre_questions.py --csv-export data/mercadolibre/export.csv
   ```
   > Tip: Usa `python python-scripts/mercadolibre_oauth_helper.py` para generar y
   > refrescar los tokens (`MELI_ACCESS_TOKEN`/`MELI_REFRESH_TOKEN`) directamente
   > desde tu App ID y client secret.
2. Ejecuta `bash scripts/refresh_knowledge.sh`. El script:
   - Activa `.venv`
   - Corre los ingesters anteriores automáticamente (controlables con `RUN_SHOPIFY_SYNC` y `RUN_MELI_SYNC`)
   - Consolida todos los JSON de conocimiento
   - Ejecuta `python validar_integracion.py`
   - Registra el resultado en `logs/automation/ingestion_*.log`
3. Si alguna validación falla, revisa los reportes en `reporte_validacion.json/.txt` antes de iniciar el chatbot.

Consulta [DATA_INGESTION.md](DATA_INGESTION.md) para formatos, logs y consejos adicionales.

## 🚀 Iniciar el Sistema

### Opción 1: Unified Launcher (⭐ Recomendado)

El **Unified Launcher** es la forma más fácil de iniciar el sistema. Maneja automáticamente la instalación, configuración y ejecución.

**Windows:**
```batch
launch.bat
```

**Linux/Mac:**
```bash
./launch.sh
```

**Directo:**
```bash
python unified_launcher.py
```

#### Modos Disponibles

El launcher ofrece un menú interactivo con estos modos:

1. **Interactive Chatbot** - Chat interactivo en terminal
2. **API Server** - Servidor FastAPI (puerto 8000)
3. **Chat Simulator** - Simulador de conversaciones
4. **Enhanced CLI Simulator** - Simulador mejorado con formato
5. **Main System Menu** - Menú del sistema completo
6. **Automated Agent System** - Sistema de agentes automatizado
7. **System Complete** - Sistema completo integrado
8. **Next.js Dashboard (Dev)** - Dashboard de desarrollo
9. **Next.js Dashboard (Production)** - Dashboard de producción
10. **Full Stack** - API + Dashboard juntos

#### Modos Directos (sin menú)

```bash
# Chat interactivo
python unified_launcher.py --mode chat

# API Server
python unified_launcher.py --mode api

# Simulador
python unified_launcher.py --mode simulator

# Full Stack (API + Dashboard)
python unified_launcher.py --mode fullstack

# Solo setup (sin ejecutar)
python unified_launcher.py --setup-only

# Skip setup (asume configurado)
python unified_launcher.py --skip-setup --mode api
```

Para documentación completa, ver **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** y **[HOW_TO_RUN.md](./HOW_TO_RUN.md)**

### Opción 2: Inicio Manual

Si prefieres iniciar componentes manualmente:

**Terminal 1 - API Server:**
```bash
source .venv/bin/activate  # Linux/Mac
# o .venv\Scripts\activate  # Windows
python api_server.py
```

**Terminal 2 - Chat Interactivo:**
```bash
source .venv/bin/activate
python chat_interactivo.py
```

**Terminal 3 - Simulador CLI:**
```bash
source .venv/bin/activate
python simulate_chat_cli.py
```

**Terminal 4 - Next.js Frontend (opcional):**
```bash
cd nextjs-app
npm run dev
# O para producción:
npm run build && npm start
```

### Opción 3: Script de Ejecución Completa

Usa el wrapper para ejecutar todo en un solo comando:

```bash
bash scripts/run_full_stack.sh
```

Este script:
- Verifica/crea `.venv`
- Consolida y valida el conocimiento
- Inicia `api_server.py` en background
- Genera reportes en `logs/automation/`

### Persistencia y Monitoreo

Consulta **[MONITOREO_AUTOMATIZADO.md](./MONITOREO_AUTOMATIZADO.md)** para:
- Habilitar MongoDB como fallback
- Programar tareas automáticas (cron, launchd, systemd)
- Configurar refresh automático del conocimiento

## Uso del Sistema

### 1. Crear Nueva Cotización

El sistema permite crear cotizaciones de forma interactiva:

- **Datos del cliente:** nombre, teléfono, dirección, zona
- **Especificaciones del producto:** tipo, espesor, relleno, color
- **Dimensiones:** largo y ancho en metros
- **Terminaciones:** frontal, superior, laterales
- **Servicios:** anclajes, traslado
- **Información adicional:** forma de contacto, observaciones

### 2. Buscar Cotizaciones

Opciones de búsqueda disponibles:
- Por nombre del cliente
- Por número de teléfono
- Por rango de fechas
- Mostrar todas las cotizaciones

### 3. Generar Reportes

El sistema genera reportes detallados que incluyen:
- Información del cliente
- Especificaciones técnicas del producto
- Cálculos de dimensiones y precios
- Desglose de costos
- Información de contacto de BMC Uruguay

### 4. Exportar Datos

- **Cotizaciones:** Exporta todas las cotizaciones a JSON
- **Plantillas:** Exporta las plantillas de cotización
- **Configuración:** Exporta la matriz de precios

## Interfaz Web (Next.js)

El sistema incluye un dashboard web completo desarrollado con Next.js.

### Iniciar Frontend

**Desarrollo:**
```bash
cd nextjs-app
npm run dev
# Accede en http://localhost:3000
```

**Producción:**
```bash
cd nextjs-app
npm run build
npm start
```

O usa el Unified Launcher:
```bash
python unified_launcher.py --mode fullstack
```

### Páginas Disponibles

- **`/chat`** - Interfaz de chat principal
- **`/simulator`** - Simulador de conversaciones
- **`/bmc-chat`** - Chat específico para BMC
- **`/chat-evolved`** - Versión evolucionada del chat

### API Endpoints (Next.js)

El frontend expone varios endpoints en `/api`:

- `/api/chat` - Procesamiento de mensajes
- `/api/chat/stream` - Streaming de respuestas
- `/api/quote-engine` - Motor de cotizaciones
- `/api/whatsapp/webhook` - Webhook de WhatsApp
- `/api/sheets/sync` - Sincronización con Google Sheets
- `/api/health` - Health check
- Y más...

### Interfaz de Chat Local (Legacy)

Para testing local con interfaz HTML standalone:

- **Guía de Usuario**: Ver `CHAT_INTERFACE_GUIDE.md`
- **Guía de Desarrollador**: Ver `CHAT_INTERFACE_DEVELOPER.md`

## Productos Soportados

### Isodec
- **Descripción:** Panel aislante térmico con núcleo de EPS
- **Espesores:** 50mm, 75mm, 100mm, 125mm, 150mm
- **Rellenos:** EPS, Poliuretano, Lana de roca
- **Colores:** Blanco, Gris, Personalizado
- **Terminaciones:** Gotero, Hormigón, Aluminio

### Poliestireno Expandido
- **Descripción:** Aislante térmico de poliestireno expandido
- **Espesores:** 25mm, 50mm, 75mm, 100mm

### Lana de Roca
- **Descripción:** Aislante térmico y acústico de lana de roca
- **Espesores:** 50mm, 75mm, 100mm

## Fórmulas de Cálculo

### Precio Base
```
Precio base = Área (m²) × Precio por m²
```

### Factores de Ajuste
- **Espesor:** 0.8 (50mm) a 1.2 (150mm)
- **Color:** 1.0 (Blanco) a 1.15 (Personalizado)
- **Terminaciones:** +5% (Gotero) a +15% (Aluminio)
- **Servicios:** Incluidos o con descuento

### Precio Final
```
Precio final = Precio base × Factor espesor × Factor color × Factor terminaciones × Factor servicios
```

## Integración con Google Sheets

El sistema puede importar datos desde la planilla "Administrador de Cotizaciones II":

1. **Exportar datos de Google Sheets** a CSV
2. **Usar el importador** para procesar los datos
3. **Mapear campos** entre la planilla y el sistema
4. **Calcular precios** automáticamente

### Campos Mapeados

| Google Sheets | Sistema |
|---------------|---------|
| Cliente | cliente.nombre |
| Telefono-Contacto | cliente.telefono |
| Direccion / Zona | cliente.direccion |
| Producto | especificaciones.producto |
| Espesor | especificaciones.espesor |
| Relleno | especificaciones.relleno |
| Largo (M) | especificaciones.largo_metros |
| Ancho (M) | especificaciones.ancho_metros |
| Color | especificaciones.color |
| TerminaFront | especificaciones.termina_front |
| TerminaSup | especificaciones.termina_sup |
| Termina Lat. 1 | especificaciones.termina_lat_1 |
| Termina Lat. 2 | especificaciones.termina_lat_2 |
| Anclajes a | especificaciones.anclajes |
| Traslado | especificaciones.traslado |

## Plantillas de Cotización

### 1. Isodec - Cotización Estándar
- Para productos Isodec con especificaciones completas
- Incluye todos los campos técnicos
- Cálculo detallado de precios

### 2. Cotización Rápida
- Para estimaciones rápidas
- Campos mínimos requeridos
- Precio estimado por m²

### 3. Cotización Detallada
- Para cotizaciones completas
- Desglose de costos
- Incluye IVA y servicios

## Configuración

### Matriz de Precios (matriz_precios.json)

```json
{
  "productos": {
    "isodec": {
      "espesores_disponibles": {
        "100mm": {
          "precio_base": 150.00,
          "factor_espesor": 1.0
        }
      },
      "colores_disponibles": {
        "Blanco": {
          "precio_base": 0.00,
          "factor_color": 1.0
        }
      }
    }
  },
  "configuracion": {
    "moneda": "UYU",
    "iva_porcentaje": 22
  }
}
```

## Estados de Cotización

- **Pendiente:** Cotización creada, pendiente de asignación
- **Asignado:** Asignada a un vendedor
- **Enviado:** Enviada al cliente
- **Listo:** Lista para confirmación
- **Confirmado:** Confirmada por el cliente
- **Rechazado:** Rechazada por el cliente

## Asignaciones

- **MA:** Vendedor A
- **MO:** Vendedor B
- **RA:** Vendedor C
- **SPRT:** Soporte técnico
- **Ref:** Referencia

## Enlaces de Productos

El sistema incluye enlaces directos a los productos en bmcuruguay.com.uy:

- [Isodec](https://bmcuruguay.com.uy/productos/isodec)
- [Poliestireno](https://bmcuruguay.com.uy/productos/poliestireno)
- [Lana de Roca](https://bmcuruguay.com.uy/productos/lana-roca)

## 🔧 Desarrollo y Personalización

### Agregar Nuevos Productos

1. Editar `matriz_precios.json`
2. Agregar el producto con sus especificaciones
3. Actualizar el sistema con `actualizar_precio_producto()`
4. Ejecutar `bash scripts/refresh_knowledge.sh` para actualizar el conocimiento

### Crear Nuevas Plantillas

1. Usar `generador_plantillas.py` o `python-scripts/generador_plantillas.py`
2. Definir campos requeridos y opcionales
3. Crear fórmulas de cálculo
4. Generar templates HTML/PDF

### Modificar Fórmulas de Cálculo

Editar los métodos en `SistemaCotizacionesBMC` (`sistema_cotizaciones.py`):
- `_calcular_factor_espesor()`
- `_calcular_factor_color()`
- `_calcular_factor_terminaciones()`
- `_calcular_factor_anclajes()`
- `_calcular_factor_traslado()`

### Agregar Nuevos Endpoints API

1. Editar `api_server.py` para endpoints FastAPI
2. O agregar rutas en `src/app/api/` para Next.js API routes
3. Documentar en OpenAPI/Swagger (FastAPI lo genera automáticamente)

### Personalizar Frontend

1. Editar componentes en `src/app/components/`
2. Modificar páginas en `src/app/`
3. Actualizar estilos en `src/app/globals.css`
4. Consulta `CHAT_INTERFACE_DEVELOPER.md` para más detalles

## 🔍 Solución de Problemas

### Errores Comunes

**Error: "Producto no encontrado"**
- Verificar que el producto esté en `matriz_precios.json`
- Usar códigos exactos (isodec, poliestireno, lana_roca)
- Ejecutar `bash scripts/refresh_knowledge.sh` para actualizar conocimiento

**Error: "Precio no calculado"**
- Verificar que el precio base esté configurado en `matriz_precios.json`
- Revisar las especificaciones del producto
- Verificar logs en `logs/` para más detalles

**Error: "Archivo no encontrado"**
- Verificar que `matriz_precios.json` esté en el directorio raíz
- Verificar permisos de lectura/escritura
- Verificar que el entorno virtual esté activado

**Error: "Module not found"**
- Activar entorno virtual: `source .venv/bin/activate`
- Instalar dependencias: `pip install -r requirements.txt`
- Verificar que estás en el directorio correcto

**Error: "API connection failed"**
- Verificar que `api_server.py` esté corriendo
- Verificar que el puerto 8000 esté disponible
- Verificar variables de entorno en `.env`

**Error: "OpenAI API key not found"**
- Verificar que `OPENAI_API_KEY` esté en `.env`
- Consulta `SETUP_CREDENTIALS_GUIDE.md` para configuración

### Logs y Debugging

- **Logs del launcher:** `logs/launcher.log`
- **Logs de la API:** `logs/api_server.log`
- **Logs de automatización:** `logs/automation/`
- **Reportes de validación:** `reporte_validacion.json/.txt`

### Obtener Ayuda

- Consulta la documentación en los archivos `.md` del proyecto
- Revisa `HOW_TO_RUN.md` para guías de ejecución
- Consulta `TESTING_GUIDE.md` para guías de testing

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema:

- **Email:** info@bmcuruguay.com.uy
- **Web:** https://bmcuruguay.com.uy
- **Teléfono:** +598 XX XXX XXX

## 📚 Documentación Adicional

### Guías Principales

- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Cómo ejecutar el sistema
- **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** - Documentación completa del launcher
- **[START_HERE.md](./START_HERE.md)** - Guía de inicio rápido
- **[DATA_INGESTION.md](./DATA_INGESTION.md)** - Sincronización de conocimiento
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Guía de deployment
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Guía de testing

### Configuración

- **[SETUP_CREDENTIALS_GUIDE.md](./SETUP_CREDENTIALS_GUIDE.md)** - Configuración de credenciales
- **[SETUP_WHATSAPP.md](./SETUP_WHATSAPP.md)** - Configuración de WhatsApp
- **[MONITOREO_AUTOMATIZADO.md](./MONITOREO_AUTOMATIZADO.md)** - Monitoreo y automatización

### Interfaces

- **[CHAT_INTERFACE_GUIDE.md](./CHAT_INTERFACE_GUIDE.md)** - Guía de usuario del chat
- **[CHAT_INTERFACE_DEVELOPER.md](./CHAT_INTERFACE_DEVELOPER.md)** - Guía de desarrollador

### Integraciones

- **[README_INTEGRACION_N8N.md](./README_INTEGRACION_N8N.md)** - Integración con n8n
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Guía de integraciones

### Deployment

- **[VERCEL_DEPLOY_GUIDE.md](./VERCEL_DEPLOY_GUIDE.md)** - Deployment en Vercel
- **[RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)** - Deployment en Railway
- **[CPANEL_HOSTING_GUIDE.md](./CPANEL_HOSTING_GUIDE.md)** - Hosting en cPanel

## Licencia

Sistema desarrollado específicamente para BMC Uruguay. Todos los derechos reservados.

---

## 📊 Estado del Proyecto

**Versión:** 2.0  
**Última actualización:** Enero 2025  
**Desarrollado para:** BMC Uruguay

### Componentes Activos

✅ **Backend FastAPI** - API REST completa y funcional  
✅ **Frontend Next.js** - Dashboard web moderno  
✅ **Unified Launcher** - Sistema de ejecución unificado  
✅ **IA Conversacional** - Integración con OpenAI  
✅ **Sistema de Cotizaciones** - Lógica de negocio completa  
✅ **Integración WhatsApp** - Webhooks y comunicación  
✅ **Integración n8n** - Automatización de workflows  
✅ **MongoDB** - Persistencia de datos  
✅ **Google Sheets** - Sincronización de datos  
✅ **Shopify/MercadoLibre** - Sincronización de productos  

### Próximos Pasos

- Mejoras en la UI del dashboard
- Optimización de performance
- Expansión de integraciones
- Mejoras en el sistema de monitoreo

---

**Desarrollado específicamente para BMC Uruguay. Todos los derechos reservados.**
