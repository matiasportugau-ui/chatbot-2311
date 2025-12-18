# 🤖 AI Agents - BMC Chatbot Project

Este directorio contiene los agentes de IA especializados para el proyecto BMC Chatbot.

---

## 📁 Estructura

```
AI_AGENTS/
├── EXECUTOR/                    # Agente de ejecución del sistema
│   ├── execution_ai_agent.py    # Agente principal
│   ├── ejecutor_ai_assisted.py  # Ejecutor asistido por IA
│   ├── knowledge_manager.py     # Gestor de conocimiento
│   ├── training_system.py       # Sistema de entrenamiento
│   └── README.md                # Documentación
│
├── GRAVITY_ORCHESTRATOR/        # Agente de orquestación Gravity
│   ├── gravity_development_agent.py  # Agente principal
│   ├── config.json              # Configuración
│   ├── AGENT_PROMPT.md          # Prompt y persona
│   ├── QUICK_START.md           # Guía rápida
│   ├── .cursorrules             # Reglas para Cursor
│   └── README.md                # Documentación
│
├── watcher_agent.py             # Agente observador
└── __init__.py                  # Módulo Python
```

---

## 🌌 Gravity Development Orchestrator Agent

**El agente principal para modo Agent de Cursor (Gravity)**

### Descripción
Agente especializado en interpretar y orquestar el desarrollo automatizado del proyecto BMC Chatbot.

### Capacidades
- ✅ Análisis de Pull Requests
- ✅ Orquestación de 16 fases de desarrollo
- ✅ Coordinación de 12+ agentes especializados
- ✅ Ejecución automatizada con patrón ReAct
- ✅ Generación de tareas con prioridades

### Quick Start

```bash
# Analizar PR #87 (Sistema de Entrenamiento)
python3 AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --analyze-pr 87

# Ejecutar objetivo con ReAct
python3 AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --goal "Implementar sistema"

# Verificar estado
python3 AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --status
```

### Documentación
- [README.md](GRAVITY_ORCHESTRATOR/README.md) - Documentación completa
- [AGENT_PROMPT.md](GRAVITY_ORCHESTRATOR/AGENT_PROMPT.md) - Prompt y persona
- [QUICK_START.md](GRAVITY_ORCHESTRATOR/QUICK_START.md) - Guía rápida

---

## ⚙️ Execution AI Agent

**Agente para ejecución y monitoreo del sistema**

### Descripción
Agente de IA para instalación, configuración y ejecución del sistema chatbot BMC.

### Capacidades
- ✅ Revisión del sistema
- ✅ Instalación de dependencias
- ✅ Configuración de servicios
- ✅ Ejecución del sistema
- ✅ Monitoreo y seguimiento

### Quick Start

```bash
# Modo ReAct (recomendado)
python3 AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode react

# Solo crear plan
python3 AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode plan

# Ejecución completa
python3 AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode full
```

### Documentación
- [README.md](EXECUTOR/EXECUTION_AI_AGENT_README.md) - Documentación completa
- [QUICK_START.md](EXECUTOR/QUICK_START_AI_AGENT.md) - Guía rápida

---

## 👁️ Watcher Agent

**Agente observador para aprendizaje automático**

### Descripción
Monitorea interacciones de WhatsApp y las correlaciona con actualizaciones de Google Sheets para aprender cómo el equipo califica leads.

### Capacidades
- ✅ Observación de chat
- ✅ Correlación con actualizaciones de hojas de cálculo
- ✅ Generación de patrones de entrenamiento
- ✅ Aprendizaje automático

### Uso

```python
from AI_AGENTS.watcher_agent import watcher

# Observar chat
watcher.observe_chat(user_id, message, role)

# Observar actualización de hoja
watcher.observe_sheet_update(row_data)
```

---

## 🔧 Configuración

### Variables de Entorno

```bash
# API Keys para IA
OPENAI_API_KEY=tu_key_aqui
GROQ_API_KEY=tu_key_groq        # Opcional
GEMINI_API_KEY=tu_key_gemini    # Opcional
```

### Reglas del Proyecto

Los agentes siguen las reglas definidas en `.cursorrules`:

- **Auto-aprobación:** Habilitada
- **Modo de ejecución:** Automatizado
- **Sin confirmaciones manuales**

---

## 🏗️ Arquitectura

```
                    ┌─────────────────────────┐
                    │   Gravity Orchestrator  │
                    │     (Agent Mode)        │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   Executor    │      │    Watcher    │      │  12+ Agents   │
│    Agent      │      │     Agent     │      │ Specialized   │
└───────────────┘      └───────────────┘      └───────────────┘
```

---

## 📚 Referencias

- [AGENT_TEAM_RUNNER_GUIDE.md](../AGENT_TEAM_RUNNER_GUIDE.md) - Guía del equipo de agentes
- [.cursorrules](../.cursorrules) - Reglas del proyecto
- [UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md](../.cursor/plans/UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md) - Plan de consolidación

---

## 🤝 Contribución

Para agregar nuevos agentes:

1. Crear directorio en `AI_AGENTS/`
2. Implementar agente con patrón ReAct
3. Agregar al `__init__.py`
4. Documentar en este README

---

**Proyecto BMC Chatbot - Agentes de IA**
