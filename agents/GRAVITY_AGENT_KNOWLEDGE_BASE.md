# 🌌 GRAVITY ORCHESTRATOR AGENT - Knowledge Base

## Resumen Ejecutivo

El **Gravity Orchestrator Agent** es un agente de IA especializado para Cursor Agent Mode que interpreta y orquesta el desarrollo automatizado del proyecto BMC Chatbot 2311.

### ¿Qué hace este agente?

1. **Interpreta** el estado actual del proyecto
2. **Analiza** Pull Requests y cambios pendientes
3. **Planifica** la implementación de nuevas funcionalidades
4. **Orquesta** la ejecución automatizada por fases
5. **Coordina** múltiples agentes especializados
6. **Integra** con el sistema de training y benchmarking (PR #87)

---

## 🏗️ Arquitectura del Agente

```
┌─────────────────────────────────────────────────────────────┐
│              🌌 GRAVITY ORCHESTRATOR AGENT                  │
│    (Cerebro central de orquestación del desarrollo)        │
└─────────────────────────────────┬───────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  MainOrchestrator│   │  PlanningAgent  │   │ ExecutionAgent  │
│  (Fases 0-15)   │   │  (Análisis PRs) │   │  (Tareas)       │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMAS DEL PROYECTO                    │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│   API    │ WhatsApp │   n8n    │ Training │   Frontend     │
│ FastAPI  │ Business │ Workflows│ PR #87   │   Next.js      │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
```

---

## 📚 Conceptos Clave

### Patrón ReAct (Reasoning + Acting)

El agente utiliza el patrón ReAct para resolver tareas:

```
┌──────────────────────────────────────────────────┐
│                  CICLO ReAct                     │
│                                                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────────┐    │
│  │  THINK  │ → │   ACT   │ → │   OBSERVE   │    │
│  │   🧠    │   │   ⚡    │   │     👁️      │    │
│  └─────────┘   └─────────┘   └─────────────┘    │
│       ▲                              │          │
│       └──────────────────────────────┘          │
│              (repeat until done)                │
└──────────────────────────────────────────────────┘
```

- **THINK:** Analiza la situación, evalúa el contexto, planifica
- **ACT:** Ejecuta acciones usando herramientas disponibles
- **OBSERVE:** Evalúa resultados, ajusta estrategia si es necesario

### Fases del Proyecto

El proyecto se divide en 24 fases (-8 a 15):

| Categoría | Fases | Enfoque |
|-----------|-------|---------|
| **Preliminary** | -8 a -1 | Preparación, configuración inicial |
| **Foundation** | 0-3 | Estructura base, dependencias |
| **Integration** | 4-7 | Integración de componentes |
| **Enhancement** | 8-11 | Optimizaciones, mejoras |
| **Production** | 12-15 | Despliegue, producción |

### Estados de Tareas

- `pending` - Pendiente de ejecución
- `in_progress` - En ejecución
- `completed` - Completada exitosamente
- `failed` - Falló
- `blocked` - Bloqueada por dependencias
- `skipped` - Saltada

### Prioridades

- `critical` - Bloquea todo lo demás
- `high` - Importante
- `medium` - Normal
- `low` - Puede esperar

---

## 🎯 Casos de Uso

### Caso 1: Análisis de un nuevo PR

**Situación:** Se crea un nuevo PR en el repositorio.

**Flujo:**
1. El agente detecta el PR (o es notificado)
2. Ejecuta `analyze_pr(pr_number)`
3. Evalúa impacto, complejidad, sistemas afectados
4. Genera tareas de integración
5. Planifica la ejecución

**Ejemplo:**
```python
# Para PR #87 (Training System)
agent = GravityOrchestratorAgent()
analysis = agent.analyze_pr(87)

# Resultado:
# - Impacto: high (nuevos componentes)
# - Complejidad: medium (3 archivos principales)
# - Sistemas: Training, Benchmarking
# - Training relevante: True
```

### Caso 2: Ejecución Automatizada de Fases

**Situación:** Se necesita ejecutar varias fases del proyecto.

**Flujo:**
1. El agente revisa el estado actual
2. Identifica la fase actual
3. Ejecuta fases secuencialmente
4. Maneja errores y reintentos
5. Reporta resultados

**Ejemplo:**
```python
result = agent.execute_orchestrated_development(
    start_phase=0,
    end_phase=5,
    interactive=False  # Auto-approve habilitado
)
```

### Caso 3: Modo Training (PR #87)

**Situación:** Se necesita entrenar el chatbot.

**Flujo:**
1. Activar modo training
2. Procesar mensajes con detección de correcciones
3. Reformular respuestas con razonamiento
4. Aprobar/rechazar cambios
5. Persistir en knowledge base

**Ejemplo:**
```python
agent.activate_training_mode("session_001")

# El sistema detecta correcciones como:
# "✏️ La respuesta debería incluir precios por espesor"
```

### Caso 4: Ciclo ReAct Completo

**Situación:** Solicitud abierta de desarrollo.

**Flujo:**
1. Think: Analizar situación
2. Act: Ejecutar acción prioritaria
3. Observe: Evaluar resultado
4. Repeat: Hasta completar o máx. iteraciones

**Ejemplo:**
```python
result = agent.react_cycle(
    "Preparar el proyecto para integración del sistema de training"
)
```

---

## 🔧 Referencia de API

### Clase Principal: `GravityOrchestratorAgent`

```python
class GravityOrchestratorAgent:
    def __init__(self, 
                 mode: AgentMode = AgentMode.ORCHESTRATION,
                 auto_approve: bool = True,
                 verbose: bool = True):
        ...
```

### Métodos Principales

| Método | Descripción | Retorno |
|--------|-------------|---------|
| `think(situation, context)` | Analiza situación | Dict con plan |
| `act(action, parameters)` | Ejecuta acción | Dict con resultado |
| `observe(action_result)` | Evalúa resultado | Dict con observación |
| `react_cycle(situation, max_iter)` | Ciclo ReAct completo | Dict resumen |
| `analyze_pr(pr_number)` | Analiza un PR | PRAnalysis |
| `generate_implementation_plan(...)` | Genera plan | List[DevelopmentTask] |
| `execute_orchestrated_development(...)` | Ejecuta fases | Dict resultado |
| `activate_training_mode(session_id)` | Activa training | Dict estado |
| `run_benchmark(suite)` | Ejecuta benchmark | Dict resultados |

### Enums Importantes

```python
class AgentMode(Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    TRAINING = "training"
    EVALUATION = "evaluation"
    ORCHESTRATION = "orchestration"

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
```

---

## 📁 Archivos y Paths

### Archivos del Agente
- `/workspace/agents/gravity_orchestrator_agent.py` - Código principal
- `/workspace/.cursor/agents/gravity-agent-rules.md` - Reglas para Cursor
- `/workspace/agents/GRAVITY_AGENT_KNOWLEDGE_BASE.md` - Este documento

### Archivos de Estado
- `/workspace/consolidation/gravity_agent_state.json` - Estado persistente
- `/workspace/consolidation/tasks/` - Tareas generadas

### Archivos Relacionados
- `/workspace/scripts/orchestrator/main_orchestrator.py` - Orchestrator principal
- `/workspace/scripts/orchestrator/planning_agent.py` - Agente de planificación
- `/workspace/AI_AGENTS/EXECUTOR/execution_ai_agent.py` - Agente ejecutor

---

## 🚀 Guía de Inicio Rápido

### Paso 1: Verificar el estado del proyecto
```bash
python agents/gravity_orchestrator_agent.py --mode orchestration
```

### Paso 2: Analizar PR pendientes
```bash
python agents/gravity_orchestrator_agent.py --analyze-pr 87
```

### Paso 3: Ejecutar ciclo de desarrollo
```bash
python agents/gravity_orchestrator_agent.py --react "Preparar integración de PR #87"
```

### Paso 4: Ejecutar fases específicas
```bash
python agents/gravity_orchestrator_agent.py --execute-phases 0 5
```

---

## 🔌 Integración con PR #87 (Training System)

El PR #87 introduce un sistema completo de entrenamiento y evaluación:

### Componentes
1. **training_evaluation_system.py** - Gestión de modos training/production
2. **benchmark_system.py** - Sistema de benchmarking
3. **training_integrated_bot.py** - Bot con awareness de training

### Flujo de Training
```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Activar Training │ → │ Detectar         │ → │ Reformular       │
│ Mode             │    │ Corrección (✏️)  │    │ Respuesta        │
└──────────────────┘    └──────────────────┘    └────────┬─────────┘
                                                         │
                                                         ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Persistir        │ ← │ Aprobar          │ ← │ Mostrar          │
│ Knowledge        │    │ (APROBAR)        │    │ Razonamiento     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Comandos de Training
```
MODO ENTRENAMIENTO    # Activar modo training
✏️ [corrección]       # Corregir última respuesta
🔧 [corrección]       # Alternativa para corregir
CORREGIR: [texto]     # Corrección con texto
APROBAR              # Aprobar reformulación
RECHAZAR [razón]     # Rechazar reformulación
ESTADÍSTICAS         # Ver estadísticas de sesión
BENCHMARK            # Ejecutar benchmark
REPORTE              # Generar reporte
SALIR ENTRENAMIENTO  # Finalizar sesión
```

---

## 🛠️ Troubleshooting

### Problema: Componentes no disponibles
```
⚠️ Algunos componentes no disponibles: ImportError
```
**Solución:** Verificar que los módulos del orchestrator estén en el path.

### Problema: PR no encontrado
```
⚠️ Error obteniendo PR: gh: No such repository
```
**Solución:** Verificar que `gh` está autenticado: `gh auth status`

### Problema: Fase falla repetidamente
```
❌ Fase X falló después de 3 reintentos
```
**Solución:** 
1. Revisar logs en `consolidation/`
2. Verificar dependencias de la fase
3. Ejecutar manualmente para diagnóstico

### Problema: Estado corrupto
**Solución:** Eliminar `consolidation/gravity_agent_state.json` y reiniciar.

---

## 📊 Métricas y Reportes

El agente genera métricas de:
- Fases ejecutadas/completadas/fallidas
- Tareas por estado y prioridad
- Historial de ejecuciones
- Tiempo de ejecución

Reportes disponibles en:
- `consolidation/gravity_agent_state.json` - Estado del agente
- `consolidation/execution_report_*.json` - Reportes de ejecución

---

## 🤝 Contribución y Extensión

### Agregar Nueva Acción
1. Añadir método `_act_nueva_accion(self, params)` 
2. Registrar en `action_map` dentro de `act()`
3. Documentar en este knowledge base

### Agregar Nuevo Modo
1. Añadir valor a `AgentMode` enum
2. Implementar lógica específica del modo
3. Actualizar CLI si es necesario

### Integrar Nuevo Agente
1. Importar en `_init_components()`
2. Usar `coordinate_agents` para delegar
3. Documentar en reglas

---

## 📞 Soporte

Para problemas o mejoras:
1. Revisar este knowledge base
2. Verificar logs en `consolidation/`
3. Abrir issue en GitHub con detalles

---

*Última actualización: Diciembre 2024*
*Versión del Agente: 1.0.0*
