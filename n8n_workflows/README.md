# n8n Workflows - Sistema de Cotizaciones BMC

Este directorio contiene los workflows de n8n para el sistema de cotizaciones.

## Workflows Disponibles

### 1. Chat Conversacional (`workflow-chat.json`)
- **Trigger**: Webhook POST `/webhook/chat`
- **Descripción**: Procesa mensajes conversacionales con IA
- **Flujo**: Webhook → Validación → Python Script → MongoDB → Response

### 2. WhatsApp Business (`workflow-whatsapp.json`)
- **Trigger**: Webhook WhatsApp Business
- **Descripción**: Procesa mensajes de WhatsApp y genera cotizaciones
- **Flujo**: WhatsApp → Extraer mensaje → IA → Google Sheets → Respuesta WhatsApp

### 3. Google Sheets Sync (`workflow-sheets-sync.json`)
- **Trigger**: Schedule (cada 5 minutos)
- **Descripción**: Sincroniza cotizaciones con Google Sheets
- **Flujo**: Schedule → Leer Sheet → Python Script → MongoDB → Notificación

### 4. Analytics Diario (`workflow-analytics.json`)
- **Trigger**: Schedule (diario 9am)
- **Descripción**: Genera reporte diario de métricas
- **Flujo**: Schedule → Insights → Análisis → Email → Google Sheets

## Instalación

### Opción 1: Importar en n8n Cloud

1. Ir a https://n8n.cloud
2. Crear cuenta
3. Click en "Import workflow"
4. Seleccionar archivo JSON del workflow
5. Configurar credenciales (Google Sheets, MongoDB, etc.)
6. Activar workflow

### Opción 2: n8n Self-hosted

```bash
# Iniciar n8n localmente
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Luego acceder a http://localhost:5678 e importar workflows.

## Configuración de Credenciales

### Python Script Execution

El nodo "Execute Command" debe apuntar a:
```bash
python3 /ruta/completa/a/n8n_integration.py
```

Input via STDIN:
```javascript
{{ JSON.stringify($json) }}
```

### MongoDB

- **Connection String**: `mongodb+srv://...`
- **Database**: `bmc_cotizaciones`
- **Collections**: `conversaciones`, `cotizaciones`, `insights`

### Google Sheets API

- **Spreadsheet ID**: `1bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0`
- **Service Account**: Configurar con JSON key
- **Scopes**: `https://www.googleapis.com/auth/spreadsheets`

### WhatsApp Business API

- **Access Token**: Desde Meta Business Suite
- **Phone Number ID**: ID del número de WhatsApp
- **Verify Token**: `bmc_whatsapp_verify_2024`

## Estructura de los Workflows

### Input Format para Python Script

```json
{
  "action": "procesar_mensaje|crear_cotizacion|obtener_insights|analisis_conversiones|listar_cotizaciones|obtener_productos|health_check",
  "mensaje": "texto del mensaje (para procesar_mensaje)",
  "telefono": "+59891234567",
  "sesion_id": "sess_123456",
  "cliente": {
    "nombre": "Cliente Ejemplo",
    "telefono": "+59891234567",
    "direccion": "Dirección",
    "zona": "Montevideo"
  },
  "especificaciones": {
    "producto": "isodec",
    "espesor": "100mm",
    "relleno": "EPS",
    "largo_metros": 10,
    "ancho_metros": 5,
    "color": "Blanco"
  }
}
```

### Output Format del Python Script

```json
{
  "success": true,
  "data": {
    // Datos específicos según la acción
  },
  "timestamp": "2024-12-19T10:30:00"
}
```

## Testing de Workflows

### Test con curl

```bash
# Test del webhook de chat
curl -X POST https://tu-n8n.cloud/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "action": "procesar_mensaje",
    "mensaje": "Necesito cotizar Isodec 100mm para 50m2",
    "telefono": "+59891234567"
  }'
```

### Test Python Script Standalone

```bash
# Test local del script
echo '{"action":"health_check"}' | python3 n8n_integration.py
```

## Monitoreo

n8n provee:
- Dashboard de ejecuciones
- Logs por workflow
- Métricas de performance
- Alertas en caso de error

## Troubleshooting

### Error: "Module not found"
- Verificar que el path del script Python sea correcto
- Instalar dependencias: `pip install -r requirements.txt`

### Error: "Permission denied"
- Hacer el script ejecutable: `chmod +x n8n_integration.py`

### Workflow no se activa
- Verificar que el trigger esté configurado correctamente
- Para webhooks, verificar la URL del webhook

## Costos

- **n8n Cloud**: $20/mes (Starter)
- **n8n Self-hosted**: $0 (solo infraestructura)
- **Railway (n8n)**: $5/mes

## Support

Para ayuda con n8n:
- Documentación: https://docs.n8n.io
- Community: https://community.n8n.io
- Discord: https://discord.gg/n8n

