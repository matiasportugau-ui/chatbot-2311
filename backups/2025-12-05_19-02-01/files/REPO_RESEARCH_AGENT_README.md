# Agente de Investigación de Repositorios iOS

Agente especializado en investigación de repositorios GitHub iOS y análisis de workspace local para generar planes de consolidación y mejora cruzada.

## 🎯 Objetivo

Este agente investiga:
1. **Todos los repositorios iOS en GitHub** y sus branches
2. **Estado del workspace local** (estructura, módulos, dependencias)
3. **Mejoras cruzadas** desde distintos orígenes
4. **Plan de consolidación** para crear un nuevo repositorio evolucionado

## ✨ Características

- 🔍 **Descubrimiento automático** de repositorios iOS en GitHub
- 🌿 **Análisis completo de branches** (todas las ramas de cada repo)
- 📦 **Evaluación del workspace local** (archivos, módulos, dependencias, Git)
- 🤖 **Análisis con IA** para identificar fortalezas y mejoras
- 🔄 **Identificación de mejoras cruzadas** desde múltiples fuentes
- 📋 **Generación de plan de consolidación** estructurado y accionable
- 📊 **Reportes completos** en JSON con toda la información

## 🚀 Uso Rápido

### Opción 1: Script de ejecución (recomendado)

```bash
# Hacer ejecutable
chmod +x run_repo_research.sh

# Ejecutar
./run_repo_research.sh
```

### Opción 2: Ejecución directa

```bash
python3 repo_research_agent.py
```

### Opción 3: Con opciones personalizadas

```bash
python3 repo_research_agent.py \
    --workspace /ruta/al/workspace \
    --github-owner matiasportugau-ui \
    --output mi_reporte.json
```

## 📋 Opciones de Línea de Comandos

```
--workspace PATH       Ruta del workspace a analizar (default: directorio actual)
--github-owner OWNER   Propietario/organización de GitHub (default: matiasportugau-ui)
--output FILE          Archivo de salida para el reporte JSON
--skip-github          Saltar investigación de repositorios GitHub
--skip-workspace       Saltar análisis del workspace local
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# GitHub Token (opcional pero recomendado)
export GITHUB_TOKEN="tu_token_de_github"

# GitHub Owner (opcional, default: matiasportugau-ui)
export GITHUB_OWNER="matiasportugau-ui"
```

### Configuración en .env

Crea un archivo `.env` o `.env.local`:

```env
GITHUB_TOKEN=tu_token_aqui
GITHUB_OWNER=matiasportugau-ui
```

## 📊 Salida del Agente

El agente genera un reporte JSON completo con:

### 1. Repositorios iOS de GitHub
- Lista completa de repositorios iOS encontrados
- Branches de cada repositorio
- Workflows de GitHub Actions
- Pull Requests relevantes
- Estadísticas resumidas

### 2. Análisis del Workspace Local
- Estructura de archivos (por extensión, tipo, tamaño)
- Módulos identificados (Python, iOS, etc.)
- Dependencias (Python, Node, iOS)
- Estado Git (branches, remotes, cambios)
- Calidad de código (tests, linting)
- Documentación disponible
- Archivos de configuración

### 3. Mejoras Identificadas
- Mejoras desde repositorios GitHub
- Mejoras sugeridas por IA
- Priorización de mejoras
- Acciones recomendadas

### 4. Plan de Consolidación
- Fases de ejecución detalladas
- Arquitectura propuesta
- Estrategia de migración
- Timeline estimado
- Riesgos y mitigaciones
- Criterios de éxito

### 5. Recomendaciones
- Recomendaciones prioritarias
- Próximos pasos sugeridos
- Mejores prácticas

## 🔍 Ejemplo de Uso Completo

```python
from repo_research_agent import RepoResearchAgent

# Crear agente
agent = RepoResearchAgent(workspace_path="/ruta/al/workspace")

# Fase 1: Investigar repositorios iOS en GitHub
github_results = agent.research_github_ios_repos(owner="matiasportugau-ui")

# Fase 2: Evaluar workspace local
workspace_results = agent.evaluate_local_workspace()

# Fase 3: Identificar mejoras cruzadas
improvements = agent.identify_cross_improvements()

# Fase 4: Generar plan de consolidación
consolidation_plan = agent.generate_consolidation_plan()

# Generar reporte completo
report = agent.generate_full_report()

# Guardar reporte
output_file = agent.save_report(report, filename="mi_reporte.json")
print(f"Reporte guardado en: {output_file}")
```

## 🏗️ Arquitectura del Agente

El agente utiliza:

1. **Prompt Generator**: Genera prompts optimizados usando patrones de prompt engineering
2. **Model Integrator**: Integra con múltiples proveedores de IA (OpenAI, Groq, Gemini, etc.)
3. **GitHub Analyzer**: Analiza repositorios, branches, workflows y PRs
4. **Análisis Local**: Evalúa estructura, módulos, dependencias y calidad del código

## 📝 Formato del Reporte

El reporte se guarda en formato JSON con la siguiente estructura:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "agent_prompt": "...",
  "github_ios_repos": {
    "summary": {
      "total_repos": 5,
      "total_branches": 15,
      "total_workflows": 8
    },
    "repositories": [...]
  },
  "local_workspace": {
    "files": {...},
    "modules": {...},
    "dependencies": {...},
    "git_status": {...},
    "code_quality": {...},
    "documentation": {...},
    "configuration": {...}
  },
  "improvements": [...],
  "consolidation_plan": {
    "phases": [...],
    "architecture": {...},
    "migration_strategy": {...},
    "timeline": "...",
    "risks": [...],
    "success_criteria": [...]
  },
  "recommendations": [...]
}
```

## 🔑 Palabras Clave para iOS

El agente busca repositorios iOS usando estas palabras clave:
- `ios`
- `swift`
- `swiftui`
- `uikit`
- `xcode`
- `ios-app`
- `iphone`
- `ipad`

## ⚙️ Dependencias

El agente utiliza componentes del proyecto:
- `model_integrator.py` - Integración con modelos de IA
- `github_analyzer.py` - Análisis de GitHub
- `prompt_generator.py` - Generación de prompts

Dependencias externas:
- `requests` - Para GitHub API
- Python 3.8+

## 🎯 Casos de Uso

1. **Consolidación de Repositorios**: Identificar repositorios iOS para consolidar
2. **Análisis de Workspace**: Evaluar estado actual del proyecto local
3. **Identificación de Mejoras**: Encontrar mejoras desde distintos orígenes
4. **Planificación de Migración**: Generar plan estructurado para consolidación
5. **Arquitectura Evolucionada**: Diseñar nuevo repositorio mejorado

## 📈 Próximos Pasos

Después de ejecutar el agente:

1. **Revisar el reporte JSON** generado
2. **Analizar mejoras identificadas** y priorizarlas
3. **Revisar el plan de consolidación** y ajustar según necesidades
4. **Implementar mejoras** siguiendo las fases del plan
5. **Crear nuevo repositorio** siguiendo la arquitectura propuesta

## 🐛 Solución de Problemas

### Error: "GitHub Analyzer no disponible"
- Verifica que `github_analyzer.py` esté en el mismo directorio
- Verifica que `requests` esté instalado: `pip install requests`

### Error: "Model Integrator no disponible"
- Verifica que `model_integrator.py` esté disponible
- Configura las variables de entorno para IA (OPENAI_API_KEY, GROQ_API_KEY, etc.)

### Error: "GitHub API rate limit"
- El agente respeta los límites de la API
- Considera usar un token de GitHub con más permisos
- Ejecuta en horarios de menor uso

### No se encuentran repositorios iOS
- Verifica que el `GITHUB_OWNER` sea correcto
- Verifica que el `GITHUB_TOKEN` tenga permisos de lectura
- Revisa las palabras clave de búsqueda en el código

## 📚 Referencias

- [Prompt Engineering Knowledge Base](./PROMPT_ENGINEERING_KNOWLEDGE_BASE.md)
- [GitHub Analyzer](./github_analyzer.py)
- [Model Integrator](./model_integrator.py)
- [Prompt Generator](./prompt_generator.py)

## 🤝 Contribuciones

Para mejorar el agente:
1. Agrega nuevos patrones de análisis
2. Mejora la detección de repositorios iOS
3. Optimiza la generación de planes
4. Agrega más fuentes de mejoras

---

**Creado con**: Patrones de Prompt Engineering y Model Integrator del proyecto  
**Versión**: 1.0.0  
**Última actualización**: 2024


