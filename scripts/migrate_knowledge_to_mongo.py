#!/usr/bin/env python3
"""
Migrate Knowledge Base from JSON to MongoDB
Part of the Database Unification Strategy
"""

import json
import os
import sys
from pathlib import Path
from pymongo import MongoClient

# Add parent directory to path to allow imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_to_mongo(json_file_path, mongo_uri="mongodb://localhost:27017/bmc_chat"):
    """
    Reads a JSON knowledge base file and pushes it to MongoDB.
    """
    print(f"🚀 Starting migration from {json_file_path} to MongoDB...")
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return False

    try:
        # 1. Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client.get_database() # Uses database from URI
        print(f"✅ Connected to MongoDB: {db.name}")

        # 2. Load JSON Data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("✅ JSON Data loaded into memory")

        # 3. Migrate Collections
        
        # Interactions
        if "interacciones" in data and data["interacciones"]:
            col = db["kb_interactions"]
            count = len(data["interacciones"])
            print(f"📦 Migrating {count} interactions...")
            # Use upsert based on ID to avoid duplicates
            ops = 0
            for item in data["interacciones"]:
                if "id" in item:
                    col.replace_one({"id": item["id"]}, item, upsert=True)
                    ops += 1
            print(f"   ✨ Upserted {ops} interactions")

        # Sales Patterns
        if "patrones_venta" in data and data["patrones_venta"]:
            col = db["kb_patterns"]
            count = len(data["patrones_venta"])
            print(f"📦 Migrating {count} sales patterns...")
            ops = 0
            for item in data["patrones_venta"]:
                if "id" in item:
                    col.replace_one({"id": item["id"]}, item, upsert=True)
                    ops += 1
            print(f"   ✨ Upserted {ops} patterns")

        # Product Knowledge
        # In JSON this is a dict {id: data}, in Mongo better as documents
        if "conocimiento_productos" in data and data["conocimiento_productos"]:
            col = db["kb_products"]
            products = data["conocimiento_productos"]
            print(f"📦 Migrating {len(products)} products...")
            ops = 0
            for prod_id, prod_data in products.items():
                if "producto_id" not in prod_data:
                    prod_data["producto_id"] = prod_id
                col.replace_one({"producto_id": prod_id}, prod_data, upsert=True)
                ops += 1
            print(f"   ✨ Upserted {ops} products")
            
        # Metrics & Insights
        if "metricas_evolucion" in data:
            col = db["kb_metrics"]
            # Just save as a single document with a timestamp or ID
            metrics = data["metricas_evolucion"]
            metrics["type"] = "evolution_metrics"
            col.replace_one({"type": "evolution_metrics"}, metrics, upsert=True)
            print("   ✨ Updated evolution metrics")

        print("\n🎉 Migration completed successfully!")
        client.close()
        return True

    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Allow passing file path as argument
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # Default to the reliable final file if argument not provided
        target_file = "base_conocimiento_final.json"
        # Fallback to consolidated if final doesn't exist
        if not os.path.exists(target_file) and not os.path.exists(f"../{target_file}"):
             target_file = "conocimiento_consolidado.json"

    # Check if file exists in current dir or parent
    if os.path.exists(target_file):
        path = target_file
    elif os.path.exists(f"../{target_file}"):
        path = f"../{target_file}"
    else:
        # Fallback to absolute path assumption
        path = f"/Users/matias/chatbot2511/chatbot-2311/{target_file}"

    migrate_to_mongo(path)
