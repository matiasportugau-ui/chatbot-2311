
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMC Chat API Proxy
Redirects to sistema_completo_integrado.py to support existing deployment config
"""

import os
import sys
import json
import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

# Ensure current directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import the new application
try:
    from sistema_completo_integrado import app
except ImportError as e:
    print(f"Error importing sistema_completo_integrado: {e}")
    # Fallback for debugging
    app = FastAPI(title="Error Loading App")

# REMOVE CONFLICTING ROUTE FROM IMPORTED APP
# The imported app likely has /api/chat defined, which returns JSON.
# We want to override it with our streaming endpoint.
# FastAPI prioritizes the first matching route, so we must remove the old one.
# FastAPI/Starlette routes are in app.router.routes
filtered_routes = [
    route for route in app.router.routes 
    if not (hasattr(route, "path") and route.path == "/api/chat")
]
app.router.routes = filtered_routes
logger.info("✅ Removed conflicting /api/chat route from upstream app")

@app.get("/api/debug/routes", tags=["Debug"])
async def list_routes():
    """List all registered routes for debugging"""
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, "methods") else None
            })
    return {"routes": routes}


@app.post("/api/chat", tags=["Chat"])
async def chat(request: Request):
    """
    Process chat messages with AI assistant (Streaming)
    Compatible with Vercel AI SDK
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])
        
        # Extract the last user message
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
            
        last_message = messages[-1]["content"]
        # In a real scenario, you'd handle session ID differently or extract from headers/body
        # For now, we use a default or generate one
        session_id = body.get("sessionId", "default")
        
        logger.info(f"Chat request: {last_message[:50]}...")
        
        async def event_generator():
            try:
                # Import chat processing
                # We need to instantiate the class as the method is an instance method
                from ia_conversacional_integrada import IAConversacionalIntegrada
                
                # Create instance (in production this should be a singleton)
                ia_service = IAConversacionalIntegrada()
                
                # procesar_mensaje_usuario signature: (self, mensaje, telefono_cliente, sesion_id)
                # We use a placeholder phone number if not provided
                user_phone = body.get("userPhone", "web_user")
                
                # It returns a dict now!
                # { "mensaje": ..., "tipo": ..., ... }
                response_data = ia_service.procesar_mensaje_usuario(last_message, user_phone, session_id)
                
                # Extract text response
                if isinstance(response_data, dict):
                    response_text = response_data.get("mensaje", "")
                else:
                    response_text = str(response_data)
                
                # Split into chunks to simulate streaming (aesthetic) or just send matching format
                chunk_size = 20
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i+chunk_size]
                    yield chunk
                    import asyncio
                    await asyncio.sleep(0.01) # Small delay for visual effect
                    
            except ImportError:
                 yield "Lo siento, el módulo de inteligencia artificial no está disponible."
            except Exception as e:
                 logger.error(f"Error generating stream: {e}")
                 yield f"Error: {str(e)}"

        return StreamingResponse(event_generator(), media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

