# AI Agents Directory

Este directorio contiene todos los agentes de IA del sistema chatbot BMC.

## Estructura

```
AI_AGENTS/
├── EXECUTOR/          # Agentes de ejecución del sistema
│   ├── execution_ai_agent.py
│   ├── ejecutor_ai_assisted.py
│   ├── EXECUTION_AI_AGENT_README.md
│   └── QUICK_START_AI_AGENT.md
└── README.md          # Este archivo
```

## Agentes Disponibles

### EXECUTOR
Agentes para la ejecución, instalación, configuración y monitoreo del sistema.

**Características:**
- Revisión inteligente del sistema
- Planificación automática de tareas
- Ejecución guiada paso a paso
- Sugerencias contextuales
- Monitoreo y seguimiento

**Uso:**
```bash
# Desde el directorio raíz del proyecto
python AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode full
```

Ver `EXECUTOR/EXECUTION_AI_AGENT_README.md` para documentación completa.

## Agregar Nuevos Agentes

Para agregar un nuevo agente:

1. Crear subdirectorio en `AI_AGENTS/`:
   ```bash
   mkdir -p AI_AGENTS/NUEVO_AGENTE
   ```

2. Crear `__init__.py` en el subdirectorio

3. Agregar documentación en el subdirectorio

4. Actualizar este README con la descripción del nuevo agente

## Convenciones

- Cada agente debe tener su propio subdirectorio
- Cada subdirectorio debe tener un `__init__.py`
- Documentación en formato Markdown
- Scripts ejecutables deben tener permisos de ejecución


