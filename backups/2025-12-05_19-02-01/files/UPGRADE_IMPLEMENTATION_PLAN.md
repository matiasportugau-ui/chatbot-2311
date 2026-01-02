# Chat System Upgrade Implementation Plan

## Quick Start: Critical Upgrades

This document provides step-by-step implementation for the most critical upgrades identified in the evaluation report.

---

## Upgrade 1: MongoDB Conversation Persistence

### Step 1: Update `api_server.py`

Add conversation persistence to the `/chat/process` endpoint:

```python
@app.post("/chat/process", response_model=ChatResponse)
async def process_chat_message(request: ChatRequest):
    try:
        logger.info(f"Processing message from {request.telefono}: {request.mensaje[:50]}...")
        
        # Process message
        resultado = ia.procesar_mensaje_usuario(
            mensaje=request.mensaje,
            telefono_cliente=request.telefono,
            sesion_id=request.sesionId
        )
        
        # CRITICAL: Save conversation to MongoDB
        try:
            from mongodb_service import get_mongodb_service, ensure_mongodb_connected
            if ensure_mongodb_connected():
                conversations_col = get_mongodb_service().get_collection('conversations')
                if conversations_col:
                    conversations_col.insert_one({
                        "session_id": resultado.get("sesion_id", request.sesionId),
                        "phone": request.telefono,
                        "message": request.mensaje,
                        "response": resultado.get("mensaje", ""),
                        "response_type": resultado.get("tipo", ""),
                        "confidence": resultado.get("confianza", 0.0),
                        "intent": resultado.get("intencion", ""),
                        "entities": resultado.get("entidades", {}),
                        "timestamp": datetime.now(),
                        "source": "api"
                    })
        except Exception as e:
            logger.warning(f"Could not save conversation to MongoDB: {e}")
        
        return ChatResponse(**resultado)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 2: Create MongoDB Indexes

```python
# Add to api_server.py startup
@app.on_event("startup")
async def startup_event():
    try:
        from mongodb_service import get_mongodb_service, ensure_mongodb_connected
        if ensure_mongodb_connected():
            conversations_col = get_mongodb_service().get_collection('conversations')
            if conversations_col:
                # Create indexes for better query performance
                conversations_col.create_index("session_id")
                conversations_col.create_index("phone")
                conversations_col.create_index("timestamp")
                conversations_col.create_index([("phone", 1), ("timestamp", -1)])
                logger.info("MongoDB indexes created")
    except Exception as e:
        logger.warning(f"Could not create MongoDB indexes: {e}")
```

---

## Upgrade 2: Session Management

### Step 1: Create Session Manager

Create `session_manager.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Manager for Chat System
Manages session creation, validation, and persistence
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from mongodb_service import get_mongodb_service, ensure_mongodb_connected

logger = logging.getLogger(__name__)

SESSION_EXPIRY_HOURS = 24  # Sessions expire after 24 hours of inactivity

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return f"sesion_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(datetime.now().isoformat()) % 10000}"

def get_or_create_session(phone: str, session_id: Optional[str] = None) -> str:
    """
    Get existing session or create new one
    Returns: session_id
    """
    if session_id:
        # Validate existing session
        if validate_session(session_id, phone):
            update_session_activity(session_id)
            return session_id
        else:
            logger.warning(f"Invalid session {session_id} for phone {phone}, creating new")
    
    # Create new session
    new_session_id = generate_session_id()
    create_session(new_session_id, phone)
    return new_session_id

def validate_session(session_id: str, phone: str) -> bool:
    """Validate that session exists and belongs to phone"""
    try:
        if not ensure_mongodb_connected():
            return False
        
        sessions_col = get_mongodb_service().get_collection('sessions')
        if not sessions_col:
            return False
        
        session = sessions_col.find_one({
            "session_id": session_id,
            "phone": phone
        })
        
        if not session:
            return False
        
        # Check if expired
        last_activity = session.get("last_activity", session.get("created_at"))
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        
        hours_since_activity = (datetime.now() - last_activity).total_seconds() / 3600
        if hours_since_activity > SESSION_EXPIRY_HOURS:
            # Expired, delete it
            sessions_col.delete_one({"session_id": session_id})
            return False
        
        return True
    except Exception as e:
        logger.warning(f"Error validating session: {e}")
        return False

def create_session(session_id: str, phone: str) -> bool:
    """Create a new session in MongoDB"""
    try:
        if not ensure_mongodb_connected():
            return False
        
        sessions_col = get_mongodb_service().get_collection('sessions')
        if not sessions_col:
            return False
        
        sessions_col.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "session_id": session_id,
                    "phone": phone,
                    "created_at": datetime.now(),
                    "last_activity": datetime.now(),
                    "status": "active"
                }
            },
            upsert=True
        )
        logger.info(f"Created session {session_id} for phone {phone}")
        return True
    except Exception as e:
        logger.warning(f"Error creating session: {e}")
        return False

def update_session_activity(session_id: str) -> bool:
    """Update session last activity timestamp"""
    try:
        if not ensure_mongodb_connected():
            return False
        
        sessions_col = get_mongodb_service().get_collection('sessions')
        if not sessions_col:
            return False
        
        sessions_col.update_one(
            {"session_id": session_id},
            {"$set": {"last_activity": datetime.now()}}
        )
        return True
    except Exception as e:
        logger.warning(f"Error updating session activity: {e}")
        return False

def get_active_sessions(phone: str, limit: int = 5) -> list:
    """Get recent active sessions for a phone"""
    try:
        if not ensure_mongodb_connected():
            return []
        
        sessions_col = get_mongodb_service().get_collection('sessions')
        if not sessions_col:
            return []
        
        sessions = list(sessions_col.find(
            {
                "phone": phone,
                "status": "active"
            }
        ).sort("last_activity", -1).limit(limit))
        
        return [s["session_id"] for s in sessions]
    except Exception as e:
        logger.warning(f"Error getting active sessions: {e}")
        return []
```

### Step 2: Update `api_server.py` to Use Session Manager

```python
from session_manager import get_or_create_session

@app.post("/chat/process", response_model=ChatResponse)
async def process_chat_message(request: ChatRequest):
    try:
        logger.info(f"Processing message from {request.telefono}: {request.mensaje[:50]}...")
        
        # Get or create session
        session_id = get_or_create_session(request.telefono, request.sesionId)
        
        # Process message
        resultado = ia.procesar_mensaje_usuario(
            mensaje=request.mensaje,
            telefono_cliente=request.telefono,
            sesion_id=session_id
        )
        
        # Ensure session_id is in result
        resultado["sesion_id"] = session_id
        
        # Save conversation (from Upgrade 1)
        # ... conversation persistence code ...
        
        return ChatResponse(**resultado)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Upgrade 3: Enhanced Entity Extraction

### Step 1: Add Fuzzy Matching

Add to `ia_conversacional_integrada.py`:

```python
from difflib import SequenceMatcher

def _fuzzy_match(self, pattern: str, text: str, threshold: float = 0.7) -> bool:
    """Simple fuzzy matching using similarity ratio"""
    similarity = SequenceMatcher(None, pattern.lower(), text.lower()).ratio()
    return similarity >= threshold

def _extraer_entidades_mejorado(self, mensaje: str) -> Dict[str, Any]:
    """Enhanced entity extraction with fuzzy matching"""
    mensaje_lower = mensaje.lower()
    entidades = {}
    
    # Enhanced product extraction with fuzzy matching
    productos_encontrados = []
    for producto in self.entidades_reconocidas["productos"]:
        if producto in mensaje_lower or self._fuzzy_match(producto, mensaje_lower):
            productos_encontrados.append(producto)
    if productos_encontrados:
        entidades["productos"] = productos_encontrados
    
    # Enhanced thickness extraction (handle variations)
    espesores_encontrados = []
    espesor_patterns = [
        r'(\d+)\s*mm',
        r'(\d+)\s*mil[ií]metros',
        r'(\d+)\s*cm',
        r'espesor.*?(\d+)'
    ]
    for pattern in espesor_patterns:
        matches = re.findall(pattern, mensaje_lower)
        for match in matches:
            if match.isdigit():
                espesores_encontrados.append(f"{match}mm")
    if espesores_encontrados:
        entidades["espesores"] = list(set(espesores_encontrados))  # Remove duplicates
    
    # Rest of extraction...
    return entidades
```

### Step 2: Update `procesar_mensaje` to Use Enhanced Extraction

```python
def procesar_mensaje(self, mensaje: str, cliente_id: str, sesion_id: str = None) -> RespuestaIA:
    # ... existing code ...
    
    # Use enhanced entity extraction
    entidades = self._extraer_entidades_mejorado(mensaje)
    
    # ... rest of processing ...
```

---

## Upgrade 4: Rate Limiting

### Step 1: Install Dependencies

```bash
pip install slowapi
```

### Step 2: Add Rate Limiting to `api_server.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat/process", response_model=ChatResponse)
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def process_chat_message(request: ChatRequest):
    # ... existing code ...
```

---

## Upgrade 5: Conversation Analytics

### Step 1: Create Analytics Endpoint

Add to `api_server.py`:

```python
@app.get("/analytics/conversations")
async def get_conversation_analytics(
    days: int = 7,
    phone: Optional[str] = None
):
    """Get conversation analytics"""
    try:
        from mongodb_service import get_mongodb_service, ensure_mongodb_connected
        from datetime import timedelta
        
        if not ensure_mongodb_connected():
            return {"error": "MongoDB not available"}
        
        conversations_col = get_mongodb_service().get_collection('conversations')
        if not conversations_col:
            return {"error": "Conversations collection not available"}
        
        # Build query
        query = {
            "timestamp": {
                "$gte": datetime.now() - timedelta(days=days)
            }
        }
        if phone:
            query["phone"] = phone
        
        # Get statistics
        total_conversations = conversations_col.count_documents(query)
        
        # Intent distribution
        intent_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$intent", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        intent_distribution = list(conversations_col.aggregate(intent_pipeline))
        
        # Average confidence
        confidence_pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence"}}}
        ]
        avg_confidence_result = list(conversations_col.aggregate(confidence_pipeline))
        avg_confidence = avg_confidence_result[0]["avg_confidence"] if avg_confidence_result else 0
        
        return {
            "total_conversations": total_conversations,
            "intent_distribution": intent_distribution,
            "average_confidence": round(avg_confidence, 2),
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Checklist

After implementing upgrades, test:

- [ ] Conversation persistence works
- [ ] Sessions are created and validated
- [ ] Rate limiting prevents abuse
- [ ] Enhanced entity extraction finds more entities
- [ ] Analytics endpoint returns correct data
- [ ] MongoDB indexes improve query performance
- [ ] Error handling works correctly

---

## Deployment Notes

1. **Database Migration**: No migration needed - new collections will be created automatically
2. **Backward Compatibility**: All upgrades are backward compatible
3. **Rollback Plan**: Keep old code commented for quick rollback if needed
4. **Monitoring**: Add alerts for:
   - MongoDB connection failures
   - High error rates
   - Rate limit violations
   - Slow response times

---

**Implementation Priority:**
1. ✅ Upgrade 1: MongoDB Persistence (Critical)
2. ✅ Upgrade 2: Session Management (Critical)
3. ✅ Upgrade 3: Enhanced Entity Extraction (High)
4. ✅ Upgrade 4: Rate Limiting (High)
5. ✅ Upgrade 5: Analytics (Medium)

