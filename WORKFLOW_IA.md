# Workflow de Integración con IA - BMC Chatbot

## Estado Actual

El sistema tiene integración con OpenAI configurada pero requiere:
1. **OPENAI_API_KEY** configurada en el archivo `.env`
2. Paquete `openai` instalado (`pip install openai`)

## Workflow Completo de Procesamiento

### 1. Entrada de Mensaje
```
Usuario envía mensaje → API /chat/process → procesar_mensaje_usuario()
```

### 2. Decisión de Procesamiento

```
procesar_mensaje_usuario()
│
├─ ¿use_ai == True AND openai_client != None?
│  │
│  ├─ SÍ → _procesar_con_openai()
│  │     │
│  │     ├─ Obtener contexto de conversación
│  │     ├─ Construir historial (últimos 5 mensajes)
│  │     ├─ Llamar a OpenAI con prompt estructurado
│  │     ├─ Parsear respuesta JSON
│  │     ├─ Actualizar contexto
│  │     └─ Retornar respuesta
│  │
│  └─ NO → _procesar_mensaje_patrones()
│           │
│           ├─ Analizar intención (_analizar_intencion)
│           ├─ Extraer entidades (_extraer_entidades)
│           ├─ Generar respuesta inteligente (_generar_respuesta_inteligente)
│           │   │
│           │   ├─ Buscar en base de conocimiento
│           │   ├─ Si intención != "general" → usar handler específico
│           │   └─ Si intención == "general" → usar handler general
│           │
│           └─ Retornar respuesta
```

### 3. Workflow con IA (OpenAI)

Cuando la IA está activa:

1. **Contexto de Conversación**
   - Se mantiene por sesión (cliente_id + sesion_id)
   - Almacena historial de mensajes
   - Estado de cotización
   - Datos del cliente y producto

2. **Prompt del Sistema**
   - Define el rol: asistente experto en ventas BMC Uruguay
   - Especifica productos: Isodec, Poliestireno, Lana de Roca
   - Formato de respuesta: JSON estructurado
   - Estilo: conversacional, profesional, español de Uruguay

3. **Historial de Conversación**
   - Últimos 5 mensajes intercambiados
   - Formato: role (user/assistant) + content
   - Permite contexto conversacional

4. **Respuesta de OpenAI**
   - Formato JSON obligatorio:
     ```json
     {
       "mensaje": "respuesta al cliente",
       "tipo": "cotizacion|informacion|pregunta|seguimiento|general",
       "acciones": ["accion1", "accion2"],
       "confianza": 0.95,
       "necesita_datos": ["dato1", "dato2"]
     }
     ```

5. **Fallback**
   - Si OpenAI falla → automáticamente usa pattern matching
   - Si no hay API key → usa pattern matching

### 4. Workflow sin IA (Pattern Matching)

Cuando la IA NO está activa:

1. **Análisis de Intención**
   - Patrones de palabras clave
   - Puntuación por intención
   - Retorna intención con mayor puntuación

2. **Extracción de Entidades**
   - Productos mencionados
   - Dimensiones (largo x ancho)
   - Espesores
   - Colores

3. **Generación de Respuesta**
   - Si intención específica → handler especializado
   - Si intención general → respuesta genérica
   - Filtrado de respuestas genéricas de base de conocimiento

## Mejoras Propuestas

### 1. Workflow Híbrido Inteligente
Combinar IA con pattern matching de forma inteligente:

```
procesar_mensaje_usuario()
│
├─ Analizar intención básica (rápido, sin IA)
│
├─ ¿Intención clara y simple (saludo, despedida)?
│  └─ Usar pattern matching (rápido y eficiente)
│
├─ ¿Intención compleja (cotización, consulta técnica)?
│  └─ Usar OpenAI (más inteligente y contextual)
│
└─ ¿Intención ambigua?
   └─ Usar OpenAI con contexto mejorado
```

### 2. Enriquecimiento de Contexto para IA
- Incluir información de productos en el prompt
- Incluir precios actuales
- Incluir estado de cotización en curso
- Incluir historial de interacciones exitosas

### 3. Validación y Mejora de Respuestas
- Validar que la respuesta JSON de OpenAI sea correcta
- Mejorar respuestas genéricas con información específica
- Combinar respuestas de IA con datos del sistema

## Configuración

### Variables de Entorno Requeridas

```bash
# .env
OPENAI_API_KEY=sk-...  # Tu API key de OpenAI
OPENAI_MODEL=gpt-4o-mini  # Modelo a usar (default: gpt-4o-mini)
```

### Instalación

```bash
pip install openai
```

### Verificación

```python
from ia_conversacional_integrada import IAConversacionalIntegrada

ia = IAConversacionalIntegrada()
print(f"IA activa: {ia.use_ai}")
print(f"Modelo: {ia.openai_model}")
```

## Flujo de Datos

```
Mensaje Usuario
    ↓
API Server (api_server.py)
    ↓
IAConversacionalIntegrada.procesar_mensaje_usuario()
    ↓
┌─────────────────────┬──────────────────────┐
│   Con IA (OpenAI)   │  Sin IA (Patterns)   │
└─────────────────────┴──────────────────────┘
    ↓                        ↓
OpenAI API              Pattern Matching
    ↓                        ↓
JSON Response          Respuesta Estructurada
    ↓                        ↓
    └──────────┬─────────────┘
               ↓
    Formato API Unificado
               ↓
    Chat Interface (HTML)
```

## Mejoras Implementadas

### ✅ Workflow Híbrido Inteligente
- **Intenciones simples** (saludo, despedida) → Pattern matching (rápido)
- **Intenciones complejas** (cotización, consultas técnicas) → OpenAI (inteligente)
- Fallback automático a pattern matching si OpenAI falla

### ✅ Contexto Enriquecido para OpenAI
- Información de productos con precios actuales
- Estado de cotización en curso
- Datos del cliente y producto recopilados
- Historial de conversación (últimos 5 mensajes)

### ✅ Prompt Mejorado
- Identidad: "Superchapita" (asistente BMC Uruguay)
- Información de productos: Isodec, Poliestireno, Lana de Roca
- Precios base por m²
- Espesores y colores disponibles
- Estado de cotización actual

## Estado Actual

✅ **IA Activada**: OpenAI integration enabled
✅ **Modelo**: gpt-4o-mini (configurable via OPENAI_MODEL)
✅ **Workflow Híbrido**: Funcionando correctamente
✅ **Contexto Enriquecido**: Implementado

## Próximos Pasos

1. ✅ Configurar OPENAI_API_KEY en .env
2. ✅ Mejorar workflow híbrido (IA + patterns)
3. ✅ Enriquecer contexto para OpenAI
4. ⏳ Agregar validación de respuestas JSON
5. ⏳ Implementar cache de respuestas comunes
6. ⏳ Agregar métricas de uso de IA vs patterns
7. ⏳ Mejorar extracción de entidades para cotizaciones

