# GitHub Cloud Agent Blueprint
## ONE COPY-PASTE PACK (placeholders)

**Repo:** `{CONTROLLER_REPO}` (ej: Matiasportugau-ui)  
**Objetivo:** diario + evolutivo

### Funcionalidades

- **Research eCommerce UY** (stub operativo, enchufable a extractores reales)
- **Scan .env (keys-only)** ALL repos + ALL branches
- **Publica artifacts** + issue diario + (opcional) PR/commit env template

---

## Estructura de Archivos

```
{CONTROLLER_REPO}/
├── .gitignore
├── config/
│   └── weights.yml
├── env/
│   └── .gitkeep
├── scripts/
│   ├── scan_env_all_repos.py
│   ├── research_opportunities.py
│   └── build_issue_body.py
└── .github/
    └── workflows/
        └── cloud-agent-daily.yml
```

---

## Placeholders a Reemplazar

Antes de usar, reemplazar en `.github/workflows/cloud-agent-daily.yml`:

- `{CONTROLLER_REPO}` → Nombre del repo controlador (ej: "Matiasportugau-ui")
- `{GH_OWNER}` → Usuario/org de GitHub (ya configurado: `matiasportugau-ui`)
- `{FOCUS}` → "aislamiento, impermeabilización, construcción, techos, selladores" (ya configurado)
- `{BRANCH_ALLOW_REGEX}` → `^(main|master|develop|dev|staging|production|release/|hotfix/)` (ya configurado)
- `{BRANCH_LIMIT}` → `50` (ya configurado)
- `{SCHEDULE_CRON_UTC}` → `15 11 * * *` (ya configurado - 11:15 UTC diario)

---

## Instrucciones de Activación (1 vez)

### A) En {CONTROLLER_REPO}:

1. **Crear carpetas** (ya creadas):
   ```bash
   mkdir -p config/ env/ scripts/ .github/workflows/
   ```

2. **Archivos creados** con el contenido exacto del blueprint.

3. **Commit & push** a main:
   ```bash
   git add .
   git commit -m "feat: add GitHub Cloud Agent blueprint"
   git push origin main
   ```

### B) Configurar Secrets en GitHub

En GitHub → Settings → Secrets and variables → Actions:

- **GH_OWNER** = `matiasportugau-ui` (o tu usuario/org)
- **GH_SCAN_TOKEN** = Token read-only con acceso a todos los repos a escanear
  - Permisos requeridos: `Contents: Read` en todos los repos
  - Crear Fine-grained PAT o usar GitHub App token

### C) Ejecutar Manualmente (Primera vez)

1. Ir a: **Actions** → workflow "cloud-agent-daily" → **Run workflow**
2. Seleccionar branch: `main`
3. Click en **Run workflow**

### D) Validar Outputs

Después de la ejecución, verificar:

- ✅ **Artifacts:** `cloud-agent-output` (contiene `out/*` + `env/.env.unified.example`)
- ✅ **Issue:** "Cloud Agent Daily - YYYY-MM-DD" (creado/actualizado)
- ✅ **Archivo actualizado:** `env/.env.unified.example` (commit automático si hay cambios)

### E) Ajuste de Performance

Si el workflow tarda mucho:

- Reducir `BRANCH_LIMIT` a `20` o `10`
- Ajustar `BRANCH_ALLOW_REGEX` para filtrar menos branches
- Usar `REPO_FILTER` para escanear solo repos específicos

---

## Riesgos (Semáforo)

### 🟢 Verde
- **Keys-only** (sin valores secretos)
- Artifacts seguros
- Issue diario informativo

### 🟡 Amarillo
- **Rate limits:** Escanear todos los repos + branches puede pegar rate limits de GitHub API
  - Mitigación: Usar `BRANCH_LIMIT` y `BRANCH_ALLOW_REGEX`
- **Timeout:** Workflows pueden tardar > 6 horas con muchos repos
  - Mitigación: Filtrar repos con `REPO_FILTER`

### 🔴 Rojo
- **Token con permisos excesivos:** Usar solo read-only
  - Mitigación: Fine-grained PAT con `Contents: Read` únicamente
  - Rotar token si se expone

---

## Mini-Scorecard

| Aspecto | Score | Notas |
|---------|-------|-------|
| Operatividad diaria | 9/10 | Funciona out-of-the-box |
| Seguridad (no secretos) | 10/10 | Solo keys, nunca valores |
| Cobertura repos/branches | 8/10 | Sube con tuning de filtros |
| Research real (extractores) | 3/10 | Stub; listo para enchufar extractores reales |

---

## Próximos Pasos

1. **Conectar extractores reales:**
   - MLU (MercadoLibre Uruguay)
   - Retailers locales
   - Google Trends API
   - Agregar evidencia `url` y `fecha` verificables

2. **Mejorar scoring:**
   - Ajustar pesos en `config/weights.yml`
   - Agregar más factores (estacionalidad, competencia, etc.)

3. **Optimizar performance:**
   - Cache de resultados de escaneo
   - Escaneo incremental (solo cambios desde último run)
   - Paralelización de escaneos

4. **Notificaciones:**
   - Slack/Discord webhooks para issues importantes
   - Email alerts para cambios críticos en .env

---

## Archivos del Blueprint

### `.gitignore`
Ignora archivos sensibles y outputs temporales.

### `config/weights.yml`
Pesos para scoring de oportunidades:
- `demanda`: 0.35
- `margen_potencial`: 0.25
- `fit_bmc`: 0.15
- `facilidad_logistica`: 0.15
- `ventaja_competitiva`: 0.10

### `scripts/scan_env_all_repos.py`
Escanea todos los repos y branches buscando archivos `.env`, extrae solo las **keys** (nunca valores).

**Outputs:**
- `out/env_inventory.json` - Inventario completo por repo/branch
- `out/env_keys_unified.json` - Lista unificada de todas las keys
- `env/.env.unified.example` - Template con placeholders `KEY=__REQUIRED__`

### `scripts/research_opportunities.py`
Stub de investigación de oportunidades eCommerce con scoring.

**Outputs:**
- `out/opportunities_YYYY-MM-DD.json` - Datos estructurados
- `out/opportunities_YYYY-MM-DD.md` - Reporte markdown

### `scripts/build_issue_body.py`
Construye el body del issue diario combinando outputs de research y env scan.

**Output:**
- `out/ISSUE_BODY.md` - Body del issue

### `.github/workflows/cloud-agent-daily.yml`
Workflow de GitHub Actions que ejecuta todo el pipeline diariamente.

**Triggers:**
- Schedule: `15 11 * * *` (11:15 UTC diario)
- Manual: `workflow_dispatch`

**Steps:**
1. Checkout repo
2. Setup Python 3.11
3. Install deps (requests, PyYAML)
4. Research opportunities
5. Scan env (all repos + branches)
6. Build issue body
7. Upload artifacts
8. Create/update daily issue
9. Commit unified env template (si hay cambios)

---

## Seguridad

### ✅ Buenas Prácticas Implementadas

1. **Keys-only:** Nunca se leen/imprimen valores de secretos
2. **Read-only token:** Solo permisos de lectura
3. **Artifacts:** Outputs seguros sin valores sensibles
4. **Git ignore:** `.env*` ignorados en git

### ⚠️ Consideraciones

- El token `GH_SCAN_TOKEN` necesita acceso a todos los repos a escanear
- Si el repo es privado, el token debe tener permisos adecuados
- Rotar token periódicamente (cada 90 días recomendado)

---

## Troubleshooting

### Error: "Missing GH_SCAN_TOKEN or GH_OWNER"
- Verificar que los secrets estén configurados en GitHub Settings → Secrets

### Error: "Rate limit exceeded"
- Reducir `BRANCH_LIMIT` o usar `BRANCH_ALLOW_REGEX` más restrictivo
- Agregar delay entre requests (modificar `scan_env_all_repos.py`)

### Error: "Repository not found"
- Verificar que el token tenga acceso al repo
- Verificar que `GH_OWNER` sea correcto

### Workflow timeout (> 6 horas)
- Filtrar repos con `REPO_FILTER`
- Reducir `BRANCH_LIMIT`
- Usar `BRANCH_ALLOW_REGEX` más restrictivo

---

## Export Seal

Todos los archivos incluyen metadata EXPORT_SEAL v1 con:
- project: bmc-uy
- prompt_id: cloud-agent-pack
- version: 1.0.0
- author: Matias Portugau
- origin: github-cloud-agent-blueprint

---

**Creado:** 2025-12-14  
**Versión:** 1.0.0  
**Autor:** Matias Portugau
