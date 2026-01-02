# 🚀 Guía de Implementación: APIs de Cursor

**Fecha:** 2024-12-28  
**Proyecto:** Sistema de Cotizaciones BMC Uruguay

---

## 📋 Resumen Rápido

Esta guía te ayudará a implementar las APIs de Cursor en tu proyecto paso a paso.

---

## 🔧 Setup Inicial

### 1. Obtener API Key

1. Ve a [Cursor Dashboard](https://cursor.com/dashboard)
2. Navega a **Settings** → **Advanced** → **Admin API Keys**
3. Haz clic en **Create New API Key**
4. Copia la clave (formato: `key_xxxxxxxxxxxxxxxx...`)

### 2. Configurar Variables de Entorno

Crea o actualiza tu archivo `.env`:

```bash
# Cursor API Configuration
CURSOR_API_KEY=key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Opcional: Configuración de caché
CURSOR_CACHE_ENABLED=true
CURSOR_CACHE_TTL_MINUTES=15

# Opcional: Rate limiting
CURSOR_RATE_LIMIT_REQUESTS_PER_MINUTE=15
```

### 3. Instalar Dependencias

```bash
pip install requests
```

---

## 📦 Estructura de Archivos

```
chatbot-2311/
├── cursor_api_client.py              # Cliente base de Cursor API
├── cursor_analytics_service.py        # Servicio de analytics
├── cursor_code_tracking_service.py    # Servicio de code tracking
├── cursor_dashboard_api.py            # API endpoints para dashboard
└── CURSOR_APIS_BEST_PRACTICES_ANALYSIS.md  # Análisis completo
```

---

## 🎯 Casos de Uso Prácticos

### Caso 1: Dashboard de Uso Diario

**Objetivo:** Mostrar métricas de uso del equipo en un dashboard

**Implementación:**

```python
from cursor_analytics_service import CursorAnalyticsService
from datetime import datetime

# Inicializar servicio
analytics = CursorAnalyticsService()

# Obtener métricas del día
today = datetime.now().strftime("%Y-%m-%d")
metrics = analytics.get_team_metrics(date=today)

print(f"Usuarios activos hoy: {metrics.dau}")
print(f"Costo total: ${metrics.total_cost:.2f}")
print(f"Modelos usados: {len(metrics.model_usage)}")
```

**Integración con FastAPI:**

```python
from fastapi import APIRouter
from cursor_analytics_service import CursorAnalyticsService

router = APIRouter()
analytics = CursorAnalyticsService()

@router.get("/api/cursor/metrics/daily")
async def get_daily_metrics():
    """Obtiene métricas diarias de Cursor"""
    metrics = analytics.get_team_metrics()
    return {
        "date": metrics.date,
        "dau": metrics.dau,
        "total_cost": metrics.total_cost,
        "model_usage": [m.__dict__ for m in metrics.model_usage]
    }
```

### Caso 2: Tracking de Código Generado por IA

**Objetivo:** Rastrear qué código fue generado por IA en cada commit

**Implementación:**

```python
from cursor_code_tracking_service import CursorCodeTrackingService

# Inicializar servicio
tracking = CursorCodeTrackingService()

# Obtener commits con código IA
commits = tracking.get_ai_commits(
    repository="chatbot-2311",
    start_date="7d"
)

for commit in commits:
    print(f"Commit: {commit.commit_id}")
    print(f"  AI Lines: {commit.ai_lines}/{commit.total_lines} ({commit.ai_percentage:.1f}%)")
    print(f"  Files: {commit.files_changed}")
```

**Integración con Webhook de Git:**

```python
from fastapi import APIRouter, Request
from cursor_code_tracking_service import CursorCodeTrackingService

router = APIRouter()
tracking = CursorCodeTrackingService()

@router.post("/api/git/webhook")
async def git_webhook(request: Request):
    """Webhook para tracking automático de commits"""
    payload = await request.json()
    commit_id = payload.get("commit", {}).get("id")
    
    if commit_id:
        changes = tracking.get_ai_changes(commit_id)
        # Guardar en base de datos o procesar
        return {"status": "tracked", "changes": len(changes)}
```

### Caso 3: Reporte Semanal de Productividad

**Objetivo:** Generar reporte semanal de uso y productividad

**Implementación:**

```python
from cursor_analytics_service import CursorAnalyticsService
from cursor_code_tracking_service import CursorCodeTrackingService
from datetime import datetime, timedelta

analytics = CursorAnalyticsService()
tracking = CursorCodeTrackingService()

# Obtener resumen de la semana
summary = analytics.get_usage_summary(days=7)
code_metrics = tracking.get_code_metrics(
    repository="chatbot-2311",
    start_date="7d"
)

report = {
    "period": "Última semana",
    "usage": {
        "avg_dau": summary["dau"]["average"],
        "total_cost": summary["cost"]["total"],
        "avg_cost_per_day": summary["cost"]["average_per_day"]
    },
    "code": {
        "ai_commits": code_metrics.ai_commits,
        "ai_lines": code_metrics.ai_lines,
        "ai_percentage": code_metrics.ai_lines_percentage
    }
}

print(json.dumps(report, indent=2))
```

### Caso 4: Alertas de Costo

**Objetivo:** Enviar alertas cuando el costo se acerque al límite

**Implementación:**

```python
from cursor_analytics_service import CursorAnalyticsService
from datetime import datetime

analytics = CursorAnalyticsService()
DAILY_LIMIT = 50.0  # Límite diario en USD

def check_daily_spend():
    """Verifica el gasto diario y envía alerta si es necesario"""
    today = datetime.now().strftime("%Y-%m-%d")
    metrics = analytics.get_team_metrics(date=today)
    
    if metrics.total_cost > DAILY_LIMIT * 0.9:  # 90% del límite
        # Enviar alerta (email, Slack, etc.)
        send_alert(
            f"⚠️ Gasto diario alto: ${metrics.total_cost:.2f} "
            f"({metrics.total_cost / DAILY_LIMIT * 100:.1f}% del límite)"
        )
    
    return metrics.total_cost

# Ejecutar cada hora
# schedule.every().hour.do(check_daily_spend)
```

---

## 🔄 Integración con el Sistema Existente

### Integración con FastAPI

Agregar endpoints a `api_server.py`:

```python
from fastapi import APIRouter
from cursor_analytics_service import CursorAnalyticsService
from cursor_code_tracking_service import CursorCodeTrackingService

# Crear router
cursor_router = APIRouter(prefix="/api/cursor", tags=["cursor"])

# Inicializar servicios
analytics = CursorAnalyticsService()
tracking = CursorCodeTrackingService()

@cursor_router.get("/metrics/daily")
async def get_daily_metrics():
    """Métricas diarias de Cursor"""
    return analytics.get_team_metrics()

@cursor_router.get("/metrics/summary")
async def get_usage_summary(days: int = 30):
    """Resumen de uso"""
    return analytics.get_usage_summary(days=days)

@cursor_router.get("/code/metrics")
async def get_code_metrics(days: int = 30):
    """Métricas de código generado por IA"""
    return tracking.get_code_metrics(
        repository="chatbot-2311",
        start_date=f"{days}d"
    )

# Registrar router en app
app.include_router(cursor_router)
```

### Integración con MongoDB

Almacenar métricas históricas:

```python
from pymongo import MongoClient
from cursor_analytics_service import CursorAnalyticsService
from datetime import datetime

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["bmc_analytics"]
collection = db["cursor_metrics"]

analytics = CursorAnalyticsService()

def store_daily_metrics():
    """Almacena métricas diarias en MongoDB"""
    metrics = analytics.get_team_metrics()
    
    document = {
        "date": metrics.date,
        "dau": metrics.dau,
        "total_cost": metrics.total_cost,
        "model_usage": [m.__dict__ for m in metrics.model_usage],
        "timestamp": datetime.now()
    }
    
    collection.insert_one(document)
    print(f"Métricas del {metrics.date} almacenadas")

# Ejecutar diariamente
# schedule.every().day.at("23:59").do(store_daily_metrics)
```

---

## 📊 Dashboard en Next.js

### Componente de Dashboard

```typescript
// nextjs-app/components/CursorDashboard.tsx
import { useEffect, useState } from 'react';

interface CursorMetrics {
  dau: number;
  total_cost: number;
  model_usage: any[];
}

export default function CursorDashboard() {
  const [metrics, setMetrics] = useState<CursorMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/cursor/metrics/daily')
      .then(res => res.json())
      .then(data => {
        setMetrics(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="cursor-dashboard">
      <h2>Cursor Analytics</h2>
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Usuarios Activos</h3>
          <p className="metric-value">{metrics?.dau || 0}</p>
        </div>
        <div className="metric-card">
          <h3>Costo Total</h3>
          <p className="metric-value">${metrics?.total_cost?.toFixed(2) || 0}</p>
        </div>
      </div>
    </div>
  );
}
```

---

## 🧪 Testing

### Test Básico de Conectividad

```python
import pytest
from cursor_api_client import CursorAPIClient, AuthenticationError

def test_api_connection():
    """Test de conexión básica"""
    client = CursorAPIClient()
    
    # Debe poder hacer una solicitud básica
    try:
        response = client.get("/analytics/team/dau", params={"start_date": "7d"})
        assert "data" in response
    except AuthenticationError:
        pytest.skip("API key no configurada")
```

### Test de Rate Limiting

```python
def test_rate_limiting():
    """Test de manejo de rate limits"""
    client = CursorAPIClient()
    
    # Hacer múltiples solicitudes rápidas
    for i in range(25):  # Más que el límite
        try:
            client.get("/analytics/team/dau", params={"start_date": "7d"})
        except RateLimitError:
            # Debe manejar rate limit correctamente
            assert True
            break
```

---

## 📈 Monitoreo y Alertas

### Configurar Alertas

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(message: str):
    """Envía alerta por email"""
    # Configurar SMTP
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_from = os.getenv("ALERT_EMAIL_FROM")
    email_to = os.getenv("ALERT_EMAIL_TO")
    email_password = os.getenv("ALERT_EMAIL_PASSWORD")
    
    msg = MIMEText(message)
    msg["Subject"] = "Cursor API Alert"
    msg["From"] = email_from
    msg["To"] = email_to
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_from, email_password)
        server.send_message(msg)
```

---

## 🚨 Troubleshooting

### Error: "Clave de API inválida"

**Solución:**
1. Verifica que `CURSOR_API_KEY` esté configurada
2. Verifica que la clave comience con `key_`
3. Verifica que la clave no tenga espacios extra

### Error: "Rate limit excedido"

**Solución:**
1. Reduce la frecuencia de solicitudes
2. Usa caché con ETags
3. Implementa backoff exponencial

### Error: "Permisos insuficientes"

**Solución:**
1. Verifica que tengas plan Enterprise
2. Verifica que la API key tenga permisos necesarios
3. Contacta soporte de Cursor si persiste

---

## 📚 Recursos Adicionales

- [Documentación de Cursor APIs](https://cursor.com/docs)
- [Análisis de Mejores Prácticas](./CURSOR_APIS_BEST_PRACTICES_ANALYSIS.md)
- [Ejemplos de Código](./cursor_api_client.py)

---

**Última actualización:** 2024-12-28  
**Versión:** 1.0


