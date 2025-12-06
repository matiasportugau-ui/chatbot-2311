# Data Ingestion Workflow

This document explains how to keep the chatbot knowledge base synchronized with
live product data (Shopify) and customer interactions (Mercado Libre) using
lightweight scripts with minimal dependencies.

## Prerequisites

- Python 3.11 (already required by the project).
- `requests`, `beautifulsoup4`, `lxml` (installed through `requirements.txt`).
- `.venv` created via `bash scripts/setup_chatbot_env.sh`.

Optional environment variables (can be stored in `.env`):

```
SHOPIFY_PAGE_SIZE=250
MELI_ACCESS_TOKEN=<<token>>
MELI_SELLER_ID=<<seller>>
RUN_SHOPIFY_SYNC=true
RUN_MELI_SYNC=true
```

> If `MELI_ACCESS_TOKEN` or `MELI_SELLER_ID` are missing, the Mercado Libre step
> will be skipped automatically.

## Shopify Catalog Sync

Command:

```bash
source .venv/bin/activate
python python-scripts/fetch_shopify_products.py
```

Results:

- `data/shopify/shopify_products_raw.json` (raw storefront feed).
- `conocimiento_shopify.json` (normalized product knowledge).

## Mercado Libre Questions Sync

Command (requires valid token & seller ID):

```bash
source .venv/bin/activate
python python-scripts/fetch_mercadolibre_questions.py
```

CSV fallback (no API token required):

```bash
source .venv/bin/activate
python python-scripts/fetch_mercadolibre_questions.py --csv-export data/mercadolibre/export.csv
```

Results:

- `data/mercadolibre/mercadolibre_questions_raw.json` (raw API payload).
- `conocimiento_mercadolibre.json` (normalized interactions).

## Automated Refresh

`bash scripts/refresh_knowledge.sh` now:

1. Activates the virtualenv.
2. Runs Shopify & Mercado Libre ingestions (opt-in via env vars).
3. Consolidates all knowledge JSON files.
4. Executes validation (`validar_integracion.py`).
5. Stores logs under `logs/automation/ingestion_*.log`.

To disable an ingestion temporarily:

```bash
RUN_SHOPIFY_SYNC=false RUN_MELI_SYNC=false bash scripts/refresh_knowledge.sh
```

## Files Produced

| File | Description |
| --- | --- |
| `data/shopify/shopify_products_raw.json` | Raw Shopify products feed |
| `conocimiento_shopify.json` | Shopify catalog in bot schema |
| `data/mercadolibre/mercadolibre_questions_raw.json` | Raw Mercado Libre Q&A |
| `conocimiento_mercadolibre.json` | Mercado Libre interactions in bot schema |
| `conocimiento_consolidado.json` | Final merged knowledge source |
| `reporte_validacion.json/.txt` | Result of integration validation |

Keep these artifacts for auditability and to reproduce chatbot responses.

