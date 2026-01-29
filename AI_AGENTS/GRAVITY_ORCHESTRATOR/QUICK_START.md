# ⚡ Quick Start - Gravity Development Orchestrator Agent

## 1. Uso Inmediato

### Analizar el PR #87 (Sistema de Entrenamiento)

```bash
cd /workspace
python AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --analyze-pr 87
```

### Verificar Estado del Proyecto

```bash
python AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --status
```

---

## 2. Uso en Modo Agent de Cursor

Copia y pega este prompt en el modo Agent de Cursor:

```
Actúa como el Gravity Development Orchestrator Agent.

Tu rol es interpretar y orquestar el desarrollo automatizado del proyecto BMC Chatbot.

Sigue el patrón ReAct:
1. THINK: Analiza la situación
2. ACT: Ejecuta acciones
3. OBSERVE: Evalúa resultados

Tienes acceso a 12+ agentes especializados y un plan de 16 fases.

Reglas:
- Auto-aprobación habilitada
- Ejecución automatizada
- Sin confirmaciones manuales

¿Qué necesitas que orqueste?
```

---

## 3. Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `--analyze-pr <N>` | Analiza PR número N |
| `--goal "<objetivo>"` | Ejecuta ciclo ReAct |
| `--status` | Verifica estado |
| `--phase <N>` | Ejecuta fase N |
| `--save-state <file>` | Guarda estado |
| `--load-state <file>` | Carga estado |

---

## 4. Ejemplo: Implementar Sistema de Entrenamiento

```bash
# 1. Analizar el PR
python AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --analyze-pr 87

# 2. Ejecutar implementación
python AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py \
  --goal "Implementar y validar el sistema de entrenamiento del PR #87"
```

---

## 5. Archivos Importantes

```
AI_AGENTS/GRAVITY_ORCHESTRATOR/
├── gravity_development_agent.py  # Agente principal
├── config.json                   # Configuración
├── AGENT_PROMPT.md               # Prompt completo
└── README.md                     # Documentación
```

---

## 6. Verificar Instalación

```python
# Verificar que el agente funciona
python -c "
from AI_AGENTS.GRAVITY_ORCHESTRATOR import GravityDevelopmentAgent
agent = GravityDevelopmentAgent()
print('✅ Agent loaded')
print(f'   AI enabled: {agent.ai_enabled}')
print(f'   Workspace: {agent.workspace_path}')
"
```

---

## 🎯 Siguiente Paso

Para orquestar el desarrollo del PR #87:

```bash
python AI_AGENTS/GRAVITY_ORCHESTRATOR/gravity_development_agent.py --analyze-pr 87
```
