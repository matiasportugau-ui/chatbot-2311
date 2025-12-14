# GitHub Cloud Agent Blueprint - Guía de Configuración

## 📋 Resumen

Este sistema automatiza diariamente:
- **Research de oportunidades eCommerce** (Uruguay) - stub operativo listo para conectar extractores reales
- **Scan de .env** (keys-only) en todos los repos y branches
- **Publicación de artifacts** + issue diario
- **Commit automático** del template unificado de env (keys-only)

## 🚀 Configuración Inicial (Una vez)

### 1. Secrets en GitHub

En el repositorio `Matiasportugau-ui` (o tu repo controlador), ve a:
**Settings → Secrets and variables → Actions**

Agrega estos secrets:

- **`GH_OWNER`**: Tu usuario u organización de GitHub (ej: `tuUsuarioOrOrg`)
- **`GH_SCAN_TOKEN`**: Token de GitHub con permisos read-only
  - Puede ser un Fine-grained PAT con `Contents: Read` en todos los repos a escanear
  - O un GitHub App token con permisos mínimos

### 2. Estructura de Archivos

Los siguientes archivos ya están creados:

```
/config/weights.yml                    # Pesos para scoring de oportunidades
/env/.gitkeep                          # Mantiene el directorio en git
/env/.env.unified.example              # Se genera automáticamente (keys-only)
/scripts/scan_env_all_repos.py         # Escanea repos y branches
/scripts/research_opportunities.py     # Research stub de oportunidades
/scripts/build_issue_body.py           # Construye el cuerpo del issue
/.github/workflows/cloud-agent-daily.yml  # Workflow diario
```

### 3. Ejecución Manual (Primera vez)

1. Ve a **Actions** en GitHub
2. Selecciona el workflow **"cloud-agent-daily"**
3. Click en **"Run workflow"**
4. Selecciona la branch (normalmente `main` o `master`)
5. Click en **"Run workflow"**

### 4. Validar Outputs

Después de la primera ejecución, verifica:

- ✅ **Artifacts**: `cloud-agent-output` (contiene `out/*` + `env/.env.unified.example`)
- ✅ **Issue**: "Cloud Agent Daily - YYYY-MM-DD" (se crea/actualiza automáticamente)
- ✅ **Archivo actualizado**: `env/.env.unified.example` (si hay cambios, se commitea automáticamente)

## ⚙️ Configuración Avanzada

### Variables de Entorno en el Workflow

Puedes ajustar estos valores en `.github/workflows/cloud-agent-daily.yml`:

- **`FOCUS`**: Categorías de productos (default: `"aislamiento, impermeabilización, construcción, techos, selladores"`)
- **`BRANCH_LIMIT`**: Límite de branches a escanear (default: `50`, `0` = sin límite)
- **`BRANCH_ALLOW_REGEX`**: Regex para filtrar branches (default: `"^(main|master|develop|dev|staging|production|release/|hotfix/)"`)
- **`REPO_FILTER`**: Filtro opcional para nombres de repos (default: `""` = todos)
- **`SCHEDULE_CRON_UTC`**: Horario de ejecución diaria (default: `"15 11 * * *"` = 11:15 UTC diario)

### Ajuste de Performance

Si el workflow tarda mucho o pega rate limits:

1. **Reducir branches**: Ajusta `BRANCH_LIMIT` a un número menor (ej: `20`)
2. **Filtrar branches**: Usa `BRANCH_ALLOW_REGEX` más restrictivo
3. **Filtrar repos**: Usa `REPO_FILTER` para escanear solo repos específicos

## 🔒 Seguridad

### ✅ Verde (Seguro)
- Solo se escanean **keys** de variables de entorno (nunca valores)
- Los artifacts se almacenan de forma segura
- El token debe tener permisos mínimos (read-only)

### ⚠️ Amarillo (Precaución)
- Escanear todos los repos + todas las branches puede:
  - Pegar rate limits de GitHub API
  - Tomar mucho tiempo (timeout)
  - Mitigar con `BRANCH_LIMIT` y `BRANCH_ALLOW_REGEX`

### 🔴 Rojo (Riesgo)
- Token con permisos excesivos → usar read-only siempre
- Si el token se expone → rotarlo inmediatamente

## 📊 Próximos Pasos

### Conectar Extractores Reales

El sistema actual usa un **stub** para research de oportunidades. Para producción:

1. **MercadoLibre Uruguay (MLU)**: Conectar API para extraer productos/trends
2. **Retailers locales**: Integrar con APIs de tiendas uruguayas
3. **Google Trends**: Agregar datos de búsquedas
4. **Evidencia verificable**: Agregar `url` y `fecha` reales en lugar de `null`

### Mejoras Futuras

- [ ] Agregar costos de proveedor para calcular ROI/margen real
- [ ] Dashboard de visualización de oportunidades
- [ ] Alertas cuando se detecten nuevas keys en .env
- [ ] Integración con sistema de gestión de productos

## 📝 Notas Técnicas

- **Python 3.11+** requerido
- Dependencias: `requests`, `PyYAML`
- Los scripts son ejecutables (`chmod +x`)
- El workflow usa `gh` CLI para crear/actualizar issues
- Los commits automáticos usan usuario `cloud-agent@users.noreply.github.com`

## 🐛 Troubleshooting

### El workflow falla con "Missing GH_SCAN_TOKEN"
→ Verifica que el secret esté configurado correctamente en GitHub

### Timeout en scan de repos
→ Reduce `BRANCH_LIMIT` o ajusta `BRANCH_ALLOW_REGEX` para filtrar branches

### Rate limit de GitHub API
→ El workflow espera automáticamente, pero puedes reducir el scope con `REPO_FILTER`

### No se crea el issue
→ Verifica que el workflow tenga permisos `issues: write` (ya está configurado)

---

**Versión**: 1.0.0  
**Autor**: Matias Portugau  
**Fecha**: 2025-12-14
