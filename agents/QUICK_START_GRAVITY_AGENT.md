# 🚀 Quick Start - Gravity Orchestrator Agent

## Instalación Completada ✅

El **Gravity Orchestrator Agent** ha sido instalado y está listo para usar.

---

## 📁 Archivos Creados

| Archivo | Descripción |
|---------|-------------|
| `agents/gravity_orchestrator_agent.py` | Agente principal (1200+ líneas) |
| `agents/GRAVITY_AGENT_KNOWLEDGE_BASE.md` | Documentación completa |
| `agents/README.md` | Índice del directorio de agentes |
| `agents/QUICK_START_GRAVITY_AGENT.md` | Este archivo |
| `.cursor/agents/gravity-agent-rules.md` | Reglas para Cursor Agent Mode |

---

## 🎯 Uso Rápido

### 1. Ver Ayuda
```bash
python3 agents/gravity_orchestrator_agent.py --help
```

### 2. Analizar PR #87 (Training System)
```bash
python3 agents/gravity_orchestrator_agent.py --analyze-pr 87
```

### 3. Ejecutar Ciclo ReAct
```bash
python3 agents/gravity_orchestrator_agent.py --react "Preparar integración del sistema de training"
```

### 4. Ejecutar Fases 0-5
```bash
python3 agents/gravity_orchestrator_agent.py --execute-phases 0 5
```

### 5. Activar Modo Training
```bash
python3 agents/gravity_orchestrator_agent.py --training
```

### 6. Ejecutar Benchmark
```bash
python3 agents/gravity_orchestrator_agent.py --benchmark
```

---

## 🌌 Capacidades del Agente

### Patrón ReAct (Reasoning + Acting)
- **THINK** 🧠 - Analiza situación y planifica
- **ACT** ⚡ - Ejecuta acciones con herramientas
- **OBSERVE** 👁️ - Evalúa resultados y ajusta

### Modos de Operación
- `orchestration` - Orquestación general (default)
- `planning` - Planificación de tareas
- `execution` - Ejecución de fases
- `training` - Modo entrenamiento (PR #87)
- `evaluation` - Benchmarking
- `monitoring` - Monitoreo continuo

### Acciones Disponibles
- `analyze_pr` - Analizar Pull Request
- `review_project_state` - Revisar estado del proyecto
- `generate_implementation_plan` - Generar plan
- `execute_phase` - Ejecutar fase específica
- `run_training_mode` - Activar training
- `run_benchmark` - Ejecutar benchmarks
- `check_github_prs` - Verificar PRs abiertos
- `prepare_training_integration` - Preparar integración PR #87

---

## 📊 Integración con PR #87

El agente está preparado para integrarse con el sistema de training del PR #87:

```
PR #87: Training/Evaluation System
├── training_evaluation_system.py  ← Sistema de modos
├── benchmark_system.py            ← Benchmarking
└── training_integrated_bot.py     ← Bot integrado
```

### Estado Actual
- ✅ Agente detecta archivos del PR #87
- ✅ Modo training activable
- ⚠️ Requiere merge de PR #87 para funcionalidad completa

---

## 💻 Uso desde Cursor Agent Mode

### En Cursor:
1. Abre el proyecto en Cursor
2. Activa Agent Mode (Cmd/Ctrl + Shift + A)
3. El agente usa las reglas de `.cursor/agents/gravity-agent-rules.md`
4. Interactúa siguiendo el patrón ReAct

### Comandos Ejemplo en Agent Mode:
```
"Analiza el PR 87 y genera un plan de implementación"
"Revisa el estado del proyecto y ejecuta las fases pendientes"
"Activa el modo de entrenamiento y ejecuta un benchmark"
```

---

## 📝 Estado Persistente

El agente guarda estado en:
```
consolidation/gravity_agent_state.json
```

Contiene:
- Estado del proyecto
- Tareas pendientes/completadas
- Historial de ejecución
- Configuración actual

---

## 🔗 Enlaces Útiles

- **PR #87:** https://github.com/matiasportugau-ui/chatbot-2311/pull/87
- **Knowledge Base:** [GRAVITY_AGENT_KNOWLEDGE_BASE.md](GRAVITY_AGENT_KNOWLEDGE_BASE.md)
- **Reglas Cursor:** [../.cursor/agents/gravity-agent-rules.md](../.cursor/agents/gravity-agent-rules.md)

---

## ⚙️ Configuración

Según `.cursorrules`:
```
Auto-approve: SIEMPRE true
Execution mode: automated
Require manual approval: false
```

Para cambiar:
```bash
python3 agents/gravity_orchestrator_agent.py --no-auto-approve --interactive
```

---

*Creado: Diciembre 2024 | Versión: 1.0.0*
