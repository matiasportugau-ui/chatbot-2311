# Gravity Agent - Inicio Rápido

## 🚀 Uso Inmediato

### Analizar PR #87 y Orquestar Desarrollo

```bash
# Paso 1: Analizar el PR
python3 agents/gravity_agent.py --mode analyze-pr --pr-number 87

# Paso 2: Orquestar el desarrollo basado en el análisis
python3 agents/gravity_agent.py --mode orchestrate --phase 15
```

### Verificar Estado del Proyecto

```bash
python3 agents/gravity_agent.py --mode status
```

### Monitorear Continuamente

```bash
python3 agents/gravity_agent.py --mode monitor --interval 30
```

## 📋 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `--mode orchestrate --phase N` | Orquestar desarrollo hasta fase N |
| `--mode analyze-pr --pr-number N` | Analizar PR número N |
| `--mode analyze-pr --pr-url URL` | Analizar PR por URL |
| `--mode monitor --interval N` | Monitorear cada N segundos |
| `--mode status` | Obtener reporte de estado |

## 💻 Uso Programático

```python
from agents.gravity_agent import GravityAgent

# Crear agente
agent = GravityAgent()

# Interpretar estado
state = agent.interpret_project_state()
print(f"Fase actual: {state.current_phase}")

# Orquestar desarrollo
result = agent.orchestrate_development(target_phase=10)

# Analizar PR
pr_result = agent.analyze_pr(pr_number=87)
```

## 📚 Documentación Completa

- **[Instrucciones](./GRAVITY_AGENT_INSTRUCTIONS.md)**: Guía completa
- **[Prompt](./GRAVITY_AGENT_PROMPT.md)**: Para agent mode
- **[Ejemplos](./example_usage.py)**: Ejemplos de código
- **[Resumen](./GRAVITY_AGENT_SUMMARY.md)**: Resumen de implementación

## ✅ Verificación

El agente está funcionando correctamente. Componentes disponibles:

- ✅ Orchestrator: Disponible
- ✅ Agent Coordinator: Disponible  
- ✅ State Manager: Disponible
- ⚠️ Planning Agent: No disponible (error en módulo externo, no crítico)

El agente funciona correctamente incluso sin algunos componentes opcionales.

---

**¡Listo para usar!** 🎉
