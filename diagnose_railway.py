#!/usr/bin/env python3
"""
Diagnostic script for Railway deployment
Prints environment info and attempts MongoDB connection
"""
import os
import sys
import json
from datetime import datetime

print("="*50)
print(f"DIAGNOSTIC START: {datetime.now().isoformat()}")
print("="*50)

# 1. System Info
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Files in CWD: {os.listdir('.')}")

# 2. Environment Variables (safely)
print("\n[ENVIRONMENT VARIABLES]")
relevant_keys = [
    "MONGODB_URI", 
    "MONGO_URL", 
    "PORT", 
    "HOST", 
    "RAILWAY_ENVIRONMENT",
    "RAILWAY_PROJECT_NAME",
    "OPENAI_API_KEY",
    "RAILWAY_GIT_COMMIT_SHA"
]

for key in relevant_keys:
    val = os.getenv(key)
    if val:
        # Mask secrets
        if "KEY" in key or "URI" in key or "URL" in key:
            if len(val) > 20:
                masked = f"{val[:10]}...{val[-5:]}"
            else:
                masked = "***"
            print(f"{key}: {masked} (Length: {len(val)})")
        else:
            print(f"{key}: {val}")
    else:
        print(f"{key}: [NOT SET]")

# 3. MongoDB Connection Test
print("\n[MONGODB TEST]")
mongodb_uri = os.getenv("MONGODB_URI") or os.getenv("MONGO_URL")

if not mongodb_uri:
    print("❌ No MongoDB URI found in env vars!")
else:
    try:
        from pymongo import MongoClient
        print(f"Attempting connection to: {mongodb_uri.split('@')[-1] if '@' in mongodb_uri else '***'}")
        
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        info = client.server_info()
        print("✅ Connection successful!")
        print(f"Server version: {info.get('version')}")
        
        # List databases
        dbs = client.list_database_names()
        print(f"Databases: {dbs}")
        
    except ImportError:
        print("❌ pymongo not installed!")
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")

# 4. Check shared context service availability
print("\n[SHARED CONTEXT SERVICE]")
try:
    sys.path.append(os.path.join(os.getcwd(), "python-scripts"))
    from shared_context_service import get_shared_context_service, ensure_mongodb_connected
    print("✅ Module imported successfully")
    
    service = get_shared_context_service()
    if service:
        print("✅ Service initialized")
        print(f"Mongo Available in service: {ensure_mongodb_connected()}")
    else:
        print("❌ Service failed to initialize")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Print python-scripts content
    if os.path.exists("python-scripts"):
        print(f"python-scripts content: {os.listdir('python-scripts')}")
    else:
        print("❌ python-scripts directory not found")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("="*50)
print(f"DIAGNOSTIC END: {datetime.now().isoformat()}")
print("="*50)
