#!/usr/bin/env python3
"""
Backfill Embeddings
------------------
Iterates over 'kb_interactions' collection in MongoDB and generates embeddings
for documents that are missing them.
"""

import os
import sys
import time
from pymongo import MongoClient
try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI module not found. Please install it.")
    sys.exit(1)

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def backfill_embeddings():
    uri = os.getenv("MONGODB_URI")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not uri:
        print("❌ MONGODB_URI not found.")
        return
    if not openai_key:
        print("❌ OPENAI_API_KEY not found.")
        return

    try:
        # Connect
        client = MongoClient(uri)
        db = client.get_database()
        col = db["kb_interactions"]
        
        # Init OpenAI
        openai = OpenAI(api_key=openai_key)
        
        # Find docs without embedding
        # or where embedding is empty list
        query = {
            "$or": [
                {"embedding": {"$exists": False}},
                {"embedding": []},
                {"embedding": None}
            ]
        }
        
        docs_to_update = list(col.find(query))
        total = len(docs_to_update)
        print(f"📦 Found {total} documents needing embeddings.")
        
        processed = 0
        for doc in docs_to_update:
            text_to_embed = doc.get("mensaje_cliente")
            if not text_to_embed:
                continue
                
            try:
                # Normalize text
                text_to_embed = text_to_embed.replace("\n", " ")
                
                # Generate
                embedding = openai.embeddings.create(
                    input=[text_to_embed],
                    model="text-embedding-3-small"
                ).data[0].embedding
                
                # Update
                col.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"embedding": embedding}}
                )
                processed += 1
                if processed % 10 == 0:
                    print(f"   ⏳ Processed {processed}/{total}...")
                    
                # Rate limit (gentle)
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️ Error embedding doc {doc.get('id')}: {e}")
                
        print(f"✅ Backfill complete. Updated {processed} documents.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    backfill_embeddings()
