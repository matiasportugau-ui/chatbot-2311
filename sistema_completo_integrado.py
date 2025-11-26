#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI application for BMC Quote System
Ready for deployment on Railway, Render, or any Python hosting
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BMC Quote System API",
    description="Intelligent quotation system for BMC Uruguay - Thermal insulation products",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class QuoteRequest(BaseModel):
    """Request model for creating a quote"""
    customer_name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="Customer phone number")
    product: str = Field(..., description="Product type: isodec, poliestireno, lana_roca")
    thickness: str = Field(..., description="Product thickness: 50mm, 75mm, 100mm, 125mm, 150mm")
    length: float = Field(..., gt=0, description="Length in meters")
    width: float = Field(..., gt=0, description="Width in meters")
    address: Optional[str] = Field(None, description="Delivery address")
    zone: Optional[str] = Field(None, description="Zone/area")
    observations: Optional[str] = Field(None, description="Additional observations")

class QuoteResponse(BaseModel):
    """Response model for quote creation"""
    quote_id: str
    total: float
    area: float
    status: str
    created_at: str

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session identifier")

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    context: Optional[Dict[str, Any]] = None

class WebhookVerification(BaseModel):
    """WhatsApp webhook verification"""
    hub_mode: str
    hub_verify_token: str
    hub_challenge: str

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting BMC Quote System API...")
    logger.info(f"   Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"   Port: {os.getenv('PORT', '8000')}")
    logger.info(f"   OpenAI Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    
    # Test MongoDB connection
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        if mongodb_uri:
            from pymongo import MongoClient
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            client.server_info()
            logger.info("✅ MongoDB connection successful")
        else:
            logger.warning("⚠️  MONGODB_URI not set - using in-memory storage")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.warning("⚠️  Continuing with in-memory storage")
    
    logger.info("✅ BMC Quote System API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down BMC Quote System API...")

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "service": "BMC Quote System API",
        "version": "1.0.0",
        "status": "online",
        "description": "Intelligent quotation system for thermal insulation products",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "chat": "/api/chat",
            "quotes": "/api/quotes",
            "whatsapp": "/api/whatsapp/webhook"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "online",
            "mongodb": "online" if os.getenv("MONGODB_URI") else "not_configured",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
        }
    }

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(message: ChatMessage):
    """
    Process chat messages with AI assistant
    
    The AI assistant can:
    - Answer product questions
    - Create quotes conversationally
    - Provide technical information
    - Assist with product selection
    """
    try:
        logger.info(f"Chat request: {message.message[:50]}...")
        
        # Import chat processing
        try:
            from ia_conversacional_integrada import procesar_mensaje_usuario
            
            response_text = procesar_mensaje_usuario(
                message.message,
                message.session_id
            )
            
            return ChatResponse(
                response=response_text,
                session_id=message.session_id or "default"
            )
            
        except ImportError:
            # Fallback response if IA module not available
            logger.warning("IA conversacional module not available, using fallback")
            return ChatResponse(
                response="Hola! Soy el asistente de BMC Uruguay. ¿En qué puedo ayudarte?",
                session_id=message.session_id or "default"
            )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

# ============================================================================
# QUOTE ENDPOINTS
# ============================================================================

@app.post("/api/quotes", response_model=QuoteResponse, tags=["Quotes"])
async def create_quote(quote: QuoteRequest):
    """
    Create a new quote
    
    Calculates pricing based on:
    - Product type
    - Thickness
    - Area (length × width)
    - Additional specifications
    """
    try:
        logger.info(f"Quote request for: {quote.customer_name} - {quote.product}")
        
        # Import quote system
        from sistema_cotizaciones import SistemaCotizacionesBMC, Cliente, EspecificacionCotizacion
        from decimal import Decimal
        
        # Initialize system
        sistema = SistemaCotizacionesBMC()
        
        # Create customer
        cliente = Cliente(
            nombre=quote.customer_name,
            telefono=quote.phone,
            direccion=quote.address or "",
            zona=quote.zone or ""
        )
        
        # Create specifications
        especificaciones = EspecificacionCotizacion(
            producto=quote.product,
            espesor=quote.thickness,
            largo_metros=Decimal(str(quote.length)),
            ancho_metros=Decimal(str(quote.width))
        )
        
        # Create quote
        cotizacion = sistema.crear_cotizacion(
            cliente=cliente,
            especificaciones=especificaciones,
            observaciones=quote.observations or ""
        )
        
        # Calculate area
        area = float(quote.length * quote.width)
        
        logger.info(f"Quote created: {cotizacion.id} - Total: ${cotizacion.precio_total}")
        
        return QuoteResponse(
            quote_id=cotizacion.id,
            total=float(cotizacion.precio_total),
            area=area,
            status="created",
            created_at=cotizacion.fecha.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating quote: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating quote: {str(e)}"
        )

@app.get("/api/quotes/{quote_id}", tags=["Quotes"])
async def get_quote(quote_id: str):
    """Get quote by ID"""
    try:
        from sistema_cotizaciones import SistemaCotizacionesBMC
        
        sistema = SistemaCotizacionesBMC()
        
        # Find quote
        for cotizacion in sistema.cotizaciones:
            if cotizacion.id == quote_id:
                return {
                    "quote_id": cotizacion.id,
                    "customer": {
                        "name": cotizacion.cliente.nombre,
                        "phone": cotizacion.cliente.telefono
                    },
                    "product": {
                        "type": cotizacion.especificaciones.producto,
                        "thickness": cotizacion.especificaciones.espesor,
                        "area": float(cotizacion.especificaciones.largo_metros * cotizacion.especificaciones.ancho_metros)
                    },
                    "total": float(cotizacion.precio_total),
                    "status": cotizacion.estado,
                    "created_at": cotizacion.fecha.isoformat()
                }
        
        raise HTTPException(status_code=404, detail="Quote not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving quote: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WHATSAPP WEBHOOK ENDPOINTS
# ============================================================================

@app.get("/api/whatsapp/webhook", tags=["WhatsApp"])
async def whatsapp_webhook_verify(request: Request):
    """
    WhatsApp webhook verification endpoint
    
    Called by Meta to verify webhook ownership
    """
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "bmc_verify_token_2024")
        
        logger.info(f"WhatsApp verification attempt - Mode: {mode}, Token match: {token == verify_token}")
        
        if mode == "subscribe" and token == verify_token:
            logger.info("✅ WhatsApp webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning("❌ WhatsApp verification failed")
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        logger.error(f"Error in WhatsApp verification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/whatsapp/webhook", tags=["WhatsApp"])
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook endpoint for incoming messages
    
    Processes incoming WhatsApp messages and responds with AI
    """
    try:
        data = await request.json()
        logger.info(f"WhatsApp webhook received: {data}")
        
        # Extract message from WhatsApp payload
        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change.get("field") == "messages":
                            value = change.get("value", {})
                            messages = value.get("messages", [])
                            
                            for message in messages:
                                # Process text message
                                if message.get("type") == "text":
                                    from_number = message.get("from")
                                    text = message.get("text", {}).get("body", "")
                                    
                                    logger.info(f"Processing WhatsApp message from {from_number}: {text}")
                                    
                                    # Process with AI
                                    try:
                                        from ia_conversacional_integrada import procesar_mensaje_usuario
                                        response_text = procesar_mensaje_usuario(text, from_number)
                                        
                                        # TODO: Send response back via WhatsApp API
                                        # This requires WhatsApp Business API credentials
                                        logger.info(f"Response generated: {response_text[:100]}...")
                                        
                                    except ImportError:
                                        logger.warning("IA module not available for WhatsApp processing")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}", exc_info=True)
        # Return 200 to avoid webhook retries
        return {"status": "error", "message": str(e)}

# ============================================================================
# PRODUCTS ENDPOINT
# ============================================================================

@app.get("/api/products", tags=["Products"])
async def get_products():
    """Get available products catalog"""
    return {
        "products": [
            {
                "id": "isodec",
                "name": "Isodec",
                "description": "Panel aislante térmico con núcleo de EPS",
                "thicknesses": ["50mm", "75mm", "100mm", "125mm", "150mm"],
                "features": [
                    "Alta eficiencia térmica",
                    "Fácil instalación",
                    "Durabilidad garantizada"
                ]
            },
            {
                "id": "poliestireno",
                "name": "Poliestireno Expandido",
                "description": "Aislante térmico de poliestireno expandido",
                "thicknesses": ["25mm", "50mm", "75mm", "100mm"],
                "features": [
                    "Excelente aislación",
                    "Económico",
                    "Versátil"
                ]
            },
            {
                "id": "lana_roca",
                "name": "Lana de Roca",
                "description": "Aislante térmico y acústico de lana de roca",
                "thicknesses": ["50mm", "75mm", "100mm"],
                "features": [
                    "Aislación térmica y acústica",
                    "Resistente al fuego",
                    "No absorbe humedad"
                ]
            }
        ]
    }

# ============================================================================
# ADMIN ENDPOINTS (Protected - Add authentication in production)
# ============================================================================

@app.get("/api/admin/stats", tags=["Admin"])
async def get_stats():
    """Get system statistics"""
    # TODO: Add authentication
    try:
        from sistema_cotizaciones import SistemaCotizacionesBMC
        sistema = SistemaCotizacionesBMC()
        
        return {
            "total_quotes": len(sistema.cotizaciones),
            "total_products": len(sistema.productos),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"error": str(e)}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return {
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "path": str(request.url),
        "available_endpoints": [
            "/",
            "/health",
            "/docs",
            "/api/chat",
            "/api/quotes",
            "/api/products"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    logger.error(f"Internal error: {exc}", exc_info=True)
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "details": str(exc) if os.getenv("DEBUG") else "Contact support"
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "sistema_completo_integrado:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
