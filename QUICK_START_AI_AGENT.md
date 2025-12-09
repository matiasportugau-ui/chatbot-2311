# 🚀 Quick Start: AI Execution Agent

## Inicio Rápido

### 1. Configurar API Key (Opcional pero Recomendado)

```bash
# Edita .env o .env.local
echo "OPENAI_API_KEY=tu_key_aqui" >> .env.local
# O usa Groq/Gemini:
# echo "GROQ_API_KEY=tu_key_aqui" >> .env.local
```

### 2. Ejecutar Modo Completo (Recomendado)

```bash
python ejecutor_ai_assisted.py --mode full
```

Esto:
- ✅ Crea un plan inteligente
- ✅ Ejecuta todas las tareas
- ✅ Proporciona sugerencias finales
- ✅ Genera un reporte

### 3. Modos Disponibles

```bash
# ReAct cycle (inteligente paso a paso)
python ejecutor_ai_assisted.py --mode react

# Solo obtener sugerencias
python ejecutor_ai_assisted.py --mode suggest

# Crear plan sin ejecutar
python ejecutor_ai_assisted.py --mode plan

# Ejecutar plan existente
python ejecutor_ai_assisted.py --mode execute

# Modo interactivo (pregunta antes de cada paso)
python ejecutor_ai_assisted.py --mode full --interactive
```

## ¿Qué Hace el Agente?

1. **Revisa** el sistema (Python, dependencias, archivos, configuración)
2. **Sugiere** qué hacer a continuación
3. **Planifica** las tareas necesarias
4. **Ejecuta** instalaciones y configuraciones
5. **Monitorea** el progreso
6. **Sigue** el estado y sugiere mejoras

## Sin IA

Si no tienes API key, funciona en modo básico:

```bash
python ejecutor_ai_assisted.py --mode execute --no-ai
```

## Ayuda

```bash
python ejecutor_ai_assisted.py --help
```

## Documentación Completa

Ver `EXECUTION_AI_AGENT_README.md` para detalles completos.


