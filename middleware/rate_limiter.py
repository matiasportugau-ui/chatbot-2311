#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiter Middleware
Implementa límites de tasa según Google Cloud best practices

Based on Google Cloud Architecture Framework security recommendations
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
import os
import logging

logger = logging.getLogger(__name__)

# Configuración de límites por entorno
RATE_LIMITS = {
    "development": {
        "chat": "100/minute",
        "quotes": "50/minute",
        "products": "200/minute",
        "admin": "30/minute",
        "default": "1000/minute"
    },
    "production": {
        "chat": "30/minute",
        "quotes": "10/minute",
        "products": "60/minute",
        "admin": "10/minute",
        "default": "100/minute"
    }
}


def get_rate_limits():
    """Obtener límites según entorno"""
    env = os.getenv("ENVIRONMENT", "production")
    return RATE_LIMITS.get(env, RATE_LIMITS["production"])


def get_client_identifier(request: Request) -> str:
    """
    Identificador de cliente para rate limiting
    Usa API key si está presente, sino IP
    
    Supports:
    - X-API-Key header
    - X-Forwarded-For (for proxied requests)
    - Direct client IP
    """
    # Verificar si hay API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key[:8]}"
    
    # Usar IP (considerando proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    return get_remote_address(request)


# Inicializar limiter
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=["100/minute"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
    strategy="fixed-window"
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler personalizado para límite excedido"""
    logger.warning(
        f"Rate limit exceeded for {get_client_identifier(request)} "
        f"on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "message": "Has excedido el límite de solicitudes. Por favor, espera un momento.",
            "retry_after": str(exc.detail) if hasattr(exc, 'detail') else "60 seconds",
            "documentation": "https://bmcuruguay.com.uy/api/docs"
        },
        headers={"Retry-After": str(60)}
    )


def setup_rate_limiting(app: FastAPI):
    """
    Configurar rate limiting en la aplicación FastAPI
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    logger.info("✅ Rate limiting configurado correctamente")
