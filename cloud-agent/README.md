# ☁️ Cloud Agent Blueprint

Automated daily workflow for eCommerce research and environment variable management.

## Features

- **📊 Research Opportunities**: Stub-based scoring system ready for real extractors
- **🔑 Env Scanner**: Multi-repo, multi-branch .env file analysis (keys-only, NO secrets)
- **📋 Daily Reports**: Auto-generated GitHub issues with opportunities and env inventory
- **🔄 Unified Templates**: Auto-generated `.env.unified.example` across all repos

## Structure

```
cloud-agent/
├── README.md                     # This file
├── scan_env_all_repos.py         # Multi-repo env scanner
├── research_opportunities.py     # Opportunity research + scoring
└── build_issue_body.py           # Daily issue body builder

config/
└── weights.yml                   # Scoring weights configuration

env/
├── .gitkeep                      # Keep directory in git
└── .env.unified.example          # Auto-generated unified template

.github/workflows/
└── cloud-agent-daily.yml         # Daily workflow (schedule + manual)
```

## Setup

### 1. Configure GitHub Secrets

Go to **Settings > Secrets and variables > Actions** and add:

| Secret | Description |
|--------|-------------|
| `GH_OWNER` | Your GitHub username or organization |
| `GH_SCAN_TOKEN` | Fine-grained PAT with `Contents: Read` permission on target repos |

### 2. Token Requirements

Create a **Fine-grained Personal Access Token** with:
- **Repository access**: All repositories (or select specific ones)
- **Permissions**: `Contents: Read` (read-only)

⚠️ **NEVER use tokens with write access** - this agent only needs to read .env file structures.

### 3. Run the Workflow

#### Manual Run
1. Go to **Actions** tab
2. Select **cloud-agent-daily**
3. Click **Run workflow**
4. Optionally configure:
   - `repo_filter`: Filter repos by name
   - `branch_limit`: Max branches per repo (default: 50)

#### Scheduled Run
- Default: Daily at 11:15 UTC (08:15 Uruguay time)
- Modify cron in `.github/workflows/cloud-agent-daily.yml`

## Outputs

### Artifacts (30 days retention)
- `out/opportunities_YYYY-MM-DD.json` - Opportunity data
- `out/opportunities_YYYY-MM-DD.md` - Markdown report
- `out/env_inventory.json` - Full env file inventory
- `out/env_keys_unified.json` - Unified key list
- `env/.env.unified.example` - Template with all keys

### GitHub Issue
- Title: `☁️ Cloud Agent Daily - YYYY-MM-DD`
- Labels: `cloud-agent`, `daily-report`
- Content: Opportunities + env summary + next steps

## Scoring System

Opportunities are scored using weighted factors (see `config/weights.yml`):

| Factor | Weight | Description |
|--------|--------|-------------|
| `demanda` | 35% | Market demand level |
| `margen_potencial` | 25% | Profit margin potential |
| `fit_bmc` | 15% | Fit with BMC product line |
| `facilidad_logistica` | 15% | Logistics feasibility |
| `ventaja_competitiva` | 10% | Competitive advantage |

## Security

### ✅ Safe by Design
- **Keys-only**: Never reads or stores secret VALUES
- **Read-only**: Uses read-only GitHub token
- **No persistence**: Temp directories cleaned up
- **Artifact-based**: No secrets in commits

### 🚦 Risk Semaphore
| Status | Description |
|--------|-------------|
| 🟢 Green | Keys-only scan, artifacts generated |
| 🟡 Yellow | All repos + branches may hit rate limits |
| 🔴 Red | Token has excessive permissions |

## Extending

### Connect Real Extractors

Replace the stub in `research_opportunities.py`:

```python
def generate_candidates_stub(focus: str) -> list:
    # TODO: Connect to real extractors
    # - MercadoLibre API
    # - Retailer scrapers  
    # - Google Trends API
    
    # Return candidates with real evidence:
    return [
        {
            "producto": "...",
            "evidencia": {
                "url": "https://...",  # Real source
                "fecha": "2025-01-01",  # Real date
                "nota": "From MLU API"
            },
            ...
        }
    ]
```

### Adjust Performance

For large organizations:

```yaml
# In workflow or environment
BRANCH_LIMIT: "10"  # Reduce branches per repo
BRANCH_ALLOW_REGEX: "^(main|master)$"  # Only main branches
REPO_FILTER: "chatbot"  # Filter by name
```

## Local Testing

```bash
# Set environment variables
export GH_OWNER="your-username"
export GH_SCAN_TOKEN="ghp_..."
export MARKET="Uruguay"
export FOCUS="aislamiento, impermeabilización"
export BRANCH_LIMIT="10"

# Run scripts
python cloud-agent/research_opportunities.py
python cloud-agent/scan_env_all_repos.py
python cloud-agent/build_issue_body.py
```

## License

MIT - Part of the BMC-UY project.

---

*EXPORT_SEAL v1 | project: bmc-uy | version: 1.0.0*
