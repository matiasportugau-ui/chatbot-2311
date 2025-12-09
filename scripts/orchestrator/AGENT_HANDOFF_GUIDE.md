# Agent Handoff Guide: Ejecución de Fases en Agentes Separados

## ¿Es Recomendado Ejecutar Fases en Agentes Separados?

### ✅ **SÍ, es recomendado cuando:**

1. **Fases Independientes**: Fases que no requieren estado compartido en memoria
2. **Fases Largas**: Fases que pueden tardar horas o días
3. **Recursos Especializados**: Fases que requieren recursos específicos (GPU, memoria, etc.)
4. **Paralelización**: Fases que pueden ejecutarse en paralelo
5. **Aislamiento**: Fases críticas que necesitan ejecutarse en entornos aislados
6. **Distribución**: Ejecución distribuida en múltiples máquinas/entornos

### ⚠️ **NO es recomendado cuando:**

1. **Estado Compartido**: Fases que requieren estado en memoria compartido
2. **Comunicación Frecuente**: Fases que necesitan comunicación constante
3. **Dependencias Estrechas**: Fases muy acopladas que comparten muchos datos
4. **Overhead**: El overhead de handoff es mayor que el beneficio

## Arquitectura de Handoff

### Flujo de Handoff

```
Phase N Completes
    ↓
Capture Context
    ↓
Create Handoff Package
    ↓
Save Handoff File
    ↓
Create Agent Script
    ↓
[Separate Agent Executes Phase N+1]
    ↓
Load Handoff Package
    ↓
Execute Phase N+1
    ↓
Save Results
    ↓
Update State
```

### Componentes

1. **ContextManager**: Gestiona el contexto de ejecución
2. **AgentHandoff**: Crea y gestiona paquetes de handoff
3. **Handoff Package**: Contiene todo el contexto necesario

## Uso

### Modo 1: Handoff Automático (Preparar pero no ejecutar)

```python
# En orchestrator_config.json
{
  "use_separate_agents": false,  # No ejecuta en agente separado
  "agent_handoff_enabled": true  # Pero prepara handoffs
}
```

Esto prepara los handoff packages pero ejecuta normalmente. Útil para:
- Debugging
- Análisis de contexto
- Preparación para ejecución distribuida futura

### Modo 2: Handoff con Agentes Separados

```python
# En orchestrator_config.json
{
  "use_separate_agents": true,   # Prepara handoff y espera ejecución externa
  "agent_handoff_enabled": true
}
```

Esto prepara el handoff y crea un script standalone para ejecutar en otro agente.

### Modo 3: Ejecución Manual de Handoff

```bash
# Después de que Phase N complete, ejecutar Phase N+1 manualmente:
python consolidation/handoffs/execute_phase_N+1.py
```

## Estructura del Handoff Package

```json
{
  "execution_id": "uuid",
  "from_phase": N,
  "to_phase": N+1,
  "previous_phase_context": {...},
  "dependency_contexts": {
    "0": {...},
    "1": {...},
    ...
  },
  "shared_artifacts": {...},
  "global_context": {...},
  "state_summary": {...},
  "execution_instructions": {...},
  "phase_config": {...}
}
```

## Ventajas del Handoff

### 1. **Aislamiento**
- Cada fase se ejecuta en su propio contexto
- Errores no afectan otras fases
- Fácil debugging

### 2. **Escalabilidad**
- Ejecutar fases en diferentes máquinas
- Distribuir carga de trabajo
- Usar recursos especializados

### 3. **Flexibilidad**
- Pausar y reanudar en cualquier momento
- Ejecutar fases manualmente si es necesario
- Re-ejecutar fases sin afectar otras

### 4. **Trazabilidad**
- Contexto completo capturado
- Historial de handoffs
- Fácil auditoría

## Ejemplo de Uso

### Ejecutar Phase 0 normalmente, Phase 1 en agente separado:

```python
orchestrator = MainOrchestrator()

# Phase 0 - ejecución normal
orchestrator.execute_phase(0, use_separate_agent=False)

# Phase 1 - preparar handoff
orchestrator.execute_phase(1, use_separate_agent=True)

# En otro agente/máquina:
# python consolidation/handoffs/execute_phase_1.py
```

### Cargar y usar handoff manualmente:

```python
from scripts.orchestrator.agent_handoff import AgentHandoff
from scripts.orchestrator.context_manager import ContextManager
from scripts.orchestrator.state_manager import StateManager

state_manager = StateManager()
context_manager = ContextManager(state_manager)
agent_handoff = AgentHandoff(context_manager, state_manager)

# Cargar handoff
handoff = agent_handoff.load_handoff(phase=1)

# Usar contexto
previous_context = handoff['previous_phase_context']
shared_artifacts = handoff['shared_artifacts']
global_context = handoff['global_context']

# Ejecutar fase con contexto
# ... tu lógica de ejecución ...
```

## Mejores Prácticas

### 1. **Capturar Contexto Relevante**
- Solo capturar lo necesario
- Evitar datos sensibles en contexto
- Usar referencias a archivos grandes, no los datos

### 2. **Validar Handoff**
- Verificar que todas las dependencias están en el handoff
- Validar que los archivos referenciados existen
- Verificar integridad del contexto

### 3. **Manejo de Errores**
- Si handoff falla, poder ejecutar normalmente
- Logging detallado de handoffs
- Rollback si es necesario

### 4. **Seguridad**
- No incluir credenciales en handoff
- Validar origen del handoff
- Usar firmas si es necesario

## Casos de Uso Específicos

### Caso 1: Fase Larga de Análisis
```python
# Phase 0: Discovery (puede tardar horas)
# Preparar handoff para ejecutar en servidor dedicado
orchestrator.execute_phase(0, use_separate_agent=True)
# Ejecutar en servidor con más recursos
```

### Caso 2: Fase que Requiere GPU
```python
# Phase 12: Performance Testing (requiere GPU)
# Preparar handoff para ejecutar en máquina con GPU
orchestrator.execute_phase(12, use_separate_agent=True)
# Ejecutar en máquina con GPU
```

### Caso 3: Ejecución Distribuida
```python
# Múltiples fases en paralelo (si no tienen dependencias)
# Preparar handoffs para todas
for phase in [7, 8, 9]:  # Si pueden ejecutarse en paralelo
    orchestrator.execute_phase(phase, use_separate_agent=True)
# Ejecutar en diferentes máquinas simultáneamente
```

## Troubleshooting

### Handoff no se crea
- Verificar que `agent_handoff_enabled = true`
- Verificar que fase anterior está completada
- Verificar dependencias

### Contexto incompleto
- Revisar `consolidation/execution_context.json`
- Verificar que outputs de fases anteriores están guardados
- Revisar logs de contexto

### Agente no puede ejecutar
- Verificar que handoff file existe
- Verificar que todas las dependencias están disponibles
- Verificar paths en handoff package

## Conclusión

**Sí, es recomendado usar agentes separados para:**
- Fases largas o que requieren recursos especializados
- Ejecución distribuida
- Aislamiento y debugging
- Flexibilidad en ejecución

**El sistema de handoff proporciona:**
- Contexto completo entre fases
- Flexibilidad en ejecución
- Trazabilidad completa
- Escalabilidad

**Recomendación:** Habilitar `agent_handoff_enabled: true` siempre, y usar `use_separate_agents: true` cuando sea necesario ejecutar en agentes separados.

