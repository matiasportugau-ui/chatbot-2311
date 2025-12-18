# Gravity Agent - Quick Start Guide

## 🚀 Inicio Rápido

### Instalación

No requiere instalación adicional. Solo asegúrate de tener las dependencias del proyecto instaladas.

### Uso Básico

#### 1. Analizar un PR de GitHub

```bash
# Usando el script de inicio rápido
./agents/run_gravity_agent.sh --pr 87

# O directamente con Python
python3 agents/gravity_agent.py --pr 87
```

#### 2. Analizar cambios locales

```bash
./agents/run_gravity_agent.sh --local
```

#### 3. Modo dry-run (solo análisis, sin ejecución)

```bash
./agents/run_gravity_agent.sh --pr 87 --mode dry_run
```

## 📋 Modos de Ejecución

| Modo | Descripción | Ejecuta cambios |
|------|-------------|-----------------|
| `automated` | Ejecución completamente automatizada | ✅ Sí |
| `interactive` | Requiere confirmaciones | ✅ Sí |
| `dry_run` | Solo genera el plan | ❌ No |
| `analysis_only` | Solo interpretación | ❌ No |

## 🎯 Casos de Uso Comunes

### Caso 1: Revisar un PR antes de mergear

```bash
./agents/run_gravity_agent.sh --pr 87 --mode dry_run
```

Esto te mostrará:
- Qué componentes serán afectados
- Qué agentes se necesitarán
- El plan de ejecución propuesto
- Evaluación de riesgos

### Caso 2: Ejecutar cambios de un PR automáticamente

```bash
./agents/run_gravity_agent.sh --pr 87 --mode automated
```

Esto:
1. Analiza el PR
2. Genera un plan
3. Ejecuta el plan automáticamente

### Caso 3: Validar cambios locales antes de commit

```bash
./agents/run_gravity_agent.sh --local --mode analysis_only
```

## 🔍 Ver Resultados

Los resultados se guardan en:
```
consolidation/gravity_agent/gravity_result_<identifier>_<timestamp>.json
```

Para ver el último resultado:
```bash
ls -lt consolidation/gravity_agent/ | head -5
cat consolidation/gravity_agent/gravity_result_87_*.json | jq .
```

## 🛠️ Uso Programático

```python
from agents.gravity_agent import GravityAgent, ExecutionMode

# Crear agente
agent = GravityAgent(execution_mode=ExecutionMode.DRY_RUN)

# Analizar PR
result = agent.interpret_and_orchestrate(pr_number=87)

# Ver resultados
print(f"Intención: {result['interpretation']['intent']}")
print(f"Componentes: {result['interpretation']['affected_components']}")
```

## 📚 Más Información

- Documentación completa: [GRAVITY_AGENT_README.md](GRAVITY_AGENT_README.md)
- Ejemplos de código: [gravity_agent_example.py](gravity_agent_example.py)

## ⚠️ Notas Importantes

1. **Modo dry-run recomendado para pruebas**: Usa `--mode dry_run` la primera vez
2. **Backup antes de ejecutar**: El modo `automated` puede modificar archivos
3. **GitHub token opcional**: Solo necesario si quieres analizar PRs privados
4. **Resultados guardados**: Todos los resultados se guardan automáticamente

## 🆘 Troubleshooting

### Error: "Planning components not available"
- Verifica que las dependencias del proyecto estén instaladas
- Asegúrate de estar en el directorio raíz del proyecto

### Error: "GitHub integration not available"
- Esto es normal si no tienes configurado el token de GitHub
- Puedes proporcionar `pr_data` directamente en el código

### Error: "Orchestrator not available"
- Verifica que `scripts/orchestrator/main_orchestrator.py` exista
- El agente funcionará en modo limitado sin el orchestrator

## 🎓 Ejemplos Avanzados

Ver [gravity_agent_example.py](gravity_agent_example.py) para ejemplos más detallados.
