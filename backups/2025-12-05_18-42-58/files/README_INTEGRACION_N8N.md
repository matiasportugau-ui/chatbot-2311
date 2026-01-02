# 🚀 Integración Completa con n8n - Sistema BMC

## 📋 Resumen de la Integración

El Sistema BMC de Cotización Inteligente ahora está completamente integrado con **n8n** como orquestador principal, proporcionando una arquitectura robusta y escalable.

## 🏗️ Arquitectura Integrada

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   Dashboard     │    │   Google Sheets │
│   Business API  │    │   Next.js       │    │   API           │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        n8n (Orquestador)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   Chat      │ │  WhatsApp   │ │   Sheets    │ │Analytics │ │
│  │ Workflow    │ │  Workflow   │ │   Sync      │ │ Workflow │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Sistema Python (Motor de Cotización)              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │   Base de   │ │   Motor de  │ │   Análisis  │ │   IA     │ │
│  │Conocimiento │ │Cotización   │ │Conversiones │ │Conversac.│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MongoDB Atlas                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │  Cotizac.   │ │  Sesiones   │ │  Contexto   │ │Analytics │ │
│  │             │ │             │ │             │ │          │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Componentes de la Integración

### 1. **Cliente TypeScript (n8n-client.ts)**
- Interfaz completa para comunicación con n8n
- Métodos para todos los workflows
- Manejo de errores y reintentos
- Tipos TypeScript para type safety

### 2. **Workflows n8n Exportables**

#### 📱 **Chat Conversacional** (`workflow-chat.json`)
- **Endpoint**: `/webhook/chat`
- **Función**: Procesar mensajes del chat web
- **Flujo**: Webhook → Validación → Python → MongoDB → Respuesta

#### 📲 **WhatsApp Business** (`workflow-whatsapp.json`)
- **Endpoint**: `/webhook/whatsapp`
- **Función**: Procesar mensajes de WhatsApp
- **Flujo**: Webhook → Extracción → Python → Google Sheets → WhatsApp API

#### 📊 **Google Sheets Sync** (`workflow-sheets-sync.json`)
- **Trigger**: Cada 5 minutos
- **Función**: Sincronizar datos con Google Sheets
- **Flujo**: Schedule → Leer Sheets → Python → MongoDB → Log

#### 📈 **Analytics Diario** (`workflow-analytics.json`)
- **Trigger**: Diario a las 9:00 AM
- **Función**: Generar reportes y insights
- **Flujo**: Schedule → Insights → Conversiones → Email → Sheets

### 3. **Docker Compose Completo**
- **n8n**: Orquestador principal
- **bmc-python**: Motor de cotización
- **bmc-dashboard**: Frontend Next.js
- **mongodb**: Base de datos
- **redis**: Cache y sesiones
- **nginx**: Proxy reverso

## 🚀 Instalación y Configuración

### 1. **Clonar y Configurar**
```bash
git clone https://github.com/matiasportugau-ui/bmc-cotizacion-inteligente.git
cd bmc-cotizacion-inteligente
```

### 2. **Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. **Ejecutar con Docker Compose**
```bash
docker-compose up -d
```

### 4. **Acceder a los Servicios**
- **Dashboard**: http://localhost:3000
- **n8n Interface**: http://localhost:5678
- **MongoDB**: localhost:27017

## 📋 Configuración de n8n

### 1. **Importar Workflows**
1. Acceder a n8n en http://localhost:5678
2. Usuario: `admin` / Contraseña: `bmc2024secure`
3. Importar los 4 workflows desde `n8n_workflows/`

### 2. **Configurar Credenciales en n8n**
- **Google Sheets API**: Service Account
- **WhatsApp Business API**: Access Token
- **MongoDB**: Connection String
- **OpenAI**: API Key

### 3. **Activar Workflows**
- Todos los workflows vienen pre-configurados
- Activar según necesidades de producción

## 🔄 Flujos de Trabajo

### **Flujo de Chat Web**
```
Usuario → Dashboard → n8n Chat Workflow → Python Script → MongoDB → Respuesta
```

### **Flujo de WhatsApp**
```
WhatsApp → n8n WhatsApp Workflow → Python Script → Google Sheets → WhatsApp API
```

### **Flujo de Sincronización**
```
Schedule → n8n Sheets Workflow → Python Script → MongoDB → Log
```

### **Flujo de Analytics**
```
Schedule → n8n Analytics Workflow → Python Script → Email + Sheets
```

## 📊 Monitoreo y Logs

### **Logs de n8n**
- Acceder a n8n interface
- Ver ejecuciones de workflows
- Monitorear errores y rendimiento

### **Logs de Docker**
```bash
docker-compose logs -f n8n
docker-compose logs -f bmc-python
docker-compose logs -f bmc-dashboard
```

### **Métricas de MongoDB**
- Colección `sync_logs` para sincronización
- Colección `reportes_diarios` para analytics
- Colección `conversaciones` para chat

## 🛠️ Desarrollo y Testing

### **Testing de Workflows**
```bash
# Test Chat Workflow
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Cotizar Isodec 100mm para 50m2"}'

# Test WhatsApp Workflow
curl -X POST http://localhost:5678/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"entry": [{"changes": [{"field": "messages", "value": {"messages": [{"from": "+59891234567", "text": {"body": "Hola, necesito cotizar"}}]}}]}]}'
```

### **Desarrollo Local**
```bash
# Solo n8n y MongoDB
docker-compose up n8n mongodb -d

# Ejecutar Python localmente
python sistema_final_integrado.py

# Ejecutar Dashboard localmente
cd Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
npm run dev
```

## 🔒 Seguridad

### **Configuración de Red**
- Red Docker aislada (`bmc-network`)
- Comunicación interna entre contenedores
- Nginx como único punto de entrada

### **Autenticación**
- n8n con autenticación básica
- MongoDB con usuario/contraseña
- Variables de entorno para credenciales

### **Rate Limiting**
- API: 10 req/s
- Webhooks: 5 req/s
- Configurado en Nginx

## 📈 Escalabilidad

### **Horizontal Scaling**
- n8n puede escalarse horizontalmente
- MongoDB con réplicas
- Redis para cache distribuido

### **Load Balancing**
- Nginx como load balancer
- Múltiples instancias de Python
- CDN para assets estáticos

## 🚨 Troubleshooting

### **Problemas Comunes**

1. **n8n no inicia**
   ```bash
   docker-compose logs n8n
   # Verificar variables de entorno
   ```

2. **Workflows no se ejecutan**
   - Verificar credenciales en n8n
   - Revisar logs de ejecución
   - Verificar conectividad con Python

3. **MongoDB connection error**
   ```bash
   docker-compose logs mongodb
   # Verificar MONGODB_URI
   ```

4. **Python script errors**
   ```bash
   docker-compose logs bmc-python
   # Verificar dependencias y credenciales
   ```

## 🎯 Próximos Pasos

1. **Configurar credenciales reales**
2. **Importar workflows en n8n**
3. **Activar workflows de producción**
4. **Configurar monitoreo avanzado**
5. **Implementar alertas automáticas**
6. **Optimizar rendimiento**

## 📞 Soporte

- **Documentación**: README.md
- **Issues**: GitHub Issues
- **Email**: soporte@bmc-construcciones.com

---

**¡Sistema BMC completamente integrado con n8n y listo para producción!** 🚀
