# GitHub Cloud Agent Blueprint

> Agente diario + evolutivo para BMC Uruguay

## Funcionalidades

1. **Research eCommerce UY** - Stub operativo, enchufable a extractores reales (MLU/retailers/trends)
2. **Scan .env ALL repos + ALL branches** - Keys-only (nunca valores), genera inventario unificado
3. **Publica artifacts + issue diario** - Reporte automático con oportunidades y estado de env
4. **Commit env template** - Actualiza `.env.unified.example` con todas las keys detectadas

## Estructura de Archivos

```
cloud-agent/
├── .github/
│   └── workflows/
│       └── cloud-agent-daily.yml    # Workflow diario + manual trigger
├── config/
│   └── weights.yml                  # Pesos para scoring de oportunidades
├── env/
│   ├── .gitkeep                     # Placeholder para directorio
│   └── .env.unified.example         # (generado) Template unificado de keys
├── scripts/
│   ├── build_issue_body.py          # Genera cuerpo del issue diario
│   ├── research_opportunities.py    # Research stub + scoring
│   └── scan_env_all_repos.py        # Scan multi-repo/multi-branch
├── out/                             # (generado) Outputs del agente
├── .gitignore
└── README.md
```

## Configuración Requerida

### 1. Secrets en GitHub (Settings → Secrets and variables → Actions)

| Secret | Valor | Descripción |
|--------|-------|-------------|
| `GH_OWNER` | `tuUsuarioOrOrg` | Tu usuario u organización de GitHub |
| `GH_SCAN_TOKEN` | `ghp_xxx...` | GitHub App token o Fine-grained PAT **read-only** con `Contents: Read` |

### 2. Variables de Entorno (en workflow)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `MARKET` | `Uruguay` | Mercado objetivo |
| `FOCUS` | `aislamiento, impermeabilización, construcción, techos, selladores` | Categorías de enfoque |
| `REPO_FILTER` | `""` | Filtro de repos (vacío = todos) |
| `BRANCH_LIMIT` | `50` | Límite de branches por repo (0 = sin límite) |
| `BRANCH_ALLOW_REGEX` | `^(main\|master\|develop\|dev\|staging\|production\|release/\|hotfix/)` | Regex para filtrar branches |

## Activación (1 vez)

### A) Subir archivos al repositorio controller

```bash
# Desde el directorio cloud-agent/
git add .
git commit -m "feat: add cloud-agent blueprint"
git push origin main
```

### B) Configurar Secrets en GitHub

1. Ir a **Settings → Secrets and variables → Actions**
2. Crear:
   - `GH_OWNER` = tu usuario/org
   - `GH_SCAN_TOKEN` = token read-only con acceso a repos

### C) Ejecutar manual (primera vez)

1. Ir a **Actions** → workflow "cloud-agent-daily"
2. Click **Run workflow**

### D) Validar outputs

- **Artifacts**: `cloud-agent-output` (contiene `out/*` + `env/.env.unified.example`)
- **Issue**: "Cloud Agent Daily - YYYY-MM-DD"
- **Commit**: `env/.env.unified.example` actualizado

## Ajuste de Performance

Si el scan tarda mucho:

1. **Limitar branches**: Ajustar `BRANCH_LIMIT` (ej: `50`)
2. **Filtrar branches**: Usar `BRANCH_ALLOW_REGEX` más restrictivo
3. **Filtrar repos**: Usar `REPO_FILTER` para escanear solo repos específicos

## Riesgos (Semáforo)

| Color | Descripción |
|-------|-------------|
| 🟢 Verde | Keys-only (sin valores) + artifacts |
| 🟡 Amarillo | All repos + all branches puede pegar rate limits / timeout |
| 🔴 Rojo | Token con permisos excesivos (usar read-only, rotar si se expone) |

## Seguridad

⚠️ **IMPORTANTE**: Este agente JAMÁS lee/imprime valores secretos; solo KEYS.

- El token `GH_SCAN_TOKEN` debe ser **read-only**
- Solo se extraen nombres de variables, nunca valores
- El archivo `.env.unified.example` contiene placeholders (`=__REQUIRED__`)

## Próximos Pasos

1. Conectar extractores reales (MLU/retailers/trends) y agregar evidencia url/fecha
2. Implementar análisis de tendencias con datos verificables
3. Agregar integración con sistemas de pricing

## Mini-Scorecard

| Aspecto | Puntuación |
|---------|------------|
| Operatividad diaria | 9/10 |
| Seguridad (no secretos) | 10/10 |
| Cobertura repos/branches | 8/10 (sube con tuning) |
| Research real (extractores) | 3/10 (stub; listo para enchufar) |

---

**EXPORT_SEAL v1**
- project: bmc-uy
- prompt_id: cloud-agent-pack
- version: 1.0.0
- created_at: 2025-12-14
- author: Matias Portugau
- origin: github-cloud-agent-blueprint
