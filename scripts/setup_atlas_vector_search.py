#!/usr/bin/env python3
"""
Setup MongoDB Atlas Vector Search
--------------------------------
This script creates the necessary Vector Search Indices on MongoDB Atlas.
It requires `pymongo` and a valid `MONGODB_URI` in .env pointing to an Atlas Cluster.
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Try to load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def setup_vector_search():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("❌ Error: MONGODB_URI not found in environment variables.")
        return False
    
    if "mongodb+srv" not in uri:
        print("⚠️ Warning: URI does not look like an Atlas SRV string. Vector Search requires Atlas.")
        print("❌ Aborting Atlas setup to prevent hang on local MongoDB.")
        return False

    try:
        client = MongoClient(uri)
        db = client.get_database()
        print(f"✅ Connected to MongoDB: {db.name}")
        
        # 1. Index for Interactions (Chat History / RAG)
        # We will index the 'embedding' field
        index_name = "vector_index"
        collection_name = "kb_interactions"
        
        print(f"📦 Setting up index for {collection_name}...")
        
        # Define the index model for Atlas Vector Search
        # Note: This uses the 'vectorSearch' type which is specific to Atlas
        search_index_model = {
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1536,  # OpenAI text-embedding-3-small
                        "similarity": "cosine"
                    },
                    {
                        "type": "filter",
                        "path": "tipo_interaccion" # Allow filtering by type
                    }
                ]
            },
            "name": index_name,
            "type": "vectorSearch"
        }
        
        collection = db[collection_name]
        
        # Check if index exists (this checks standard indexes, search indexes are different)
        # PyMongo 4.7+ supports list_search_indexes() and create_search_index()
        
        try:
            # Attempt to create the search index
            # Note: This might fail if the driver is old or not Atlas
            result = collection.create_search_index(model=search_index_model)
            print(f"   ✨ Index creation initiated: {result}")
            print("   ⏳ Note: Index creation on Atlas takes a minute. You may see errors until it is ready.")
            
        except AttributeError:
             print("   ❌ Error: Your PyMongo version might be too old to create Search Indexes programmatically.")
             print("   Action: Please run 'pip install -U pymongo'")
        except OperationFailure as e:
            if "already exists" in str(e) or "Duplicate" in str(e):
                print(f"   ℹ️ Index '{index_name}' likely already exists.")
            else:
                print(f"   ❌ Atlas Error: {e}")
                print("   👉 You may need to create this index manually in Atlas UI > Search > Vector Search.")

        # 2. Index for Products (if we decide to embed them too)
        # For now, interactions are the most critical for dynamic RAG
        
        print("\n✅ Setup attempt finished.")
        return True

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

if __name__ == "__main__":
    setup_vector_search()
