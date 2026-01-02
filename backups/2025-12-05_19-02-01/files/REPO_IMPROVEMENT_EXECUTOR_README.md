# Ejecutor de Mejoras del Repositorio con Aprobación

Sistema que **propone mejoras** pero **NUNCA las ejecuta automáticamente** sin tu aprobación explícita.

## 🎯 Características Principales

✅ **Genera Planes de Ejecución Detallados**
- Analiza el repositorio completo
- Identifica mejoras necesarias
- Crea plan de ejecución paso a paso
- Estima tiempo y riesgos

✅ **Sistema de Aprobación Obligatorio**
- **NUNCA ejecuta sin tu aprobación**
- Te muestra exactamente qué se va a hacer
- Permite aprobar todo o por fases
- Puedes rechazar cualquier acción

✅ **Ejecución Controlada**
- Solo ejecuta lo que apruebes
- Crea backup antes de ejecutar
- Reporta resultados de cada acción
- Plan de rollback incluido

## 🚀 Uso Rápido

### Opción 1: Solo Generar Plan (Recomendado para empezar)

```bash
# Genera el plan pero NO ejecuta nada
python3 repo_improvement_executor.py --plan-only
```

Esto te mostrará:
- Qué mejoras se proponen
- Qué acciones se ejecutarían
- Tiempo estimado
- Riesgos identificados
- Plan de rollback

### Opción 2: Generar Plan y Solicitar Aprobación

```bash
# Genera plan y te pregunta qué ejecutar
python3 repo_improvement_executor.py
```

O usando el script:

```bash
./ejecutar_plan_mejoras.sh
```

## 📋 Flujo de Trabajo

```
1. Análisis del Repositorio
   ↓
2. Generación de Plan de Ejecución
   ↓
3. Revisión del Plan (TÚ decides)
   ↓
4. Aprobación (TÚ apruebas qué ejecutar)
   ↓
5. Backup Automático (antes de ejecutar)
   ↓
6. Ejecución Solo de lo Aprobado
   ↓
7. Reporte de Resultados
```

## 🔍 Qué Hace el Plan

### Fase 1: Limpieza de Branches (Bajo Riesgo)
- Elimina branches merged que ya no se usan
- Comando: `git branch -d <branch-name>`
- **Reversible**: No (pero branches merged ya están en main)

### Fase 2: Configuración de Conventional Commits (Bajo Riesgo)
- Crea archivos de configuración
- Documenta convenciones
- **Reversible**: Sí

### Fase 3: Sistema de Backups (Bajo Riesgo)
- Crea estructura de directorios de backup
- Configura organización
- **Reversible**: Sí

### Fase 4: Configuración de Remotes (Bajo Riesgo)
- Agrega remote de backup (requiere URL)
- **Reversible**: Sí

## 💡 Ejemplo de Interacción

```
================================================================================
PLAN DE EJECUCIÓN GENERADO
================================================================================

📊 Resumen del Análisis:
  • Branches: 67
  • Commits: 96
  • Issues detectados: 5
  • Mejoras identificadas: 12

⏱️  Tiempo estimado: 35-45 minutos

📋 Fases de Ejecución (4):

  Fase 1: Limpieza de Branches
    Descripción: Eliminar branches merged y organizar estructura
    Riesgo: LOW
    Tiempo: 5-10 minutos
    Acciones: 3

      1. Eliminar branches merged sin usar
         Tipo: git_branch_delete
         Seguro: ✅ Sí
         Reversible: ❌ No
         Comando:
           git branch -d feature/old-feature-1
           git branch -d feature/old-feature-2

================================================================================
APROBACIÓN REQUERIDA
================================================================================

⚠️  IMPORTANTE: Este plan modificará tu repositorio.
   Revisa cuidadosamente cada fase antes de aprobar.

Opciones:
  1. Aprobar TODO el plan
  2. Aprobar por fases (seleccionar qué ejecutar)
  3. Rechazar (no ejecutar nada)
  4. Ver detalles de una fase específica
  5. Modificar plan

¿Qué deseas hacer? [3]: 
```

## 🛡️ Seguridad

### Antes de Ejecutar
- ✅ Crea backup automático del estado actual
- ✅ Muestra exactamente qué se va a hacer
- ✅ Requiere aprobación explícita

### Durante la Ejecución
- ✅ Solo ejecuta acciones aprobadas
- ✅ Reporta cada acción
- ✅ Maneja errores gracefully

### Después de Ejecutar
- ✅ Reporte completo de resultados
- ✅ Plan de rollback disponible
- ✅ Backup guardado para recuperación

## 📄 Archivos Generados

1. **`execution_plan_YYYYMMDD_HHMMSS.json`**
   - Plan completo de ejecución
   - Puedes revisarlo y modificarlo antes de aprobar

2. **`execution_results_YYYYMMDD_HHMMSS.json`**
   - Resultados de la ejecución
   - Qué se ejecutó exitosamente
   - Qué falló

3. **Backup Git Bundle**
   - `~/backups/chatbot-2311/pre_execution/repo_backup_*.bundle`
   - Backup completo antes de ejecutar

## 🔧 Opciones de Línea de Comandos

```bash
# Solo generar plan (no ejecutar)
python3 repo_improvement_executor.py --plan-only

# Generar plan y solicitar aprobación
python3 repo_improvement_executor.py

# Especificar ruta del repositorio
python3 repo_improvement_executor.py --repo-path /ruta/al/repo

# Aprobar todo automáticamente (NO RECOMENDADO)
python3 repo_improvement_executor.py --approve-all
```

## 📊 Estructura del Plan

El plan JSON incluye:

```json
{
  "timestamp": "2025-12-05T10:35:52",
  "repo_path": "/ruta/al/repo",
  "analysis_summary": {
    "branches": 67,
    "commits": 96,
    "issues": 5,
    "improvements": 12
  },
  "execution_phases": [
    {
      "phase": 1,
      "name": "Limpieza de Branches",
      "description": "...",
      "risk_level": "low",
      "estimated_time": "5-10 minutos",
      "actions": [...]
    }
  ],
  "estimated_time": "35-45 minutos",
  "risks": [...],
  "rollback_plan": {...}
}
```

## ⚠️ Importante

1. **Siempre revisa el plan** antes de aprobar
2. **El backup se crea automáticamente** pero verifica que se creó
3. **Puedes aprobar por fases** - no necesitas aprobar todo
4. **Puedes rechazar** cualquier fase o acción
5. **El plan se guarda** - puedes ejecutarlo más tarde

## 🎯 Casos de Uso

### Caso 1: Primera Vez (Explorar)
```bash
# Solo generar plan para ver qué se propone
python3 repo_improvement_executor.py --plan-only
```

### Caso 2: Ejecución Selectiva
```bash
# Generar plan y aprobar solo algunas fases
python3 repo_improvement_executor.py
# Luego seleccionar opción 2 y elegir fases específicas
```

### Caso 3: Ejecución Completa
```bash
# Generar plan y aprobar todo
python3 repo_improvement_executor.py
# Luego seleccionar opción 1 para aprobar todo
```

## 🔄 Rollback

Si algo sale mal:

1. **Usar backup creado**:
   ```bash
   git clone repo_backup_*.bundle backup-repo
   ```

2. **Revertir cambios específicos**:
   - Ver plan de rollback en el JSON del plan
   - Ejecutar comandos de rollback manualmente

3. **Restaurar desde remote**:
   ```bash
   git fetch origin
   git reset --hard origin/main
   ```

## 📚 Integración

El ejecutor se integra con:
- ✅ `repo_analysis_improvement_agent.py` - Para análisis
- ✅ `unified_credentials_manager.py` - Para credenciales
- ✅ `auto_backup_agent.py` - Para backups

---

**Recuerda**: Este sistema **NUNCA ejecuta cambios sin tu aprobación explícita**. 
Siempre revisa el plan antes de aprobar.

