# Agente de IA para Análisis y Mejora del Repositorio

Agente especializado que analiza el estado completo del repositorio usando prompts optimizados y sugiere mejores prácticas para commits, branches, y almacenamiento.

## 🎯 Características

✅ **Análisis Completo del Repositorio**
- Análisis de branches (local, remote, merged, stale)
- Análisis de commits (calidad, conventional commits, frecuencia)
- Análisis de remotes y estado Git
- Análisis de estructura del repositorio

✅ **Sugerencias Inteligentes con IA**
- Mejores prácticas para commits (conventional commits, mensajes)
- Gestión de branches (naming, limpieza, estrategia)
- Almacenamiento y backups (local, remoto, frecuencia)
- Organización del repositorio

✅ **Recomendaciones Específicas**
- Plan de acción priorizado (alta/media/baja prioridad)
- Ejemplos concretos de implementación
- Acciones específicas a tomar

## 🚀 Uso Rápido

```bash
# Análisis completo del repositorio actual
python3 repo_analysis_improvement_agent.py

# Análisis de un repositorio específico
python3 repo_analysis_improvement_agent.py --repo-path /ruta/al/repo

# Guardar reporte con nombre personalizado
python3 repo_analysis_improvement_agent.py --output mi_analisis.json
```

## 📊 Qué Analiza

### 1. Repositorio Git
- ✅ Estado de branches (local y remote)
- ✅ Calidad de commits y mensajes
- ✅ Uso de conventional commits
- ✅ Branches merged que deberían eliminarse
- ✅ Naming conventions de branches
- ✅ Estado del working directory
- ✅ Configuración de remotes

### 2. Estructura del Repositorio
- ✅ Archivos por tipo
- ✅ Directorios y organización
- ✅ Archivos grandes (>1MB)
- ✅ Estructura general

### 3. Almacenamiento y Backups
- ✅ Backups locales detectados
- ✅ Remotes configurados
- ✅ Estrategia de backup actual
- ✅ Recomendaciones de almacenamiento

## 💡 Mejoras que Sugiere

### Commits
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, etc.
- **Calidad de mensajes**: Longitud, claridad, formato
- **Frecuencia**: Cuándo hacer commits

### Branches
- **Naming conventions**: `feature/`, `fix/`, `hotfix/`, etc.
- **Limpieza**: Eliminar branches merged
- **Estrategia**: Git flow, GitHub flow, etc.

### Almacenamiento
- **Backups locales**: Estructura y frecuencia
- **Backups remotos**: Múltiples remotes
- **Estrategia**: Daily, weekly, monthly backups

## 📋 Ejemplo de Salida

```
================================================================================
RESUMEN DEL ANÁLISIS
================================================================================

📊 Estadísticas:
  • Branches: 67
  • Commits: 96
  • Conventional commits: 27.1%
  • Issues detectados: 5

💡 Mejoras identificadas: 12
  • Alta prioridad: 5
  • Media prioridad: 4
  • Baja prioridad: 3

📄 Reporte completo guardado en: repo_analysis_report_20251205_103552.json
```

## 📄 Formato del Reporte

El reporte JSON incluye:

```json
{
  "timestamp": "2025-12-05T10:35:52",
  "repo_path": "/ruta/al/repo",
  "git_analysis": {
    "branches": {...},
    "commits": {...},
    "remotes": {...},
    "status": {...},
    "statistics": {...},
    "issues": [...]
  },
  "repo_structure": {...},
  "storage_analysis": {...},
  "improvements": [
    {
      "category": "commits",
      "priority": "high",
      "issue": "Bajo porcentaje de conventional commits",
      "recommendation": "Usar conventional commits",
      "action": "Configurar commitizen",
      "example": "feat: agregar sistema de autenticación"
    }
  ],
  "recommendations": {...},
  "action_plan": [
    {
      "phase": "Inmediato (Esta semana)",
      "items": [...]
    }
  ]
}
```

## 🔧 Integración con Otros Agentes

El agente se integra automáticamente con:
- ✅ `unified_credentials_manager.py` - Carga credenciales automáticamente
- ✅ `prompt_generator.py` - Usa prompts optimizados
- ✅ `model_integrator.py` - Análisis con IA
- ✅ `github_analyzer.py` - Análisis de GitHub (opcional)

## 📚 Mejores Prácticas Sugeridas

### Commits
1. **Conventional Commits**: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`
2. **Mensajes claros**: 50 caracteres máximo para título, cuerpo opcional
3. **Frecuencia**: Commits pequeños y frecuentes

### Branches
1. **Naming**: `feature/nombre`, `fix/nombre`, `hotfix/nombre`
2. **Limpieza**: Eliminar branches merged regularmente
3. **Estrategia**: Usar Git Flow o GitHub Flow

### Almacenamiento
1. **Backups locales**: Estructura organizada por frecuencia
2. **Múltiples remotes**: GitHub + backup remote
3. **Frecuencia**: Daily para desarrollo activo, weekly para mantenimiento

## 🎯 Plan de Acción

El agente genera un plan de acción priorizado:

1. **Inmediato (Esta semana)**: Mejoras de alta prioridad
2. **Corto plazo (Este mes)**: Mejoras de media prioridad
3. **Largo plazo (Este trimestre)**: Mejoras de baja prioridad

## 💻 Ejemplo de Uso en Python

```python
from repo_analysis_improvement_agent import RepoAnalysisImprovementAgent

# Crear agente
agent = RepoAnalysisImprovementAgent(repo_path=".")

# Ejecutar análisis completo
git_analysis = agent.analyze_git_repository()
repo_structure = agent.analyze_repo_structure()
storage_analysis = agent.analyze_storage()
improvements = agent.generate_improvements()

# Generar reporte
report = agent.generate_full_report()
agent.save_report(report, "mi_analisis.json")
```

## 🔍 Ver Resultados

```bash
# Ver reporte JSON
cat repo_analysis_report_*.json | python3 -m json.tool | less

# Filtrar solo mejoras de alta prioridad
cat repo_analysis_report_*.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
high_priority = [i for i in data['improvements'] if i.get('priority') == 'high']
print(json.dumps(high_priority, indent=2, ensure_ascii=False))
"
```

## 📈 Métricas Analizadas

- **Branches**: Total, merged, stale, naming issues
- **Commits**: Total, conventional %, calidad de mensajes
- **Storage**: Backups locales, remotes, estrategia
- **Structure**: Archivos por tipo, organización

## 🛠️ Solución de Problemas

### Error: "No es un repositorio Git"
- Verifica que estés en un directorio con `.git`
- Usa `--repo-path` para especificar la ruta

### Error: "Model Integrator no disponible"
- El agente funcionará pero con recomendaciones básicas
- Configura API keys en `unified_credentials_manager.py`

### Reporte muy grande
- El análisis puede tardar en repositorios grandes
- Usa `head` o `less` para ver el reporte por partes

---

**Creado con**: Prompt Engineering patterns y Model Integrator  
**Versión**: 1.0.0  
**Última actualización**: 2025-12-05

