#!/bin/bash
set -e

echo "🚀 Starting Cloud Training / Ingestion Pipeline..."

# 1. Ingest General Knowledge (Products, etc.)
echo "📚 Ingesting Knowledge Base..."
python3 scripts/ingest_knowledge.py

# 2. Ingest Dropbox Quotes
# This requires DROPBOX_API_KEY
echo "📦 Downloading and Ingesting Dropbox Quotes..."
python3 scripts/ingest_dropbox_quotes.py

# 3. Sync & Match Quotes to Google Sheets
# This requires GOOGLE_SHEETS_CREDENTIALS (json) and Sheet access
# We use --live to actually update the sheet
echo "📊 Syncing Quotes to Google Sheets..."
# Check if credentials file exists, if not try to create it from env var
if [ ! -f "credentials.json" ] && [ -n "$GOOGLE_SHEETS_CREDENTIALS" ]; then
    echo "🔑 creating credentials.json from environment variable..."
    echo "$GOOGLE_SHEETS_CREDENTIALS" > credentials.json
fi

# Run the matcher
python3 scripts/match_quotes.py --live

echo "✅ Training Pipeline Complete!"
