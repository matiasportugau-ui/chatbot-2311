# 🚀 Quick Start: Agente de Investigación de Repositorios iOS

Guía rápida para empezar a usar el agente de investigación.

## ⚡ Inicio Rápido (3 pasos)

### 1. Configurar Variables de Entorno

Crea un archivo `.env` o `.env.local`:

```bash
GITHUB_TOKEN=tu_token_de_github_aqui
GITHUB_OWNER=matiasportugau-ui
```

**Obtener GitHub Token:**
1. Ve a GitHub → Settings → Developer settings → Personal access tokens
2. Genera un nuevo token con permisos de `repo` (lectura de repositorios)
3. Copia el token al archivo `.env`

### 2. Ejecutar el Agente

```bash
# Opción A: Script de ejecución (más fácil)
./run_repo_research.sh

# Opción B: Ejecución directa
python3 repo_research_agent.py

# Opción C: Con opciones personalizadas
python3 repo_research_agent.py --workspace . --output mi_reporte.json
```

### 3. Revisar el Reporte

El agente genera un archivo JSON con el reporte completo:

```bash
# Ver el reporte
cat repo_research_report_*.json | python3 -m json.tool | less
```

## 📋 Qué Hace el Agente

El agente ejecuta 4 fases automáticamente:

1. **🔍 Investigación GitHub**: Busca todos los repositorios iOS y analiza sus branches
2. **📁 Evaluación Workspace**: Analiza tu proyecto local (archivos, módulos, dependencias)
3. **🔄 Mejoras Cruzadas**: Identifica mejoras desde distintos repositorios
4. **📋 Plan Consolidación**: Genera un plan completo para crear un nuevo repo evolucionado

## 📊 Salida Esperada

```
🚀 Iniciando Agente de Investigación de Repositorios iOS
========================================================

✅ Model Integrator inicializado
✅ GitHub Analyzer inicializado
✅ Prompt Generator inicializado

================================================================================
FASE 1: INVESTIGACIÓN DE REPOSITORIOS iOS EN GITHUB
================================================================================

🔍 Descubriendo repositorios bajo matiasportugau-ui...
  ✅ Found: matiasportugau-ui/repo-ios-1
  ✅ Found: matiasportugau-ui/repo-ios-2
📊 Total repositorios iOS encontrados: 2

🌿 Analizando branches de repo-ios-1...
  📦 5 branches, 2 workflows, 10 PRs

================================================================================
FASE 2: EVALUACIÓN DEL WORKSPACE LOCAL
================================================================================

📁 Analizando estructura de archivos...
📦 Analizando módulos...
🔗 Analizando dependencias...
🌿 Analizando estado Git...
✨ Analizando calidad de código...
📚 Analizando documentación...
⚙️  Analizando configuración...

🤖 Usando IA para análisis avanzado...

================================================================================
FASE 3: IDENTIFICACIÓN DE MEJORAS CRUZADAS
================================================================================

🔍 Comparando repositorios GitHub con workspace local...
🤖 Usando IA para identificar mejoras adicionales...

📊 Total mejoras identificadas: 8

================================================================================
FASE 4: GENERACIÓN DE PLAN DE CONSOLIDACIÓN
================================================================================

📄 Reporte guardado en: repo_research_report_20240101_120000.json
```

## 🎯 Casos de Uso Comunes

### Caso 1: Investigar solo repositorios GitHub

```bash
python3 repo_research_agent.py --skip-workspace
```

### Caso 2: Analizar solo workspace local

```bash
python3 repo_research_agent.py --skip-github
```

### Caso 3: Análisis completo con salida personalizada

```bash
python3 repo_research_agent.py \
    --workspace /ruta/al/proyecto \
    --github-owner mi-org \
    --output analisis_completo.json
```

## 📖 Ejemplo de Uso en Python

```python
from repo_research_agent import RepoResearchAgent

# Crear agente
agent = RepoResearchAgent(workspace_path=".")

# Ejecutar investigación completa
github_results = agent.research_github_ios_repos()
workspace_results = agent.evaluate_local_workspace()
improvements = agent.identify_cross_improvements()
plan = agent.generate_consolidation_plan()

# Generar y guardar reporte
report = agent.generate_full_report()
agent.save_report(report, "mi_reporte.json")
```

## 🔧 Solución Rápida de Problemas

### ❌ "GITHUB_TOKEN no está configurado"
**Solución**: Agrega `GITHUB_TOKEN=tu_token` al archivo `.env`

### ❌ "GitHub Analyzer no disponible"
**Solución**: Verifica que `github_analyzer.py` esté en el mismo directorio

### ❌ "Model Integrator no disponible"
**Solución**: Configura al menos una API key de IA (OPENAI_API_KEY, GROQ_API_KEY, etc.)

### ❌ "No se encuentran repositorios iOS"
**Solución**: 
- Verifica que el `GITHUB_OWNER` sea correcto
- Verifica que el token tenga permisos de lectura
- Revisa que los repositorios tengan palabras clave iOS (swift, ios, etc.)

## 📚 Documentación Completa

Para más detalles, consulta:
- [README Completo](./REPO_RESEARCH_AGENT_README.md)
- [Ejemplo de Código](./ejemplo_repo_research.py)

## 💡 Tips

1. **Primera ejecución**: Ejecuta sin opciones para ver qué encuentra
2. **Análisis profundo**: Usa IA configurada para mejores insights
3. **Reportes**: Guarda los reportes para comparar evolución
4. **Mejoras**: Prioriza mejoras por impacto y facilidad de implementación

## ✅ Checklist Pre-Ejecución

- [ ] GitHub Token configurado en `.env`
- [ ] Python 3.8+ instalado
- [ ] `github_analyzer.py` disponible
- [ ] `model_integrator.py` disponible (opcional pero recomendado)
- [ ] Permisos de lectura en repositorios GitHub

---

**¿Listo?** Ejecuta `./run_repo_research.sh` y revisa el reporte generado! 🚀


