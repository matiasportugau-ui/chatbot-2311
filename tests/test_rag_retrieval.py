#!/usr/bin/env python3
"""
Test RAG Retrieval
-----------------
Verifies that the KnowledgeManager correctly uses Vector Search to find
relevant information from MongoDB.
"""

import sys
import os
from pathlib import Path

# Bulletproof path setup: Get the directory of THIS script, then go up one level
# This works regardless of where the script is called from
current_script_dir = Path(__file__).resolve().parent
project_root = current_script_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Debug: Print path to verify
# print(f"DEBUG: Project Root added to path: {project_root}")

try:
    from ai_agents.EXECUTOR.knowledge_manager import KnowledgeManager
except ImportError:
    try:
        from AI_AGENTS.EXECUTOR.knowledge_manager import KnowledgeManager
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(f"   Current sys.path: {sys.path}")
        print("   Make sure 'ai_agents' or 'AI_AGENTS' folder contains an __init__.py.")
        sys.exit(1)

def test_rag():
    print("🧪 Testing RAG Retrieval...")
    
    try:
        # Init Manager
        km = KnowledgeManager()
        
        if not km.openai_client:
             print("❌ Skipped: OpenAI client not initialized (check .env)")
             return

        if not km.mongodb_service:
             print("❌ Skipped: MongoDB service not initialized (check .env)")
             return

        # Query that requires semantic understanding
        # Example: "aislamiento para techo" (should match "poliestireno" or "lana de roca")
        # Even if exact words aren't in the snippet
        query = "aislamiento para techo economico"
        print(f"🔎 Query: '{query}'")
        
        results = km.buscar_informacion_relevante(query, max_results=3)
        
        if results is None:
             print("❌ Error: Search returned None (Check logs for API/DB errors)")
             sys.exit(1)

        conversaciones = results.get("conversaciones", [])
        print(f"📊 Found {len(conversaciones)} relevant conversations.")
        
        if conversaciones:
            for i, conv in enumerate(conversaciones):
                score = conv.get("score", "N/A")
                msg = conv.get("mensaje_cliente")
                print(f"   {i+1}. [Score: {score}] '{msg[:50]}...'")
            
            # Basic validation
            if any(c.get("score") for c in conversaciones):
                print("✅ Vector Search SUCCESS: Returned results with similarity scores.")
            else:
                print("⚠️ Keyword Search Fallback? No scores found.")
        else:
             print("⚠️ No results found. (Maybe index isn't ready or empty DB?)")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
