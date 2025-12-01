# Sistema de Cotizaciones BMC Uruguay

Sistema completo full-stack para la gestión de cotizaciones de productos de aislamiento térmico, desarrollado específicamente para BMC Uruguay. Integra un backend Python (FastAPI) con un frontend Next.js moderno, proporcionando una experiencia conversacional completa para generar cotizaciones automáticas.

## Características Principales

- **Sistema Conversacional Inteligente** - Chatbot con IA que guía a los clientes en la creación de cotizaciones
- **Backend FastAPI** - API REST robusta para procesamiento de mensajes y cotizaciones
- **Dashboard Next.js** - Interfaz web moderna con métricas, análisis y gestión de cotizaciones
- **Gestión completa de cotizaciones** con seguimiento de estados
- **Cálculo automático de precios** basado en especificaciones técnicas
- **Integración con matriz de precios** actualizable desde bmcuruguay.com.uy
- **Plantillas personalizables** para diferentes tipos de cotizaciones
- **Integración con Google Sheets** - Sincronización bidireccional con planillas
- **Integración con WhatsApp** - Respuestas automáticas vía WhatsApp Business API
- **Integración con MercadoLibre** - Gestión de productos y preguntas
- **Base de datos MongoDB** - Persistencia de conversaciones y cotizaciones
- **Mapeo automático de productos** con enlaces web
- **Búsqueda avanzada** por cliente, teléfono, fecha
- **Exportación de datos** en formato JSON, CSV, XLSX
- **Reportes detallados** con análisis y tendencias
- **Sistema modular** con componentes independientes
- **Validación inteligente de datos** - El bot solicita automáticamente información faltante

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
├── unified_launcher.py          # 🚀 Punto de entrada principal (recomendado)
├── launch.sh / launch.bat       # Scripts de inicio rápido
│
├── api_server.py                # Servidor FastAPI (backend)
├── python-scripts/              # Módulos Python principales
│   ├── sistema_cotizaciones.py      # Lógica principal del sistema
│   ├── ia_conversacional_integrada.py # IA conversacional con validación
│   ├── chat_interactivo.py          # Chat interactivo con validación
│   ├── simulacion_agente.py         # Simulación de agente
│   ├── integracion_whatsapp.py      # Integración WhatsApp
│   ├── integracion_google_sheets.py  # Integración Google Sheets
│   ├── mercadolibre_store.py        # Integración MercadoLibre
│   ├── config.py                    # Configuración centralizada
│   └── ...                         # Otros módulos
│
├── src/app/                     # Aplicación Next.js (frontend)
│   ├── api/                     # API Routes de Next.js
│   │   ├── chat/               # Endpoints de chat
│   │   ├── quote-engine/       # Motor de cotizaciones
│   │   ├── whatsapp/           # Webhooks WhatsApp
│   │   ├── sheets/             # Sincronización Google Sheets
│   │   ├── mercado-libre/      # Integración MercadoLibre
│   │   └── ...                 # Otros endpoints
│   ├── chat/                    # Página de chat
│   ├── simulator/               # Simulador de conversaciones
│   ├── components/              # Componentes React
│   └── ...
│
├── package.json                 # Dependencias Node.js
├── requirements.txt             # Dependencias Python
├── next.config.js              # Configuración Next.js
│
├── scripts/                    # Scripts de utilidad
│   ├── setup_chatbot_env.sh   # Setup del entorno
│   ├── refresh_knowledge.sh    # Actualizar conocimiento
│   └── ...
│
├── data/                       # Datos y conocimiento
│   └── *.json                  # Archivos de conocimiento consolidado
│
├── .devcontainer/              # Configuración Dev Container
│   └── devcontainer.json       # Para Codespaces/Cursor Cloud
│
└── README.md                   # Esta documentación
```

## Trabajo en la Nube (Codespaces / Cursor Cloud)

1. **Sincroniza el repositorio:** verifica que tu rama local esté en GitHub (`git push origin <rama>`). Esto asegura que el workspace cloud arranque con la última versión.
2. **Crea el workspace remoto:**
   - **GitHub Codespaces:** en la página del repo haz clic en `Code → Create codespace on main`.
   - **Cursor Cloud:** abre Cursor, selecciona `New Cloud Workspace` y pega la URL del repositorio.
3. **Dev Container automático:** al iniciar, el archivo `.devcontainer/devcontainer.json` cargará el contenedor `python:3.11` con Node.js 20 y ejecutará `.devcontainer/post-create.sh` para instalar dependencias de Python (`requirements.txt`) y Node (`nextjs-app`).
4. **Variables y secretos:** usa `SETUP_CREDENTIALS_GUIDE.md` y `SETUP_WHATSAPP.md` para cargar las API keys o tokens necesarios dentro del workspace (puedes usar los Secrets de GitHub/Cursor).
5. **Ciclo local ↔ nube:** antes de cambiar de entorno haz `git pull` y al terminar en la nube confirma tus cambios (`git commit && git push`) para evitar divergencias.

### Verificación rápida dentro del workspace

- `python ejecutar_sistema.py` para validar el flujo principal.
- `cd nextjs-app && npm run dev` para probar la UI en `http://localhost:3000`.
- `python gestionar_servicios.py` o los scripts de `python-scripts/` según lo que necesites probar.

Una vez que el workspace funcione, considera activar despliegues automáticos (por ejemplo GitHub Actions + Vercel) reutilizando los mismos comandos usados en el contenedor.

## Instalación

### Requisitos del Sistema

- **Python 3.11+** (recomendado 3.11 o superior)
- **Node.js 18+** (opcional, para el dashboard Next.js)
- **MongoDB** (opcional, para persistencia de conversaciones)
- **Docker** (opcional, para MongoDB local)

### Instalación Automática (Recomendada)

El **Unified Launcher** maneja automáticamente la instalación y configuración:

**Windows:**
```batch
launch.bat
```

**Linux/Mac:**
```bash
chmod +x launch.sh
./launch.sh
```

**O directamente:**
```bash
python unified_launcher.py
```

El launcher:
- ✅ Verifica requisitos (Python 3.11+, Node.js)
- ✅ Crea entorno virtual (`.venv`)
- ✅ Instala dependencias Python (`requirements.txt`)
- ✅ Instala dependencias Node.js (`package.json`)
- ✅ Configura archivo `.env` si no existe
- ✅ Muestra menú interactivo con todos los modos

### Instalación Manual

Si prefieres instalar manualmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [url-del-repositorio]
   cd sistema-cotizaciones-bmc
   ```

2. **Configurar entorno Python:**
   ```bash
   # Crear entorno virtual
   python -m venv .venv
   
   # Activar entorno (Linux/Mac)
   source .venv/bin/activate
   # O en Windows
   .venv\Scripts\activate
   
   # Instalar dependencias
   pip install -r requirements.txt
   ```

3. **Configurar entorno Node.js (para dashboard):**
   ```bash
   # Instalar dependencias
   npm install
   ```

4. **Configurar variables de entorno:**
   ```bash
   # Copiar archivo de ejemplo
   cp .env.example .env
   
   # Editar .env y agregar tus credenciales:
   # - OPENAI_API_KEY
   # - MONGODB_URI (opcional)
   # - GOOGLE_SHEET_ID (opcional)
   # - WHATSAPP_ACCESS_TOKEN (opcional)
   ```

5. **Verificar instalación:**
   ```bash
   python unified_launcher.py --setup-only
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

## 🚀 Iniciar el Sistema - Unified Launcher (Recomendado)

La forma más fácil de iniciar el sistema es usando el **Unified Launcher**, que maneja automáticamente la instalación, configuración y ejecución.

### Inicio Rápido

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

### ¿Qué hace el Unified Launcher?

- ✅ **Verifica requisitos** (Python 3.11+, Node.js opcional)
- ✅ **Instala dependencias** automáticamente
- ✅ **Configura entorno** (crea .env si falta)
- ✅ **Menú interactivo** con todos los modos disponibles
- ✅ **Gestión de servicios** (API, MongoDB, Next.js)

### Modos Disponibles

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
```

Para documentación completa, ver **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)**

---

## Dashboard Next.js

El sistema incluye un dashboard web moderno construido con Next.js que proporciona:

- **Interfaz de Chat** - Conversación en tiempo real con el bot
- **Gestión de Cotizaciones** - Visualización y edición de cotizaciones
- **Analytics y Métricas** - KPIs, tendencias y análisis de conversiones
- **Simulador** - Prueba conversaciones sin WhatsApp
- **Integración Google Sheets** - Sincronización visual de datos
- **Gestión MercadoLibre** - Administración de productos y preguntas

### Iniciar el Dashboard

**Opción 1: Usando Unified Launcher**
```bash
python unified_launcher.py --mode fullstack
```

**Opción 2: Manualmente**
```bash
# Terminal 1: Iniciar API backend
python api_server.py

# Terminal 2: Iniciar dashboard Next.js
npm run dev
```

El dashboard estará disponible en `http://localhost:3000`

## Alternativa: Inicio Manual

Si prefieres iniciar componentes manualmente:

1. Activa el entorno: `source .venv/bin/activate`.
2. Exporta las variables sensibles (`OPENAI_API_KEY`, opcional `CHAT_USE_FULL_IA=true`).
3. Inicia la API: `python api_server.py` (carga el conocimiento consolidado al arrancar).
4. En otra terminal puedes interactuar con el bot:
   - `python python-scripts/simulate_chat_cli.py` para pruebas rápidas.
   - `CHAT_USE_FULL_IA=true python python-scripts/chat_interactivo.py` para la versión completa.

## Ejecución automatizada end-to-end

### Opción 1: Unified Launcher (Recomendado)

```bash
# Inicia todo el sistema con un comando
python unified_launcher.py --mode fullstack
```

### Opción 2: Script de ejecución completa

Usa el wrapper `bash scripts/run_full_stack.sh` para ejecutar todo en un solo comando:

1. Verifica/crea `.venv` (usa `scripts/setup_chatbot_env.sh` si falta).
2. Consolida y valida el conocimiento (genera reportes en `logs/automation/`).
3. Inicia `api_server.py` dejando el log en el mismo archivo.

Detén la API con `CTRL+C`. Si necesitas lanzar el simulador, abre otra terminal y usa los comandos de la sección anterior mientras la API sigue corriendo.

### Persistencia y monitoreo opcional

Consulta `[MONITOREO_AUTOMATIZADO.md](MONITOREO_AUTOMATIZADO.md)` para habilitar MongoDB como fallback y programar tareas (cron, launchd o systemd) que ejecuten `scripts/refresh_knowledge.sh` o `scripts/run_full_stack.sh`.

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

## Interfaz de Chat Local

El sistema incluye una interfaz de chat HTML standalone para testing y entrenamiento local.

### Inicio Rápido

```bash
# Iniciar todo el sistema (API + servidor HTTP)
bash start_chat_interface.sh
```

Esto iniciará:
- Servidor API FastAPI en `http://localhost:8000`
- Servidor HTTP en `http://localhost:8080` (o puerto disponible)
- Abrirá automáticamente el navegador

### Características

- ✅ **Interfaz completa**: Chat UI similar a producción
- ✅ **Persistencia de sesión**: IDs de sesión en localStorage
- ✅ **Historial de mensajes**: Últimos 100 mensajes guardados
- ✅ **Reintentos automáticos**: Hasta 3 intentos en caso de error
- ✅ **Indicador de conexión**: Estado visual de la conexión API
- ✅ **Panel de configuración**: Personalizar URL API y teléfono
- ✅ **Exportar conversaciones**: Descargar historial como JSON
- ✅ **Notificaciones**: Alertas cuando el bot responde
- ✅ **Accesibilidad**: Soporte completo para lectores de pantalla

### Documentación Completa

- **Guía de Usuario**: Ver `CHAT_INTERFACE_GUIDE.md`
- **Guía de Desarrollador**: Ver `CHAT_INTERFACE_DEVELOPER.md`

### Uso Básico

1. **Iniciar el sistema:**
   ```bash
   bash start_chat_interface.sh
   ```

2. **Abrir en navegador:**
   - El script abrirá automáticamente
   - O navegar manualmente a `http://localhost:8080/chat-interface.html`

3. **Enviar mensajes:**
   - Escribe en el campo de entrada
   - Presiona Enter o clic en el botón de enviar
   - El bot responderá automáticamente

4. **Configurar:**
   - Clic en el menú (⋯) para acceder a configuración
   - Cambiar URL API o teléfono por defecto
   - Los cambios se guardan automáticamente

### Testing y Entrenamiento

La interfaz es ideal para:
- **Testing local**: Probar respuestas del bot sin depender de WhatsApp
- **Entrenamiento**: Generar datasets de conversaciones reales
- **Desarrollo**: Iterar rápidamente en prompts y conocimiento
- **Validación**: Verificar flujos de conversación completos

Todos los mensajes y respuestas se guardan en localStorage y pueden exportarse para análisis.

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

## Integraciones

El sistema se integra con múltiples servicios externos para proporcionar una experiencia completa:

### OpenAI
- **Propósito:** Procesamiento de lenguaje natural y generación de respuestas conversacionales
- **Configuración:** Requiere `OPENAI_API_KEY` en `.env`
- **Uso:** Motor de IA del chatbot para entender y responder a los clientes

### MongoDB
- **Propósito:** Persistencia de conversaciones, cotizaciones y contexto compartido
- **Configuración:** Requiere `MONGODB_URI` en `.env` (opcional)
- **Uso:** Almacenar historial de conversaciones y cotizaciones

### Google Sheets
- **Propósito:** Sincronización bidireccional con planillas de gestión
- **Configuración:** Requiere credenciales de Service Account y `GOOGLE_SHEET_ID`
- **Uso:** Importar/exportar cotizaciones, sincronizar datos con planillas administrativas
- **Documentación:** Ver `INTEGRACION_GOOGLE_SHEETS_MEJORADA.md`

### WhatsApp Business API
- **Propósito:** Respuestas automáticas vía WhatsApp
- **Configuración:** Requiere `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- **Uso:** El bot responde automáticamente a mensajes de WhatsApp
- **Documentación:** Ver `SETUP_WHATSAPP.md`

### MercadoLibre
- **Propósito:** Gestión de productos y respuestas a preguntas
- **Configuración:** Requiere OAuth tokens (`MERCADO_LIBRE_APP_ID`, `MERCADO_LIBRE_CLIENT_SECRET`)
- **Uso:** Sincronizar productos, responder preguntas automáticamente
- **Endpoints:** `/api/mercado-libre/*`

### n8n (Opcional)
- **Propósito:** Automatización de workflows y orquestación
- **Configuración:** Requiere `N8N_WEBHOOK_URL`
- **Uso:** Integración con workflows de n8n para automatizaciones avanzadas
- **Documentación:** Ver `N8N_WORKFLOW_GUIDE.md`

## Integración con Google Sheets

El sistema puede importar y sincronizar datos con la planilla "Administrador de Cotizaciones II":

### Sincronización Automática

El sistema puede sincronizar automáticamente con Google Sheets usando la API:

1. **Configurar credenciales** de Google Service Account
2. **Especificar Sheet ID** en variables de entorno
3. **Sincronización bidireccional** - Los cambios se reflejan en ambos lados

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

### Uso desde el Dashboard

El dashboard Next.js incluye una interfaz visual para:
- Ver cotizaciones sincronizadas
- Importar/exportar datos
- Configurar sincronización automática

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

## Desarrollo y Personalización

### Agregar Nuevos Productos

1. Editar `matriz_precios.json`
2. Agregar el producto con sus especificaciones
3. Actualizar el sistema con `actualizar_precio_producto()`

### Crear Nuevas Plantillas

1. Usar `GeneradorPlantillas`
2. Definir campos requeridos y opcionales
3. Crear fórmulas de cálculo
4. Generar templates HTML/PDF

### Modificar Fórmulas de Cálculo

Editar los métodos en `SistemaCotizacionesBMC`:
- `_calcular_factor_espesor()`
- `_calcular_factor_color()`
- `_calcular_factor_terminaciones()`
- `_calcular_factor_anclajes()`
- `_calcular_factor_traslado()`

## Solución de Problemas

### Error: "Producto no encontrado"
- Verificar que el producto esté en `matriz_precios.json`
- Usar códigos exactos (isodec, poliestireno, lana_roca)

### Error: "Precio no calculado"
- Verificar que el precio base esté configurado
- Revisar las especificaciones del producto

### Error: "Archivo no encontrado"
- Verificar que `matriz_precios.json` esté en el directorio
- Verificar permisos de lectura/escritura

## Contacto y Soporte

Para soporte técnico o consultas sobre el sistema:

- **Email:** info@bmcuruguay.com.uy
- **Web:** https://bmcuruguay.com.uy
- **Teléfono:** +598 XX XXX XXX

## 📚 Referencias Rápidas

### Cheat Sheet CLI
Para comandos rápidos de Git, Node.js, deployment y más, consulta:
- **[CHEAT_SHEET_CLI.md](./CHEAT_SHEET_CLI.md)** - Guía completa de comandos CLI
- **[CHEAT_SHEET_CLI.json](./CHEAT_SHEET_CLI.json)** - Versión JSON para referencia programática

Incluye comandos para:
- 🔀 Git & GitHub (ramas, commits, PRs)
- 📦 Node.js & npm (desarrollo, build, testing)
- 🤖 Chatbot (embeddings, health checks, métricas)
- 🚀 Deployment (Vercel, Docker, PM2)
- 📚 Documentación (generación, validación)
- 🍎 Utilidades macOS

## Deployment

El sistema puede desplegarse en múltiples plataformas:

### Vercel (Recomendado para Next.js)

El dashboard Next.js puede desplegarse directamente en Vercel:

1. Conectar repositorio a Vercel
2. Configurar variables de entorno
3. Deploy automático en cada push

Ver **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** para instrucciones completas.

### Railway / Otros Plataformas

El backend Python (FastAPI) puede desplegarse en:
- Railway
- Heroku
- AWS/GCP/Azure
- Docker containers

Ver **[RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)** para más opciones.

## Documentación Adicional

- **[START_HERE.md](./START_HERE.md)** - Guía de inicio rápido
- **[HOW_TO_RUN.md](./HOW_TO_RUN.md)** - Instrucciones detalladas de ejecución
- **[UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md)** - Documentación completa del launcher
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Guía de deployment
- **[SETUP_WHATSAPP.md](./SETUP_WHATSAPP.md)** - Configuración WhatsApp
- **[N8N_WORKFLOW_GUIDE.md](./N8N_WORKFLOW_GUIDE.md)** - Integración n8n

## Licencia

Sistema desarrollado específicamente para BMC Uruguay. Todos los derechos reservados.

---

**Versión:** 2.0  
**Última actualización:** Enero 2025  
**Desarrollado para:** BMC Uruguay
