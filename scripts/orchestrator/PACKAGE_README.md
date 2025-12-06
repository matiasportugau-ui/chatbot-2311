# 📦 Paquete de Orquestación - Sistema Multi-Agente

## 🚀 Instalación y Configuración Automática

Este paquete incluye un sistema completo de orquestación multi-agente que se ejecuta automáticamente en todas tus sesiones.

### Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r scripts/orchestrator/requirements.txt

# 2. Instalar auto-start
bash scripts/orchestrator/install_auto_start.sh

# 3. Reiniciar terminal o ejecutar:
source ~/.zshrc  # o ~/.bashrc según tu shell
```

### Verificación

```bash
# Verificar que está instalado
cat ~/.zshrc | grep "Auto-Start Orchestrator"

# Ver logs
tail -f consolidation/logs/auto_start.log

# Verificar estado
python scripts/orchestrator/run_automated_execution.py --status
```

---

## 🏗️ Arquitectura Multi-Agente

### Sistema de Delegación de Tareas

La Fase 0 utiliza un sistema de delegación donde el **DiscoveryAgent** coordina y delega tareas a agentes especializados:

```
DiscoveryAgent (Coordinador)
    ├── RepositoryAgent
    │   ├── T0.1: Análisis de repositorios
    │   └── T0.2: Análisis de workspace
    │
    ├── IntegrationAgent
    │   └── T0.4: Validación de integraciones
    │
    ├── QuotationAgent
    │   ├── T0.3: Inventario componentes BMC
    │   └── T0.5: Assessment motor cotizaciones
    │
    └── DiscoveryAgent (directo)
        ├── T0.6: Identificación de gaps
        └── T0.7: Baseline de producción
```

### Componentes

1. **AgentInterface** (`agent_interface.py`)
   - Interfaz base para todos los agentes
   - Sistema de comunicación entre agentes
   - Gestión de tareas delegadas

2. **AgentCoordinator** (`agent_interface.py`)
   - Coordina delegación de tareas
   - Gestiona comunicación entre agentes
   - Monitorea ejecución de tareas

3. **Phase0Executor** (`phase_executors/phase_0_executor.py`)
   - Ejecutor principal de Fase 0
   - Delega tareas a agentes especializados
   - Consolida resultados

---

## 📋 Uso Manual

### Ejecutar Fase 0

```bash
# Ejecución automática completa
python scripts/orchestrator/run_automated_execution.py

# Ejecutar solo Fase 0
python -c "
from scripts.orchestrator.main_orchestrator import MainOrchestrator
orchestrator = MainOrchestrator()
orchestrator.execute_phase(0)
"
```

### Delegar Tareas Manualmente

```python
from scripts.orchestrator.agent_interface import AgentCoordinator

coordinator = AgentCoordinator()

# Delegar tarea
coordinator.delegate_task(
    "RepositoryAgent",
    "T0.1",
    {"type": "analyze_repositories", "repositories": [...]}
)

# Ejecutar tarea delegada
result = coordinator.execute_delegated_task("T0.1", "RepositoryAgent")

# Obtener resultado
result = coordinator.get_task_result("T0.1")
```

---

## ⚙️ Configuración

### Auto-Start Config

Archivo: `scripts/orchestrator/config/auto_start_config.json`

```json
{
  "enabled": true,           // Habilitar/deshabilitar auto-start
  "mode": "automated",       // automated | manual | dry-run
  "resume": true,            // Reanudar desde último estado
  "check_interval": 300,     // Intervalo de verificación (segundos)
  "auto_restart": true,      // Reiniciar automáticamente si falla
  "log_file": "consolidation/logs/auto_start.log"
}
```

### Deshabilitar Auto-Start

```bash
# Opción 1: Editar configuración
vim scripts/orchestrator/config/auto_start_config.json
# Cambiar "enabled": false

# Opción 2: Comentar en shell RC
vim ~/.zshrc
# Comentar las líneas de Auto-Start Orchestrator
```

---

## 📊 Monitoreo

### Logs

```bash
# Logs de auto-start
tail -f consolidation/logs/auto_start.log

# Logs de ejecución
tail -f consolidation/reports/status_report_*.json

# Estado de ejecución
cat consolidation/execution_state.json | jq
```

### Estado de Tareas

```bash
# Ver tareas delegadas
ls -la consolidation/tasks/

# Ver resultado de tarea específica
cat consolidation/tasks/T0.1_result.json | jq
```

---

## 🔧 Troubleshooting

### Auto-Start No Funciona

1. Verificar instalación:
```bash
grep "Auto-Start Orchestrator" ~/.zshrc
```

2. Verificar permisos:
```bash
ls -la scripts/orchestrator/auto_start.py
# Debe ser ejecutable
```

3. Verificar logs:
```bash
tail -f consolidation/logs/auto_start.log
```

### Tareas No Se Delegan

1. Verificar que AgentCoordinator está disponible:
```python
from scripts.orchestrator.agent_interface import AgentCoordinator
coordinator = AgentCoordinator()
print(coordinator.agents.keys())
```

2. Verificar directorio de tareas:
```bash
ls -la consolidation/tasks/
```

3. Ver logs de ejecución:
```bash
python scripts/orchestrator/run_automated_execution.py --mode manual
```

---

## 📝 Estructura de Archivos

```
scripts/orchestrator/
├── agent_interface.py          # Sistema de comunicación entre agentes
├── auto_start.py               # Script de auto-inicio
├── install_auto_start.sh       # Instalador de auto-start
├── run_automated_execution.py  # Ejecutor principal
├── phase_executors/
│   └── phase_0_executor.py     # Ejecutor Fase 0 (multi-agente)
├── config/
│   └── auto_start_config.json  # Configuración auto-start
└── consolidation/
    ├── tasks/                  # Tareas delegadas
    ├── discovery/              # Outputs Fase 0
    └── logs/                   # Logs del sistema
```

---

## ✅ Verificación de Instalación

Ejecutar script de verificación:

```bash
python scripts/orchestrator/verify_implementation.py
```

Debería mostrar:
- ✅ Imports: PASS
- ✅ Files: PASS
- ✅ Config Files: PASS
- ✅ Classes: PASS
- ✅ Agent Interface: PASS
- ✅ Multi-Agent System: PASS

---

## 🎯 Próximos Pasos

1. **Ejecutar Fase 0** para validar sistema multi-agente
2. **Revisar outputs** en `consolidation/discovery/`
3. **Continuar con Fases 1-15** usando el mismo sistema

---

**Estado:** ✅ Sistema Multi-Agente Operativo  
**Última Actualización:** 2025-01-12

