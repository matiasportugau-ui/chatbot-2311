# Gravity Agent - Development Orchestration Specialist

## 🌌 Descripción

El **Gravity Agent** es un agente especializado que actúa como el "centro de gravedad" del sistema de desarrollo automatizado. Su función principal es **interpretar** requerimientos (PRs, cambios locales, solicitudes) y **orquestar** su ejecución automatizada coordinando múltiples agentes especializados.

## 🎯 Capacidades Principales

### 1. Interpretación Inteligente
- **Análisis de PRs**: Interpreta Pull Requests de GitHub para entender su propósito y alcance
- **Análisis de cambios locales**: Analiza cambios no commiteados en el workspace
- **Extracción de contexto**: Identifica componentes afectados, dependencias y complejidad
- **Evaluación de impacto**: Determina el impacto del cambio en el sistema

### 2. Orquestación Automatizada
- **Generación de planes**: Crea planes de ejecución estructurados basados en la interpretación
- **Coordinación de agentes**: Delega tareas a agentes especializados (PlanningAgent, RepositoryAgent, etc.)
- **Gestión de fases**: Orquesta la ejecución de múltiples fases del desarrollo
- **Monitoreo y ajuste**: Supervisa el progreso y ajusta la ejecución según sea necesario

### 3. Toma de Decisiones
- **Estrategias de ejecución**: Selecciona la estrategia óptima (fast-track, standard, staged rollout)
- **Evaluación de riesgos**: Identifica y mitiga riesgos potenciales
- **Recomendaciones**: Proporciona recomendaciones basadas en el análisis

## 🚀 Uso

### Uso Básico

```bash
# Analizar un PR específico
python3 agents/gravity_agent.py --pr 87

# Analizar cambios locales
python3 agents/gravity_agent.py --local

# Modo dry-run (solo análisis, sin ejecución)
python3 agents/gravity_agent.py --pr 87 --mode dry_run

# Modo interactivo
python3 agents/gravity_agent.py --pr 87 --mode interactive
```

### Modos de Ejecución

- **`automated`** (default): Ejecución completamente automatizada
- **`interactive`**: Requiere confirmaciones en pasos clave
- **`dry_run`**: Solo genera el plan sin ejecutarlo
- **`analysis_only`**: Solo realiza la interpretación sin generar plan

### Opciones Avanzadas

```bash
# Especificar rango de fases
python3 agents/gravity_agent.py --pr 87 --start-phase 0 --end-phase 5

# Combinar opciones
python3 agents/gravity_agent.py --pr 87 --mode dry_run --start-phase -8 --end-phase 15
```

## 📋 Flujo de Trabajo

```
1. INTERPRETACIÓN
   ├── Análisis del PR/Cambios
   ├── Evaluación de impacto
   ├── Identificación de componentes afectados
   └── Determinación de agentes requeridos

2. PLANIFICACIÓN
   ├── Generación de plan de orquestación
   ├── Identificación de dependencias
   ├── Estimación de duración
   └── Evaluación de riesgos

3. ORQUESTACIÓN
   ├── Inicialización del orchestrator
   ├── Ejecución de fases
   ├── Coordinación de agentes
   └── Monitoreo del progreso

4. RESULTADOS
   ├── Generación de reportes
   ├── Guardado de resultados
   └── Actualización de estado
```

## 🔧 Integración con Otros Agentes

El Gravity Agent coordina los siguientes agentes especializados:

- **PlanningAgent**: Análisis de PRs y generación de planes
- **RepositoryAgent**: Análisis de estructura y cambios en repositorio
- **IntegrationAgent**: Validación de integraciones
- **QuotationAgent**: Tareas relacionadas con el motor de cotizaciones BMC

## 📊 Estructura de Resultados

Los resultados se guardan en `consolidation/gravity_agent/` con el siguiente formato:

```json
{
  "interpretation": {
    "intent": "Bug fix",
    "context": {...},
    "affected_components": ["scripts", "system"],
    "required_agents": ["PlanningAgent", "RepositoryAgent"],
    "estimated_complexity": "medium",
    "confidence": 0.85,
    "recommendations": [...]
  },
  "orchestration_plan": {
    "plan_id": "gravity_plan_20241201_120000",
    "phases": [...],
    "dependencies": {...},
    "estimated_duration": 120,
    "risk_assessment": {...},
    "execution_strategy": "standard_execution"
  },
  "execution_result": {
    "status": "completed",
    "success": true,
    "start_phase": -8,
    "end_phase": 15
  },
  "timestamp": "2024-12-01T12:00:00",
  "status": "completed"
}
```

## 🎛️ Configuración

El Gravity Agent utiliza la configuración del proyecto:

- **Orchestrator config**: `scripts/orchestrator/config/orchestrator_config.json`
- **State manager**: Gestiona el estado de ejecución
- **Context manager**: Mantiene el contexto entre fases
- **GitHub integration**: Para análisis de PRs (opcional)

## 📝 Ejemplos de Uso

### Ejemplo 1: Analizar PR #87

```bash
python3 agents/gravity_agent.py --pr 87
```

Esto:
1. Obtiene el PR #87 de GitHub
2. Lo interpreta completamente
3. Genera un plan de orquestación
4. Ejecuta el plan automáticamente

### Ejemplo 2: Solo análisis sin ejecución

```bash
python3 agents/gravity_agent.py --pr 87 --mode analysis_only
```

Esto solo realiza la interpretación sin generar ni ejecutar el plan.

### Ejemplo 3: Análisis de cambios locales

```bash
python3 agents/gravity_agent.py --local --mode dry_run
```

Esto analiza los cambios locales y genera un plan sin ejecutarlo.

## 🔍 Debugging

Para obtener más información sobre el proceso:

```bash
# Ver logs detallados
python3 agents/gravity_agent.py --pr 87 --mode dry_run 2>&1 | tee gravity_log.txt

# Revisar resultados guardados
ls -la consolidation/gravity_agent/
cat consolidation/gravity_agent/gravity_result_87_*.json
```

## 🛠️ Desarrollo

### Estructura del Código

```
agents/
├── gravity_agent.py          # Clase principal GravityAgent
└── GRAVITY_AGENT_README.md   # Esta documentación
```

### Extensión del Agente

Para agregar nuevas capacidades:

1. **Nuevos tipos de interpretación**: Extender `interpret_pr()` o crear nuevos métodos
2. **Nuevos agentes**: Agregar al `AgentCoordinator` y actualizar `_determine_required_agents()`
3. **Nuevas estrategias**: Extender `_determine_execution_strategy()`

## 📚 Referencias

- [Planning Agent Documentation](../scripts/orchestrator/planning_agent.py)
- [Main Orchestrator](../scripts/orchestrator/main_orchestrator.py)
- [Agent Interface](../scripts/orchestrator/agent_interface.py)

## 🤝 Contribución

El Gravity Agent está diseñado para ser extensible. Si necesitas agregar nuevas funcionalidades:

1. Identifica el punto de extensión apropiado
2. Implementa la nueva funcionalidad siguiendo los patrones existentes
3. Actualiza esta documentación
4. Prueba con diferentes escenarios

## ⚠️ Notas Importantes

- El agente requiere acceso a GitHub para analizar PRs (opcional si se proporciona `pr_data`)
- La ejecución automatizada puede modificar el workspace
- Usa `--mode dry_run` para probar sin ejecutar cambios
- Los resultados se guardan automáticamente en `consolidation/gravity_agent/`

## 🎯 Casos de Uso Principales

1. **Análisis automático de PRs**: Interpretar y ejecutar cambios de PRs
2. **Validación de cambios locales**: Analizar cambios antes de commit
3. **Orquestación de desarrollo**: Coordinar múltiples fases de desarrollo
4. **Análisis de impacto**: Evaluar el impacto de cambios propuestos
5. **Generación de planes**: Crear planes de ejecución estructurados

---

**Gravity Agent** - El centro de coordinación para desarrollo automatizado 🚀
