# GitHub Cloud Agent Blueprint - Setup Guide

## Overview

This Cloud Agent system runs daily to:
1. **Research eCommerce opportunities** (Uruguay market) - stub implementation ready for real extractors
2. **Scan all repos + all branches** for `.env` files (keys-only, no values)
3. **Publish artifacts** + daily issue + unified env template

## Files Created

```
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

## Activation Steps

### A) Repository Setup (Already Done)
✅ Directory structure created
✅ All files created with placeholders replaced:
   - `FOCUS`: "aislamiento, impermeabilización, construcción, techos, selladores"
   - `BRANCH_ALLOW_REGEX`: "^(main|master|develop|dev|staging|production|release/|hotfix/)"
   - `BRANCH_LIMIT`: "50"
   - `SCHEDULE_CRON_UTC`: "15 11 * * *" (runs daily at 11:15 UTC)

### B) GitHub Secrets Configuration

**Required:** Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

1. **GH_OWNER**
   - Value: Your GitHub username or organization name
   - Example: `Matiasportugau-ui` or `tuUsuarioOrOrg`

2. **GH_SCAN_TOKEN**
   - Value: GitHub Personal Access Token (PAT) or Fine-grained PAT
   - Permissions needed: `Contents: Read` (read-only access to repos you want to scan)
   - **Security:** Use read-only token, rotate if exposed

### C) Manual Test Run

1. Go to Actions tab in GitHub
2. Select "cloud-agent-daily" workflow
3. Click "Run workflow" → "Run workflow"

### D) Validate Outputs

After first run, check:

- ✅ **Artifacts**: `cloud-agent-output` (contains `out/*` + `env/.env.unified.example`)
- ✅ **Issue**: "Cloud Agent Daily - YYYY-MM-DD" (created/updated)
- ✅ **File**: `env/.env.unified.example` (committed if changed)

## Configuration

### Adjust Performance

If the workflow is slow or hits rate limits:

1. **Limit branches**: Set `BRANCH_LIMIT` to a lower number (e.g., "20")
2. **Filter branches**: Adjust `BRANCH_ALLOW_REGEX` to exclude feature branches
3. **Filter repos**: Set `REPO_FILTER` environment variable in workflow

### Customize Focus

Edit `.github/workflows/cloud-agent-daily.yml`:
```yaml
FOCUS: "your, custom, focus, keywords"
```

### Schedule

Edit cron in `.github/workflows/cloud-agent-daily.yml`:
```yaml
- cron: "15 11 * * *"  # UTC time: hour minute day month weekday
```

## Security Notes

🟢 **Green (Safe)**:
- Keys-only scanning (no secret values)
- Artifacts stored securely
- Read-only token recommended

🟡 **Yellow (Monitor)**:
- Scanning all repos + branches may hit rate limits
- Long execution times possible
- Mitigate with `BRANCH_LIMIT` and `BRANCH_ALLOW_REGEX`

🔴 **Red (Avoid)**:
- Token with excessive permissions
- Writing secret values anywhere
- Exposing tokens in logs

## Next Steps

1. **Connect Real Extractors**: Replace stub in `research_opportunities.py` with:
   - MercadoLibre Uruguay API
   - Retailer APIs
   - Trend analysis tools

2. **Add Provider Costs**: Integrate supplier cost data for real ROI/margin calculations

3. **Enhance Scoring**: Adjust weights in `config/weights.yml` based on business priorities

## Troubleshooting

### Workflow Fails

- Check GitHub Actions logs
- Verify secrets are set correctly
- Ensure token has required permissions
- Check rate limits (may need to reduce `BRANCH_LIMIT`)

### No Repos Found

- Verify `GH_OWNER` secret matches your username/org
- Check token permissions
- Review `REPO_FILTER` setting

### Issue Not Created

- Verify workflow has `issues: write` permission
- Check GitHub Actions logs for errors
- Ensure `gh` CLI is available (included in GitHub Actions)

## Scorecard

- **Operatividad diaria**: 9/10
- **Seguridad (no secretos)**: 10/10
- **Cobertura repos/branches**: 8/10 (improves with tuning)
- **Research real (extractores)**: 3/10 (stub; ready for real extractors)
