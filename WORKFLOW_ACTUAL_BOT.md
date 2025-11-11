# Workflow Actual del Bot BMC - Superchapita

## Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    USUARIO ENVÍA MENSAJE                        │
│              (chat-interface.html o WhatsApp)                   │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              API SERVER: /chat/process (POST)                   │
│  api_server.py → process_chat_message()                         │
│                                                                 │
│  Request: {                                                    │
│    "mensaje": "texto del usuario",                            │
│    "telefono": "+59891234567",                                 │
│    "sesionId": "session_id" (opcional)                        │
│  }                                                             │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│     IAConversacionalIntegrada.procesar_mensaje_usuario()       │
│                                                                 │
│  1. Generar/validar sesion_id                                   │
│  2. Análisis rápido de intención (_analizar_intencion)          │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐  ┌───────────────────┐
        │ INTENCIÓN SIMPLE  │  │ INTENCIÓN COMPLEJA│
        │ (saludo/despedida)│  │ (cotización/      │
        │                   │  │  consulta técnica)│
        └─────────┬─────────┘  └─────────┬─────────┘
                  │                      │
                  ▼                      ▼
    ┌─────────────────────────┐  ┌─────────────────────────┐
    │ PATTERN MATCHING        │  │ OPENAI (si disponible)     │
    │ (rápido y eficiente)    │  │ o Pattern Matching       │
    └─────────┬───────────────┘  └─────────┬───────────────┘
              │                            │
              └────────────┬───────────────┘
                           │
                           ▼
```

## Flujo Detallado: Pattern Matching

```
_procesar_mensaje_patrones()
│
├─ 1. Obtener/Crear Contexto de Conversación
│     └─ ContextoConversacion (cliente_id, sesion_id, historial)
│
├─ 2. Analizar Intención (_analizar_intencion)
│     │
│     ├─ Patrones de intención:
│     │   • saludo: ["hola", "buenos", "buenas", "hi", "hello"]
│     │   • despedida: ["gracias", "chau", "adios", "bye"]
│     │   • cotizacion: ["cotizar", "precio", "costo", "cuanto"]
│     │   • informacion: ["informacion", "caracteristicas", "techos", "aislamiento"]
│     │   • producto: ["isodec", "poliestireno", "lana", "producto"]
│     │   • instalacion: ["instalar", "instalacion", "montaje"]
│     │   • objecion: ["caro", "costoso", "no estoy seguro"]
│     │
│     └─ Retorna intención con mayor puntuación
│
├─ 3. Extraer Entidades (_extraer_entidades)
│     │
│     ├─ Productos: ["isodec", "poliestireno", "lana_roca"]
│     ├─ Dimensiones: largo x ancho (regex)
│     ├─ Espesores: ["50mm", "75mm", "100mm", "125mm", "150mm"]
│     └─ Colores: ["blanco", "gris", "beige"]
│
├─ 4. Generar Respuesta Inteligente (_generar_respuesta_inteligente)
│     │
│     ├─ ¿Respuesta en base de conocimiento? (y no genérica)
│     │   └─ SÍ → Usar respuesta de base de conocimiento
│     │
│     ├─ ¿Intención != "general"?
│     │   ├─ saludo → _manejar_saludo()
│     │   ├─ despedida → _manejar_despedida()
│     │   ├─ cotizacion → _manejar_cotizacion(entidades, contexto)
│     │   ├─ informacion → _manejar_informacion(entidades, contexto)
│     │   ├─ producto → _manejar_consulta_producto(entidades, contexto)
│     │   └─ objecion → _manejar_objecion(mensaje, contexto)
│     │
│     └─ general → _manejar_consulta_general(mensaje, contexto)
│
├─ 5. Registrar Interacción
│     └─ Guardar en base de conocimiento
│
└─ 6. Retornar Respuesta en Formato API
      {
        "mensaje": "respuesta al cliente",
        "tipo": "informativa|pregunta|cotizacion|...",
        "acciones": [],
        "confianza": 0.9,
        "necesita_datos": [],
        "sesion_id": "...",
        "timestamp": "..."
      }
```

## Flujo Detallado: OpenAI (IA)

```
_procesar_con_openai()
│
├─ 1. Obtener Contexto de Conversación
│     └─ ContextoConversacion (con historial de mensajes)
│
├─ 2. Obtener Historial Reciente
│     └─ Últimos 5 mensajes intercambiados
│
├─ 3. Enriquecer Contexto
│     │
│     ├─ _obtener_info_productos_para_prompt()
│     │   └─ Productos disponibles con precios:
│     │       • ISODEC: $150.00/m²
│     │       • POLIESTIRENO: $120.00/m²
│     │       • LANA DE ROCA: $140.00/m²
│     │       • Espesores: 50mm, 75mm, 100mm, 125mm, 150mm
│     │       • Colores: Blanco, Gris, Beige
│     │
│     └─ _obtener_estado_cotizacion_para_prompt()
│         └─ Si hay cotización en curso:
│             • Estado actual
│             • Datos del cliente
│             • Datos del producto
│             • Datos faltantes
│
├─ 4. Construir Prompt para OpenAI
│     │
│     ├─ System Message:
│     │   • Rol: Superchapita (asistente BMC Uruguay)
│     │   • Información de productos y precios
│     │   • Estado de cotización (si aplica)
│     │   • Instrucciones de formato JSON
│     │
│     ├─ Historial de Conversación:
│     │   • Últimos 5 mensajes (user/assistant)
│     │
│     └─ Mensaje Actual:
│         • Mensaje del usuario
│
├─ 5. Llamar a OpenAI API
│     │
│     ├─ Modelo: gpt-4o-mini (configurable)
│     ├─ Temperature: 0.7
│     ├─ Response Format: JSON Object
│     │
│     └─ Response esperado:
│         {
│           "mensaje": "respuesta al cliente",
│           "tipo": "cotizacion|informacion|pregunta|...",
│           "acciones": ["accion1", "accion2"],
│           "confianza": 0.95,
│           "necesita_datos": ["dato1", "dato2"]
│         }
│
├─ 6. Parsear Respuesta JSON
│     └─ Validar estructura y campos
│
├─ 7. Actualizar Contexto
│     │
│     ├─ Agregar mensaje del cliente al historial
│     ├─ Agregar respuesta de IA al historial
│     └─ Actualizar timestamp de última actividad
│
├─ 8. Registrar Interacción
│     └─ Guardar en base de conocimiento para aprendizaje
│
└─ 9. Retornar Respuesta en Formato API
      {
        "mensaje": "respuesta de OpenAI",
        "tipo": "...",
        "acciones": [...],
        "confianza": 0.95,
        "necesita_datos": [...],
        "sesion_id": "...",
        "timestamp": "..."
      }
```

## Decisiones del Workflow

### ¿Cuándo usar Pattern Matching?
- ✅ Intención simple detectada (saludo, despedida)
- ✅ OpenAI no disponible o falla
- ✅ Respuesta rápida requerida

### ¿Cuándo usar OpenAI?
- ✅ Intención compleja (cotización, consulta técnica)
- ✅ OpenAI disponible y configurado
- ✅ Se necesita contexto conversacional avanzado

### Fallback Automático
```
OpenAI Error → Pattern Matching
Pattern Matching Error → Respuesta genérica
```

## Estados de Cotización

```
inicial
    ↓
recopilando_datos
    ├─ Datos faltantes: producto, dimensiones, espesor
    └─ Preguntar al cliente
    ↓
cotizacion_completada
    └─ Mostrar cotización final
```

## Gestión de Contexto

### ContextoConversacion
```python
{
  "cliente_id": "+59891234567",
  "sesion_id": "sesion_20251110020819",
  "mensajes_intercambiados": [
    {"tipo": "cliente", "mensaje": "...", "timestamp": "..."},
    {"tipo": "ia", "mensaje": "...", "timestamp": "..."}
  ],
  "intencion_actual": "cotizacion",
  "entidades_extraidas": {"productos": ["isodec"], "dimensiones": {...}},
  "estado_cotizacion": "recopilando_datos",
  "datos_cliente": {"nombre": "...", "telefono": "..."},
  "datos_producto": {"producto": "isodec", "largo": 10, "ancho": 5},
  "timestamp_inicio": "...",
  "timestamp_ultima_actividad": "..."
}
```

## Flujo de Datos Completo

```
┌──────────────┐
│   Usuario    │
└──────┬───────┘
       │ Mensaje
       ▼
┌──────────────────┐
│  chat-interface  │
│      .html        │
└──────┬───────────┘
       │ POST /chat/process
       ▼
┌──────────────────┐
│   api_server.py  │
│ FastAPI Server   │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────┐
│ IAConversacionalIntegrada    │
│  procesar_mensaje_usuario()  │
└──────┬───────────────────────┘
       │
       ├─ Análisis de intención
       │
       ├─┐
       │ │ Simple → Pattern Matching
       │ │
       │ └─ _procesar_mensaje_patrones()
       │    ├─ Analizar intención
       │    ├─ Extraer entidades
       │    ├─ Generar respuesta
       │    └─ Retornar
       │
       └─┐
         │ Compleja → OpenAI
         │
         └─ _procesar_con_openai()
            ├─ Obtener contexto
            ├─ Enriquecer prompt
            ├─ Llamar OpenAI API
            ├─ Parsear respuesta
            └─ Retornar
       │
       ▼
┌──────────────────┐
│  Respuesta API   │
│  (JSON)          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ chat-interface   │
│  (mostrar)       │
└──────────────────┘
```

## Componentes del Sistema

### 1. API Server (api_server.py)
- Endpoint: `POST /chat/process`
- Valida request
- Llama a `IAConversacionalIntegrada`
- Retorna respuesta JSON

### 2. IA Conversacional (ia_conversacional_integrada.py)
- **Procesamiento principal**: `procesar_mensaje_usuario()`
- **Pattern Matching**: `_procesar_mensaje_patrones()`
- **OpenAI**: `_procesar_con_openai()`
- **Análisis**: `_analizar_intencion()`, `_extraer_entidades()`
- **Handlers**: `_manejar_saludo()`, `_manejar_cotizacion()`, etc.

### 3. Base de Conocimiento (base_conocimiento_dinamica.py)
- Almacena interacciones exitosas
- Patrones de venta
- Aprende de conversaciones

### 4. Sistema de Cotizaciones (sistema_cotizaciones.py)
- Precios de productos
- Cálculo de cotizaciones
- Gestión de clientes

## Configuración Actual

```python
# Variables de entorno
OPENAI_API_KEY = "configurada" ✅
OPENAI_MODEL = "gpt-4o-mini"
PY_CHAT_SERVICE_URL = "http://localhost:8000"

# Estado
use_ai = True ✅
openai_client = OpenAI() ✅
```

## Ejemplo de Flujo Completo

### Escenario: Usuario solicita cotización

```
1. Usuario: "Quiero cotizar Isodec para un techo de 10x5 metros"
   │
   ▼
2. API Server recibe request
   │
   ▼
3. procesar_mensaje_usuario()
   │
   ├─ Análisis rápido: intención = "cotizacion" (compleja)
   │
   ▼
4. _procesar_con_openai()
   │
   ├─ Contexto: sesión nueva
   ├─ Info productos: ISODEC $150/m², etc.
   ├─ Prompt: "Eres Superchapita..."
   │
   ▼
5. OpenAI API
   │
   ├─ Response JSON:
   │   {
   │     "mensaje": "Perfecto! Para cotizar Isodec...",
   │     "tipo": "cotizacion",
   │     "necesita_datos": ["espesor", "color"]
   │   }
   │
   ▼
6. Actualizar contexto
   │
   ├─ estado_cotizacion = "recopilando_datos"
   ├─ datos_producto = {"producto": "isodec", "largo": 10, "ancho": 5}
   │
   ▼
7. Retornar respuesta al usuario
   │
   ▼
8. Usuario ve: "Perfecto! Para cotizar Isodec necesito..."
```

## Métricas y Monitoreo

- **Confianza**: 0.0 - 1.0 (mayor = más seguro)
- **Tipo de respuesta**: informativa, pregunta, cotizacion, seguimiento, general
- **Fuente**: ["openai"] o ["patrones_respuesta", "base_conocimiento"]
- **Tiempo de respuesta**: registrado en logs

## Próximas Mejoras

1. ⏳ Validación robusta de respuestas JSON de OpenAI
2. ⏳ Cache de respuestas comunes
3. ⏳ Métricas de uso (IA vs patterns)
4. ⏳ Mejora en extracción de entidades
5. ⏳ Integración con sistema de cotizaciones para cálculos automáticos

