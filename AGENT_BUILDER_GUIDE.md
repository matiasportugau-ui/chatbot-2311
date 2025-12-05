# Agent Builder - Sistema de Desarrollo de Agentes Personalizado

## Descripción General

El **Agent Builder** es un sistema personalizado de desarrollo de agentes que proporciona consultas progresivamente más profundas con cada interacción. Funciona como un mentor de desarrollo que acumula contexto de cada consulta y ofrece recomendaciones cada vez más avanzadas.

## Características Principales

### 🎯 Consultas Progresivas
- **Nivel Básico (Consulta 1)**: Conceptos fundamentales y configuración inicial
- **Nivel Intermedio (Consultas 2-4)**: Características avanzadas e integración
- **Nivel Avanzado (Consultas 5-8)**: Optimización y workflows complejos
- **Nivel Experto (Consulta 9+)**: Arquitectura y sistemas especializados

### 📋 Gestión de Agenda
- Programación de consultas futuras
- Seguimiento de tareas de desarrollo
- Gestión de hitos (milestones)
- Sugerencias inteligentes de temas

### 📊 Seguimiento de Progreso
- Porcentaje de completitud
- Etapas de desarrollo (planning → development → testing → production)
- Métricas de tiempo y eficiencia
- Historial completo de consultas

## Instalación y Configuración

### Requisitos
- Python 3.7+
- Módulos estándar de Python (incluidos por defecto)

### Archivos del Sistema
```
agent_builder.py              # Core del builder
agent_builder_agenda.py       # Sistema de agenda y tareas
agent_builder_cli.py          # Interfaz de línea de comandos
agent_config.json             # Configuración del sistema
```

### Directorio de Datos
El sistema crea automáticamente:
```
./data/agent_builder/
  ├── blueprint_*.json        # Blueprints de agentes
  └── agendas/
      ├── task_*.json         # Tareas de desarrollo
      ├── agenda_*.json       # Items de agenda
      └── milestone_*.json    # Hitos
```

## Uso del Sistema

### 1. Interfaz de Línea de Comandos (Recomendado)

```bash
python agent_builder_cli.py
```

#### Menú Principal
```
1. Crear nuevo agente
2. Listar agentes
3. Seleccionar agente
4. Consultar con el Builder
5. Ver agenda y tareas
6. Crear tarea
7. Programar consulta
8. Ver progreso
9. Generar reporte
0. Salir
```

#### Flujo de Trabajo Típico

1. **Crear un Agente**
   ```
   Opción 1 → Ingresar nombre → Seleccionar tipo → Definir capacidades
   ```

2. **Consultar con el Builder**
   ```
   Opción 3 (seleccionar agente) → Opción 4 (consultar)
   ```
   - Cada consulta proporciona recomendaciones más profundas
   - Incluye ejemplos de código relevantes
   - Sugiere próximos pasos

3. **Gestionar Tareas**
   ```
   Opción 6 (crear tarea) → Definir prioridad y fecha límite
   ```

4. **Seguir Progreso**
   ```
   Opción 8 (ver progreso) → Revisar métricas y completitud
   ```

### 2. Uso Programático

#### Crear y Consultar con el Builder

```python
from agent_builder import get_agent_builder, AgentType

# Obtener instancia del builder
builder = get_agent_builder()

# Crear un nuevo agente
blueprint = builder.create_agent_blueprint(
    agent_name="MiAgenteDeVentas",
    agent_type=AgentType.SALES,
    initial_capabilities=["crear_cotizaciones", "responder_consultas"]
)

# Primera consulta (nivel básico)
consultation1 = builder.consult(
    blueprint.agent_id,
    "¿Cómo configuro el routing del agente?"
)

print(f"Nivel: {consultation1.level.value}")
print(f"Recomendaciones: {len(consultation1.recommendations)}")
for rec in consultation1.recommendations:
    print(f"  - {rec}")

# Segunda consulta (nivel intermedio)
consultation2 = builder.consult(
    blueprint.agent_id,
    "¿Cómo implemento workflows complejos?"
)

# Ver progreso
print(f"Etapa: {blueprint.development_stage}")
print(f"Completitud: {blueprint.completion_percentage}%")
```

#### Gestionar Agenda y Tareas

```python
from agent_builder_agenda import get_agent_builder_agenda, TaskPriority
from datetime import datetime, timedelta

# Obtener instancia de agenda
agenda = get_agent_builder_agenda()

# Crear tarea
task = agenda.create_task(
    agent_id=blueprint.agent_id,
    title="Implementar lógica de routing",
    description="Añadir routing context-aware",
    priority=TaskPriority.HIGH,
    due_date=datetime.now() + timedelta(days=3),
    estimated_hours=4.0
)

# Programar consulta
consultation = agenda.schedule_consultation(
    agent_id=blueprint.agent_id,
    topic="Optimización de performance",
    scheduled_time=datetime.now() + timedelta(days=2),
    duration_minutes=90
)

# Ver progreso
summary = agenda.get_progress_summary(blueprint.agent_id)
print(f"Tareas completadas: {summary['tasks']['completed']}")
print(f"Tasa de completitud: {summary['completion_rate']:.1f}%")
```

## Tipos de Agentes Disponibles

| Tipo | Descripción | Casos de Uso |
|------|-------------|--------------|
| **SALES** | Agente de ventas | Cotizaciones, ventas, conversión |
| **SUPPORT** | Agente de soporte | Atención al cliente, tickets |
| **FOLLOW_UP** | Agente de seguimiento | Follow-ups automáticos |
| **QUOTES** | Agente de cotizaciones | Generación de presupuestos |
| **ANALYTICS** | Agente analítico | Métricas, reportes, insights |
| **CUSTOM** | Agente personalizado | Casos específicos |

## Niveles de Consulta

### Básico (Consulta 1)
**Enfoque**: Conceptos fundamentales
- Definición del propósito del agente
- Identificación de capacidades básicas
- Configuración inicial
- Ejemplos de código simple

**Ejemplo de Recomendaciones**:
- Define el propósito core de tu agente
- Identifica las capacidades principales
- Establece workflows básicos
- Configura agent_config.json

### Intermedio (Consultas 2-4)
**Enfoque**: Características avanzadas
- Lógica de routing avanzada
- Context awareness
- Integración con workflow engine
- Manejo de errores

**Ejemplo de Recomendaciones**:
- Implementa routing con contexto
- Añade retención de contexto
- Usa análisis de intents
- Implementa fallback mechanisms

### Avanzado (Consultas 5-8)
**Enfoque**: Optimización y automation
- Comportamientos proactivos
- Monitoring comprehensivo
- Workflows con branching condicional
- Integraciones externas
- A/B testing

**Ejemplo de Recomendaciones**:
- Implementa agentes proactivos
- Crea workflows complejos
- Optimiza basado en métricas
- Diseña para escalabilidad

### Experto (Consulta 9+)
**Enfoque**: Arquitectura especializada
- Arquitecturas custom
- Sistemas multi-agente
- Agentes auto-mejorables
- Scheduling dinámico
- Security y compliance
- Analytics avanzado

**Ejemplo de Recomendaciones**:
- Construye sistemas multi-agente
- Implementa especialización
- Usa arquitecturas event-driven
- Diseña para fault tolerance

## Gestión de Agenda

### Tipos de Items de Agenda

| Tipo | Descripción |
|------|-------------|
| **CONSULTATION** | Sesión de consulta programada |
| **TASK** | Tarea de desarrollo |
| **MILESTONE** | Hito importante |
| **REVIEW** | Revisión de progreso |
| **LEARNING** | Sesión de aprendizaje |

### Estados de Tareas

| Estado | Descripción |
|--------|-------------|
| **PENDING** | Pendiente de inicio |
| **IN_PROGRESS** | En desarrollo |
| **COMPLETED** | Completada |
| **BLOCKED** | Bloqueada por dependencias |
| **CANCELLED** | Cancelada |

### Prioridades

| Prioridad | Uso |
|-----------|-----|
| **LOW** 🟢 | Tareas opcionales o de mejora |
| **MEDIUM** 🟡 | Tareas estándar |
| **HIGH** 🟠 | Tareas importantes |
| **URGENT** 🔴 | Tareas críticas |

## Etapas de Desarrollo

El sistema rastrea automáticamente la etapa de desarrollo basándose en el número de consultas:

| Etapa | Consultas | Completitud | Descripción |
|-------|-----------|-------------|-------------|
| **Planning** | 0-1 | 25% | Planificación inicial |
| **Development** | 2-4 | 50% | Desarrollo activo |
| **Testing** | 5-7 | 75% | Pruebas e integración |
| **Production** | 8+ | 95% | Listo para producción |

## Sugerencias Inteligentes

El sistema analiza el estado actual y sugiere temas de consulta:

### Basado en Tareas Bloqueadas
```
"Resolving blockers: Task1, Task2, Task3"
```

### Basado en Tareas Atrasadas
```
"Addressing overdue tasks: Task1, Task2"
```

### Basado en Hitos Próximos
```
"Preparing for milestone: MVP Release"
```

### Basado en Carga de Trabajo
```
"Managing workload: Focusing efforts"
```

## Reportes y Métricas

### Reporte de Agente
```python
report = builder.generate_report(agent_id)
```

Incluye:
- Información general del agente
- Estadísticas de desarrollo
- Historial de consultas
- Progreso por etapa

### Resumen de Progreso
```python
summary = agenda.get_progress_summary(agent_id)
```

Incluye:
- Conteo de tareas por estado
- Estadísticas de hitos
- Horas estimadas vs reales
- Tasa de completitud

## Integración con Sistema Existente

### Con Agent Coordinator
```python
from agent_coordinator import get_coordinator

coordinator = get_coordinator()

# Registrar agente desarrollado
agent_id = coordinator.register_agent(
    agent_type=blueprint.agent_type.value,
    agent_instance=my_agent,
    capabilities=blueprint.capabilities
)
```

### Con Automated Agent System
```python
from automated_agent_system import AutomatedAgentSystem

system = AutomatedAgentSystem()
system.start()

# El builder puede guiar el desarrollo de agentes
# que luego se integran al sistema automatizado
```

## Ejemplos de Uso

### Ejemplo 1: Crear Agente de Soporte
```python
from agent_builder import get_agent_builder, AgentType

builder = get_agent_builder()

# Crear blueprint
support_agent = builder.create_agent_blueprint(
    agent_name="SoporteTécnico",
    agent_type=AgentType.SUPPORT,
    initial_capabilities=[
        "responder_consultas_tecnicas",
        "crear_tickets",
        "escalar_problemas"
    ]
)

# Consulta 1: Setup básico
c1 = builder.consult(
    support_agent.agent_id,
    "¿Cómo configuro las intenciones y capacidades?"
)

# Consulta 2: Integración
c2 = builder.consult(
    support_agent.agent_id,
    "¿Cómo integro con el sistema de tickets?"
)

# Consulta 3: Workflows
c3 = builder.consult(
    support_agent.agent_id,
    "¿Cómo implemento escalamiento automático?"
)
```

### Ejemplo 2: Gestión Completa de Proyecto
```python
from agent_builder import get_agent_builder, AgentType
from agent_builder_agenda import get_agent_builder_agenda, TaskPriority
from datetime import datetime, timedelta

builder = get_agent_builder()
agenda = get_agent_builder_agenda()

# Crear agente
agent = builder.create_agent_blueprint(
    agent_name="AgenteVentas",
    agent_type=AgentType.SALES
)

# Crear tareas
tasks = [
    agenda.create_task(
        agent_id=agent.agent_id,
        title="Implementar routing",
        priority=TaskPriority.HIGH,
        due_date=datetime.now() + timedelta(days=3)
    ),
    agenda.create_task(
        agent_id=agent.agent_id,
        title="Añadir context awareness",
        priority=TaskPriority.HIGH,
        due_date=datetime.now() + timedelta(days=5)
    ),
    agenda.create_task(
        agent_id=agent.agent_id,
        title="Implementar error handling",
        priority=TaskPriority.MEDIUM,
        due_date=datetime.now() + timedelta(days=7)
    )
]

# Crear milestone
milestone = agenda.create_milestone(
    agent_id=agent.agent_id,
    title="Beta Release",
    description="Primera versión funcional",
    target_date=datetime.now() + timedelta(days=14),
    criteria=[
        "Todas las tareas completadas",
        "Tests pasando",
        "Documentación lista"
    ]
)

# Programar consultas
for i in range(1, 4):
    agenda.schedule_consultation(
        agent_id=agent.agent_id,
        topic=f"Sesión de desarrollo {i}",
        scheduled_time=datetime.now() + timedelta(days=i*3)
    )

# Realizar consultas progresivas
for i, topic in enumerate([
    "Setup inicial del agente",
    "Integración con workflows",
    "Optimización de performance"
], 1):
    consultation = builder.consult(agent.agent_id, topic)
    print(f"\nConsulta {i}: {topic}")
    print(f"Nivel: {consultation.level.value}")
    print(f"Recomendaciones: {len(consultation.recommendations)}")
```

## Mejores Prácticas

### 1. Programación Regular de Consultas
- Programa consultas cada 2-3 días durante desarrollo activo
- Permite tiempo entre consultas para implementar recomendaciones

### 2. Seguimiento de Tareas
- Crea tareas inmediatamente después de cada consulta
- Actualiza estados de tareas regularmente
- Revisa tareas atrasadas semanalmente

### 3. Definición de Hitos
- Define hitos claros con criterios específicos
- Programa revisiones antes de cada hito
- Celebra hitos completados

### 4. Aprovechamiento de Sugerencias
- Revisa sugerencias inteligentes regularmente
- Usa sugerencias para planear próximas consultas
- Adapta el plan basado en sugerencias

### 5. Documentación de Progreso
- Genera reportes regularmente
- Documenta decisiones importantes
- Mantén historial de cambios

## Solución de Problemas

### Error: "Agent blueprint not found"
**Solución**: Verifica que el agent_id sea correcto y que el blueprint exista.

### Consultas No Progresan de Nivel
**Problema**: Todas las consultas son nivel básico.
**Solución**: El nivel se basa en el conteo de consultas. Asegúrate de que las consultas se estén guardando correctamente.

### Tareas No Aparecen en Agenda
**Problema**: Las tareas creadas no se muestran.
**Solución**: Verifica que el agent_id coincida entre blueprint y tareas.

### Datos Perdidos Después de Reinicio
**Problema**: Los datos no persisten.
**Solución**: Asegúrate de que el directorio `./data/agent_builder` tenga permisos de escritura.

## Configuración Avanzada

### Personalizar Niveles de Consulta
Edita `agent_config.json`:
```json
{
  "agent_builder": {
    "consultation_levels": {
      "basic": {
        "consultation_count": 0,
        "focus": "tu enfoque personalizado"
      }
    }
  }
}
```

### Cambiar Ruta de Almacenamiento
```python
from agent_builder import AgentBuilder

builder = AgentBuilder(storage_path="/ruta/personalizada")
```

## Contribuir

Para añadir nuevas funcionalidades al Agent Builder:

1. Extiende la clase `AgentBuilder` o `AgentBuilderAgenda`
2. Añade métodos helper en `agent_builder_cli.py` si es necesario
3. Actualiza `agent_config.json` con nueva configuración
4. Documenta los cambios en este archivo

## Soporte

Para preguntas o problemas:
- Revisa este documento primero
- Consulta los ejemplos en cada archivo Python
- Revisa los logs en la consola

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2024  
**Parte del**: Sistema BMC Uruguay Chatbot
