# Google Cloud Architecture Framework - Guía de Implementación Práctica

## Introducción

Esta guía proporciona código y configuraciones listas para implementar las mejoras recomendadas basadas en el Google Cloud Architecture Framework. Todos los ejemplos están diseñados para integrarse directamente con la arquitectura actual del chatbot BMC Uruguay.

---

## 1. Mejoras de Seguridad Inmediatas

### 1.1 Rate Limiting Implementation

Agregar al `requirements.txt`:
```
slowapi==0.1.9
```

Crear archivo `middleware/rate_limiter.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limiter Middleware
Implementa límites de tasa según Google Cloud best practices
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
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
    strategy="fixed-window"  # or "moving-window" for stricter limits
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
            "retry_after": exc.detail,
            "documentation": "https://bmcuruguay.com.uy/api/docs"
        },
        headers={"Retry-After": str(60)}  # Retry after 60 seconds
    )


def setup_rate_limiting(app: FastAPI):
    """Configurar rate limiting en la aplicación"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting configurado correctamente")
```

### 1.2 Input Validation Enhancement

Crear archivo `models/validators.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validadores de entrada mejorados
Implementa validación robusta según Google Cloud security best practices
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List
import re
import html

# Patrones de validación
PHONE_PATTERN = re.compile(r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{4,6}$')
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')
PRODUCT_CODES = {'isodec', 'poliestireno', 'lana_roca', 'poliuretano', 'fibra_vidrio'}
THICKNESS_VALUES = {'25mm', '50mm', '75mm', '100mm', '125mm', '150mm'}


def sanitize_string(value: str, max_length: int = 2000) -> str:
    """Sanitizar string removiendo contenido potencialmente peligroso"""
    if not value:
        return value
    
    # Escapar HTML
    value = html.escape(value)
    
    # Remover caracteres de control (excepto newlines y tabs)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
    
    # Limitar longitud
    value = value[:max_length]
    
    return value.strip()


class SecureChatMessage(BaseModel):
    """Modelo de mensaje de chat con validación de seguridad"""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensaje del usuario"
    )
    session_id: Optional[str] = Field(
        None,
        max_length=128,
        description="Identificador de sesión"
    )
    
    @validator('message', pre=True)
    def sanitize_message(cls, v):
        if not isinstance(v, str):
            raise ValueError('El mensaje debe ser texto')
        
        v = sanitize_string(v, max_length=2000)
        
        if not v:
            raise ValueError('El mensaje no puede estar vacío')
        
        # Detectar patrones sospechosos (inyección básica)
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'onload=',
            r'onerror='
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Mensaje contiene contenido no permitido')
        
        return v
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v is None:
            return v
        
        if not SESSION_ID_PATTERN.match(v):
            raise ValueError('session_id contiene caracteres no permitidos')
        
        return v


class SecureQuoteRequest(BaseModel):
    """Modelo de solicitud de cotización con validación de seguridad"""
    
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre completo del cliente"
    )
    phone: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Número de teléfono"
    )
    product: str = Field(
        ...,
        description="Tipo de producto"
    )
    thickness: str = Field(
        ...,
        description="Espesor del producto"
    )
    length: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Largo en metros"
    )
    width: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Ancho en metros"
    )
    address: Optional[str] = Field(
        None,
        max_length=200,
        description="Dirección de entrega"
    )
    zone: Optional[str] = Field(
        None,
        max_length=50,
        description="Zona"
    )
    observations: Optional[str] = Field(
        None,
        max_length=500,
        description="Observaciones adicionales"
    )
    
    @validator('customer_name', pre=True)
    def sanitize_name(cls, v):
        v = sanitize_string(v, max_length=100)
        
        # Validar que contenga solo caracteres válidos para nombres
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'-]+$', v):
            raise ValueError('El nombre contiene caracteres no válidos')
        
        return v.title()
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remover espacios y caracteres de formato
        v = re.sub(r'[\s\-\.\(\)]', '', v)
        
        if not PHONE_PATTERN.match(v):
            raise ValueError('Formato de teléfono inválido')
        
        return v
    
    @validator('product')
    def validate_product(cls, v):
        v = v.lower().strip()
        if v not in PRODUCT_CODES:
            raise ValueError(
                f'Producto no válido. Opciones: {", ".join(PRODUCT_CODES)}'
            )
        return v
    
    @validator('thickness')
    def validate_thickness(cls, v):
        v = v.lower().strip()
        if v not in THICKNESS_VALUES:
            raise ValueError(
                f'Espesor no válido. Opciones: {", ".join(sorted(THICKNESS_VALUES))}'
            )
        return v
    
    @validator('address', 'zone', 'observations', pre=True)
    def sanitize_optional_fields(cls, v):
        if v is None:
            return v
        return sanitize_string(v)
    
    @root_validator
    def validate_dimensions(cls, values):
        """Validar que las dimensiones sean razonables"""
        length = values.get('length', 0)
        width = values.get('width', 0)
        
        area = length * width
        if area > 10000:  # Máximo 10,000 m²
            raise ValueError('El área total excede el máximo permitido (10,000 m²)')
        
        return values
```

---

## 2. Mejoras de Observabilidad

### 2.1 Structured Logging

Crear archivo `utils/structured_logging.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging estructurado compatible con Google Cloud Logging
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
import os


class StructuredFormatter(logging.Formatter):
    """
    Formatter que genera logs en formato JSON estructurado
    Compatible con Google Cloud Logging
    """
    
    SEVERITY_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL"
    }
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": self.SEVERITY_MAP.get(record.levelno, "DEFAULT"),
            "message": record.getMessage(),
            "logger": record.name,
            "sourceLocation": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stackTrace": traceback.format_exception(*record.exc_info)
            }
        
        # Agregar contexto adicional
        for attr in ['request_id', 'session_id', 'user_id', 'endpoint', 'method', 
                     'latency_ms', 'status_code', 'error_type']:
            if hasattr(record, attr):
                log_entry[attr] = getattr(record, attr)
        
        # Agregar campos extra
        if hasattr(record, 'extra_fields') and isinstance(record.extra_fields, dict):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, default=str)


class ContextualLogger(logging.LoggerAdapter):
    """
    Logger adapter que permite agregar contexto a los logs
    """
    
    def process(self, msg, kwargs):
        # Agregar contexto extra al mensaje
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs


def setup_structured_logging(
    level: str = "INFO",
    service_name: str = "bmc-chatbot",
    environment: str = None
) -> logging.Logger:
    """
    Configurar logging estructurado
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Nombre del servicio
        environment: Entorno (development, staging, production)
    
    Returns:
        Logger configurado
    """
    environment = environment or os.getenv("ENVIRONMENT", "production")
    
    # Crear handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Usar formato estructurado en producción, formato legible en desarrollo
    if environment == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    # Configurar logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers = [handler]
    
    # Logger específico del servicio
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def get_contextual_logger(
    name: str,
    request_id: str = None,
    session_id: str = None,
    user_id: str = None
) -> ContextualLogger:
    """
    Obtener logger con contexto
    
    Args:
        name: Nombre del logger
        request_id: ID de la request
        session_id: ID de sesión
        user_id: ID de usuario
    
    Returns:
        Logger con contexto
    """
    logger = logging.getLogger(name)
    extra = {}
    
    if request_id:
        extra['request_id'] = request_id
    if session_id:
        extra['session_id'] = session_id
    if user_id:
        extra['user_id'] = user_id
    
    return ContextualLogger(logger, extra)


# Ejemplo de uso
if __name__ == "__main__":
    # Setup
    logger = setup_structured_logging(
        level="DEBUG",
        service_name="bmc-chatbot",
        environment="development"
    )
    
    # Log básico
    logger.info("Aplicación iniciada")
    
    # Log con contexto
    ctx_logger = get_contextual_logger(
        "chat_handler",
        request_id="req-123",
        session_id="sess-456"
    )
    ctx_logger.info("Procesando mensaje de chat")
    
    # Log con error
    try:
        raise ValueError("Error de ejemplo")
    except Exception:
        logger.exception("Error procesando solicitud")
```

### 2.2 Request Metrics Middleware

Crear archivo `middleware/metrics.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de métricas para FastAPI
Implementa las Four Golden Signals de Google SRE
"""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Métricas en memoria (en producción usar Prometheus o Cloud Monitoring)
class MetricsCollector:
    def __init__(self):
        self.request_count = {}
        self.error_count = {}
        self.latency_sum = {}
        self.latency_count = {}
        self.active_requests = 0
    
    def record_request(self, endpoint: str, method: str, status: int, latency: float):
        key = f"{method}:{endpoint}"
        
        # Request count
        if key not in self.request_count:
            self.request_count[key] = {}
        status_key = str(status)
        self.request_count[key][status_key] = self.request_count[key].get(status_key, 0) + 1
        
        # Latency
        if key not in self.latency_sum:
            self.latency_sum[key] = 0
            self.latency_count[key] = 0
        self.latency_sum[key] += latency
        self.latency_count[key] += 1
        
        # Error count
        if status >= 400:
            self.error_count[key] = self.error_count.get(key, 0) + 1
    
    def get_metrics(self) -> dict:
        metrics = {
            "requests": self.request_count,
            "errors": self.error_count,
            "latency_avg": {},
            "active_requests": self.active_requests
        }
        
        for key in self.latency_count:
            if self.latency_count[key] > 0:
                metrics["latency_avg"][key] = (
                    self.latency_sum[key] / self.latency_count[key]
                )
        
        return metrics


# Instancia global
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para recolectar métricas de requests"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        metrics_collector.active_requests += 1
        
        try:
            response = await call_next(request)
            
            # Calcular latencia
            latency = (time.perf_counter() - start_time) * 1000  # ms
            
            # Registrar métricas
            metrics_collector.record_request(
                endpoint=request.url.path,
                method=request.method,
                status=response.status_code,
                latency=latency
            )
            
            # Agregar headers de timing
            response.headers["X-Response-Time"] = f"{latency:.2f}ms"
            
            # Log estructurado
            logger.info(
                f"Request completed",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency_ms": round(latency, 2),
                    "client_ip": request.client.host if request.client else "unknown"
                }
            )
            
            return response
            
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000
            
            metrics_collector.record_request(
                endpoint=request.url.path,
                method=request.method,
                status=500,
                latency=latency
            )
            
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                    "latency_ms": round(latency, 2)
                }
            )
            raise
            
        finally:
            metrics_collector.active_requests -= 1


def setup_metrics(app: FastAPI):
    """Configurar métricas en la aplicación"""
    app.add_middleware(MetricsMiddleware)
    
    @app.get("/metrics", tags=["Monitoring"])
    async def get_metrics():
        """Endpoint de métricas (estilo Prometheus)"""
        return metrics_collector.get_metrics()
    
    logger.info("Métricas configuradas correctamente")
```

---

## 3. Mejoras de Fiabilidad

### 3.1 Circuit Breaker Implementation

Crear archivo `utils/circuit_breaker.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Pattern Implementation
Protege el sistema de fallos en cascada
"""

import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerError(Exception):
    """Excepción cuando el circuit breaker está abierto"""
    pass


class CircuitBreaker:
    """
    Circuit Breaker para proteger llamadas a servicios externos
    
    Estados:
    - CLOSED: Normal, las llamadas pasan
    - OPEN: Servicio fallando, rechaza llamadas inmediatamente
    - HALF_OPEN: Probando si el servicio se recuperó
    """
    
    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0,
        expected_exceptions: tuple = (Exception,)
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exceptions = expected_exceptions
        
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    async def _transition_to(self, new_state: CircuitState):
        """Transicionar a nuevo estado"""
        old_state = self._state
        self._state = new_state
        
        logger.info(
            f"Circuit breaker '{self.name}' transitioned: {old_state.value} -> {new_state.value}"
        )
        
        if new_state == CircuitState.CLOSED:
            self._failures = 0
            self._successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._successes = 0
    
    async def _handle_success(self):
        """Manejar llamada exitosa"""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._successes += 1
                if self._successes >= self.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._failures = 0
    
    async def _handle_failure(self):
        """Manejar fallo"""
        async with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failures >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)
    
    async def _should_allow(self) -> bool:
        """Verificar si se debe permitir la llamada"""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                # Verificar si ya pasó el timeout
                if (self._last_failure_time and 
                    time.time() - self._last_failure_time >= self.timeout):
                    await self._transition_to(CircuitState.HALF_OPEN)
                    return True
                return False
            
            # HALF_OPEN - permitir llamadas de prueba
            return True
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecutar función a través del circuit breaker"""
        if not await self._should_allow():
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
            )
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._handle_success()
            return result
        except self.expected_exceptions as e:
            await self._handle_failure()
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator para usar circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
    
    def get_status(self) -> dict:
        """Obtener estado actual del circuit breaker"""
        return {
            "name": self.name,
            "state": self._state.value,
            "failures": self._failures,
            "successes": self._successes,
            "last_failure": self._last_failure_time
        }


# Circuit breakers preconfigurados
openai_circuit = CircuitBreaker(
    name="openai",
    failure_threshold=3,
    success_threshold=2,
    timeout=60.0
)

mongodb_circuit = CircuitBreaker(
    name="mongodb",
    failure_threshold=5,
    success_threshold=3,
    timeout=30.0
)

whatsapp_circuit = CircuitBreaker(
    name="whatsapp",
    failure_threshold=5,
    success_threshold=2,
    timeout=120.0
)


# Ejemplo de uso
@openai_circuit
async def call_openai_with_circuit_breaker(prompt: str) -> str:
    """Llamada a OpenAI protegida por circuit breaker"""
    # Implementación real aquí
    pass
```

### 3.2 Retry with Exponential Backoff

Crear archivo `utils/retry.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry con Exponential Backoff
"""

import asyncio
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RetryExhausted(Exception):
    """Todos los reintentos agotados"""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator para reintentar funciones con exponential backoff
    
    Args:
        max_retries: Número máximo de reintentos
        base_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        exponential_base: Base para el cálculo exponencial
        jitter: Agregar variación aleatoria al delay
        retry_exceptions: Excepciones que disparan reintento
        on_retry: Callback llamado en cada reintento
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                        
                except retry_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Retry exhausted for {func.__name__} after {max_retries + 1} attempts",
                            extra={
                                "function": func.__name__,
                                "attempts": max_retries + 1,
                                "error": str(e)
                            }
                        )
                        break
                    
                    # Calcular delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        delay *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s...",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_attempts": max_retries + 1,
                            "delay_seconds": delay,
                            "error": str(e)
                        }
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    await asyncio.sleep(delay)
            
            raise RetryExhausted(
                f"Function {func.__name__} failed after {max_retries + 1} attempts"
            ) from last_exception
        
        return wrapper
    return decorator


# Configuraciones predefinidas
def retry_for_api_calls(func):
    """Configuración de retry para llamadas a APIs externas"""
    return retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        retry_exceptions=(ConnectionError, TimeoutError, Exception)
    )(func)


def retry_for_database(func):
    """Configuración de retry para operaciones de base de datos"""
    return retry_with_backoff(
        max_retries=2,
        base_delay=0.5,
        max_delay=10.0,
        retry_exceptions=(ConnectionError, TimeoutError)
    )(func)


# Ejemplo de uso
@retry_with_backoff(max_retries=3, base_delay=1.0)
async def fetch_data_from_api(url: str) -> dict:
    """Ejemplo de función con retry"""
    # Implementación
    pass
```

---

## 4. Cómo Integrar

### 4.1 Modificar `sistema_completo_integrado.py`

Agregar al inicio del archivo:

```python
# Importar mejoras
from middleware.rate_limiter import setup_rate_limiting, limiter
from middleware.metrics import setup_metrics
from models.validators import SecureChatMessage, SecureQuoteRequest
from utils.structured_logging import setup_structured_logging
from utils.circuit_breaker import openai_circuit, CircuitBreakerError

# Configurar logging estructurado
logger = setup_structured_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    service_name="bmc-chatbot",
    environment=os.getenv("ENVIRONMENT", "production")
)

# Después de crear la app FastAPI, agregar:
setup_rate_limiting(app)
setup_metrics(app)
```

### 4.2 Actualizar Endpoint de Chat

```python
from middleware.rate_limiter import limiter

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit("30/minute")
async def chat(request: Request, message: SecureChatMessage):
    """Endpoint de chat con rate limiting y validación mejorada"""
    try:
        # Usar circuit breaker para OpenAI
        try:
            response_text = await openai_circuit.call(
                procesar_mensaje_usuario,
                message.message,
                message.session_id
            )
        except CircuitBreakerError:
            logger.warning("OpenAI circuit breaker open, using fallback")
            response_text = "Disculpa, estoy teniendo problemas técnicos. Por favor, intenta más tarde."
        
        return ChatResponse(
            response=response_text,
            session_id=message.session_id or "default"
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 5. Variables de Entorno Recomendadas

Agregar a `.env.example`:

```bash
# Configuración de entorno
ENVIRONMENT=production
LOG_LEVEL=INFO

# Rate Limiting
REDIS_URL=redis://localhost:6379
RATE_LIMIT_DEFAULT=100/minute

# Circuit Breaker
OPENAI_CIRCUIT_FAILURE_THRESHOLD=3
OPENAI_CIRCUIT_TIMEOUT=60

# Google Cloud (opcional para producción)
GOOGLE_CLOUD_PROJECT=bmc-uruguay-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

---

## Próximos Pasos

1. **Instalar dependencias adicionales**:
   ```bash
   pip install slowapi aiocache prometheus-client
   ```

2. **Crear estructura de directorios**:
   ```bash
   mkdir -p middleware models utils
   touch middleware/__init__.py models/__init__.py utils/__init__.py
   ```

3. **Copiar los archivos de esta guía** a sus respectivas ubicaciones

4. **Actualizar imports** en el archivo principal

5. **Probar en desarrollo** antes de desplegar a producción

---

**Documento creado**: Diciembre 2024  
**Basado en**: Google Cloud Architecture Framework  
**Versión**: 1.0
