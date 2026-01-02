
# MongoDB Connection Issue Analysis
**Date:** December 1, 2025  
**Status:** 🔍 **Issue Identified**

## Problem Summary

The `shared_context_service.py` module is trying to import a `mongodb_service` module that **does not exist** in the codebase. This causes the service to fall back to in-memory storage even though MongoDB is running and accessible.

## Current Situation

### ✅ What's Working

- **MongoDB Container**: Running and healthy (`bmc-mongodb`)
- **MongoDB Connection**: Direct connection test successful (MongoDB 7.0.25)
- **Environment Variable**: `MONGODB_URI=mongodb://mongodb:27017/bmc_chat` is set correctly
- **Other Services**: `api_server.py` and `sistema_completo_integrado.py` connect to MongoDB successfully using `pymongo.MongoClient` directly

### ❌ What's Not Working

- **shared_context_service.py**: Cannot import `mongodb_service` module (doesn't exist)
- **Fallback Mode**: Service is using in-memory storage instead of MongoDB
- **Warning Message**: `mongodb_service not available, using in-memory fallback`

## Root Cause

The `shared_context_service.py` file (lines 13-28) tries to import:

```python
from mongodb_service import ensure_mongodb_connected, get_mongodb_service
```

However, **no `mongodb_service.py` file exists** in the codebase. The import fails, causing:

1. `MONGODB_AVAILABLE = False`
2. Service falls back to in-memory storage
3. Warning message is logged

## Impact

### Functional Impact

- ⚠️ **Low to Medium**: The service still works using in-memory storage
- ⚠️ **Data Persistence**: Session data is not persisted to MongoDB
- ⚠️ **Multi-Instance**: Won't work correctly if multiple instances are running (each has separate memory)

### Technical Impact

- The warning is misleading - MongoDB IS available, just the service module is missing
- Data stored in `shared_context_service` is lost on container restart
- Cannot share session data across multiple API instances

## Solution Options

### Option 1: Create `mongodb_service.py` Module (Recommended)

Create a MongoDB service module that provides the expected interface:

**File:** `mongodb_service.py` (in project root)

```python
from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

_client = None
_db = None

def ensure_mongodb_connected() -> bool:
    """Ensure MongoDB connection is established"""
    global _client, _db
    try:
        if _client is None:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bmc_chat")
            _client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            _client.server_info()  # Test connection
            db_name = mongodb_uri.split('/')[-1] if '/' in mongodb_uri else 'bmc_chat'
            _db = _client[db_name]
            logger.info("MongoDB connection established")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False

def get_mongodb_service():
    """Get MongoDB database instance"""
    if _db is None:
        ensure_mongodb_connected()
    return _db
```

**Pros:**

- Minimal code changes
- Follows existing pattern in `shared_context_service.py`
- Centralized MongoDB connection management

**Cons:**

- Adds another abstraction layer

### Option 2: Modify `shared_context_service.py` to Use pymongo Directly

Modify `shared_context_service.py` to use `pymongo.MongoClient` directly like other parts of the codebase.

**Pros:**

- Consistent with rest of codebase
- No new files needed
- Direct connection management

**Cons:**

- Requires more changes to `shared_context_service.py`
- Duplicates connection logic

### Option 3: Remove MongoDB Dependency from shared_context_service

If the shared context service doesn't need MongoDB persistence, remove the MongoDB dependency entirely.

**Pros:**

- Simplest solution
- No MongoDB connection needed

**Cons:**

- Loses data persistence capability
- May not meet requirements

## Recommended Solution

**Option 1** is recommended because:

1. It's the least invasive change
2. It follows the existing code pattern in `shared_context_service.py`
3. It provides a reusable MongoDB service for other modules
4. It maintains backward compatibility

## Verification Steps

After implementing the fix:

1. **Check Logs:**

   ```bash
   docker logs bmc-chat-api | grep -i mongo
   ```

   Should see: "MongoDB connection established" instead of warning

2. **Test Connection:**

   ```bash
   docker exec bmc-chat-api python3 -c "from mongodb_service import ensure_mongodb_connected; print(ensure_mongodb_connected())"
   ```

   Should return: `True`

3. **Verify Data Persistence:**
   - Create a session via API
   - Restart container
   - Verify session still exists

## Files to Modify

1. **Create:** `mongodb_service.py` (new file in project root)
2. **Update:** `docker-compose.yml` - ensure `MONGODB_URI` is set (already done ✅)
3. **Test:** Restart `bmc-chat-api` container to load new module

## Next Steps

1. Create `mongodb_service.py` with the implementation above
2. Restart the `bmc-chat-api` container
3. Verify the warning is gone from logs
4. Test that sessions are persisted to MongoDB
