<!-- 826775db-d09c-4acd-9717-e29f196b10cb eb61f2b4-0c84-4188-bc5e-92959386a048 -->
# Plan Maestro de Consolidación: Repositorios + Workspace + Evolución Cruzada

## Objetivo General

Crear un repositorio monorepo maestro `Ultimate-CHATBOT` que consolide:

1. **Repositorios de GitHub** (preservando historial Git)
2. **Workspace actual** (`chatbot-2311` con 30+ archivos Python, 217 MD, sistema funcional al 70%)
3. **Evolución cruzada** de componentes (identificar mejores versiones, resolver duplicados, optimizar dependencias)

## Fuentes de Consolidación

### Repositorios de GitHub

1. **bmc-cotizacion-inteligente** → `services/quotation/`
2. **chatbot-2311** (GitHub) → Comparar/mergear con workspace local
3. **ChatBOT** → `docker/` + `scripts/`
4. **background-agents** → `packages/background-agents/`
5. **Dashboard-bmc** → `apps/dashboard/`

### Workspace Actual (chatbot-2311)

- **Ubicación:** `/Users/matias/chatbot2511/chatbot-2311`
- **Estado:** Sistema core funcional (70% completado, cerca de producción)
- **Componentes clave:**
  - `api_server.py` (API FastAPI funcional)
  - `ia_conversacional_integrada.py` (IA conversacional 95%)
  - `sistema_cotizaciones.py` (Sistema cotizaciones 100%)
  - `base_conocimiento_dinamica.py` (Knowledge base 90%)
  - 217 archivos Markdown de documentación
  - 20+ archivos JSON de configuración
  - 4 workflows n8n creados

## Estructura del Monorepo Maestro

```
Ultimate-CHATBOT/
├── .github/workflows/          # CI/CD workflows
├── apps/
│   ├── dashboard/              # Dashboard-bmc (GitHub)
│   └── integrations/
│       └── whatsapp/           # chatbot-2311 (workspace + GitHub merge)
├── services/
│   ├── quotation/              # bmc-cotizacion-inteligente (GitHub)
│   └── core/                   # Sistema core del workspace
│       ├── api/                # api_server.py
│       ├── ai/                 # ia_conversacional_integrada.py
│       └── knowledge/          # base_conocimiento_dinamica.py
├── packages/
│   └── background-agents/     # background-agents (GitHub)
├── docker/                     # ChatBOT docker configs
├── scripts/
│   ├── consolidation/         # Scripts de consolidación
│   └── ...                    # Scripts del workspace
├── docs/
│   ├── architecture/          # Documentación arquitectura
│   ├── deployment/            # Guías deployment
│   ├── integration/           # Guías integración
│   └── guides/                # 217 archivos MD organizados
├── data/
│   ├── knowledge_base/        # Base de conocimiento
│   └── config/                # Archivos JSON consolidados
├── docker-compose.yml          # Configuración unificada
├── README.md
└── .gitignore
```

## Fase 1: Análisis Cualitativo y Mapeo Completo

### 1.1 Análisis Cualitativo de Componentes (Cross-Evolution)

- **Archivo:** `scripts/qualitative_analysis.py`
- **Guía de Referencia:** Usar documentos en `/Users/matias/chatbot2511/chatbot-2311/.cursor/plans/`:
  - `BMC_ECOSYSTEM_ANALYSIS_EXECUTIVE_SUMMARY.md` - Health Score B+ (75/100), mapa de módulos
  - `BMC_ECOSYSTEM_ANALYSIS_chatbot-2311.md` - Maturity Score 72/100, scores por módulo
  - `BMC_ECOSYSTEM_INTEGRATION_OPPORTUNITIES.md` - 4 oportunidades de integración estratégicas
- **Funcionalidad:**
  - Comparar versiones de archivos entre repos GitHub y workspace
  - Evaluar calidad: código, tests, documentación, completitud
  - **Usar scores de madurez del análisis:** Priorizar componentes con scores >80/100
  - Detectar dependencias cruzadas entre componentes
  - Identificar evolución: versión más reciente/completa
  - Generar matriz de decisión para cada componente duplicado
  - Analizar métricas: líneas de código, complejidad, cobertura de tests
  - **Referencias clave:**
    - `bmc-cotizacion-inteligente/quote-engine`: 85/100 (más evolucionado)
    - `chatbot-2311/base_conocimiento_dinamica`: 80/100 (sistema de aprendizaje)
    - `chatbot-2311/api_server`: 85/100 (API funcional)

### 1.2 Análisis del Workspace Actual

- **Archivo:** `scripts/analyze_workspace.py`
- **Funcionalidad:**
  - Inventariar todos los archivos del workspace (`chatbot-2311`)
  - Identificar componentes core vs integraciones
  - Mapear dependencias internas (imports, referencias)
  - Detectar archivos únicos del workspace
  - Generar estructura de componentes con estado (funcional/parcial/pendiente)
  - Analizar 217 archivos MD y organizarlos por categoría

### 1.3 Análisis de Repositorios GitHub

- **Archivo:** `scripts/analyze_github_repos.py`
- **Funcionalidad:**
  - Clonar/analizar cada repositorio de GitHub
  - Comparar estructura con workspace
  - Detectar archivos duplicados
  - Identificar versiones más recientes (fechas de commit)
  - Mapear historial de commits
  - Analizar ramas y tags

### 1.4 Matriz de Decisión (Cross-Evolution Matrix)

- **Archivo:** `scripts/cross_evolution_matrix.json`
- **Contenido:** Para cada componente duplicado:
  ```json
  {
    "component": "api_server.py",
    "sources": [
      {
        "location": "workspace/chatbot-2311",
        "version": "latest",
        "quality_score": 95,
        "completeness": 100,
        "last_modified": "2024-12-28",
        "features": ["health_check", "structured_logging"]
      },
      {
        "location": "github/chatbot-2311",
        "version": "v1.2",
        "quality_score": 88,
        "completeness": 85,
        "last_modified": "2024-12-15"
      }
    ],
    "decision": "use_workspace",
    "reason": "Más reciente, más completo, mejor documentado",
    "merge_strategy": "workspace_base_with_github_features"
  }
  ```


## Fase 2: Creación del Monorepo Base

### 2.1 Inicializar Nuevo Repositorio

- Crear directorio `Ultimate-CHATBOT`
- Inicializar git: `git init`
- Crear estructura base de directorios según arquitectura
- Crear `.gitignore` unificado (consolidar de todos los repos)
- Crear `README.md` principal con overview del monorepo

### 2.2 Configuración Base Unificada

- **Archivos a crear:**
  - `docker-compose.yml` (consolidar servicios de todos los repos)
  - `package.json` (raíz, workspace config para npm/pnpm)
  - `requirements.txt` (raíz, dependencias Python unificadas)
  - `.env.example` (variables de entorno consolidadas)
  - `pyproject.toml` (configuración Python moderna)
  - `tsconfig.json` (si hay TypeScript)

## Fase 3: Incorporación del Workspace Actual

### 3.1 Incorporar Workspace como Base

- **Estrategia:** El workspace actual es la versión más reciente y funcional
- **Proceso:**

  1. Copiar workspace completo a estructura del monorepo
  2. Organizar componentes según arquitectura:

     - Core system → `services/core/`
     - Integraciones → `apps/integrations/whatsapp/`
     - Scripts → `scripts/`
     - Documentación → `docs/` (organizada)

  1. Preservar historial Git del workspace si existe

### 3.2 Organización de Componentes del Workspace

- **Core System:**
  - `api_server.py` → `services/core/api/api_server.py`
  - `ia_conversacional_integrada.py` → `services/core/ai/ia_conversacional_integrada.py`
  - `sistema_cotizaciones.py` → `services/core/quotation/sistema_cotizaciones.py`
  - `base_conocimiento_dinamica.py` → `services/core/knowledge/base_conocimiento_dinamica.py`
- **Integraciones:**
  - `integracion_whatsapp.py` → `apps/integrations/whatsapp/integracion_whatsapp.py`
  - `n8n_integration.py` → `apps/integrations/n8n/n8n_integration.py`
- **Scripts:**
  - Mantener en `scripts/` con organización por propósito

## Fase 4: Incorporación de Repositorios GitHub (con Cross-Evolution)

### 4.1 Script de Incorporación Inteligente

- **Archivo:** `scripts/consolidate_repos.sh`
- **Estrategia:** Usar `git subtree` + lógica de cross-evolution
- **Proceso para cada repo:**

  1. Consultar matriz de decisión
  2. Si componente existe en workspace:

     - Comparar versiones
     - Decidir: usar workspace, usar GitHub, o mergear

  1. Si no existe: incorporar con `git subtree`
  2. Preservar historial completo con `--prefix`

### 4.2 Orden de Incorporación (Respetando Dependencias)

1. **background-agents** → `packages/background-agents/` (independiente)
2. **bmc-cotizacion-inteligente** → `services/quotation/` (comparar con `sistema_cotizaciones.py` del workspace)
3. **ChatBOT** → `docker/` + `scripts/` (separar componentes)
4. **Dashboard-bmc** → `apps/dashboard/` (independiente)
5. **chatbot-2311 (GitHub)** → Comparar/mergear con workspace

### 4.3 Resolución de Duplicados (Cross-Evolution)

- **Estrategia por tipo de archivo:**
  - **Código Python:** Usar versión del workspace (más reciente, funcional)
  - **Configuración:** Mergear inteligentemente (docker-compose, env vars)
  - **Documentación:** Consolidar y organizar (217 MD → estructura clara)
  - **Tests:** Mantener todos, organizar por componente
  - **Scripts:** Consolidar, eliminar duplicados funcionales

## Fase 5: Evolución Cruzada de Componentes

### 5.1 Merge Inteligente de Componentes Similares

- **Archivo:** `scripts/cross_evolution_merge.py`
- **Componentes a mergear:**
  - `sistema_cotizaciones.py` (workspace) + `bmc-cotizacion-inteligente` (GitHub)
  - `integracion_whatsapp.py` (workspace) + versión GitHub si existe
  - Configuraciones docker-compose (unificar servicios)
  - Dependencias (requirements.txt, package.json)

### 5.2 Optimización de Dependencias Cruzadas

- **Archivo:** `scripts/optimize_dependencies.py`
- **Funcionalidad:**
  - Detectar dependencias compartidas
  - Resolver conflictos de versiones (usar más reciente compatible)
  - Eliminar duplicados
  - Generar `requirements.txt` y `package.json` unificados
  - Configurar workspaces para desarrollo local

## Fase 6: Actualización de Paths y Referencias

### 6.1 Script de Actualización de Imports

- **Archivo:** `scripts/update_imports.py`
- **Funcionalidad:**
  - Buscar imports relativos en todos los archivos Python
  - Actualizar paths según nueva estructura del monorepo
  - Actualizar imports en TypeScript/JavaScript
  - Actualizar paths en configuraciones (docker-compose, n8n workflows)
  - Actualizar referencias en documentación

### 6.2 Actualización de Configuraciones

- **Archivo:** `scripts/update_configs.py`
- **Funcionalidad:**
  - Actualizar paths en `docker-compose.yml`
  - Actualizar variables de entorno
  - Actualizar paths en workflows n8n
  - Actualizar paths en scripts de build/test

## Fase 7: Organización de Documentación

### 7.1 Consolidación de 217 Archivos Markdown

- **Archivo:** `scripts/organize_docs.py`
- **Estructura propuesta:**
  ```
  docs/
  ├── architecture/
  │   ├── system-overview.md
  │   └── component-diagrams.md
  ├── deployment/
  │   ├── docker-deployment.md
  │   └── production-checklist.md
  ├── integration/
  │   ├── whatsapp-setup.md
  │   └── n8n-workflows.md
  ├── api/
  │   └── api-reference.md
  ├── guides/
  │   ├── quick-start.md
  │   └── development-guide.md
  └── README.md (índice principal)
  ```

- **Funcionalidad:**
  - Analizar contenido de cada MD
  - Categorizar automáticamente
  - Mover a estructura organizada
  - Generar índices y enlaces cruzados
  - Eliminar duplicados

## Fase 8: Configuración Unificada

### 8.1 Docker Compose Unificado

- Consolidar servicios de todos los repos y workspace
- Unificar variables de entorno
- Configurar networks y volumes compartidos
- Agregar Qdrant (pendiente del workspace)
- Optimizar configuración para desarrollo y producción

### 8.2 Configuración de Workspaces

- Configurar npm/pnpm workspaces
- Configurar Python paths para imports relativos
- Actualizar scripts de build, test, y deploy
- Configurar pre-commit hooks

## Fase 9: Validación y Testing

### 9.1 Script de Validación Completa

- **Archivo:** `scripts/validate_consolidation.py`
- **Verificaciones:**
  - Todos los archivos migrados correctamente
  - Historial de Git preservado
  - Imports actualizados y funcionando
  - Dependencias resueltas
  - Docker Compose funcional
  - No hay referencias rotas
  - Documentación accesible

### 9.2 Testing de Integración

- Verificar que cada componente funciona en su nueva ubicación
- Probar builds y tests
- Validar que no se rompieron referencias
- Probar flujo completo: API → IA → Cotizaciones

## Fase 10: Documentación Final

### 10.1 README Principal del Monorepo

- Documentar estructura completa del monorepo
- Guía de desarrollo
- Instrucciones de setup
- Referencias a documentación específica
- Roadmap y estado del proyecto

### 10.2 Guía de Migración y Cross-Evolution

- Documentar proceso de consolidación realizado
- Listar decisiones de cross-evolution
- Documentar cambios importantes
- Guía para contribuidores
- Matriz de componentes y sus orígenes

## Scripts a Crear

1. **`scripts/qualitative_analysis.py`** - Análisis cualitativo y cross-evolution
2. **`scripts/analyze_workspace.py`** - Análisis del workspace actual
3. **`scripts/analyze_github_repos.py`** - Análisis de repos GitHub
4. **`scripts/cross_evolution_matrix.json`** - Matriz de decisión
5. **`scripts/consolidate_repos.sh`** - Incorporación con git subtree
6. **`scripts/cross_evolution_merge.py`** - Merge inteligente de componentes
7. **`scripts/optimize_dependencies.py`** - Optimización de dependencias
8. **`scripts/update_imports.py`** - Actualización de paths
9. **`scripts/update_configs.py`** - Actualización de configuraciones
10. **`scripts/organize_docs.py`** - Organización de documentación
11. **`scripts/validate_consolidation.py`** - Validación final

## Guía de Referencia: Análisis del Ecosistema BMC

### Documentos de Análisis (Ubicación: `/Users/matias/chatbot2511/chatbot-2311/.cursor/plans/`)

1. **BMC_ECOSYSTEM_ANALYSIS_EXECUTIVE_SUMMARY.md**

   - Health Score: **B+ (75/100)**
   - Mapa de módulos con scores de madurez
   - Evaluación de riesgos y plan de acción

2. **BMC_ECOSYSTEM_ANALYSIS_chatbot-2311.md**

   - Maturity Score: **72/100 (Tier 2: Mature)**
   - 12 módulos con scores individuales
   - 4 prioridades de evolución

3. **BMC_ECOSYSTEM_INTEGRATION_OPPORTUNITIES.md**

   - 4 oportunidades estratégicas (Unified Quotation P0, Centralized KB P1, Multi-Channel P1, Agent Network P2)
   - Roadmap Q1-Q4 2025

### Métricas Clave para Cross-Evolution

**Módulos de Alta Madurez (usar como referencia):**

- `bmc-cotizacion-inteligente/quote-engine`: **85/100** → Usar como base para Unified Quotation
- `chatbot-2311/base_conocimiento_dinamica`: **85/100** → Integrar con Qdrant
- `chatbot-2311/api_server`: **85/100** → Mantener como base
- `chatbot-2311/ia_conversacional_integrada`: **80/100** → Mantener como base
- `chatbot-2311/sistema_cotizaciones`: **72/100** → Consolidar con bmc-cotizacion-inteligente (85/100)

**Riesgos Críticos (P0) a resolver:**

1. Credenciales WhatsApp pendientes
2. Validación de firmas webhook no implementada
3. Qdrant no desplegado

## Consideraciones Especiales

- **Workspace como base:** El workspace actual es la versión más funcional (70% completo, Maturity 72/100)
- **Preservar historial:** Usar `git subtree` para repos GitHub
- **Cross-evolution:** Priorizar componentes con scores >80/100 del análisis del ecosistema
- **Oportunidades de integración:** Aplicar las 4 oportunidades identificadas durante consolidación
- **Conflictos:** Resolver usando matriz de decisión + scores de madurez
- **Dependencias:** Consolidar y optimizar
- **Documentación:** Organizar 217 archivos MD en estructura clara
- **Testing:** Validar que todo funciona después de consolidación

## Guía de Referencia: Análisis del Ecosistema BMC

### Documentos de Análisis Disponibles

Los siguientes documentos en `/Users/matias/chatbot2511/chatbot-2311/.cursor/plans/` deben usarse como guía durante la consolidación:

1. **BMC_ECOSYSTEM_ANALYSIS_EXECUTIVE_SUMMARY.md**

   - Health Score: **B+ (75/100)**
   - Mapa de módulos con scores de madurez
   - Diagrama de flujo de datos (Mermaid)
   - Evaluación de riesgos (Alto/Medio/Bajo)
   - Plan de acción priorizado

2. **BMC_ECOSYSTEM_ANALYSIS_chatbot-2311.md**

   - Maturity Score: **72/100 (Tier 2: Mature)**
   - Inventario de 12 módulos con scores individuales
   - 4 prioridades de evolución recomendadas
   - Oportunidades de integración
   - Comparación con otros repositorios

3. **BMC_ECOSYSTEM_INTEGRATION_OPPORTUNITIES.md**

   - 4 oportunidades de integración estratégicas:

     1. Unified Quotation System (P0)
     2. Centralized Knowledge Base (P1)
     3. Multi-Channel Orchestration (P1)
     4. Autonomous Agent Network (P2)

   - Roadmap Q1-Q4 2025
   - Matriz de prioridades
   - Análisis de riesgos y mitigaciones

### Métricas Clave del Ecosistema

**Health Score General:** B+ (75/100)

- Funcionalidad: 85/100
- Integración: 60/100
- Seguridad: 40/100
- Documentación: 70/100
- Testing: 50/100
- Deployment: 70/100

**Módulos con Mayor Madurez (usar como referencia en cross-evolution):**

- `bmc-cotizacion-inteligente/quote-engine`: **85/100** (más evolucionado - usar como referencia)
- `chatbot-2311/base_conocimiento_dinamica`: **85/100** (sistema de aprendizaje)
- `chatbot-2311/api_server`: **85/100** (API funcional)
- `chatbot-2311/ia_conversacional_integrada`: **80/100** (IA conversacional)
- `chatbot-2311/sistema_cotizaciones`: **72/100** (consolidar con bmc-cotizacion-inteligente)

**Riesgos Críticos (P0) - Resolver durante consolidación:**

1. Credenciales WhatsApp pendientes
2. Validación de firmas webhook no implementada
3. Qdrant no desplegado

**Oportunidades de Integración (aplicar en monorepo):**

1. **Unified Quotation System** - Consolidar `sistema_cotizaciones.py` (72/100) con `bmc-cotizacion-inteligente` (85/100)
2. **Centralized Knowledge Base** - Integrar `base_conocimiento_dinamica.py` (85/100) con Qdrant
3. **Multi-Channel Orchestration** - Completar integración n8n workflows
4. **Autonomous Agent Network** - Conectar `background-agents` (80% maturity) con sistema principal

## Orden de Ejecución

1. Análisis cualitativo y creación de matriz de decisión (usar scores de madurez como referencia)
2. Análisis del workspace actual
3. Análisis de repositorios GitHub
4. Creación del monorepo base
5. Incorporación del workspace (base funcional)
6. Incorporación de repos GitHub (con cross-evolution, priorizar componentes con scores >80/100)
7. Evolución cruzada y merge de componentes (aplicar oportunidades de integración)
8. Optimización de dependencias
9. Actualización de paths y referencias
10. Organización de documentación
11. Configuración unificada (incluir Qdrant)
12. Validación y testing
13. Documentación final

### To-dos

- [ ] Agent 1: Listar todos los repos de matiasportugau-ui en GitHub
- [ ] Agent 1: Clonar cada repositorio en temp/github-repos/
- [ ] Agent 1: Verificar que todos los repos se clonaron correctamente
- [ ] Agent 1: Analizar estructura de cada repositorio
- [ ] Agent 1: Identificar Code Anchors en cada repo (quote, knowledge, whatsapp, sheets, agents)
- [ ] Agent 1: Analizar historial Git de cada repo (commits, branches, tags)
- [ ] Agent 1: Calcular maturity scores para cada componente usando framework del ecosistema
- [ ] Agent 1: Mapear componentes principales de cada repo con features y dependencias
- [ ] Agent 1: Comparar componentes con análisis del ecosistema (BMC_ECOSYSTEM_ANALYSIS_*.md)
- [ ] Agent 1: Detectar dependencias y conflictos potenciales (package.json, requirements.txt, docker-compose)
- [ ] Agent 1: Preparar repos para git subtree (verificar ramas, crear ramas limpias)
- [ ] Agent 1: Generar reporte consolidado GIT_AGENT_REPORT.md para Orchestrator
- [ ] Agent 2: Escanear recursivamente todo el workspace (/Users/matias/chatbot2511/chatbot-2311)
- [ ] Agent 2: Categorizar archivos por tipo y función (Core, Integrations, Scripts, Docs, Config, Data)
- [ ] Agent 2: Analizar 217 archivos Markdown (categorizar, detectar duplicados, identificar más completos)
- [ ] Agent 2: Analizar componentes core (api_server, ia_conversacional, sistema_cotizaciones, base_conocimiento)
- [ ] Agent 2: Mapear dependencias internas (analizar imports, crear grafo de dependencias)
- [ ] Agent 2: Calcular maturity scores de componentes del workspace usando mismo framework que Agent 1
- [ ] Agent 2: Planificar organización según arquitectura del monorepo (mapping source → target paths)
- [ ] Agent 2: Identificar archivos únicos del workspace (que no existen en repos GitHub)
- [ ] Agent 2: Detectar conflictos potenciales con repos GitHub (nombres similares, funcionalidad duplicada)
- [ ] Agent 2: Preparar estructura de directorios objetivo según organización planificada
- [ ] Agent 2: Generar reporte consolidado WORKSPACE_AGENT_REPORT.md para Orchestrator
- [ ] Orchestrator: Inicializar monorepo Ultimate-CHATBOT (crear directorio, git init, estructura base)
- [ ] Orchestrator: Configurar sistema de comunicación con Agent 1 y Agent 2 (directorios de status, formato)
- [ ] Orchestrator: Cargar análisis del ecosistema como referencia (BMC_ECOSYSTEM_ANALYSIS_*.md)
- [ ] Orchestrator: Monitorear progreso de Agent 1 (Git) cada 5 minutos, detectar bloqueadores
- [ ] Orchestrator: Monitorear progreso de Agent 2 (Workspace) cada 5 minutos, detectar bloqueadores
- [ ] Orchestrator: Revisar reportes consolidados de ambos agentes (GIT_AGENT_REPORT.md, WORKSPACE_AGENT_REPORT.md)
- [ ] Orchestrator: Generar matriz de decisión de cross-evolution (combinar análisis de Agent 1 y Agent 2)
- [ ] Orchestrator: Validar decisiones de cross-evolution (consistencia, priorización, estrategias viables)
- [ ] Orchestrator: Incorporar workspace como base del monorepo (leer organization_plan.json, copiar archivos)
- [ ] Orchestrator: Incorporar repos GitHub usando git subtree (consultar matriz, aplicar estrategias de merge)
- [ ] Orchestrator: Ejecutar merges inteligentes según cross-evolution matrix (Unified Quotation P0, Centralized KB P1, etc.)
- [ ] Orchestrator: Detectar y resolver conflictos (archivos duplicados, dependencias conflictivas)
- [ ] Orchestrator: Validar que no hay referencias rotas (imports, paths en configs, referencias en docs)
- [ ] Orchestrator: Consolidar dependencias (requirements.txt, package.json unificados, resolver conflictos)
- [ ] Orchestrator: Unificar docker-compose.yml (consolidar servicios, agregar Qdrant, unificar env vars)
- [ ] Orchestrator: Actualizar todos los paths e imports (Python/TypeScript, configs, documentación)
- [ ] Orchestrator: Organizar 217 archivos Markdown (leer análisis de Agent 2, mover a estructura, generar índices)
- [ ] Orchestrator: Validar consolidación completa (archivos migrados, historial preservado, imports funcionando)
- [ ] Orchestrator: Ejecutar tests de integración (builds, tests existentes, flujo completo API → IA → Cotizaciones)
- [ ] Orchestrator: Generar documentación final del monorepo (README.md, MIGRATION_GUIDE.md, CROSS_EVOLUTION_DECISIONS.md, ARCHITECTURE.md)