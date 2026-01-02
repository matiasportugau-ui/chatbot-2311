#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor API Client
Cliente base para interactuar con las APIs de Cursor
Implementa mejores prácticas: autenticación, rate limiting, caché, manejo de errores
"""

import os
import base64
import time
import random
import logging
import json
from typing import Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CursorAPIError(Exception):
    """Error base para APIs de Cursor"""
    pass


class RateLimitError(CursorAPIError):
    """Error de rate limit"""
    pass


class AuthenticationError(CursorAPIError):
    """Error de autenticación"""
    pass


class PermissionError(CursorAPIError):
    """Error de permisos"""
    pass


@dataclass
class APIRequest:
    """Información de una solicitud a la API"""
    method: str
    endpoint: str
    status_code: int
    response_time: float
    timestamp: datetime
    cached: bool = False
    retries: int = 0


class RateLimitHandler:
    """Maneja rate limits con backoff exponencial"""
    
    def __init__(self, max_retries: int = 5):
        self.max_retries = max_retries
    
    def with_backoff(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Ejecuta función con backoff exponencial"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise
                
                # Backoff exponencial con jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Rate limit alcanzado. Esperando {wait_time:.2f}s "
                    f"(intento {attempt + 1}/{self.max_retries})"
                )
                time.sleep(wait_time)
        
        raise Exception("Máximo de reintentos alcanzado")


class ETagCache:
    """Maneja caché con ETags para reducir solicitudes"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
    
    def get_etag(self, endpoint: str) -> Optional[str]:
        """Obtiene ETag guardado para endpoint"""
        if endpoint in self.cache:
            return self.cache[endpoint].get("etag")
        return None
    
    def should_refresh(
        self, 
        endpoint: str, 
        max_age_minutes: int = 15
    ) -> bool:
        """Determina si necesita refrescar datos"""
        if endpoint not in self.cache:
            return True
        
        cached_time = self.cache[endpoint].get("timestamp")
        if not cached_time:
            return True
        
        if isinstance(cached_time, str):
            cached_time = datetime.fromisoformat(cached_time)
        
        age = (datetime.now() - cached_time).total_seconds() / 60
        return age > max_age_minutes
    
    def get_cached_data(self, endpoint: str) -> Optional[Dict]:
        """Obtiene datos del caché si están disponibles"""
        if endpoint in self.cache and not self.should_refresh(endpoint):
            return self.cache[endpoint].get("data")
        return None
    
    def store_data(
        self, 
        endpoint: str, 
        data: Dict, 
        etag: Optional[str] = None
    ):
        """Almacena datos en caché"""
        self.cache[endpoint] = {
            "data": data,
            "etag": etag,
            "timestamp": datetime.now()
        }


class RequestScheduler:
    """Distribuye solicitudes en el tiempo para evitar rate limits"""
    
    def __init__(self, requests_per_minute: int = 15):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    def schedule_request(self, func: Callable, *args, **kwargs):
        """Programa solicitud respetando límites de tasa"""
        now = datetime.now()
        
        # Limpiar solicitudes antiguas (más de 1 minuto)
        self.request_times = [
            t for t in self.request_times 
            if now - t < timedelta(minutes=1)
        ]
        
        # Si estamos al límite, esperar
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = min(self.request_times)
            wait_until = oldest_request + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                logger.info(
                    f"Esperando {wait_seconds:.2f}s para respetar rate limit"
                )
                time.sleep(wait_seconds)
        
        # Registrar solicitud
        self.request_times.append(datetime.now())
        
        # Ejecutar solicitud
        return func(*args, **kwargs)


class CursorAPIClient:
    """
    Cliente para interactuar con las APIs de Cursor
    Implementa mejores prácticas de uso de API
    """
    
    BASE_URL = "https://api.cursor.com"
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        enable_rate_limiting: bool = True
    ):
        """
        Inicializa cliente de Cursor API
        
        Args:
            api_key: Clave de API de Cursor (o usa CURSOR_API_KEY env var)
            enable_cache: Habilita caché con ETags
            enable_rate_limiting: Habilita rate limiting automático
        """
        self.api_key = api_key or os.getenv("CURSOR_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CURSOR_API_KEY no encontrada. "
                "Configura la variable de entorno o pásala como parámetro."
            )
        
        # Configurar autenticación
        credentials = f"{self.api_key}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
        
        # Configurar componentes
        self.cache = ETagCache() if enable_cache else None
        self.rate_limit_handler = RateLimitHandler()
        self.scheduler = RequestScheduler() if enable_rate_limiting else None
        
        # Configurar sesión HTTP con retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Historial de solicitudes
        self.request_history: list[APIRequest] = []
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Realiza solicitud a la API con manejo de errores
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API (ej: /analytics/team/dau)
            params: Parámetros de query
            data: Datos del body (para POST/PUT)
            use_cache: Usar caché si está disponible
        
        Returns:
            Respuesta de la API como diccionario
        
        Raises:
            AuthenticationError: Si la autenticación falla
            RateLimitError: Si se excede el rate limit
            CursorAPIError: Para otros errores de API
        """
        url = f"{self.BASE_URL}{endpoint}"
        start_time = time.time()
        
        # Verificar caché para GET requests
        if method == "GET" and use_cache and self.cache:
            cached_data = self.cache.get_cached_data(endpoint)
            if cached_data:
                logger.debug(f"Usando datos en caché para {endpoint}")
                response_time = time.time() - start_time
                self._log_request(method, endpoint, 200, response_time, cached=True)
                return cached_data
        
        # Preparar headers con ETag si existe
        headers = self.headers.copy()
        if method == "GET" and use_cache and self.cache:
            etag = self.cache.get_etag(endpoint)
            if etag:
                headers["If-None-Match"] = etag
        
        # Realizar solicitud
        try:
            if self.scheduler:
                response = self.scheduler.schedule_request(
                    self.session.request,
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=30
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=30
                )
            
            response_time = time.time() - start_time
            
            # Manejar respuesta
            return self._handle_response(
                response, 
                endpoint, 
                method, 
                response_time
            )
        
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.error(f"Error en solicitud a {endpoint}: {e}")
            raise CursorAPIError(f"Error de conexión: {e}")
    
    def _handle_response(
        self,
        response: requests.Response,
        endpoint: str,
        method: str,
        response_time: float
    ) -> Dict[str, Any]:
        """Maneja respuesta de la API"""
        status_code = response.status_code
        
        # Log de solicitud
        cached = False
        
        if status_code == 200:
            data = response.json()
            
            # Guardar en caché si tiene ETag
            if method == "GET" and self.cache:
                etag = response.headers.get("ETag")
                if etag:
                    self.cache.store_data(endpoint, data, etag)
            
            self._log_request(method, endpoint, status_code, response_time, cached)
            return data
        
        elif status_code == 304:
            # Not Modified - usar caché
            cached_data = self.cache.get_cached_data(endpoint) if self.cache else None
            if cached_data:
                self._log_request(method, endpoint, status_code, response_time, cached=True)
                return cached_data
            else:
                raise CursorAPIError("304 Not Modified pero no hay datos en caché")
        
        elif status_code == 400:
            error_data = response.json() if response.content else {}
            message = error_data.get("message", "Solicitud inválida")
            logger.error(f"400 Bad Request en {endpoint}: {message}")
            raise ValueError(f"Solicitud inválida: {message}")
        
        elif status_code == 401:
            logger.error(f"401 Unauthorized en {endpoint}")
            raise AuthenticationError("Clave de API inválida o ausente")
        
        elif status_code == 403:
            logger.error(f"403 Forbidden en {endpoint}")
            raise PermissionError(
                "Permisos insuficientes. Se requiere acceso Enterprise."
            )
        
        elif status_code == 404:
            logger.error(f"404 Not Found: {endpoint}")
            raise ValueError(f"Recurso no encontrado: {endpoint}")
        
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            logger.warning(f"429 Rate Limit en {endpoint}. Retry-After: {retry_after}s")
            raise RateLimitError(
                f"Límite de velocidad excedido. Reintentar después de {retry_after}s"
            )
        
        elif status_code >= 500:
            logger.error(f"Error del servidor ({status_code}) en {endpoint}")
            raise CursorAPIError(
                f"Error interno del servidor: {status_code}"
            )
        
        else:
            logger.error(f"Error desconocido ({status_code}) en {endpoint}")
            raise CursorAPIError(
                f"Error desconocido: {status_code}"
            )
    
    def _log_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        cached: bool = False
    ):
        """Registra solicitud para análisis"""
        request = APIRequest(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            timestamp=datetime.now(),
            cached=cached
        )
        self.request_history.append(request)
        
        # Mantener solo últimos 1000 requests
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        # Log estructurado
        log_data = {
            "timestamp": request.timestamp.isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
            "cached": cached
        }
        logger.info(f"API Request: {json.dumps(log_data)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza solicitud GET"""
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza solicitud POST"""
        return self._make_request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Realiza solicitud PUT"""
        return self._make_request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza solicitud DELETE"""
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de solicitudes"""
        if not self.request_history:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "cached_requests": 0,
                "error_rate": 0
            }
        
        total = len(self.request_history)
        cached = sum(1 for r in self.request_history if r.cached)
        errors = sum(1 for r in self.request_history if r.status_code >= 400)
        avg_time = sum(r.response_time for r in self.request_history) / total
        
        return {
            "total_requests": total,
            "avg_response_time_ms": avg_time * 1000,
            "cached_requests": cached,
            "cache_hit_rate": cached / total if total > 0 else 0,
            "error_rate": errors / total if total > 0 else 0,
            "requests_by_status": {
                str(r.status_code): sum(
                    1 for req in self.request_history 
                    if req.status_code == r.status_code
                )
                for r in self.request_history
            }
        }


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar cliente
    client = CursorAPIClient()
    
    # Ejemplo: Obtener usuarios activos diarios
    try:
        response = client.get(
            "/analytics/team/dau",
            params={"start_date": "7d", "end_date": "today"}
        )
        print("DAU Response:", json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # Mostrar estadísticas
    stats = client.get_request_stats()
    print("\nRequest Stats:", json.dumps(stats, indent=2))


