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

from ia_conversacional_integrada import IAConversacionalIntegrada
from sistema_cotizaciones import (
    SistemaCotizacionesBMC,
    Cliente,
    EspecificacionCotizacion,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="BMC Chat Service API",
    description="API para procesamiento de mensajes y cotizaciones BMC Uruguay",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Middleware para logging de requests con observabilidad
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = datetime.now()

    # Log structured request
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

    try:
        # Procesar request
        response = await call_next(request)

        # Log structured response
        process_time = (datetime.now() - start_time).total_seconds()
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

        return response
    except Exception as e:
        # Log error
        error_data = {
            "request_id": request_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "type": "error",
        }
        logger.error(f"Error: {json.dumps(error_data)}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "bmc-chat-api",
    }


@app.post("/chat/process", response_model=ChatResponse)
async def process_chat_message(request: ChatRequest):
    """
    Procesa un mensaje del cliente y retorna respuesta
    """
    try:
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
                    metadata={"agent_type": "fastapi", "source": "api"},
                )
            else:
                # Validate existing session
                session = shared_context_service.get_session(session_id)
                if not session or session.get("user_phone") != request.telefono:
                    # Invalid session, create new one
                    session_id = shared_context_service.create_session(
                        request.telefono,
                        request.mensaje,
                        metadata={"agent_type": "fastapi", "source": "api"},
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

        # Retornar respuesta
        return ChatResponse(**resultado)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error procesando mensaje: {str(e)}"
        )


@app.post("/quote/create", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest):
    """
    Crea una nueva cotización
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
