#!/usr/bin/env python3
"""
FastAPI Server para Sistema de Cotizaciones BMC
Expone endpoints para procesamiento de mensajes y cotizaciones
"""

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from collections.abc import Awaitable, Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_cotizaciones import (
    Cliente,
    EspecificacionCotizacion,
    SistemaCotizacionesBMC,
)

# Configurar logging primero para que logger esté disponible
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus metrics not available - prometheus_client not installed")

# FastAPI app will be initialized after lifespan is defined
# (lifespan needs to reference 'ia' which is initialized later)
app = None

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

# Initialize structured logger if available
if UTILS_AVAILABLE:
    structured_logger = get_structured_logger(__name__)
else:
    structured_logger = logger

# CORS and rate limiting configuration will be done after app initialization

# Rate limiting configuration
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    Limiter = None
    get_remote_address = None
    RateLimitExceeded = Exception
    def _rate_limit_exceeded_handler(*args, **kwargs):
        pass
    logger.warning("Rate limiting not available - slowapi not installed")

# Helper function for conditional rate limiting
def rate_limit(limit_str: str):
    """Conditional rate limit decorator"""
    def decorator(func):
        if RATE_LIMITING_AVAILABLE and limiter:
            return limiter.limit(limit_str)(func)
        return func
    return decorator


# MongoDB Service Configuration
try:
    # Try importing from local module first (if in PYTHONPATH)
    try:
        from mongodb_service import MongoDBService, get_mongodb_service
        MONGODB_SERVICE_AVAILABLE = True
    except ImportError:
        # Try relative import
        import sys
        sys.path.append(os.getcwd())
        from mongodb_service import MongoDBService, get_mongodb_service
        MONGODB_SERVICE_AVAILABLE = True
except ImportError:
    MONGODB_SERVICE_AVAILABLE = False
    logger.warning("MongoDB service not available - module not found")
    def get_mongodb_service():
        return None

def ensure_mongodb_connected():
    if not MONGODB_SERVICE_AVAILABLE:
        return False
    service = get_mongodb_service()
    if service:
        return service.is_connected()
    return False

# Inicializar IA conversacional
ia = IAConversacionalIntegrada()
sistema_cotizaciones = SistemaCotizacionesBMC()

# Periodic cleanup task to prevent memory leaks
import asyncio
from datetime import datetime, timedelta

async def periodic_cleanup():
    """Periodically cleanup old conversations to prevent memory growth"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            if hasattr(ia, '_limpiar_conversaciones_antiguas'):
                ia._limpiar_conversaciones_antiguas()
                logger.debug("Periodic conversation cleanup completed")
        except Exception as e:
            logger.warning(f"Error in periodic cleanup: {e}")

# Start cleanup task in background
cleanup_task = None

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    global cleanup_task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Background cleanup task started")

    # Initialize MongoDB connection early
    if MONGODB_SERVICE_AVAILABLE:
        try:
            if ensure_mongodb_connected():
                logger.info("MongoDB connection initialized on startup")
            else:
                logger.warning("MongoDB connection failed on startup, will retry on first request")
        except Exception as e:
            logger.warning(f"Error initializing MongoDB connection on startup: {e}")

    yield

    # Shutdown
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    logger.info("Background cleanup task stopped")

# Initialize FastAPI app with lifespan (now that ia is defined and lifespan is ready)
app = FastAPI(
    title="BMC Chat Service API",
    description="API para procesamiento de mensajes y cotizaciones BMC Uruguay",
    version="1.0.0",
    lifespan=lifespan,
)

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

# CORS configuration
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
if cors_origins_str == "*":
    cors_origins = ["*"]
else:
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Initialize Prometheus metrics
if PROMETHEUS_AVAILABLE:
    # Response time histogram
    response_time_histogram = Histogram(
        "chat_response_time_seconds", "Chat response time in seconds", ["endpoint", "method"]
    )

    # Request counter
    request_counter = Counter(
        "chat_requests_total", "Total number of chat requests", ["endpoint", "method", "status"]
    )

    # Intent detection accuracy
    intent_accuracy_counter = Counter(
        "intent_detection_accuracy", "Intent detection accuracy", ["intent", "confidence_level"]
    )

    # Error counter
    error_counter = Counter(
        "chat_errors_total", "Total number of errors", ["endpoint", "error_type"]
    )

    # Active sessions gauge
    active_sessions_gauge = Gauge("chat_active_sessions", "Number of active chat sessions")

    logger.info("Prometheus metrics initialized")

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


# Modelos Pydantic
class ChatRequest(BaseModel):
    mensaje: str = Field(..., description="Mensaje del cliente")
    telefono: str = Field(..., description="Número de teléfono del cliente")
    sesionId: str | None = Field(None, description="ID de sesión (opcional)")


class ChatResponse(BaseModel):
    mensaje: str
    tipo: str
    acciones: list[str] = []
    confianza: float
    necesita_datos: list[str] = []
    sesion_id: str
    timestamp: str


class QuoteRequest(BaseModel):
    cliente: dict[str, Any]
    especificaciones: dict[str, Any]
    asignado_a: str | None = "MA"
    observaciones: str | None = ""


class QuoteResponse(BaseModel):
    id: str
    cliente: dict[str, Any]
    producto: str
    precio_total: float
    precio_m2: float
    estado: str
    fecha: str


# Middleware para logging de requests con observabilidad y request tracking
@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = str(uuid.uuid4())
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

    # Record metrics
    # Request counter is incremented at the end of the request
    pass

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

        # Record metrics
        if PROMETHEUS_AVAILABLE:
            response_time_histogram.labels(endpoint=endpoint, method=method).observe(process_time)
            request_counter.labels(
                endpoint=endpoint, method=method, status=str(response.status_code)
            ).inc()

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

        # Record error metric
        if PROMETHEUS_AVAILABLE:
            error_counter.labels(endpoint=endpoint, error_type=type(e).__name__).inc()

        raise


@app.get("/health")
@app.get("/api/health")
@rate_limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint with dependency checks"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "bmc-chat-api",
        "dependencies": {}
    }

    # Check MongoDB connectivity
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if mongodb_uri:
            from pymongo import MongoClient
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            client.server_info()
            client.close()
            health_data["dependencies"]["mongodb"] = {"status": "healthy", "connected": True}
        else:
            health_data["dependencies"]["mongodb"] = {"status": "unknown", "connected": False, "error": "MONGODB_URI not configured"}
    except Exception as e:
        health_data["dependencies"]["mongodb"] = {"status": "unhealthy", "connected": False, "error": str(e)}
        health_data["status"] = "degraded"

    # Check Qdrant connectivity
    try:
        qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        import requests
        response = requests.get(f"{qdrant_url}/", timeout=2)
        if response.status_code == 200:
            health_data["dependencies"]["qdrant"] = {"status": "healthy", "connected": True}
        else:
            health_data["dependencies"]["qdrant"] = {"status": "unhealthy", "connected": False, "error": f"HTTP {response.status_code}"}
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["dependencies"]["qdrant"] = {"status": "unhealthy", "connected": False, "error": str(e)}
        health_data["status"] = "degraded"

    # Check OpenAI API (basic check - just verify key is set)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        health_data["dependencies"]["openai"] = {"status": "configured", "key_present": True}
    else:
        health_data["dependencies"]["openai"] = {"status": "misconfigured", "key_present": False}
        health_data["status"] = "degraded"

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
                if health_data["status"] == "healthy":
                    health_data["status"] = "degraded"

    return health_data


@app.get("/api/debug/request/{request_id}")
@rate_limit("20/minute")
async def get_request_debug(request: Request, request_id: str):
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
@rate_limit("10/minute")
async def get_rate_limits(request: Request):
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
async def process_chat_message(request: ChatRequest, http_request: Request) -> ChatResponse:
    """
    Procesa un mensaje del cliente y retorna respuesta
    Rate limit: 10 requests per minute
    """
    try:
        logger.info(f"Processing message from {request.telefono}: {request.mensaje[:50]}...")
        
        # Get request IDs from request state or generate new ones
        request_id = getattr(http_request.state, "request_id", str(uuid.uuid4()))
        client_request_id = getattr(http_request.state, "client_request_id", None)

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

        # Procesar mensaje con IA
        resultado = ia.procesar_mensaje_usuario(
            mensaje=request.mensaje,
            telefono_cliente=request.telefono,
            sesion_id=session_id or request.sesionId,
        )

        # Ensure session_id is in result
        if session_id:
            resultado["sesion_id"] = session_id

        # Record intent detection metrics
        if PROMETHEUS_AVAILABLE and "intencion" in resultado:
            intent = resultado.get("intencion", "general")
            confidence = resultado.get("confianza", 0.0)
            confidence_level = (
                "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low"
            )
            intent_accuracy_counter.labels(intent=intent, confidence_level=confidence_level).inc()

        # Update active sessions gauge
        if PROMETHEUS_AVAILABLE and active_sessions_gauge:
            # This is a simplified count - in production, track actual active sessions
            pass

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
                                "role": msg.get("tipo") == "cliente" and "user" or "assistant",
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
        # Use mongodb_service for connection pooling instead of creating new connections
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
                    logger.debug(f"Conversation saved to MongoDB for session {session_id}")
                client.close()
        except Exception as e:
            logger.warning(f"Could not save conversation to MongoDB: {e}")

        # Retornar respuesta
        return ChatResponse(**resultado)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")


@app.post("/quote/create", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest) -> QuoteResponse:
    """
    Crea una nueva cotización
    Rate limit: 5 requests per minute
    """
    try:
        logger.info(f"Creating quote for client: {request.cliente.get('nombre', 'Unknown')}")

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
        raise HTTPException(status_code=500, detail=f"Error creando cotización: {str(e)}")


@app.get("/insights")
async def get_insights() -> dict[str, Any]:
    """Obtiene insights de la base de conocimiento"""
    try:
        insights = ia.base_conocimiento.generar_insights()
        return {"success": True, "data": insights}
    except Exception as e:
        logger.error(f"Error getting insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error obteniendo insights: {str(e)}")


@app.get("/metrics")
async def get_metrics() -> Response:
    """Prometheus metrics endpoint"""
    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Prometheus metrics not available")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/auth/login")
async def login(username: str, password: str):
    """
    Login endpoint to obtain JWT token

    Args:
        username: Username for authentication
        password: Password for authentication

    Returns:
        JWT access token
    """
    # Simple authentication - in production, use proper user database
    admin_password = os.getenv("ADMIN_PASSWORD", "change-this-secure-password")

    if username == "admin" and password == admin_password:
        token = create_access_token({"username": username, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


@app.get("/conversations")
@rate_limit("20/minute")
async def get_conversations(request: Request, limit: int = 50) -> dict[str, Any]:
    """Obtiene conversaciones recientes desde MongoDB (si está disponible)"""
    try:
        if MONGODB_SERVICE_AVAILABLE:
            mongodb_service = get_mongodb_service()
            if mongodb_service:
                conversations_col = mongodb_service.get_collection("conversations")
                # Get recent conversations
                conversations = list(
                    conversations_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
                )
                return {"success": True, "data": conversations, "count": len(conversations)}
            else:
                return {"success": True, "data": [], "message": "MongoDB service unavailable"}
        else:
            # Fallback to old method if service not available (should not happen in production)
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                return {"success": True, "data": [], "message": "MongoDB not configured"}

            from pymongo import MongoClient
            client = MongoClient(mongodb_uri)
            db = client.get_database()
            conversations_col = db.conversations

        client = MongoClient(mongodb_uri)
        db = client.get_database()
        conversations_col = db.conversations

        # Get recent conversations
        conversations: list[dict[str, Any]] = list(
            conversations_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        )

        return {"success": True, "data": conversations, "count": len(conversations)}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}", exc_info=True)
        return {"success": False, "data": [], "error": str(e)}


# Startup and shutdown events are now handled by lifespan context manager above

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting BMC Chat API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
