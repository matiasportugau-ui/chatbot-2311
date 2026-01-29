# Gravity Agent - Orquestador Central del Desarrollo Automatizado

## 🎯 Visión General

El **Gravity Agent** es un agente especializado que actúa como el punto central de gravedad del proyecto chatbot-2311. Su función principal es **interpretar el estado del proyecto** y **orquestar el desarrollo automatizado** de manera inteligente y coordinada.

## 🚀 Características

- **Interpretación Profunda**: Analiza el estado del proyecto desde múltiples fuentes
- **Orquestación Automática**: Coordina la ejecución de fases y tareas
- **Coordinación de Agentes**: Delega y coordina tareas entre agentes especializados
- **Toma de Decisiones Inteligente**: Basa decisiones en contexto y prioridades
- **Manejo de Errores**: Resuelve bloqueadores y maneja fallos automáticamente

## 📦 Instalación

El agente está incluido en el proyecto. No requiere instalación adicional.

## 🎮 Uso Rápido

### Analizar y Orquestar PR #87

```bash
# Analizar el PR
python3 agents/gravity_agent.py --mode analyze-pr --pr-number 87

# Orquestar el desarrollo basado en el análisis
python3 agents/gravity_agent.py --mode orchestrate --phase 15
```

### Monitorear el Proyecto

```bash
# Monitoreo continuo
python3 agents/gravity_agent.py --mode monitor --interval 30
```

### Verificar Estado

```bash
# Obtener reporte de estado
python3 agents/gravity_agent.py --mode status
```

## 📚 Documentación Completa

- **[Instrucciones de Uso](./GRAVITY_AGENT_INSTRUCTIONS.md)**: Guía completa de uso
- **[Prompt Especializado](./GRAVITY_AGENT_PROMPT.md)**: Prompt para uso en agent mode
- **[Configuración](./gravity_agent_config.json)**: Archivo de configuración

## 🔧 Integración

El Gravity Agent se integra con:

- **MainOrchestrator**: Ejecución de fases
- **PlanningAgent**: Análisis de PRs
- **AgentCoordinator**: Coordinación de agentes
- **StateManager**: Gestión de estado
- **GitHubIntegration**: Integración con GitHub

## 📊 Archivos Generados

El agente genera archivos en `consolidation/gravity_agent/`:

- `project_state.json`: Estado actual del proyecto
- `execution_report_*.json`: Reportes de ejecución
- `pr_plan.json`: Planes generados desde PRs

## 🎯 Casos de Uso

### 1. Desarrollo Automatizado Completo

```bash
python3 agents/gravity_agent.py --mode orchestrate --phase 15
```

### 2. Análisis de PR

```bash
python3 agents/gravity_agent.py --mode analyze-pr --pr-url https://github.com/matiasportugau-ui/chatbot-2311/pull/87
```

### 3. Monitoreo Continuo

```bash
python3 agents/gravity_agent.py --mode monitor
```

## 💻 Uso Programático

```python
from agents.gravity_agent import GravityAgent

# Crear agente
agent = GravityAgent()

# Interpretar estado
state = agent.interpret_project_state()

# Orquestar desarrollo
result = agent.orchestrate_development(target_phase=10)

# Analizar PR
pr_result = agent.analyze_pr(pr_number=87)
```

## 🔗 Enlaces Relacionados

- [Sistema de Orquestación](../scripts/orchestrator/README.md)
- [Planning Agent](../scripts/orchestrator/planning_agent.py)
- [Agent Interface](../scripts/orchestrator/agent_interface.py)

---

**Gravity Agent** - El núcleo gravitacional de tu proyecto 🚀
