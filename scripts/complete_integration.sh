#!/bin/bash
# Complete DB & KB Integration Runner

echo "🚀 Starting Database & Knowledge Base Integration..."

# 1. Check requirements
echo "\n📦 Installing dependencies..."
pip install -r requirements.txt
pip install openai pymongo python-dotenv

# 2. Setup Atlas Index
echo "\n=== 1. Setting up Atlas Vector Search Index ==="
python3 scripts/setup_atlas_vector_search.py

# 3. Backfill Embeddings
echo "\n=== 2. Backfilling Embeddings for existing data ==="
python3 scripts/backfill_embeddings.py

# 4. Verify
echo "\n=== 3. Verifying RAG Retrieval ==="
python3 tests/test_rag_retrieval.py

echo "\n✨ Integration Process Finished. Check output for any errors."
