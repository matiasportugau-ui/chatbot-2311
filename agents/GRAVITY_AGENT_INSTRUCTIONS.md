# Gravity Agent - Instrucciones de Uso

## 🎯 Visión General

El **Gravity Agent** es un agente especializado que actúa como el punto central de gravedad del proyecto. Su función principal es **interpretar el estado del proyecto** y **orquestar el desarrollo automatizado** de manera inteligente y coordinada.

## 🚀 Características Principales

### 1. Interpretación Profunda del Estado
- Analiza el estado actual del proyecto desde múltiples fuentes
- Identifica fases completadas, en progreso y pendientes
- Detecta bloqueadores y dependencias no cumplidas
- Monitorea tareas activas y su progreso

### 2. Orquestación Automática
- Coordina la ejecución de fases del proyecto
- Gestiona dependencias entre fases
- Optimiza el flujo de ejecución
- Maneja errores y reintentos automáticamente

### 3. Coordinación de Agentes
- Delega tareas a agentes especializados
- Coordina la comunicación entre agentes
- Gestiona la cola de tareas
- Monitorea el progreso de las tareas delegadas

### 4. Toma de Decisiones Inteligente
- Basa decisiones en el contexto del proyecto
- Prioriza tareas según dependencias y urgencia
- Resuelve bloqueadores automáticamente cuando es posible
- Adapta la estrategia según el estado actual

## 📋 Modos de Operación

### 1. Modo Orquestación (`orchestrate`)
Orquesta el desarrollo automatizado del proyecto.

```bash
# Orquestar desde la fase actual hasta una fase específica
python3 agents/gravity_agent.py --mode orchestrate --phase 5

# Orquestar desde la fase actual hasta el final
python3 agents/gravity_agent.py --mode orchestrate
```

**Qué hace:**
- Interpreta el estado actual del proyecto
- Crea un plan de ejecución
- Ejecuta las fases necesarias
- Delega tareas a agentes especializados
- Genera un reporte de ejecución

### 2. Modo Análisis de PR (`analyze-pr`)
Analiza un Pull Request y genera un plan de implementación.

```bash
# Analizar PR por número
python3 agents/gravity_agent.py --mode analyze-pr --pr-number 87

# Analizar PR por URL
python3 agents/gravity_agent.py --mode analyze-pr --pr-url https://github.com/matiasportugau-ui/chatbot-2311/pull/87
```

**Qué hace:**
- Analiza los cambios del PR
- Evalúa el impacto en el proyecto
- Genera un plan de implementación
- Integra el plan con el sistema de orquestación

### 3. Modo Monitoreo (`monitor`)
Monitorea continuamente el estado del proyecto.

```bash
# Monitorear con intervalo por defecto (30 segundos)
python3 agents/gravity_agent.py --mode monitor

# Monitorear con intervalo personalizado
python3 agents/gravity_agent.py --mode monitor --interval 60
```

**Qué hace:**
- Interpreta el estado del proyecto periódicamente
- Detecta bloqueadores y los intenta resolver
- Identifica tareas pendientes
- Verifica si se pueden avanzar fases

### 4. Modo Estado (`status`)
Obtiene un reporte completo del estado del proyecto.

```bash
python3 agents/gravity_agent.py --mode status
```

**Qué hace:**
- Genera un reporte completo del estado
- Muestra información de componentes
- Presenta configuración actual
- Incluye estado de todas las fases

## 🔧 Configuración

### Archivo de Configuración

El agente puede usar un archivo de configuración personalizado:

```bash
python3 agents/gravity_agent.py --config agents/gravity_agent_config.json --mode orchestrate
```

### Variables de Entorno

- `GITHUB_TOKEN`: Token de GitHub para integración (opcional)

## 📊 Estructura de Salida

El agente genera varios archivos en `consolidation/gravity_agent/`:

- `project_state.json`: Estado actual del proyecto
- `execution_report_*.json`: Reportes de ejecución
- `pr_plan.json`: Planes generados desde PRs
- Logs y otros archivos de seguimiento

## 🎯 Casos de Uso Comunes

### Caso 1: Ejecutar Desarrollo Automatizado Completo

```bash
# Ejecutar todas las fases desde la actual hasta la 15
python3 agents/gravity_agent.py --mode orchestrate --phase 15
```

### Caso 2: Analizar y Planificar Implementación de PR

```bash
# Analizar PR #87 y generar plan
python3 agents/gravity_agent.py --mode analyze-pr --pr-number 87
```

### Caso 3: Monitorear Proyecto en Tiempo Real

```bash
# Monitorear cada 30 segundos
python3 agents/gravity_agent.py --mode monitor --interval 30
```

### Caso 4: Verificar Estado del Proyecto

```bash
# Obtener reporte de estado
python3 agents/gravity_agent.py --mode status
```

## 🔄 Integración con el Sistema

El Gravity Agent se integra con:

- **MainOrchestrator**: Para ejecutar fases del proyecto
- **PlanningAgent**: Para analizar PRs y generar planes
- **AgentCoordinator**: Para delegar tareas a otros agentes
- **StateManager**: Para gestionar el estado del proyecto
- **GitHubIntegration**: Para interactuar con GitHub

## 📝 Ejemplo de Uso Programático

```python
from agents.gravity_agent import GravityAgent

# Crear agente
agent = GravityAgent(config_file="agents/gravity_agent_config.json")

# Interpretar estado
state = agent.interpret_project_state()
print(f"Fase actual: {state.current_phase}")
print(f"Estado: {state.overall_status}")

# Orquestar desarrollo
result = agent.orchestrate_development(target_phase=10)
print(f"Fases ejecutadas: {result['summary']['phases_executed']}")

# Analizar PR
pr_result = agent.analyze_pr(pr_number=87)
print(f"Plan generado: {pr_result.get('plan', {})}")

# Obtener reporte de estado
status = agent.get_status_report()
print(f"Componentes activos: {status['components']}")
```

## 🚨 Manejo de Errores

El agente maneja errores de manera inteligente:

- **Fases fallidas**: Intenta reintentar automáticamente
- **Bloqueadores**: Intenta resolverlos cuando es posible
- **Dependencias faltantes**: Identifica y reporta las dependencias faltantes
- **Agentes no disponibles**: Continúa con los agentes disponibles

## 📈 Monitoreo y Reportes

El agente genera reportes detallados que incluyen:

- Estado de todas las fases
- Tareas ejecutadas y delegadas
- Bloqueadores identificados
- Tasa de éxito de ejecución
- Tiempo de ejecución

## 🎓 Mejores Prácticas

1. **Siempre interpreta el estado primero**: Usa `interpret_project_state()` antes de orquestar
2. **Monitorea regularmente**: Usa el modo monitor para detectar problemas temprano
3. **Analiza PRs antes de ejecutar**: Usa `analyze-pr` para entender el impacto
4. **Revisa los reportes**: Los reportes contienen información valiosa sobre el estado
5. **Configura adecuadamente**: Ajusta la configuración según tus necesidades

## 🔗 Referencias

- [Orchestrator Documentation](../scripts/orchestrator/README.md)
- [Planning Agent Documentation](../scripts/orchestrator/planning_agent.py)
- [Agent Interface Documentation](../scripts/orchestrator/agent_interface.py)

---

**Gravity Agent** - El núcleo gravitacional de tu proyecto 🚀
