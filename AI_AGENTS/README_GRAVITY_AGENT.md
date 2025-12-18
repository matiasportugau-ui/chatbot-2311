# Gravity Orchestrator Agent

Este agente (`AI_AGENTS/gravity_orchestrator.py`) es un especialista en interpretar y orquestar el desarrollo automatizado del proyecto Chatbot-2311.

## Características

- **Agent Mode**: Opera en un bucle continuo de observación, planificación y ejecución.
- **Interpretación**: Analiza archivos clave de estado (`ESTADO_PROYECTO_COMPLETO.md`, `ORCHESTRATOR_KICKOFF_GUIDE.md`) para entender el contexto.
- **Orquestación**: Genera planes estratégicos y delega tareas (simulado) a roles especializados.

## Uso

### Ejecutar en Agent Mode (Recomendado)

```bash
python AI_AGENTS/gravity_orchestrator.py --mode agent --goal "Implementar fase de entrenamiento"
```

### Solo Planificación

```bash
python AI_AGENTS/gravity_orchestrator.py --mode plan --goal "Revisar arquitectura"
```

### Solo Interpretación

```bash
python AI_AGENTS/gravity_orchestrator.py --mode interpret
```

## Requisitos

Requiere que el `model_integrator.py` tenga acceso a proveedores de IA (OpenAI, Groq, o Gemini) configurados mediante variables de entorno.
