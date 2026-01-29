# 🤖 Agents Directory

Este directorio contiene los agentes de IA para el proyecto BMC Chatbot 2311.

## 🌌 Gravity Orchestrator Agent

El agente principal de orquestación para Cursor Agent Mode.

### Descripción

El **Gravity Orchestrator Agent** es un agente de IA especializado que:
- Interpreta el estado del proyecto y Pull Requests
- Orquesta el desarrollo automatizado por fases
- Coordina múltiples agentes especializados
- Integra con el sistema de training (PR #87)
- Usa el patrón ReAct (Reasoning + Acting)

### Archivos

| Archivo | Descripción |
|---------|-------------|
| `gravity_orchestrator_agent.py` | Código principal del agente |
| `GRAVITY_AGENT_KNOWLEDGE_BASE.md` | Documentación completa |
| `ai/start_autonomous_execution.py` | Script de ejecución autónoma |

### Uso Rápido

```bash
# Ver estado del proyecto
python agents/gravity_orchestrator_agent.py

# Analizar un PR
python agents/gravity_orchestrator_agent.py --analyze-pr 87

# Ciclo ReAct
python agents/gravity_orchestrator_agent.py --react "Revisar estado del proyecto"

# Ejecutar fases
python agents/gravity_orchestrator_agent.py --execute-phases 0 5

# Modo training
python agents/gravity_orchestrator_agent.py --training
```

### Documentación

- **Knowledge Base:** [GRAVITY_AGENT_KNOWLEDGE_BASE.md](GRAVITY_AGENT_KNOWLEDGE_BASE.md)
- **Reglas para Cursor:** [../.cursor/agents/gravity-agent-rules.md](../.cursor/agents/gravity-agent-rules.md)

---

## 🏃 Otros Agentes

### AI_AGENTS/EXECUTOR
Agente ejecutor para tareas de sistema.
- Ubicación: `/workspace/AI_AGENTS/EXECUTOR/`
- Archivo principal: `execution_ai_agent.py`

### Orchestrator/PlanningAgent
Agente de planificación para análisis de PRs.
- Ubicación: `/workspace/scripts/orchestrator/`
- Archivo principal: `planning_agent.py`

---

## 📋 Configuración

### Auto-Approval

Según `.cursorrules`, la auto-aprobación está **SIEMPRE habilitada**:

```json
{
  "auto_approve": true,
  "execution_mode": "automated",
  "require_manual_approval": false
}
```

### Fases del Proyecto

El proyecto tiene 24 fases (-8 a 15):
- **Preliminary (-8 a -1):** Preparación
- **Foundation (0-3):** Base
- **Integration (4-7):** Integración
- **Enhancement (8-11):** Mejoras
- **Production (12-15):** Producción

---

## 🔗 Enlaces Útiles

- [Main Orchestrator](../scripts/orchestrator/README.md)
- [Cursor Rules](../.cursorrules)
- [Project Documentation](../docs/)
