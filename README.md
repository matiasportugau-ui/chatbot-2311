# Sistema de Cotizaciones BMC Uruguay

Sistema completo para la gestión de cotizaciones de productos de aislamiento térmico, desarrollado específicamente para BMC Uruguay. Integra la lógica de cotización basada en plantillas, matriz de precios actualizable, y mapeo de productos con enlaces web.

## 📊 Estado del Sistema

| Componente | Estado | Descripción |
|------------|--------|-------------|
| **Backend Python** | ✅ Operativo | API FastAPI, IA conversacional, motor de cotizaciones |
| **Frontend Next.js** | ✅ Operativo | Dashboard, chat UI, simulador web |
| **Unified Launcher** | ✅ Operativo | Lanzador único para todos los modos |
| **n8n Workflows** | ✅ Configurado | Integración WhatsApp, Google Sheets, Analytics |
| **Base de Conocimiento** | ✅ Poblada | JSON consolidado con interacciones y productos |
| **Integración WhatsApp** | ⚙️ Requiere configuración | Necesita tokens de Meta Business |
| **Integración Google Sheets** | ⚙️ Requiere configuración | Necesita credenciales de servicio |
| **MongoDB** | ⚙️ Opcional | Persistencia avanzada (fallback a JSON) |

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.11+, FastAPI, OpenAI API
- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Automatización:** n8n, scripts Bash/Python
- **Integraciones:** WhatsApp Business API, Google Sheets API, MercadoLibre API
- **Base de Datos:** MongoDB (opcional), JSON (fallback)

## Características Principales

### 🤖 IA Conversacional
- **Bot inteligente** con OpenAI para respuestas naturales
- **Validación automática de datos** - Solicita información faltante
- **Extracción de entidades** desde mensajes de texto libre
- **Contexto de conversación** persistente por sesión

### 💰 Cotizaciones
- **Gestión completa** con seguimiento de estados
- **Cálculo automático de precios** basado en especificaciones técnicas
- **Integración con matriz de precios** actualizable
- **Plantillas personalizables** para diferentes tipos de cotizaciones

### 🔗 Integraciones
- **WhatsApp Business API** para atención automatizada
- **Google Sheets** para sincronización de datos
- **MercadoLibre** para ingesta de preguntas/pedidos
- **Shopify** para sincronización de productos
- **n8n** para automatización de workflows

### 📊 Dashboard y Reportes
- **Dashboard Next.js** con métricas en tiempo real
- **Reportes detallados** en HTML y PDF
- **Analytics** de conversaciones y conversiones
- **Exportación de datos** en formato JSON

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
bmc-chatbot-system/
├── 🚀 Lanzadores
│   ├── unified_launcher.py       # Lanzador principal unificado
│   ├── launch.sh                 # Wrapper Linux/Mac
│   ├── launch.bat                # Wrapper Windows
│   └── api_server.py             # Servidor API FastAPI
│
├── 🐍 Scripts Python (Raíz)
│   ├── sistema_cotizaciones.py   # Lógica principal de cotizaciones
│   ├── utils_cotizaciones.py     # Utilidades de validación
│   ├── ia_conversacional_integrada.py  # IA conversacional
│   ├── chat_interactivo.py       # Chat interactivo CLI
│   ├── simulacion_agente.py      # Simulador de agente
│   ├── main.py                   # Sistema interactivo completo
│   ├── demo.py                   # Demostración del sistema
│   └── validar_integracion.py    # Validación de integración
│
├── 📁 python-scripts/            # Scripts adicionales
│   ├── fetch_shopify_products.py # Ingesta desde Shopify
│   ├── fetch_mercadolibre_questions.py # Ingesta MercadoLibre
│   ├── integracion_google_sheets.py    # Google Sheets API
│   ├── n8n_integration.py        # Integración con n8n
│   └── ...                       # Más scripts especializados
│
├── 📁 scripts/                   # Scripts de utilidad
│   ├── setup_chatbot_env.sh      # Configuración del entorno
│   ├── refresh_knowledge.sh      # Actualización de conocimiento
│   ├── run_full_stack.sh         # Ejecución completa
│   └── ...                       # Más scripts de automatización
│
├── 🌐 src/                       # Aplicación Next.js principal
│   ├── app/                      # App Router (páginas y API)
│   │   ├── api/                  # API routes (chat, quotes, etc.)
│   │   ├── chat/                 # Página de chat
│   │   └── simulator/            # Simulador web
│   └── components/               # Componentes React
│       ├── chat/                 # Componentes de chat
│       └── dashboard/            # Dashboard y métricas
│
├── 📁 n8n_workflows/             # Workflows de n8n
│   ├── workflow-chat.json        # Chat conversacional
│   ├── workflow-whatsapp.json    # Integración WhatsApp
│   └── workflow-sheets-sync.json # Sincronización Sheets
│
├── 📄 Configuración
│   ├── requirements.txt          # Dependencias Python
│   ├── matriz_precios.json       # Matriz de precios
│   ├── env.example               # Variables de entorno ejemplo
│   └── conocimiento_consolidado.json  # Base de conocimiento
│
└── 📚 Documentación
    ├── README.md                 # Documentación principal
    ├── UNIFIED_LAUNCHER.md       # Guía del lanzador
    ├── DEPLOYMENT_GUIDE.md       # Guía de despliegue
    └── ...                       # Más documentación
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

### Instalación Automática (Recomendada)

1. **Requisitos del sistema:**
   - Python 3.11 o superior
   - Conexión a internet (para dependencias opcionales)

2. **Configurar entorno virtual del chatbot:**
   ```bash
   bash scripts/setup_chatbot_env.sh
   ```
   Este script crea `.venv`, instala `requirements.txt` y genera un `.env` basado en `env.example` para que completes tus credenciales (`OPENAI_API_KEY`, `MONGODB_URI`, etc.).

3. **Ejecutar instalador:**
   ```bash
   python instalar.py
   ```

4. **Ejecutar el sistema:**
   ```bash
   python ejecutar_sistema.py
   ```

### Instalación Manual

1. **Requisitos del sistema:**
   - Python 3.11 o superior
   - Módulos básicos: `json`, `datetime`, `decimal`, `csv`, `dataclasses`, `typing`

2. **Dependencias opcionales (para funcionalidades avanzadas):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Clonar o descargar el sistema:**
   ```bash
   git clone [url-del-repositorio]
   cd sistema-cotizaciones-bmc
   ```

4. **Ejecutar el sistema:**
   ```bash
   python ejecutar_sistema.py
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

## Alternativa: Inicio Manual

Si prefieres iniciar componentes manualmente:

1. Activa el entorno: `source .venv/bin/activate`.
2. Exporta las variables sensibles (`OPENAI_API_KEY`, opcional `CHAT_USE_FULL_IA=true`).
3. Inicia la API: `python api_server.py` (carga el conocimiento consolidado al arrancar).
4. En otra terminal puedes interactuar con el bot:
   - `python simulate_chat_cli.py` para pruebas rápidas.
   - `CHAT_USE_FULL_IA=true python chat_interactivo.py` para la versión completa.

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

## 📚 Documentación Adicional

Para guías detalladas sobre funcionalidades específicas:

| Documento | Descripción |
|-----------|-------------|
| [UNIFIED_LAUNCHER.md](./UNIFIED_LAUNCHER.md) | Sistema de lanzamiento unificado |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | Guía de despliegue |
| [SETUP_CREDENTIALS_GUIDE.md](./SETUP_CREDENTIALS_GUIDE.md) | Configuración de credenciales |
| [SETUP_WHATSAPP.md](./SETUP_WHATSAPP.md) | Integración WhatsApp |
| [N8N_WORKFLOW_GUIDE.md](./N8N_WORKFLOW_GUIDE.md) | Workflows de n8n |
| [DATA_INGESTION.md](./DATA_INGESTION.md) | Ingesta de datos |
| [CHAT_INTERFACE_GUIDE.md](./CHAT_INTERFACE_GUIDE.md) | Guía de interfaz de chat |
| [MONITOREO_AUTOMATIZADO.md](./MONITOREO_AUTOMATIZADO.md) | Monitoreo y automatización |

## Licencia

Sistema desarrollado específicamente para BMC Uruguay. Todos los derechos reservados.

---

**Versión:** 2.0  
**Última actualización:** Diciembre 2025  
**Desarrollado para:** BMC Uruguay
