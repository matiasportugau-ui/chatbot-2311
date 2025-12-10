# Google Cloud Architecture Framework - Mejoras y Sugerencias para el Chatbot BMC Uruguay

## Resumen Ejecutivo

Este documento presenta un análisis exhaustivo basado en el **Google Cloud Architecture Framework** (también conocido como Well-Architected Framework) para mejorar el chatbot de cotizaciones de BMC Uruguay. Las recomendaciones cubren los seis pilares fundamentales del framework:

1. **Diseño del Sistema** (System Design)
2. **Excelencia Operacional** (Operational Excellence)
3. **Seguridad** (Security)
4. **Fiabilidad** (Reliability)
5. **Optimización de Costos** (Cost Optimization)
6. **Optimización del Rendimiento** (Performance Optimization)

---

## 📐 1. Diseño del Sistema (System Design)

### Estado Actual
El sistema actual tiene una arquitectura modular con:
- FastAPI para la API REST
- Integración con OpenAI para IA conversacional
- MongoDB para persistencia
- Sistema de cotizaciones Python independiente

### Mejoras Recomendadas

#### 1.1 Arquitectura de Microservicios
```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer               │
│              (Google Cloud API Gateway / Cloud Armor)        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Chat Service │   │ Quote Service │   │ Product Service│
│   (FastAPI)   │   │   (FastAPI)   │   │   (FastAPI)    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Message Queue   │
                    │ (Pub/Sub / Redis) │
                    └───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   MongoDB     │   │  Cloud Storage │   │  Firestore    │
│  (Cotizaciones)│  │    (Archivos)  │   │   (Sessions)  │
└───────────────┘   └───────────────┘   └───────────────┘
```

#### 1.2 Principios de Diseño Recomendados

| Principio | Implementación Sugerida | Prioridad |
|-----------|------------------------|-----------|
| Desacoplamiento | Separar servicios de chat, cotizaciones y productos | Alta |
| Stateless | Externalizar estado de sesión a Redis/Firestore | Alta |
| API-First | Documentar todas las APIs con OpenAPI/Swagger | Media |
| Event-Driven | Implementar eventos para actualizaciones asíncronas | Media |

#### 1.3 Integración con Vertex AI y Dialogflow

**Recomendación**: Migrar gradualmente de OpenAI a **Vertex AI** o integrar **Dialogflow CX** para:
- Mayor control sobre datos empresariales
- Cumplimiento de regulaciones locales
- Integración nativa con servicios de Google Cloud
- Reducción de latencia en la región

```python
# Ejemplo de integración con Vertex AI
from google.cloud import aiplatform

def initialize_vertex_ai():
    aiplatform.init(
        project="bmc-uruguay-project",
        location="southamerica-east1"  # São Paulo - más cercano a Uruguay
    )

def get_ai_response(prompt: str, context: dict) -> str:
    """
    Obtener respuesta usando Vertex AI Generative AI
    """
    from vertexai.preview.generative_models import GenerativeModel
    
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f"Contexto: {context}\n\nConsulta: {prompt}"
    )
    return response.text
```

---

## 🔐 2. Seguridad (Security)

### Estado Actual
El sistema tiene configuración básica de:
- CORS habilitado
- Variables de entorno para credenciales
- Logging básico

### Mejoras Críticas de Seguridad

#### 2.1 Autenticación y Autorización

**Problema Actual**: Los endpoints `/api/admin/*` no tienen autenticación.

**Solución Recomendada**:

```python
# Implementar autenticación JWT con Google Identity Platform
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT de Google Identity Platform"""
    try:
        idinfo = id_token.verify_oauth2_token(
            credentials.credentials,
            requests.Request(),
            audience="YOUR_CLIENT_ID"
        )
        return idinfo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Aplicar a endpoints protegidos
@app.get("/api/admin/stats", tags=["Admin"])
async def get_stats(user: dict = Depends(verify_token)):
    # Solo usuarios autenticados pueden acceder
    pass
```

#### 2.2 Rate Limiting

**Implementar límites de tasa para prevenir abuso**:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Aplicar límites por endpoint
@app.post("/api/chat")
@limiter.limit("30/minute")  # 30 mensajes por minuto por IP
async def chat(request: Request, message: ChatMessage):
    pass

@app.post("/api/quotes")
@limiter.limit("10/minute")  # 10 cotizaciones por minuto por IP
async def create_quote(request: Request, quote: QuoteRequest):
    pass
```

#### 2.3 Validación de Entrada Mejorada

```python
from pydantic import BaseModel, Field, validator
import re

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, max_length=100)
    
    @validator('message')
    def sanitize_message(cls, v):
        # Remover caracteres potencialmente peligrosos
        v = re.sub(r'<[^>]*>', '', v)  # Remover HTML tags
        v = v.strip()
        if not v:
            raise ValueError('El mensaje no puede estar vacío')
        return v
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('session_id contiene caracteres inválidos')
        return v
```

#### 2.4 Gestión Segura de Secretos

**Migrar a Google Cloud Secret Manager**:

```python
from google.cloud import secretmanager

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """Obtener secreto desde Google Cloud Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/bmc-uruguay-project/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Uso
OPENAI_API_KEY = get_secret("openai-api-key")
MONGODB_URI = get_secret("mongodb-uri")
WHATSAPP_TOKEN = get_secret("whatsapp-token")
```

#### 2.5 Checklist de Seguridad

- [ ] Implementar autenticación JWT para endpoints administrativos
- [ ] Agregar rate limiting a todos los endpoints públicos
- [ ] Migrar secretos a Google Cloud Secret Manager
- [ ] Habilitar Cloud Armor para protección WAF
- [ ] Implementar validación de entrada robusta
- [ ] Configurar VPC Service Controls para datos sensibles
- [ ] Habilitar audit logging para todas las operaciones
- [ ] Implementar rotación automática de claves API

---

## 📊 3. Excelencia Operacional (Operational Excellence)

### 3.1 Observabilidad - Las Cuatro Señales Doradas

Implementar monitoreo de las **Four Golden Signals**:

```python
# metrics.py - Implementación con Prometheus
from prometheus_client import Counter, Histogram, Gauge
import time

# 1. LATENCIA - Tiempo de respuesta
request_latency = Histogram(
    'bmc_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'method'],
    buckets=[.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0]
)

# 2. TRÁFICO - Volumen de requests
request_count = Counter(
    'bmc_requests_total',
    'Total request count',
    ['endpoint', 'method', 'status']
)

# 3. ERRORES - Tasa de errores
error_count = Counter(
    'bmc_errors_total',
    'Total error count',
    ['endpoint', 'error_type']
)

# 4. SATURACIÓN - Uso de recursos
active_connections = Gauge(
    'bmc_active_connections',
    'Number of active connections'
)

# Middleware para métricas automáticas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    active_connections.inc()
    
    try:
        response = await call_next(request)
        
        # Registrar latencia
        request_latency.labels(
            endpoint=request.url.path,
            method=request.method
        ).observe(time.time() - start_time)
        
        # Registrar request
        request_count.labels(
            endpoint=request.url.path,
            method=request.method,
            status=response.status_code
        ).inc()
        
        return response
        
    except Exception as e:
        error_count.labels(
            endpoint=request.url.path,
            error_type=type(e).__name__
        ).inc()
        raise
    finally:
        active_connections.dec()
```

### 3.2 Logging Estructurado

```python
# structured_logging.py
import logging
import json
from datetime import datetime
from google.cloud import logging as gcp_logging

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estructurados compatible con Google Cloud Logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "source_location": {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName
            }
        }
        
        # Agregar contexto adicional si existe
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
            
        return json.dumps(log_entry)

def setup_logging():
    """Configurar logging para Google Cloud"""
    # Para producción en GCP
    if os.getenv("ENVIRONMENT") == "production":
        client = gcp_logging.Client()
        client.setup_logging()
    else:
        # Para desarrollo local
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)
```

### 3.3 Trazabilidad Distribuida

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app):
    """Configurar trazabilidad con Google Cloud Trace"""
    tracer_provider = TracerProvider()
    cloud_trace_exporter = CloudTraceSpanExporter(
        project_id="bmc-uruguay-project"
    )
    tracer_provider.add_span_processor(
        BatchSpanProcessor(cloud_trace_exporter)
    )
    trace.set_tracer_provider(tracer_provider)
    
    # Instrumentar FastAPI automáticamente
    FastAPIInstrumentor.instrument_app(app)

# Uso en código
tracer = trace.get_tracer(__name__)

async def process_chat_message(message: str, session_id: str):
    with tracer.start_as_current_span("process_chat_message") as span:
        span.set_attribute("session_id", session_id)
        span.set_attribute("message_length", len(message))
        
        # Procesar mensaje...
        response = await generate_ai_response(message)
        
        span.set_attribute("response_length", len(response))
        return response
```

### 3.4 Dashboard de Monitoreo Recomendado

Crear dashboards en Google Cloud Monitoring con:

| Panel | Métricas | Alertas |
|-------|----------|---------|
| Latencia de Chat | P50, P95, P99 latencia | > 2s en P95 |
| Tasa de Errores | % errores por endpoint | > 1% errores |
| Uso de API OpenAI | Tokens usados, costos | > $50/día |
| Conexiones MongoDB | Conexiones activas, latencia queries | > 90% pool |
| Cotizaciones | Cotizaciones/hora, conversión | Caída > 50% |

---

## 🔄 4. Fiabilidad (Reliability)

### 4.1 Circuit Breaker Pattern

```python
# circuit_breaker.py
from enum import Enum
import time
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Uso
openai_circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

@openai_circuit
async def call_openai_api(prompt: str) -> str:
    """Llamada a OpenAI con circuit breaker"""
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### 4.2 Retry con Backoff Exponencial

```python
# retry.py
import asyncio
from functools import wraps
import random

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        break
                    
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        delay *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

# Uso
@retry_with_backoff(max_retries=3, base_delay=1.0)
async def get_ai_response(message: str) -> str:
    return await call_openai_api(message)
```

### 4.3 Graceful Degradation

```python
# graceful_degradation.py

class ResponseFallback:
    """Sistema de respuestas de fallback cuando falla la IA"""
    
    FALLBACK_RESPONSES = {
        "greeting": "¡Hola! Soy el asistente de BMC Uruguay. En este momento estoy experimentando dificultades técnicas. Por favor, intenta más tarde o contacta a nuestro equipo al +598 XX XXX XXX.",
        "quote_request": "Gracias por tu interés en nuestros productos. Actualmente no puedo generar cotizaciones automáticas. Te invito a contactarnos directamente en info@bmcuruguay.com.uy",
        "product_info": "Información sobre productos disponible en https://bmcuruguay.com.uy/productos",
        "default": "Disculpa, estoy teniendo problemas para procesar tu mensaje. Por favor, intenta más tarde o contacta a nuestro equipo de soporte."
    }
    
    @classmethod
    def get_fallback(cls, intent: str = "default") -> str:
        return cls.FALLBACK_RESPONSES.get(intent, cls.FALLBACK_RESPONSES["default"])

async def process_message_with_fallback(message: str, session_id: str) -> str:
    """Procesar mensaje con fallback graceful"""
    try:
        # Intentar con IA principal
        response = await get_ai_response(message)
        return response
    except CircuitBreakerOpenError:
        logger.warning("Circuit breaker open - using fallback")
        intent = detect_intent(message)
        return ResponseFallback.get_fallback(intent)
    except Exception as e:
        logger.error(f"AI processing failed: {e}")
        return ResponseFallback.get_fallback()
```

### 4.4 Health Checks Mejorados

```python
# health.py
from enum import Enum
from typing import Dict, Any
import asyncio

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

async def check_mongodb() -> Dict[str, Any]:
    """Verificar conexión MongoDB"""
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        return {"status": HealthStatus.HEALTHY, "latency_ms": 0}
    except Exception as e:
        return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

async def check_openai() -> Dict[str, Any]:
    """Verificar disponibilidad OpenAI API"""
    try:
        # Hacer una llamada mínima
        response = await openai_client.models.list()
        return {"status": HealthStatus.HEALTHY}
    except Exception as e:
        return {"status": HealthStatus.UNHEALTHY, "error": str(e)}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Health check detallado con verificación de dependencias"""
    checks = await asyncio.gather(
        check_mongodb(),
        check_openai(),
        return_exceptions=True
    )
    
    mongodb_health, openai_health = checks
    
    overall_status = HealthStatus.HEALTHY
    if any(c.get("status") == HealthStatus.UNHEALTHY for c in checks if isinstance(c, dict)):
        overall_status = HealthStatus.DEGRADED
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "mongodb": mongodb_health,
            "openai": openai_health
        },
        "version": "1.0.0"
    }
```

---

## 💰 5. Optimización de Costos (Cost Optimization)

### 5.1 Optimización de Llamadas a OpenAI

```python
# cost_optimization.py
from functools import lru_cache
import hashlib

class ConversationCache:
    """Cache para respuestas frecuentes y reducir llamadas a OpenAI"""
    
    def __init__(self, redis_client=None, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl
        self.local_cache = {}
    
    def _get_cache_key(self, message: str, context: dict) -> str:
        """Generar clave de cache basada en mensaje y contexto"""
        content = f"{message}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get(self, message: str, context: dict) -> Optional[str]:
        """Obtener respuesta cacheada si existe"""
        key = self._get_cache_key(message, context)
        
        # Intentar cache local primero
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Intentar Redis
        if self.redis:
            cached = await self.redis.get(f"chat:{key}")
            if cached:
                return cached.decode()
        
        return None
    
    async def set(self, message: str, context: dict, response: str):
        """Guardar respuesta en cache"""
        key = self._get_cache_key(message, context)
        
        # Guardar en ambos caches
        self.local_cache[key] = response
        if self.redis:
            await self.redis.setex(f"chat:{key}", self.ttl, response)

# Respuestas predefinidas para consultas comunes (sin costo de API)
PREDEFINED_RESPONSES = {
    "hola": "¡Hola! Soy el asistente de BMC Uruguay. ¿En qué puedo ayudarte hoy?",
    "horarios": "Nuestro horario de atención es de Lunes a Viernes de 8:00 a 18:00.",
    "direccion": "Nuestra dirección es [DIRECCIÓN]. Puedes encontrarnos en el mapa en bmcuruguay.com.uy/contacto",
    "telefono": "Puedes contactarnos al +598 XX XXX XXX",
    "productos": "Ofrecemos Isodec, Poliestireno Expandido y Lana de Roca. ¿Sobre cuál te gustaría más información?",
}

def get_predefined_response(message: str) -> Optional[str]:
    """Obtener respuesta predefinida si existe"""
    normalized = message.lower().strip()
    for keyword, response in PREDEFINED_RESPONSES.items():
        if keyword in normalized:
            return response
    return None
```

### 5.2 Modelo de Precios y Selección Inteligente

```python
# model_selection.py

class ModelSelector:
    """Selección inteligente de modelo según complejidad de la consulta"""
    
    MODELS = {
        "simple": {
            "name": "gpt-4o-mini",
            "cost_per_1k_input": 0.00015,
            "cost_per_1k_output": 0.0006
        },
        "complex": {
            "name": "gpt-4o",
            "cost_per_1k_input": 0.005,
            "cost_per_1k_output": 0.015
        }
    }
    
    COMPLEX_INDICATORS = [
        "cotización", "cotizar", "presupuesto",
        "calcular", "precio", "especificaciones técnicas",
        "comparar", "diferencias", "ventajas"
    ]
    
    @classmethod
    def select_model(cls, message: str) -> dict:
        """Seleccionar modelo óptimo según la consulta"""
        message_lower = message.lower()
        
        # Usar modelo más potente solo para consultas complejas
        for indicator in cls.COMPLEX_INDICATORS:
            if indicator in message_lower:
                return cls.MODELS["complex"]
        
        return cls.MODELS["simple"]
```

### 5.3 Recomendaciones de Infraestructura

| Componente | Opción Económica | Opción Producción | Costo Est./mes |
|------------|------------------|-------------------|----------------|
| Compute | Cloud Run (pay-per-use) | GKE Autopilot | $20-100 |
| Database | MongoDB Atlas M0 (free) | Cloud Firestore | $0-50 |
| Cache | Memorystore Basic | Memorystore Standard | $20-100 |
| AI | Vertex AI (pay-per-use) | OpenAI API | Variable |
| CDN | Cloud CDN | Cloud CDN | $10-30 |

---

## ⚡ 6. Optimización del Rendimiento (Performance Optimization)

### 6.1 Caché Multinivel

```python
# caching.py
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer

# Nivel 1: Cache en memoria (más rápido)
memory_cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

# Nivel 2: Cache Redis (compartido entre instancias)
redis_cache = Cache(
    Cache.REDIS,
    endpoint="redis-host",
    port=6379,
    serializer=JsonSerializer()
)

@cached(
    ttl=300,  # 5 minutos
    cache=Cache.MULTI_LEVEL,
    caches=[memory_cache, redis_cache]
)
async def get_product_info(product_id: str) -> dict:
    """Obtener información de producto con cache multinivel"""
    # Buscar en base de datos
    return await db.products.find_one({"id": product_id})
```

### 6.2 Conexiones Optimizadas

```python
# connection_pool.py
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

class DatabasePool:
    """Pool de conexiones MongoDB optimizado"""
    
    _instance = None
    _client = None
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls._client is None:
            cls._client = AsyncIOMotorClient(
                os.getenv("MONGODB_URI"),
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                retryWrites=True
            )
        return cls._client
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None

# Uso con FastAPI lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    DatabasePool.get_client()
    yield
    # Shutdown
    await DatabasePool.close()

app = FastAPI(lifespan=lifespan)
```

### 6.3 Compresión y Optimización de Respuestas

```python
# compression.py
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Agregar compresión GZIP
app.add_middleware(GZipMiddleware, minimum_size=500)

# Middleware para headers de cache
class CacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Cache para recursos estáticos
        if request.url.path.startswith("/static"):
            response.headers["Cache-Control"] = "public, max-age=86400"
        
        # No cachear APIs
        elif request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        
        return response

app.add_middleware(CacheHeaderMiddleware)
```

---

## 🚀 7. Plan de Implementación

### Fase 1: Fundamentos (Semanas 1-2)
- [ ] Implementar rate limiting
- [ ] Agregar validación de entrada robusta
- [ ] Configurar logging estructurado
- [ ] Implementar health checks detallados

### Fase 2: Seguridad (Semanas 3-4)
- [ ] Implementar autenticación JWT
- [ ] Migrar secretos a Secret Manager
- [ ] Configurar Cloud Armor
- [ ] Habilitar audit logging

### Fase 3: Observabilidad (Semanas 5-6)
- [ ] Implementar métricas Prometheus
- [ ] Configurar trazabilidad distribuida
- [ ] Crear dashboards de monitoreo
- [ ] Configurar alertas

### Fase 4: Fiabilidad (Semanas 7-8)
- [ ] Implementar circuit breaker
- [ ] Agregar retry con backoff
- [ ] Implementar graceful degradation
- [ ] Configurar auto-scaling

### Fase 5: Optimización (Semanas 9-10)
- [ ] Implementar cache multinivel
- [ ] Optimizar consultas a base de datos
- [ ] Implementar selección inteligente de modelos
- [ ] Configurar CDN

---

## 📚 Referencias

1. [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework)
2. [Well-Architected Framework: Security](https://cloud.google.com/architecture/framework/security)
3. [Well-Architected Framework: Operational Excellence](https://cloud.google.com/architecture/framework/operational-excellence)
4. [Well-Architected Framework: Reliability](https://cloud.google.com/architecture/framework/reliability)
5. [Conversational AI on Google Cloud](https://cloud.google.com/conversational-ai)
6. [Best practices for securing applications and APIs using Apigee](https://cloud.google.com/architecture/best-practices-securing-applications-and-apis-using-apigee)

---

**Documento creado**: Diciembre 2024  
**Autor**: Copilot basado en Google Cloud Architecture Framework  
**Versión**: 1.0
