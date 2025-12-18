# 🌌 Gravity Development Orchestrator Agent

**Agente especializado en modo Gravity de Cursor para interpretar y orquestar el desarrollo automatizado del proyecto BMC Chatbot.**

---

## 📋 Descripción

El **Gravity Development Orchestrator Agent** es un agente de IA diseñado para funcionar en el modo Agent de Cursor (Gravity). Su función principal es:

- **Interpretar** requisitos de desarrollo desde PRs, issues y solicitudes
- **Analizar** el impacto en el sistema y componentes existentes
- **Orquestar** la ejecución del plan de desarrollo de 16 fases
- **Coordinar** el equipo de 12+ agentes especializados
- **Ejecutar** desarrollo automatizado con patrones ReAct

---

## 🚀 Quick Start

### Uso Básico

```bash
# Navegar al directorio del agente
cd AI_AGENTS/GRAVITY_ORCHESTRATOR

# Analizar un PR
python gravity_development_agent.py --analyze-pr 87

# Ejecutar ciclo ReAct con un objetivo
python gravity_development_agent.py --goal "Implementar sistema de entrenamiento"

# Verificar estado del proyecto
python gravity_development_agent.py --status

# Ejecutar una fase específica
python gravity_development_agent.py --phase 0
```

### Uso en Modo Agent de Cursor

1. Abre Cursor con el proyecto BMC Chatbot
2. Activa el modo Agent (Gravity)
3. Usa el prompt del agente definido en `AGENT_PROMPT.md`
4. El agente interpretará tus solicitudes y orquestará el desarrollo

---

## 🏗️ Arquitectura

### Componentes Principales

```
AI_AGENTS/GRAVITY_ORCHESTRATOR/
├── gravity_development_agent.py  # Agente principal
├── config.json                   # Configuración
├── AGENT_PROMPT.md               # Prompt y persona
├── README.md                     # Esta guía
└── __init__.py                   # Módulo Python
```

### Patrón ReAct

El agente sigue el patrón **ReAct (Reasoning + Acting)**:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  THINK  │ ──▶ │   ACT   │ ──▶ │ OBSERVE │
└─────────┘     └─────────┘     └─────────┘
     ▲                               │
     └───────────────────────────────┘
```

1. **THINK** 🤔: Analiza la situación y planifica
2. **ACT** ⚡: Ejecuta acciones usando herramientas
3. **OBSERVE** 👁️: Evalúa resultados y ajusta

---

## 👥 Equipo de Agentes

El Gravity Agent coordina un equipo de 12+ agentes especializados:

### Nivel 1: Core Agents
| Agente | Responsabilidad | Fases |
|--------|-----------------|-------|
| OrchestratorAgent | Coordinador maestro | Todas |
| RepositoryAgent | Git y workspace | 1-8 |
| DiscoveryAgent | Descubrimiento técnico + BMC | 0 |

### Nivel 2: Consolidation Agents
| Agente | Responsabilidad | Fases |
|--------|-----------------|-------|
| MergeAgent | Merge y conflictos | 3-6 |
| IntegrationAgent | Integraciones | 7-8 |

### Nivel 3: Production Agents
| Agente | Responsabilidad | Fases |
|--------|-----------------|-------|
| SecurityAgent | Seguridad | 9 |
| InfrastructureAgent | IaC | 10 |
| ObservabilityAgent | Monitoreo | 11 |
| PerformanceAgent | Performance | 12 |

### Nivel 4: Deployment Agents
| Agente | Responsabilidad | Fases |
|--------|-----------------|-------|
| CICDAgent | CI/CD | 13 |
| DisasterRecoveryAgent | DR/Backup | 14 |
| ValidationAgent | QA final | 15 |

---

## 📊 Capacidades

### 1. Análisis de PRs

```python
# Analizar un PR
analysis = agent.analyze_pr(87)

# Resultado incluye:
# - Metadatos del PR
# - Archivos cambiados categorizados
# - Fases afectadas
# - Evaluación de impacto
# - Estrategia de integración
# - Evaluación de riesgos
```

### 2. Generación de Tareas

```python
# Generar tareas desde análisis
tasks = agent.generate_tasks_from_pr(analysis)

# Cada tarea incluye:
# - ID único (T87.1, T87.2, etc.)
# - Fase asignada
# - Agente responsable
# - Prioridad (P0-P3)
# - Dependencias
# - Tiempo estimado
```

### 3. Ciclo ReAct

```python
# Ejecutar ciclo completo
result = agent.react_cycle(
    goal="Implementar sistema de entrenamiento",
    max_iterations=5
)
```

### 4. Gestión de Estado

```python
# Guardar estado
agent.save_state("my_state.json")

# Cargar estado
agent.load_state("my_state.json")
```

---

## 🔧 Configuración

### Archivo `config.json`

```json
{
  "execution": {
    "mode": "automated",
    "auto_approval": true,
    "max_retries": 3
  },
  "react_pattern": {
    "max_iterations": 5,
    "think_temperature": 0.3
  }
}
```

### Variables de Entorno

```bash
# API Keys para IA
OPENAI_API_KEY=tu_key_aqui
GROQ_API_KEY=tu_key_groq  # Opcional
GEMINI_API_KEY=tu_key_gemini  # Opcional
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Analizar PR #87 (Sistema de Entrenamiento)

```bash
python gravity_development_agent.py --analyze-pr 87
```

**Salida:**
```
🌌 GRAVITY DEVELOPMENT ORCHESTRATOR AGENT
================================================================================

📊 Analyzing PR #87...

✅ Analysis complete!
   Title: Implement training/evaluation system with emoji-based corrections
   Status: OPEN
   Files changed: 19
   Affected phases: [0, 5, 6, 7]
   Impact level: high

📋 Generated 5 tasks:
   - T87.1: Review PR #87: Implement training/evaluation... (Phase 0, DiscoveryAgent)
   - T87.2: Phase 0 updates for PR #87 (Phase 0, DiscoveryAgent)
   - T87.3: Phase 5 updates for PR #87 (Phase 5, MergeAgent)
   - T87.4: Phase 6 updates for PR #87 (Phase 6, MergeAgent)
   - T87.integration: Integration testing for PR #87 (Phase 7, IntegrationAgent)
```

### Ejemplo 2: Objetivo con ReAct

```bash
python gravity_development_agent.py --goal "Verificar y preparar el sistema para producción"
```

**Salida:**
```
🌌 GRAVITY DEVELOPMENT ORCHESTRATOR AGENT
================================================================================

🎯 Goal: Verificar y preparar el sistema para producción

--- Iteration 1/5 ---
🤔 THINK: Analyzing situation...
✅ THINK complete: Necesito revisar el estado actual del sistema...

⚡ ACT: Executing 'check_status'...

👁️ OBSERVE: Evaluating results...
✅ OBSERVE complete: El sistema está en fase de consolidación...

--- Iteration 2/5 ---
...

✅ ReAct cycle complete!
   Iterations: 3
   Success: True
```

### Ejemplo 3: Ejecutar Fase Específica

```bash
python gravity_development_agent.py --phase 0
```

---

## 🔄 Integración con el Proyecto

### Flujo de Trabajo

```
┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│   PR/Issue   │ ──▶ │  GravityAgent   │ ──▶ │    Tasks      │
└──────────────┘     │   (Análisis)    │     └───────────────┘
                     └─────────────────┘            │
                                                    ▼
┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│   Resultado  │ ◀── │   Agentes       │ ◀── │  Asignación   │
│   Final      │     │ Especializados  │     │  de Agentes   │
└──────────────┘     └─────────────────┘     └───────────────┘
```

### Archivos de Salida

Los outputs se guardan en:
- `consolidation/pr_analysis/` - Análisis de PRs
- `consolidation/state/` - Estado del agente
- `consolidation/reports/` - Reportes de ejecución
- `system/logs/` - Logs de ejecución

---

## 🧪 Testing

```bash
# Ejecutar en modo seco
python gravity_development_agent.py --status

# Verificar conexión con IA
python -c "from gravity_development_agent import GravityDevelopmentAgent; a = GravityDevelopmentAgent(); print('AI:', a.ai_enabled)"
```

---

## 📖 Referencias

- [AGENT_PROMPT.md](./AGENT_PROMPT.md) - Prompt y persona completa
- [config.json](./config.json) - Configuración del agente
- [AGENT_TEAM_RUNNER_GUIDE.md](../../AGENT_TEAM_RUNNER_GUIDE.md) - Guía del equipo
- [.cursorrules](../../.cursorrules) - Reglas del proyecto

---

## 🤝 Contribución

Para extender el agente:

1. Nuevas acciones: Agregar métodos `_act_*` en `gravity_development_agent.py`
2. Nuevos agentes: Agregar en `AgentRole` enum
3. Nuevas fases: Actualizar `PHASE_AGENT_MAP`

---

## 📄 Licencia

Parte del proyecto BMC Chatbot.

---

**Creado para el proyecto BMC Chatbot - Modo Gravity de Cursor**
