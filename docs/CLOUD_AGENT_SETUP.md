# GitHub Cloud Agent Blueprint - Guía de Activación

## Estructura Creada

```
/config/weights.yml                    # Pesos para scoring de oportunidades
/env/.gitkeep                          # Mantiene directorio en git
/env/.env.unified.example              # (generado) Template unificado de keys
/scripts/cloud-agent/
  ├── scan_env_all_repos.py           # Escanea .env en todos los repos/branches
  ├── research_opportunities.py        # Research stub de oportunidades eCommerce
  └── build_issue_body.py              # Construye body del issue diario
/.github/workflows/cloud-agent-daily.yml  # Workflow diario
```

## Configuración Inicial (1 vez)

### A) Secrets en GitHub

En el repositorio donde está este workflow, ve a:
**Settings → Secrets and variables → Actions**

Agregar los siguientes secrets:

1. **GH_OWNER**: Tu usuario u organización de GitHub
   - Ejemplo: `Matiasportugau` o `tu-org`

2. **GH_SCAN_TOKEN**: Token de GitHub con permisos read-only
   - Debe tener acceso a **Contents: Read** en todos los repos a escanear
   - Puede ser un Fine-grained PAT o GitHub App token
   - ⚠️ **IMPORTANTE**: Solo permisos de lectura, nunca write/admin

### B) Ajustes Opcionales

Edita `.github/workflows/cloud-agent-daily.yml` si necesitas cambiar:

- **Horario**: `cron: "15 11 * * *"` (11:15 UTC diario)
- **FOCUS**: Línea `FOCUS: "aislamiento, impermeabilización..."` 
- **BRANCH_LIMIT**: `"50"` (0 = sin límite, puede ser lento)
- **BRANCH_ALLOW_REGEX**: Regex para filtrar branches permitidas

### C) Primera Ejecución

1. Commit y push de todos los archivos creados
2. Ve a **Actions** en GitHub
3. Selecciona el workflow `cloud-agent-daily`
4. Click en **Run workflow** → **Run workflow**

## Validación Post-Ejecución

Después de la primera ejecución, verifica:

✅ **Artifacts**: 
   - Descarga `cloud-agent-output` 
   - Debe contener: `out/*.json`, `out/*.md`, `env/.env.unified.example`

✅ **Issue**: 
   - Busca issue con título: `Cloud Agent Daily - YYYY-MM-DD`
   - Debe tener secciones: Oportunidades, Unificación .env, Riesgos, Próximos pasos

✅ **Commit** (si hubo cambios):
   - Debe haber un commit: `chore(env): update unified env template (keys-only)`
   - Archivo: `env/.env.unified.example`

## Ajustes de Performance

Si el workflow tarda mucho o pega rate limits:

1. **Reducir branches**: Cambiar `BRANCH_LIMIT` de `"50"` a `"20"` o menos
2. **Filtrar branches**: Ajustar `BRANCH_ALLOW_REGEX` para solo branches importantes
3. **Filtrar repos**: Agregar `REPO_FILTER` en el workflow para escanear solo repos específicos

Ejemplo de filtro de repos:
```yaml
REPO_FILTER: "mi-proyecto"  # Solo repos que contengan "mi-proyecto" en el nombre
```

## Seguridad (Semáforo)

🟢 **Verde**: 
- Solo lee **keys** de .env, nunca valores
- Artifacts son públicos pero no contienen secretos
- Token read-only

🟡 **Amarillo**: 
- Escanear todos los repos/branches puede ser lento
- Puede pegar rate limits de GitHub API
- Mitigar con límites y filtros

🔴 **Rojo**: 
- Token con permisos excesivos (usar solo read-only)
- Si el token se expone, rotarlo inmediatamente

## Próximos Pasos

1. **Conectar extractores reales**: 
   - Editar `scripts/cloud-agent/research_opportunities.py`
   - Reemplazar `generate_candidates_stub()` con llamadas a APIs reales (MLU, retailers, trends)

2. **Agregar evidencia verificable**:
   - URLs de productos
   - Fechas de investigación
   - Métricas reales (volúmenes, CPC, ROI)

3. **Mejorar scoring**:
   - Ajustar pesos en `config/weights.yml`
   - Agregar más criterios si es necesario

## Troubleshooting

### Error: "Missing GH_SCAN_TOKEN or GH_OWNER"
- Verifica que los secrets estén configurados correctamente
- Nombres exactos: `GH_SCAN_TOKEN` y `GH_OWNER`

### Error: "Rate limit exceeded"
- Reduce `BRANCH_LIMIT` o agrega más filtros
- Considera usar GitHub App en lugar de PAT para mejor rate limit

### No se crean issues
- Verifica permisos del workflow: `issues: write`
- Verifica que `gh` CLI esté disponible (viene con GitHub Actions)

### No se actualiza `.env.unified.example`
- Normal si no hay cambios en las keys detectadas
- Verifica logs del step "Commit updated unified env template"

## Scorecard

- ✅ Operatividad diaria: 9/10
- ✅ Seguridad (no secretos): 10/10  
- ✅ Cobertura repos/branches: 8/10 (mejora con tuning)
- ⚠️ Research real (extractores): 3/10 (stub; listo para enchufar)
