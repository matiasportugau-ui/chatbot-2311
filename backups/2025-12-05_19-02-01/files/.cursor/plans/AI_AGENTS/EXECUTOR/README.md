# AI Execution Agent

Agente de IA para la ejecución, instalación, configuración y monitoreo del sistema chatbot BMC.

## Archivos

- `execution_ai_agent.py` - Implementación principal del agente
- `ejecutor_ai_assisted.py` - Interfaz CLI para usar el agente
- `EXECUTION_AI_AGENT_README.md` - Documentación completa
- `QUICK_START_AI_AGENT.md` - Guía rápida de inicio

## Uso Rápido

```bash
# Desde el directorio raíz del proyecto
python AI_AGENTS/EXECUTOR/ejecutor_ai_assisted.py --mode full
```

## Modos Disponibles

- `react` - Ciclo ReAct (Think → Act → Observe)
- `plan` - Crear plan de ejecución
- `execute` - Ejecutar plan
- `suggest` - Obtener sugerencias
- `monitor` - Monitorear sistema
- `full` - Modo completo (plan + ejecución)

Ver `EXECUTION_AI_AGENT_README.md` para más detalles.


