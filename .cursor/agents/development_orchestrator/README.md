# 🤖 Development Orchestrator Agent

## Agente Especializado en Orquestación de Desarrollo Automatizado

Este agente está diseñado para funcionar en **Gravity Agent Mode** de Cursor, especializado en interpretar y orquestar el desarrollo automatizado del proyecto **chatbot-2311** (BMC Ecosystem).

---

## 📋 Descripción

El **Development Orchestrator Agent** es un agente de IA que utiliza el patrón **ReAct (Reasoning + Acting)** para:

1. **Analizar PRs y cambios** - Interpreta Pull Requests y cambios en el código
2. **Generar planes de desarrollo** - Crea planes de tareas estructurados
3. **Orquestar ejecución** - Coordina fases de desarrollo automatizado
4. **Monitorear progreso** - Rastrea estado y genera reportes

---

## 🚀 Uso Rápido

### En Cursor Agent Mode (Gravity)

El agente se activa automáticamente en Cursor cuando detecta tareas relacionadas con:
- Análisis de Pull Requests
- Orquestación de desarrollo
- Planificación de tareas
- Monitoreo de progreso

### Línea de Comandos

```bash
# Ciclo ReAct completo con análisis de PR
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py --mode react --pr 87

# Solo análisis de PR
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py --mode analyze --pr 87

# Crear plan de orquestación
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py --mode plan --pr 87

# Ejecutar plan activo
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py --mode execute

# Ver estado actual
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py --mode status
```

---

## 🔄 Patrón ReAct

El agente implementa el patrón **ReAct (Reasoning + Acting)** con tres fases:

### 1. 🤔 THINK (Pensar)
- Analiza el PR o cambios en el código
- Identifica componentes afectados
- Evalúa nivel de impacto
- Genera recomendaciones

### 2. ⚡ ACT (Actuar)
- Crea plan de orquestación
- Genera tareas estructuradas
- Asigna agentes especializados
- Define dependencias

### 3. 👁️ OBSERVE (Observar)
- Ejecuta el plan
- Monitorea progreso
- Registra resultados
- Genera reportes

---

## 📊 Estructura de Análisis de PR

Cuando analiza un PR, el agente genera:

```json
{
  "pr_number": 87,
  "title": "Implement training/evaluation system...",
  "impact_level": "high",
  "affected_components": ["training", "benchmark", "core"],
  "affected_phases": [7, 8, 11],
  "recommendations": [
    "⚠️ Requiere revisión detallada antes de merge",
    "📋 Ejecutar suite completa de tests",
    "✅ Auto-aprobación habilitada según configuración"
  ],
  "tasks": [...]
}
```

---

## 🏗️ Fases del Plan de Consolidación

El agente trabaja con las 16 fases definidas:

| Fase | Nombre | Agente Asignado |
|------|--------|-----------------|
| 0 | Discovery & Foundation | DiscoveryAgent |
| 1 | Repository Consolidation | RepositoryAgent |
| 2 | Core Integration | MergeAgent |
| 3 | Database Layer | IntegrationAgent |
| 4 | API Development | IntegrationAgent |
| 5 | WhatsApp Integration | IntegrationAgent |
| 6 | External Integrations | IntegrationAgent |
| 7 | AI/ML Components | NLUAgent |
| 8 | Training System | ValidationAgent |
| 9 | Security Hardening | SecurityAgent |
| 10 | Infrastructure Setup | InfrastructureAgent |
| 11 | Testing & QA | ValidationAgent |
| 12 | Dashboard & Monitoring | ObservabilityAgent |
| 13 | CI/CD Pipeline | CICDAgent |
| 14 | Performance Optimization | PerformanceAgent |
| 15 | Production Deployment | DisasterRecoveryAgent |

---

## ⚙️ Configuración

### Auto-Aprobación

Según las reglas del proyecto (`.cursorrules`), la **auto-aprobación está SIEMPRE habilitada**:

```python
auto_approve = True  # SIEMPRE habilitado
```

Esto significa:
- ✅ Todas las fases se aprueban automáticamente
- ✅ No se requieren confirmaciones manuales
- ✅ El sistema continúa automáticamente entre fases

### Directorios de Salida

- **Análisis de PR**: `consolidation/pr_analysis/`
- **Planes de orquestación**: `consolidation/orchestration/`
- **Logs del sistema**: `system/logs/`

---

## 🔧 Componentes Detectados

El agente identifica automáticamente estos componentes del proyecto:

| Componente | Patrones de Detección |
|------------|----------------------|
| orchestrator | `orchestrator`, `phase_executor` |
| whatsapp | `whatsapp`, `wa_`, `webhook` |
| n8n | `n8n`, `workflow` |
| qdrant | `qdrant`, `vector`, `embedding` |
| chatwoot | `chatwoot` |
| quotation | `quotation`, `pricing`, `catalog` |
| training | `training`, `benchmark`, `evaluation` |
| agents | `agent`, `ai_agent` |
| dashboard | `dashboard`, `analytics` |
| api | `api`, `endpoint`, `route` |
| database | `mongo`, `database`, `db_` |
| testing | `test_`, `tests/` |
| deployment | `deploy`, `docker`, `k8s` |
| security | `security`, `auth`, `token` |

---

## 📁 Estructura de Archivos

```
.cursor/agents/development_orchestrator/
├── __init__.py                           # Módulo Python
├── development_orchestrator_agent.py     # Implementación principal
├── README.md                             # Esta documentación
└── AGENT_RULES.md                        # Reglas para Cursor Agent Mode
```

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Analizar PR #87 (Training System)

```bash
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py \
    --mode react \
    --pr 87 \
    --goal "Integrar sistema de entrenamiento con correcciones por emoji"
```

### Ejemplo 2: Plan de Fases Específicas

```bash
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py \
    --mode plan \
    --start-phase 7 \
    --end-phase 11 \
    --goal "Implementar sistema de AI/ML y testing"
```

### Ejemplo 3: Ejecutar Plan Existente

```bash
python .cursor/agents/development_orchestrator/development_orchestrator_agent.py \
    --mode execute \
    --start-phase 0 \
    --end-phase 5
```

---

## 🔗 Integración con Otros Agentes

Este agente se integra con el ecosistema de agentes existente:

- **OrchestratorAgent**: Coordinador principal
- **RepositoryAgent**: Gestión de Git/workspace
- **DiscoveryAgent**: Descubrimiento técnico
- **MergeAgent**: Estrategia de merge
- **IntegrationAgent**: Integraciones (WhatsApp, n8n, Qdrant)
- **SecurityAgent**: Hardening de seguridad
- **ValidationAgent**: QA y testing

---

## 📚 Referencias

- [Planning Agent Task Description](.cursor/plans/PLANNING_AGENT_TASK_DESCRIPTION.md)
- [Unified Consolidation Plan](.cursor/plans/UNIFIED_CONSOLIDATION_PRODUCTION_PLAN.md)
- [Execution AI Agent](AI_AGENTS/EXECUTOR/EXECUTION_AI_AGENT_README.md)
- [Cursor Rules](.cursorrules)

---

## 🏷️ Export Seal

```json
{
  "export_seal": {
    "project": "chatbot-2311",
    "agent_id": "development-orchestrator-agent",
    "version": "1.0.0",
    "created_at": "2025-12-18T00:00:00Z",
    "author": "BMC Development Team",
    "mode": "gravity-agent-mode"
  }
}
```
