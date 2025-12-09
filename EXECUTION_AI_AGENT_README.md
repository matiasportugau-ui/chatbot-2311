# AI Execution Agent - Guía de Uso

## Descripción

El **Execution AI Agent** es un agente de IA inteligente que ayuda con la ejecución, instalación, configuración y monitoreo del sistema chatbot BMC. Utiliza patrones avanzados de prompt engineering (ReAct, Chain-of-Thought) para proporcionar:

- ✅ Revisión inteligente del sistema
- ✅ Planificación automática de tareas
- ✅ Ejecución guiada paso a paso
- ✅ Sugerencias contextuales
- ✅ Monitoreo y seguimiento

## Características Principales

### 1. Patrón ReAct (Reasoning + Acting)
- **Think**: Analiza la situación y planifica el enfoque
- **Act**: Ejecuta acciones usando herramientas disponibles
- **Observe**: Evalúa resultados y ajusta la estrategia

### 2. Planificación Context-Aware
- Genera planes de ejecución basados en el contexto del sistema
- Identifica dependencias entre tareas
- Prioriza tareas (critical, high, medium, low)
- Estima tiempos de ejecución

### 3. Sugerencias Inteligentes
- Analiza el estado actual del sistema
- Proporciona sugerencias contextuales
- Identifica problemas y soluciones

### 4. Monitoreo y Seguimiento
- Rastrea el progreso de ejecución
- Genera reportes detallados
- Mantiene historial de ejecuciones

## Instalación

El agente está integrado en el sistema. Solo necesitas tener configuradas las variables de entorno para IA:

```bash
# En .env o .env.local
OPENAI_API_KEY=tu_key_aqui
# O alternativamente:
GROQ_API_KEY=tu_key_aqui
GEMINI_API_KEY=tu_key_aqui
```

## Uso

### Modo ReAct (Recomendado)

Ejecuta un ciclo completo de análisis y ejecución:

```bash
python ejecutor_ai_assisted.py --mode react
```

El agente:
1. Analiza la situación actual
2. Crea un plan de acción
3. Ejecuta acciones paso a paso
4. Evalúa resultados
5. Ajusta la estrategia según sea necesario

### Modo Planificación

Crea un plan de ejecución detallado:

```bash
# Solo crear plan
python ejecutor_ai_assisted.py --mode plan

# Crear y ejecutar plan
python ejecutor_ai_assisted.py --mode plan --execute
```

### Modo Ejecución

Ejecuta un plan existente o crea uno nuevo:

```bash
# Ejecución automática
python ejecutor_ai_assisted.py --mode execute

# Ejecución interactiva (pregunta antes de cada paso)
python ejecutor_ai_assisted.py --mode execute --interactive
```

### Modo Sugerencias

Obtén sugerencias inteligentes sobre qué hacer a continuación:

```bash
python ejecutor_ai_assisted.py --mode suggest
```

### Modo Completo (Full)

Combina planificación y ejecución en un solo comando:

```bash
python ejecutor_ai_assisted.py --mode full
```

Este modo:
1. Crea un plan de ejecución
2. Muestra el plan
3. Ejecuta las tareas
4. Proporciona un resumen final
5. Sugiere próximos pasos

### Modo Monitoreo

Monitorea el sistema en tiempo real:

```bash
python ejecutor_ai_assisted.py --mode monitor
```

Presiona Ctrl+C para detener el monitoreo.

## Ejemplos de Uso

### Ejemplo 1: Revisión y Preparación Completa

```bash
python ejecutor_ai_assisted.py --mode full --goal "Review and prepare system for production"
```

### Ejemplo 2: Solo Obtener Sugerencias

```bash
python ejecutor_ai_assisted.py --mode suggest
```

### Ejemplo 3: Ejecución Interactiva con Plan Personalizado

```bash
python ejecutor_ai_assisted.py --mode plan --goal "Install and configure MongoDB"
python ejecutor_ai_assisted.py --mode execute --interactive
```

### Ejemplo 4: Guardar Reporte en Archivo Específico

```bash
python ejecutor_ai_assisted.py --mode full --output mi_reporte.json
```

## Estructura de Tareas

El agente organiza las tareas en categorías:

- **review**: Revisión del sistema (Python, dependencias, archivos)
- **install**: Instalación de dependencias
- **config**: Configuración de servicios (MongoDB, etc.)
- **execute**: Ejecución del sistema
- **monitor**: Monitoreo y seguimiento

Cada tarea tiene:
- ID único
- Título y descripción
- Prioridad (critical, high, medium, low)
- Dependencias
- Tiempo estimado
- Estado (pending, in_progress, completed, failed, skipped)

## Reportes

El agente genera reportes JSON con:

- Contexto del sistema
- Plan de ejecución completo
- Historial de ejecuciones
- Resumen de resultados
- Timestamps

Los reportes se guardan automáticamente en:
- `execution_report_YYYYMMDD_HHMMSS.json`

O puedes especificar un archivo con `--output`.

## Integración con ejecutor_completo.py

El agente se integra con el sistema existente:

- Usa `SystemReviewer` para revisión
- Usa `SystemInstaller` para instalación
- Usa `ServiceManager` para configuración
- Usa `SystemExecutor` para ejecución
- Usa `StatusReporter` para reportes

## Modo Sin IA

Si no tienes configuradas las API keys, el agente funciona en modo básico:

```bash
python ejecutor_ai_assisted.py --mode execute --no-ai
```

En este modo:
- Usa planes predefinidos básicos
- No genera sugerencias inteligentes
- No usa ReAct cycle
- Funciona como ejecutor estándar

## Troubleshooting

### Error: "IA no disponible"

**Solución**: Configura al menos una API key en `.env`:
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`

### Error: "SystemReviewer not available"

**Solución**: Asegúrate de que `ejecutor_completo.py` esté en el mismo directorio.

### Error: "No hay plan de ejecución"

**Solución**: Crea un plan primero:
```bash
python ejecutor_ai_assisted.py --mode plan
```

## Arquitectura

El agente está basado en:

1. **Prompt Engineering Knowledge Base**: Patrones de prompt engineering
2. **ReAct Pattern**: Reasoning + Acting para toma de decisiones
3. **Chain-of-Thought**: Razonamiento paso a paso
4. **Context-Aware Planning**: Planificación basada en contexto

## Próximas Mejoras

- [ ] Soporte para múltiples agentes colaborativos
- [ ] Integración con sistema de notificaciones
- [ ] Dashboard web para monitoreo
- [ ] Machine learning para optimización de planes
- [ ] Integración con CI/CD

## Referencias

- `PROMPT_ENGINEERING_KNOWLEDGE_BASE.md`: Base de conocimiento de prompt engineering
- `ejecutor_completo.py`: Sistema de ejecución base
- `execution_ai_agent.py`: Implementación del agente

---

**Nota**: Este agente está diseñado para trabajar con el ecosistema BMC Chatbot. Asegúrate de tener el contexto correcto antes de ejecutar.


