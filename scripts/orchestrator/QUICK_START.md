# Quick Start: Cómo Usar el Sistema de Orquestación

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r scripts/orchestrator/requirements.txt
```

### 2. Configurar GitHub (Opcional)

```bash
cp scripts/orchestrator/.env.example scripts/orchestrator/.env
# Editar .env con tu GITHUB_TOKEN
```

### 3. Ejecutar

```bash
# Ejecución automática completa
python scripts/orchestrator/run_automated_execution.py

# O con opciones
python scripts/orchestrator/run_automated_execution.py --resume
```

## 📋 Próximos Pasos

### Opción A: Ejecución Automática Completa

El sistema ejecutará todas las 16 fases automáticamente:

1. **Fase 0**: BMC Discovery & Assessment
2. **Fases 1-8**: Consolidación
3. **Fases 9-15**: Producción

**Tiempo estimado:** 8-10 semanas (según el plan)

### Opción B: Ejecución con Handoff entre Agentes

Si quieres ejecutar fases en agentes separados:

1. **Habilitar handoff** en `config/orchestrator_config.json`:
```json
{
  "use_separate_agents": true,
  "agent_handoff_enabled": true
}
```

2. **Ejecutar normalmente** - el sistema preparará handoffs automáticamente

3. **Para cada fase**, encontrarás en `consolidation/handoffs/`:
   - `handoff_phase_N.json` - Paquete de contexto completo
   - `execute_phase_N.py` - Script standalone para ejecutar
   - `handoff_phase_N_summary.md` - Resumen legible

4. **Ejecutar fase en agente separado**:
```bash
python consolidation/handoffs/execute_phase_N.py
```

## 🔍 Monitoreo

### Estado de Ejecución

```bash
# Ver estado actual
cat consolidation/execution_state.json

# Ver contexto
cat consolidation/execution_context.json

# Ver reportes
ls consolidation/reports/
```

### GitHub (si está configurado)

El sistema creará un issue en GitHub con:
- Estado de cada fase
- Progreso general
- Notificaciones de aprobaciones
- Errores y reintentos

## 🛠️ Configuración Avanzada

### Ejecutar Fase Específica con Handoff

```python
from scripts.orchestrator.main_orchestrator import MainOrchestrator

orchestrator = MainOrchestrator()

# Ejecutar Phase 0 normalmente
orchestrator.execute_phase(0, use_separate_agent=False)

# Preparar handoff para Phase 1
orchestrator.execute_phase(1, use_separate_agent=True)

# Luego ejecutar Phase 1 en otro agente:
# python consolidation/handoffs/execute_phase_1.py
```

### Ver Contexto de una Fase

```python
from scripts.orchestrator.context_manager import ContextManager
from scripts.orchestrator.state_manager import StateManager

sm = StateManager()
cm = ContextManager(sm)

# Ver contexto de Phase 0
context = cm.get_phase_context(0)
print(context)

# Ver outputs de Phase 0
outputs = cm.get_phase_outputs(0)
print(outputs)

# Ver contexto global
global_ctx = cm.context.get("global_context", {})
print(global_ctx)
```

## 📊 Verificación

```bash
# Verificar implementación
python scripts/orchestrator/verify_implementation.py

# Verificar configuración
python scripts/orchestrator/setup_config.py
```

## ❓ Preguntas Frecuentes

### ¿Puedo pausar y reanudar?

Sí, el estado se guarda automáticamente. Usa `--resume` para continuar.

### ¿Puedo ejecutar fases en paralelo?

Solo si no tienen dependencias entre sí. El sistema verifica dependencias automáticamente.

### ¿Qué pasa si una fase falla?

El sistema intentará reintentar automáticamente (hasta 3 veces). Si falla permanentemente, se detiene y requiere intervención manual.

### ¿Cómo veo el progreso?

- Estado: `consolidation/execution_state.json`
- Reportes: `consolidation/reports/`
- GitHub issue (si configurado)

## 📚 Documentación

- **README.md** - Documentación completa
- **AGENT_HANDOFF_GUIDE.md** - Guía de handoff entre agentes
- **COMPLETION_REPORT.md** - Reporte de implementación
- **FINAL_VERIFICATION.md** - Verificación final

## 🎯 Recomendaciones

1. **Primera ejecución**: Ejecutar normalmente (sin agentes separados) para validar
2. **Fases largas**: Usar handoff para fases que tardan mucho
3. **Recursos especializados**: Usar handoff para fases que requieren GPU/memoria especial
4. **Distribución**: Usar handoff para ejecución distribuida

¡Listo para comenzar! 🚀

