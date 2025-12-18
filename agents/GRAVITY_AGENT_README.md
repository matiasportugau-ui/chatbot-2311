# Gravity Orchestrator Agent

Agente especialista en interpretar y orquestar el desarrollo automatizado del proyecto chatbot-2311.

## 🎯 Propósito

Este agente está diseñado para funcionar en **"agent mode" de Gravity** y proporciona:

1. **Interpretación Inteligente**: Analiza el estado actual del proyecto, identifica bloqueadores y determina las próximas acciones
2. **Orquestación Automatizada**: Ejecuta las fases de desarrollo de forma automatizada usando el sistema de orquestación existente
3. **Toma de Decisiones**: Decide automáticamente el siguiente paso basándose en el estado y las dependencias

## 🚀 Características

- ✅ **Interpretación del Estado**: Analiza fases completadas, en progreso, fallidas y pendientes
- ✅ **Identificación de Bloqueadores**: Detecta dependencias faltantes y fases bloqueadas
- ✅ **Planificación Inteligente**: Crea planes de ejecución respetando dependencias
- ✅ **Ejecución Automatizada**: Orquesta la ejecución de fases desde -8 hasta 15
- ✅ **Auto-aprobación**: Auto-aprueba fases cuando se cumplen los criterios
- ✅ **Monitoreo Continuo**: Supervisa el progreso y detecta problemas
- ✅ **Reportes Detallados**: Genera reportes JSON con el estado completo

## 📋 Requisitos

- Python 3.8+
- Sistema de orquestación configurado (`scripts/orchestrator/`)
- Archivo de estado (`consolidation/execution_state.json`)

## 🔧 Instalación

El agente no requiere instalación adicional. Solo asegúrate de que el sistema de orquestación esté configurado:

```bash
# Verificar que el orchestrator esté disponible
python -c "from scripts.orchestrator.main_orchestrator import MainOrchestrator; print('✅ OK')"
```

## 📖 Uso

### Modo CLI

#### 1. Interpretar Estado del Proyecto

```bash
python agents/gravity_orchestrator_agent.py --action interpret
```

Analiza el estado actual y muestra:
- Fase actual
- Resumen de fases (completadas, en progreso, fallidas, pendientes)
- Bloqueadores identificados
- Próximas acciones recomendadas

#### 2. Crear Plan de Orquestación

```bash
python agents/gravity_orchestrator_agent.py --action plan
```

Crea un plan detallado de ejecución basado en el estado actual.

#### 3. Ejecutar Orquestación Completa

```bash
# Ejecutar desde la fase actual hasta la 15
python agents/gravity_orchestrator_agent.py --action execute

# Ejecutar un rango específico de fases
python agents/gravity_orchestrator_agent.py --action execute --start-phase 0 --end-phase 5
```

#### 4. Ejecutar una Fase Específica

```bash
python agents/gravity_orchestrator_agent.py --action phase --phase 0
```

#### 5. Obtener Estado Completo

```bash
python agents/gravity_orchestrator_agent.py --action status
```

### Modos de Operación

El agente puede operar en tres modos:

#### Modo Interpret (`--mode interpret`)
Solo interpreta y analiza, sin ejecutar:
```bash
python agents/gravity_orchestrator_agent.py --mode interpret --action interpret
```

#### Modo Orchestrate (`--mode orchestrate`)
Solo ejecuta, sin análisis previo:
```bash
python agents/gravity_orchestrator_agent.py --mode orchestrate --action execute
```

#### Modo Hybrid (`--mode hybrid`) - Por Defecto
Interpreta y ejecuta:
```bash
python agents/gravity_orchestrator_agent.py --mode hybrid --action execute
```

### Auto-aprobación

Por defecto, el agente auto-aprueba las fases. Para deshabilitar:

```bash
python agents/gravity_orchestrator_agent.py --action execute --no-auto-approve
```

### Guardar Reportes

Los reportes se guardan automáticamente después de ejecuciones. También puedes especificar un archivo:

```bash
python agents/gravity_orchestrator_agent.py --action execute --output consolidation/mi_reporte.json
```

## 🐍 Uso Programático

```python
from agents.gravity_orchestrator_agent import GravityOrchestratorAgent, AgentMode

# Inicializar agente
agent = GravityOrchestratorAgent(
    mode=AgentMode.HYBRID,
    auto_approve=True
)

# Interpretar estado
state = agent.interpret_project_state()
print(f"Fase actual: {state.current_phase}")
print(f"Bloqueadores: {state.blockers}")

# Crear plan
plan = agent.create_orchestration_plan(
    goal="Completar todas las fases pendientes",
    start_phase=0,
    end_phase=15
)

# Ejecutar orquestación
result = agent.orchestrate_execution(
    start_phase=0,
    end_phase=15
)

# Ejecutar fase específica
result = agent.execute_phase(phase=0)

# Obtener reporte completo
report = agent.get_status_report()

# Guardar reporte
agent.save_report("consolidation/mi_reporte.json")
```

## 📊 Estructura de Reportes

Los reportes incluyen:

```json
{
  "project_state": {
    "current_phase": 0,
    "overall_status": "in_progress",
    "phases_status": {...},
    "execution_id": "...",
    "blockers": [...],
    "next_actions": [...]
  },
  "orchestration_plan": {
    "goal": "...",
    "phases_to_execute": [0, 1, 2, ...],
    "dependencies": {...},
    "priority_order": [0, 1, 2, ...],
    "risk_assessment": {...}
  },
  "execution_history": [...],
  "mode": "hybrid",
  "auto_approve": true
}
```

## 🔗 Integración con Gravity

Para usar este agente en **Gravity agent mode**, puedes:

1. **Configurar como agente principal**:
   ```bash
   # En Gravity, configurar el agente como entry point
   gravity --agent agents/gravity_orchestrator_agent.py
   ```

2. **Usar en workflows automatizados**:
   El agente puede ser invocado automáticamente en workflows de Gravity para:
   - Monitorear el estado del proyecto
   - Ejecutar fases automáticamente
   - Generar reportes periódicos

3. **Integrar con otros agentes**:
   El agente puede coordinarse con otros agentes del sistema usando el `StateManager` compartido.

## 🎯 Casos de Uso

### Caso 1: Monitoreo Continuo
```bash
# Ejecutar cada hora para monitorear progreso
*/60 * * * * python agents/gravity_orchestrator_agent.py --action interpret --output consolidation/hourly_status.json
```

### Caso 2: Ejecución Automatizada Nocturna
```bash
# Ejecutar todas las fases pendientes durante la noche
0 2 * * * python agents/gravity_orchestrator_agent.py --action execute --start-phase 0 --end-phase 15
```

### Caso 3: Recuperación de Fases Fallidas
```bash
# Identificar y reintentar fases fallidas
python agents/gravity_orchestrator_agent.py --action interpret
# Luego ejecutar las fases identificadas como fallidas
```

## 🛠️ Configuración Avanzada

### Archivo de Configuración

El agente usa la configuración del orchestrator en `scripts/orchestrator/config/orchestrator_config.json`. Puedes personalizar:

- `max_retries`: Número máximo de reintentos
- `retry_delay`: Delay entre reintentos (segundos)
- `execution_mode`: Modo de ejecución (automated/manual)
- `github`: Configuración de integración con GitHub

### Variables de Entorno

El agente respeta las variables de entorno del orchestrator:
- `GITHUB_TOKEN`: Token de GitHub para integración
- `EXECUTION_MODE`: Modo de ejecución

## 📝 Logs y Debugging

El agente imprime información detallada en la consola:
- ✅ Operaciones exitosas
- ⚠️ Advertencias
- ❌ Errores
- 📊 Información de estado

Para debugging, revisa:
- `consolidation/execution_state.json`: Estado actual de ejecución
- `consolidation/reports/`: Reportes de estado
- Logs del orchestrator en `system/logs/`

## 🤝 Contribución

Este agente está diseñado para ser extensible. Puedes:

1. Agregar nuevas capacidades de interpretación
2. Mejorar la lógica de planificación
3. Integrar con otros sistemas
4. Agregar nuevos modos de operación

## 📄 Licencia

Parte del proyecto chatbot-2311.

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa los logs en `consolidation/execution_state.json`
2. Verifica la configuración del orchestrator
3. Consulta la documentación del orchestrator en `scripts/orchestrator/README.md`
