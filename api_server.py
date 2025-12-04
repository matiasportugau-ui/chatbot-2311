#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Server para Sistema de Cotizaciones BMC
Expone endpoints para procesamiento de mensajes y cotizaciones
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    logger.warning("Rate limiting not available - slowapi not installed")

from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_cotizaciones import (
    SistemaCotizacionesBMC,
    Cliente,
    EspecificacionCotizacion,
)

# Import request tracking utilities
try:
    from utils.request_tracking import get_request_tracker, set_request_context
    from utils.structured_logger import get_structured_logger
    from utils.rate_limit_monitor import get_rate_limit_monitor
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    def get_request_tracker():
        return None
    def set_request_context(*args, **kwargs):
        pass
    def get_structured_logger(*args, **kwargs):
        return logging.getLogger(__name__)
    def get_rate_limit_monitor():
        return None

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize structured logger if available
if UTILS_AVAILABLE:
    structured_logger = get_structured_logger(__name__)
else:
    structured_logger = logger

# Inicializar FastAPI
app = FastAPI(
    title="BMC Chat Service API",
    description="API para procesamiento de mensajes y cotizaciones BMC Uruguay",
    version="1.0.0",
)

# CORS middleware - Configure allowed origins from environment
# In production, specify exact domains. For development, allow localhost
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,http://localhost:5678").split(",")
# Remove wildcard in production - only allow specific origins
if os.getenv("ENVIRONMENT") == "production":
    # In production, only allow specific domains
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip() and origin != "*"]
else:
    # In development, allow localhost origins
    cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize rate limiter if available
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")
else:
    limiter = None

# Helper function for conditional rate limiting
def rate_limit(limit_str: str):
    """Conditional rate limit decorator"""
    def decorator(func):
        if RATE_LIMITING_AVAILABLE and limiter:
            return limiter.limit(limit_str)(func)
        return func
    return decorator

# Inicializar IA conversacional
ia = IAConversacionalIntegrada()
sistema_cotizaciones = SistemaCotizacionesBMC()

# Shared context service for multi-agent system
try:
    import sys
    from pathlib import Path

    python_scripts_path = Path(__file__).parent / "python-scripts"
    if str(python_scripts_path) not in sys.path:
        sys.path.insert(0, str(python_scripts_path))
    from shared_context_service import get_shared_context_service

    shared_context_service = get_shared_context_service()
    USE_SHARED_CONTEXT = True
    logger.info("Shared context service initialized")
except Exception as e:
    logger.warning(f"Shared context service not available: {e}")
    USE_SHARED_CONTEXT = False
    shared_context_service = None


# Modelos Pydantic
class ChatRequest(BaseModel):
    mensaje: str = Field(..., description="Mensaje del cliente")
    telefono: str = Field(..., description="Número de teléfono del cliente")
    sesionId: Optional[str] = Field(None, description="ID de sesión (opcional)")


class ChatResponse(BaseModel):
    mensaje: str
    tipo: str
    acciones: list[str] = []
    confianza: float
    necesita_datos: list[str] = []
    sesion_id: str
    timestamp: str


class QuoteRequest(BaseModel):
    cliente: Dict[str, Any]
    especificaciones: Dict[str, Any]
    asignado_a: Optional[str] = "MA"
    observaciones: Optional[str] = ""


class QuoteResponse(BaseModel):
    id: str
    cliente: Dict[str, Any]
    producto: str
    precio_total: float
    precio_m2: float
    estado: str
    fecha: str


# Middleware para logging de requests con observabilidad y request tracking
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()

    # Extract client request ID if provided
    client_request_id = request.headers.get("X-Client-Request-Id")

    # Initialize request tracking
    request_tracker = get_request_tracker() if UTILS_AVAILABLE else None
    request_metadata = None

    if request_tracker:
        request_metadata = request_tracker.create_request_metadata(
            client_request_id=client_request_id,
            endpoint=request.url.path
        )
        request_id = request_metadata.request_id
        # Set request context for structured logging
        set_request_context(
            request_metadata.request_id,
            request_metadata.client_request_id
        )
    else:
        # Fallback to UUID if tracking not available
        request_id = str(uuid.uuid4())

    # Log structured request
    if UTILS_AVAILABLE:
        structured_logger.info(
            f"API Request: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_request_id=client_request_id
        )
    else:
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "timestamp": start_time.isoformat(),
            "type": "request",
        }
        logger.info(f"Request: {json.dumps(log_data)}")

    # Agregar request_id al request state
    request.state.request_id = request_id
    if client_request_id:
        request.state.client_request_id = client_request_id

    try:
        # Procesar request
        response = await call_next(request)

        # Log structured response
        process_time = (datetime.now() - start_time).total_seconds()

        if UTILS_AVAILABLE:
            structured_logger.info(
                f"API Response: {request.method} {request.url.path} - {response.status_code}",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=process_time
            )
        else:
            response_data = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
                "timestamp": datetime.now().isoformat(),
                "type": "response",
            }
            logger.info(f"Response: {json.dumps(response_data)}")

        # Agregar request_id al header
        response.headers["X-Request-ID"] = request_id
        if client_request_id:
            response.headers["X-Client-Request-ID"] = client_request_id

        # Update request tracking
        if request_metadata and request_tracker:
            request_tracker.update_request(
                request_metadata.request_id,
                status="completed",
                response_time=process_time
            )

        return response
    except Exception as e:
        # Log error
        process_time = (datetime.now() - start_time).total_seconds()

        if UTILS_AVAILABLE:
            structured_logger.error(
                f"API Error: {request.method} {request.url.path} - {str(e)}",
                method=request.method,
                path=request.url.path,
                error=str(e),
                process_time=process_time
            )
        else:
            error_data = {
                "request_id": request_id,
                "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "error",
        }
        logger.error(f"Error: {json.dumps(error_data)}")
        raise


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint with rate limit status"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "bmc-chat-api",
    }

    # Add rate limit status if available
    if UTILS_AVAILABLE:
        rate_limit_monitor = get_rate_limit_monitor()
        if rate_limit_monitor:
            all_limits = rate_limit_monitor.get_all_rate_limits()
            health_data["rate_limits"] = all_limits

            # Check for warnings
            warnings = []
            for key in all_limits.keys():
                provider = key.split(":")[0]
                org = key.split(":")[1] if ":" in key else None
                provider_warnings = rate_limit_monitor.check_warnings(provider, org if org != "default" else None)
                warnings.extend(provider_warnings)

            if warnings:
                health_data["warnings"] = warnings
                health_data["status"] = "degraded"

    return health_data


@app.get("/api/debug/request/{request_id}")
async def get_request_debug(request_id: str):
    """
    Retrieve request details by ID for debugging.

    Args:
        request_id: Request ID or client request ID

    Returns:
        Request metadata and details
    """
    if not UTILS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Request tracking not available"
        )

    request_tracker = get_request_tracker()
    if not request_tracker:
        raise HTTPException(
            status_code=503,
            detail="Request tracker not initialized"
        )

    request_metadata = request_tracker.get_request_dict(request_id)

    if not request_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"Request {request_id} not found"
        )

    return {
        "request_id": request_id,
        "metadata": request_metadata,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/monitoring/rate-limits")
async def get_rate_limits():
    """
    Get current rate limit status for all providers.

    Returns:
        Rate limit information for all providers
    """
    if not UTILS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Rate limit monitoring not available"
        )

    rate_limit_monitor = get_rate_limit_monitor()
    if not rate_limit_monitor:
        raise HTTPException(
            status_code=503,
            detail="Rate limit monitor not initialized"
        )

    all_limits = rate_limit_monitor.get_all_rate_limits()

    # Add warnings for each provider
    result = {
        "rate_limits": all_limits,
        "warnings": {},
        "timestamp": datetime.now().isoformat()
    }

    for key in all_limits.keys():
        provider = key.split(":")[0]
        org = key.split(":")[1] if ":" in key and key.split(":")[1] != "default" else None
        warnings = rate_limit_monitor.check_warnings(provider, org)
        if warnings:
            result["warnings"][key] = warnings

    return result


@app.post("/chat/process", response_model=ChatResponse)
@rate_limit("10/minute")
async def process_chat_message(
    request: ChatRequest,
    http_request: Request
):
    """
    Procesa un mensaje del cliente y retorna respuesta
    Rate limit: 10 requests per minute
    """
    try:
        # Get request ID from middleware
        request_id = getattr(http_request.state, 'request_id', None)
        client_request_id = getattr(http_request.state, 'client_request_id', None)

        if UTILS_AVAILABLE:
            structured_logger.info(
                f"Processing message from {request.telefono}: {request.mensaje[:50]}...",
                request_id=request_id,
                client_request_id=client_request_id
            )
        else:
            logger.info(
                f"Processing message from {request.telefono}: {request.mensaje[:50]}..."
            )

        # Get or create session using shared context service
        session_id = request.sesionId
        if USE_SHARED_CONTEXT and shared_context_service:
            if not session_id:
                # Create new session
                session_id = shared_context_service.create_session(
                    request.telefono,
                    request.mensaje,
                    metadata={"agent_type": "fastapi", "source": "api", "request_id": request_id},
                )
            else:
                # Validate existing session
                session = shared_context_service.get_session(session_id)
                if not session or session.get("user_phone") != request.telefono:
                    # Invalid session, create new one
                    session_id = shared_context_service.create_session(
                        request.telefono,
                        request.mensaje,
                        metadata={"agent_type": "fastapi", "source": "api", "request_id": request_id},
                    )

        # Procesar mensaje con IA (pass request IDs if available)
        resultado = ia.procesar_mensaje_usuario(
            mensaje=request.mensaje,
            telefono_cliente=request.telefono,
            sesion_id=session_id or request.sesionId,
            request_id=request_id,
            client_request_id=client_request_id,
        )

        # Ensure session_id is in result
        if session_id:
            resultado["sesion_id"] = session_id

        # Save conversation to shared context service
        if USE_SHARED_CONTEXT and shared_context_service and session_id:
            try:
                # Get context from IA system and save it
                contexto_key = f"{request.telefono}_{session_id}"
                if (
                    hasattr(ia, "conversaciones_activas")
                    and contexto_key in ia.conversaciones_activas
                ):
                    contexto = ia.conversaciones_activas[contexto_key]
                    # Convert ContextoConversacion to dict for shared service
                    context_dict = {
                        "user_phone": request.telefono,
                        "cliente_id": request.telefono,
                        "intent": contexto.intencion_actual,
                        "entities": contexto.entidades_extraidas,
                        "quote_state": {
                            "estado": contexto.estado_cotizacion,
                            "datos_cliente": contexto.datos_cliente,
                            "datos_producto": contexto.datos_producto,
                        },
                        "messages": [
                            {
                                "role": msg.get("tipo") == "cliente"
                                and "user"
                                or "assistant",
                                "content": msg.get("mensaje", ""),
                                "timestamp": msg.get("timestamp", datetime.now()),
                            }
                            for msg in contexto.mensajes_intercambiados
                        ],
                    }
                    shared_context_service.save_context(session_id, context_dict)
            except Exception as e:
                logger.warning(f"Failed to save context to shared service: {e}")

        # CRITICAL: Save conversation directly to MongoDB conversations collection
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if mongodb_uri:
                from pymongo import MongoClient

                client = MongoClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                )
                # Test connection
                client.server_info()

                db = client.get_database()
                conversations_col = db.conversations

                if conversations_col:
                    conversations_col.insert_one(
                        {
                            "session_id": session_id or resultado.get("sesion_id", ""),
                            "phone": request.telefono,
                            "message": request.mensaje,
                            "response": resultado.get("mensaje", ""),
                            "response_type": resultado.get("tipo", ""),
                            "confidence": resultado.get("confianza", 0.0),
                            "intent": resultado.get("intencion", ""),
                            "entities": resultado.get("entidades", {}),
                            "timestamp": datetime.now(),
                            "source": "api",
                        }
                    )
                    logger.debug(
                        f"Conversation saved to MongoDB for session {session_id}"
                    )
                client.close()
        except Exception as e:
            logger.warning(f"Could not save conversation to MongoDB: {e}")

        # Retornar respuesta
        return ChatResponse(**resultado)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error procesando mensaje: {str(e)}"
        )


@app.post("/quote/create", response_model=QuoteResponse)
@rate_limit("5/minute")
async def create_quote(
    request: QuoteRequest,
    http_request: Request
):
    """
    Crea una nueva cotización
    Rate limit: 5 requests per minute
    """
    try:
        logger.info(
            f"Creating quote for client: {request.cliente.get('nombre', 'Unknown')}"
        )

        # Crear cliente
        cliente = Cliente(
            nombre=request.cliente.get("nombre", "Cliente"),
            telefono=request.cliente.get("telefono", ""),
            direccion=request.cliente.get("direccion", ""),
            zona=request.cliente.get("zona", "Montevideo"),
            email=request.cliente.get("email", ""),
        )

        # Crear especificaciones
        espec_data = request.especificaciones
        especificaciones = EspecificacionCotizacion(
            producto=espec_data.get("producto", ""),
            espesor=espec_data.get("espesor", ""),
            relleno=espec_data.get("relleno", "EPS"),
            largo_metros=Decimal(str(espec_data.get("largo_metros", 0))),
            ancho_metros=Decimal(str(espec_data.get("ancho_metros", 0))),
            color=espec_data.get("color", "Blanco"),
            termina_front=espec_data.get("termina_front", ""),
            termina_sup=espec_data.get("termina_sup", ""),
            termina_lat_1=espec_data.get("termina_lat_1", ""),
            termina_lat_2=espec_data.get("termina_lat_2", ""),
            anclajes=espec_data.get("anclajes", ""),
            traslado=espec_data.get("traslado", ""),
            direccion=espec_data.get("direccion", ""),
            forma=espec_data.get("forma", ""),
            origen=espec_data.get("origen", "WA"),
        )

        # Crear cotización
        cotizacion = sistema_cotizaciones.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            asignado_a=request.asignado_a,
            observaciones=request.observaciones,
        )

        return QuoteResponse(
            id=cotizacion.id,
            cliente={
                "nombre": cotizacion.cliente.nombre,
                "telefono": cotizacion.cliente.telefono,
                "direccion": cotizacion.cliente.direccion,
                "zona": cotizacion.cliente.zona,
            },
            producto=cotizacion.especificaciones.producto,
            precio_total=float(cotizacion.precio_total),
            precio_m2=float(cotizacion.precio_metro_cuadrado),
            estado=cotizacion.estado,
            fecha=cotizacion.fecha.isoformat(),
        )

    except Exception as e:
        logger.error(f"Error creating quote: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error creando cotización: {str(e)}"
        )


@app.get("/insights")
async def get_insights():
    """Obtiene insights de la base de conocimiento"""
    try:
        insights = ia.base_conocimiento.generar_insights()
        return {"success": True, "data": insights}
    except Exception as e:
        logger.error(f"Error getting insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo insights: {str(e)}"
        )


@app.get("/conversations")
async def get_conversations(limit: int = 50):
    """Obtiene conversaciones recientes desde MongoDB (si está disponible)"""
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            return {"success": True, "data": [], "message": "MongoDB not configured"}

        from pymongo import MongoClient

        client = MongoClient(mongodb_uri)
        db = client.get_database()
        conversations_col = db.conversations

        # Get recent conversations
        conversations = list(
            conversations_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        )

        return {"success": True, "data": conversations, "count": len(conversations)}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}", exc_info=True)
        return {"success": False, "data": [], "error": str(e)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting BMC Chat API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
