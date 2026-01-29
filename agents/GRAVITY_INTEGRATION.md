# Integración con Gravity Agent Mode

Este documento explica cómo usar el Gravity Orchestrator Agent en el modo "agent mode" de Gravity.

## 🎯 ¿Qué es Gravity Agent Mode?

Gravity Agent Mode permite que los agentes funcionen de forma autónoma, interpretando el contexto del proyecto y ejecutando acciones automáticamente.

## 🔧 Configuración en Gravity

### Opción 1: Configuración Directa

En Gravity, configura el agente como punto de entrada:

```yaml
# gravity-config.yaml (ejemplo)
agents:
  orchestrator:
    entry_point: agents/gravity_orchestrator_agent.py
    mode: hybrid
    auto_approve: true
    capabilities:
      - interpret
      - orchestrate
      - monitor
      - plan
      - execute
```

### Opción 2: Variables de Entorno

Configura las variables de entorno desde `.gravity-agent-config`:

```bash
export GRAVITY_AGENT_MODE=hybrid
export GRAVITY_AUTO_APPROVE=true
export GRAVITY_DEFAULT_START_PHASE=0
export GRAVITY_DEFAULT_END_PHASE=15
```

### Opción 3: Invocación Directa

Gravity puede invocar el agente directamente:

```bash
gravity --agent agents/gravity_orchestrator_agent.py --action interpret
gravity --agent agents/gravity_orchestrator_agent.py --action execute
```

## 🤖 Comportamiento en Agent Mode

Cuando el agente funciona en Gravity Agent Mode:

### 1. Interpretación Automática

El agente analiza automáticamente el estado del proyecto:

```python
# Gravity invoca automáticamente
agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID)
state = agent.interpret_project_state()

# El agente determina automáticamente:
# - Qué fases están pendientes
# - Qué bloqueadores existen
# - Qué acciones tomar
```

### 2. Toma de Decisiones Automatizada

Basado en el estado, el agente decide:

- **Si hay bloqueadores**: Intenta resolverlos primero
- **Si hay fases pendientes**: Crea un plan y ejecuta
- **Si hay fases fallidas**: Decide si reintentar o continuar
- **Si todo está completo**: Genera reporte final

### 3. Ejecución Autónoma

El agente puede ejecutar automáticamente:

```python
# En modo hybrid, el agente:
# 1. Interpreta el estado
# 2. Crea un plan
# 3. Ejecuta las fases automáticamente
# 4. Monitorea el progreso
# 5. Genera reportes

result = agent.orchestrate_execution(
    start_phase=None,  # Usa fase actual automáticamente
    end_phase=15
)
```

## 📋 Workflows Recomendados

### Workflow 1: Monitoreo Continuo

```python
# Gravity ejecuta esto periódicamente (cada hora)
agent = GravityOrchestratorAgent(mode=AgentMode.INTERPRET)
state = agent.interpret_project_state()

if state.blockers:
    # Notificar sobre bloqueadores
    notify_blockers(state.blockers)

if state.overall_status == "stuck":
    # Tomar acción si está bloqueado
    agent.orchestrate_execution()
```

### Workflow 2: Ejecución Nocturna

```python
# Gravity ejecuta esto durante la noche
agent = GravityOrchestratorAgent(
    mode=AgentMode.HYBRID,
    auto_approve=True
)

# Ejecutar todas las fases pendientes
result = agent.orchestrate_execution(
    start_phase=0,
    end_phase=15
)

# Guardar reporte
agent.save_report(f"consolidation/nightly_report_{datetime.now().date()}.json")
```

### Workflow 3: Recuperación Automática

```python
# Gravity ejecuta esto cuando detecta fases fallidas
agent = GravityOrchestratorAgent(mode=AgentMode.HYBRID)
state = agent.interpret_project_state()

# Identificar fases fallidas
failed_phases = [
    phase for phase, status in state.phases_status.items()
    if status == "failed"
]

# Reintentar fases fallidas
for phase in failed_phases:
    result = agent.execute_phase(phase)
    if not result.get("success"):
        # Notificar si sigue fallando
        notify_failure(phase, result.get("error"))
```

## 🔄 Integración con Otros Agentes

El Gravity Orchestrator Agent puede coordinarse con otros agentes:

```python
# En un sistema multi-agente de Gravity
from agents.gravity_orchestrator_agent import GravityOrchestratorAgent

class AgentCoordinator:
    def __init__(self):
        self.orchestrator_agent = GravityOrchestratorAgent()
        # Otros agentes...
    
    def coordinate(self):
        # El orchestrator agent interpreta el estado
        state = self.orchestrator_agent.interpret_project_state()
        
        # Decide qué agente usar para cada fase
        if state.current_phase == 0:
            # Usar DiscoveryAgent
            pass
        elif state.current_phase in [1, 2]:
            # Usar RepositoryAgent
            pass
        # etc.
```

## 📊 Reportes para Gravity

El agente genera reportes que Gravity puede usar:

```python
# Obtener reporte completo
report = agent.get_status_report()

# Gravity puede usar esta información para:
# - Mostrar estado en dashboard
# - Generar notificaciones
# - Tomar decisiones automáticas
# - Actualizar documentación
```

## 🎛️ Configuración Avanzada

### Personalizar Comportamiento

```python
# Crear agente personalizado
agent = GravityOrchestratorAgent(
    mode=AgentMode.HYBRID,
    auto_approve=True,
    config_file="custom_config.json"  # Configuración personalizada
)

# Agregar hooks personalizados
def before_execution(phase):
    print(f"Ejecutando fase {phase}...")

def after_execution(phase, result):
    if not result.get("success"):
        # Lógica personalizada de manejo de errores
        pass

# Usar en ejecución
result = agent.orchestrate_execution()
```

### Integración con CI/CD

```yaml
# .github/workflows/gravity-agent.yml
name: Gravity Orchestrator Agent

on:
  schedule:
    - cron: '0 2 * * *'  # Cada día a las 2 AM
  workflow_dispatch:

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Gravity Agent
        run: |
          python agents/gravity_orchestrator_agent.py \
            --action execute \
            --start-phase 0 \
            --end-phase 15 \
            --output consolidation/ci_report.json
```

## 🚨 Manejo de Errores

El agente maneja errores automáticamente:

```python
try:
    result = agent.orchestrate_execution()
except Exception as e:
    # El agente registra el error
    # Gravity puede acceder al estado para debugging
    state = agent.interpret_project_state()
    # Revisar state.blockers para identificar problemas
```

## 📝 Logging y Debugging

El agente genera logs detallados:

```python
# Los logs incluyen:
# - Estado de cada fase
# - Bloqueadores identificados
# - Acciones tomadas
# - Resultados de ejecución
# - Errores y advertencias

# Gravity puede acceder a estos logs para:
# - Debugging
# - Monitoreo
# - Análisis de rendimiento
```

## ✅ Checklist de Integración

- [ ] Agente instalado y verificado
- [ ] Configuración de Gravity actualizada
- [ ] Variables de entorno configuradas
- [ ] Workflows definidos
- [ ] Integración con otros agentes (si aplica)
- [ ] Reportes configurados
- [ ] Manejo de errores probado
- [ ] Logging configurado

## 🆘 Troubleshooting

### El agente no se ejecuta en Gravity

1. Verificar que el path al agente sea correcto
2. Verificar permisos de ejecución
3. Verificar que las dependencias estén instaladas

### El agente no encuentra el orchestrator

1. Verificar que `scripts/orchestrator/` exista
2. Verificar que `MainOrchestrator` sea importable
3. Revisar logs de importación

### El agente no puede ejecutar fases

1. Verificar estado en `consolidation/execution_state.json`
2. Verificar bloqueadores con `--action interpret`
3. Revisar configuración del orchestrator

---

**El agente está listo para usar en Gravity Agent Mode** 🚀
