# 🚀 Quick Start - Gravity Training Orchestrator

## ⚡ Inicio Rápido (5 minutos)

### 1. Quick Start Automático
```bash
python3 AI_AGENTS/run_gravity_orchestrator.py
```

**Esto ejecuta:**
- ✅ Análisis del PR #87
- ✅ Phase 0 (Planning)
- ✅ Generación de 5+ outputs
- ✅ Status report

### 2. Modo Interactivo
```bash
./AI_AGENTS/gravity_quick_commands.sh
```

**Menú con opciones:**
1. Analizar PR #87
2. Ejecutar fases individuales
3. Ver status y logs
4. Leer documentación

### 3. Comandos Directos

#### Análisis del PR
```bash
python3 AI_AGENTS/gravity_training_orchestrator.py --mode analyze
```

#### Ejecución Completa
```bash
python3 AI_AGENTS/gravity_training_orchestrator.py --mode execute
```

#### Status Actual
```bash
python3 AI_AGENTS/gravity_training_orchestrator.py --mode status
```

---

## 📚 Documentación

Empieza por aquí:
1. **[GRAVITY_AGENT_INDEX.md](GRAVITY_AGENT_INDEX.md)** - Índice maestro
2. **[GRAVITY_AGENT_EXECUTIVE_SUMMARY.md](GRAVITY_AGENT_EXECUTIVE_SUMMARY.md)** - Resumen ejecutivo
3. **[GRAVITY_TRAINING_ORCHESTRATOR_README.md](GRAVITY_TRAINING_ORCHESTRATOR_README.md)** - Docs completas

---

## 🎯 Uso en Python

```python
from AI_AGENTS.gravity_training_orchestrator import GravityTrainingOrchestrator

# Inicializar agente
agent = GravityTrainingOrchestrator(
    workspace_path="/workspace",
    auto_approve=True,
    execution_mode="automated"
)

# Analizar PR #87
analysis = agent.analyze_pr_87()

# Ejecutar fase específica
result = agent.execute_integration_phase("phase_1")

# Ejecución completa
summary = agent.execute_full_integration()

# Generar handoff
handoff = agent.generate_handoff_package("IntegrationAgent", "phase_2")

# Status report
report = agent.generate_status_report()
print(report)
```

---

## 📁 Ver Outputs

```bash
# Listar outputs generados
ls -lh consolidation/training_integration/

# Ver análisis del PR
cat consolidation/training_integration/pr_87_analysis.json

# Ver plan de implementación
cat consolidation/training_integration/implementation_plan.json

# Ver logs
tail -f consolidation/training_integration/logs/*.log
```

---

## ✅ Validación

El agente ya fue probado:
- ✅ Modo análisis funcional
- ✅ Quick start ejecutado exitosamente
- ✅ Phase 0 completada
- ✅ 6 outputs generados
- ✅ Integración con orchestrator validada

---

## 🆘 Troubleshooting

### Error: Python not found
```bash
# Usar python3
python3 AI_AGENTS/run_gravity_orchestrator.py
```

### Error: Orchestrator modules not available
El agente funciona en modo standalone. Esto es normal y esperado.

### Ver logs de error
```bash
cat consolidation/training_integration/logs/*.log
```

---

## 📊 Próximos Pasos

1. ✅ Ejecutar quick start (5 min)
2. ⏳ Revisar outputs generados (5 min)
3. ⏳ Leer documentación (15 min)
4. ⏳ Ejecutar Phase 1 (45 min)
5. ⏳ Completar fases 2-5 (3 horas)
6. ⏳ Validar sistema completo (30 min)

**Total estimado: 4.5 horas**

---

## 🎉 ¡Listo!

El agente está completamente funcional y listo para orquestar la implementación del sistema de entrenamiento del ChatBot.

**Comienza ahora:**
```bash
python3 AI_AGENTS/run_gravity_orchestrator.py
```
