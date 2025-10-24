# 🏗️ Sistema BMC de Cotización Inteligente

Sistema completo de cotización automática para BMC Construcciones que integra IA, WhatsApp Business, Google Sheets y MongoDB para automatizar el proceso de cotización de productos de construcción.

## 🚀 Características Principales

- **🤖 Motor de IA Integrado** - Parser inteligente con base de conocimiento evolutiva
- **🧠 Base de Conocimiento Dinámica** - Aprende y evoluciona de cada interacción
- **📊 Análisis de Patrones** - Identifica patrones de venta exitosos automáticamente
- **🎯 Personalización Inteligente** - Respuestas adaptadas al perfil del cliente
- **📱 WhatsApp Business** - Integración completa con webhooks
- **📋 Google Sheets** - Sincronización automática de cotizaciones
- **🗄️ MongoDB** - Persistencia de datos y contexto
- **💬 Chat Inteligente** - Interfaz de chat con motor de cotización integrado
- **📈 Dashboard Integrado** - Métricas del sistema evolutivo en tiempo real

## 🛠️ Tecnologías

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API Routes, MongoDB Atlas
- **IA**: OpenAI GPT-4, Parser inteligente de consultas
- **Integración**: Google Sheets API, WhatsApp Business API
- **UI**: shadcn/ui, Lucide React
- **Deploy**: Vercel

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/bmc-cotizacion-inteligente.git
cd bmc-cotizacion-inteligente
```

### 2. Instalar Dependencias

```bash
npm install
```

### 3. Configurar Credenciales

```bash
# Ejecutar script de configuración
./setup-credentials.sh

# Editar archivo de credenciales
nano credentials.json
```

### 4. Variables de Entorno Requeridas

```env
# OpenAI API Key (REQUERIDO)
OPENAI_API_KEY=sk-...

# Google Sheets API (REQUERIDO)
GOOGLE_SHEET_ID=bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=tu-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# MongoDB Atlas (REQUERIDO)
MONGODB_URI=mongodb+srv://...

# WhatsApp Business API (OPCIONAL)
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=bmc_whatsapp_verify_2024
```

### 5. Configurar Integración

```bash
# Ejecutar script de configuración de integración
./setup-integration.sh

# O configurar manualmente
./setup-credentials.sh
```

### 6. Ejecutar Sistema

```bash
npm run dev
# Navegar a http://localhost:3000
```

### 7. Probar Integración

```bash
# Ejecutar tests de integración
node test-integration.js

# O probar manualmente en el dashboard
# Ir a pestaña "Sistema Integrado"
```

## 🧠 Motor de Cotización

### Productos Soportados

- **Isodec EPS** - Paneles aislantes (50, 100, 150, 200mm)
- **Isoroof** - Paneles para techos (30, 50, 80mm)
- **Isopanel** - Paneles de uso general (50-250mm)
- **Isowall** - Paneles para paredes exteriores (50-150mm)
- **Chapas Galvanizadas** - Acero galvanizado (0.30-0.50mm)
- **Calamería** - Estructura metálica (1.5-2.5mm)

### Servicios Adicionales

- **Instalación** - Precio base + por m²
- **Flete** - Según zona geográfica (Montevideo, Canelones, etc.)
- **Accesorios** - Babetas, goteros, remates, juntas

## 📊 Integración Google Sheets

### Estructura del Sheet

**Sheet ID**: `bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0`

#### Pestañas
- **Admin.** - Cotizaciones pendientes
- **Enviados** - Cotizaciones con presupuesto entregado
- **Confirmado** - Cotizaciones confirmadas

#### Columnas
| Col | Campo | Descripción |
|-----|-------|-------------|
| A | Arg | Código único de cotización |
| B | Estado | Pendiente, Adjunto, Listo, Enviado, Asignado, Confirmado |
| C | Fecha | Fecha de la consulta |
| D | Cliente | Nombre del cliente |
| E | Orig. | Origen: WA, LO, EM, CL |
| F | Telefono | Número de contacto |
| G | Direccion | Dirección/zona |
| H | Consulta | **TEXTO COMPLETO PARA PARSING IA** |

## 💬 Chat Inteligente

### Características del Chat

1. **Motor de IA Integrado** - Respuestas contextuales
2. **Gestión de Contexto** - Mantiene hilo de conversación
3. **Cotizaciones Automáticas** - Genera presupuestos en tiempo real
4. **Información de Productos** - Detalles técnicos y precios
5. **Preguntas Frecuentes** - Respuestas a consultas comunes

### API del Chat

```typescript
// Enviar mensaje
POST /api/chat
{
  "message": "Necesito cotizar Isodec 100mm para galpón de 50m2",
  "sessionId": "sess_123",
  "userPhone": "+59891234567"
}

// Respuesta
{
  "success": true,
  "data": {
    "response": {
      "tipo": "cotizacion",
      "mensaje": "🏗️ COTIZACIÓN BMC - Código: BMC123456...",
      "cotizacion": {
        "producto": "Isodec EPS",
        "descripcion": "Galpón completo de 50m x 30m x 5m",
        "precio_base": 2250,
        "total": 2750,
        "codigo": "BMC123456"
      }
    }
  }
}
```

## 📱 Integración WhatsApp

### Webhook de WhatsApp

```typescript
// Webhook para recibir mensajes
POST /api/whatsapp/webhook
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "field": "messages",
      "value": {
        "messages": [{
          "from": "+59891234567",
          "text": { "body": "Necesito cotizar Isodec..." },
          "id": "msg_123"
        }]
      }
    }]
  }]
}
```

### Flujo Automatizado

1. **Usuario envía mensaje** por WhatsApp
2. **Webhook recibe** el mensaje
3. **Parser IA extrae** información estructurada
4. **Se crea registro** en Google Sheets
5. **Se responde** al usuario con cotización

## 🗄️ Base de Datos MongoDB

### Colecciones

- **quotes** - Cotizaciones principales
- **sessions** - Sesiones de chat
- **context** - Contexto de conversaciones
- **products** - Base de conocimiento de productos
- **analytics** - Métricas y analytics

## 🧠 Sistema Integrado con Base de Conocimiento Evolutiva

### Características del Sistema Integrado

1. **Aprendizaje Automático**
   - Aprende de cada interacción con clientes
   - Identifica patrones de venta exitosos
   - Evoluciona respuestas basadas en experiencias previas

2. **Análisis de Patrones**
   - Patrones de venta identificados automáticamente
   - Productos más consultados por zona
   - Horarios pico de actividad
   - Perfiles de clientes con alta conversión

3. **Personalización Inteligente**
   - Respuestas adaptadas al perfil del cliente
   - Recomendaciones basadas en historial
   - Manejo inteligente de objeciones
   - Seguimiento personalizado

### API del Sistema Integrado

```typescript
// Procesar consulta con IA integrada
POST /api/integrated-quote
{
  "action": "process",
  "consulta": "Necesito cotizar Isodec 100mm para galpón de 50m2",
  "userPhone": "+59891234567",
  "userName": "Cliente"
}

// Obtener métricas del sistema
POST /api/integrated-quote
{
  "action": "metrics"
}

// Actualizar base de conocimiento
POST /api/integrated-quote
{
  "action": "update_knowledge"
}
```

## 📈 Dashboard de Gestión

### Pestañas Disponibles

1. **Cotizaciones** - Gestión de cotizaciones en tiempo real
2. **Context Management** - Gestión de contexto de conversaciones
3. **Live Chat** - Chat inteligente con motor de cotización
4. **Sistema Integrado** - Métricas del sistema evolutivo
5. **Analytics** - Métricas y estadísticas
6. **Settings** - Configuración del sistema

### Métricas en Tiempo Real

- Total de cotizaciones pendientes
- Cotizaciones enviadas
- Cotizaciones confirmadas
- Uso de contexto por sesión
- Productos más consultados
- Zonas de mayor demanda

## 🔧 Configuración Avanzada

### Zonas de Flete

```typescript
const ZONAS_FLETE = {
  'montevideo': { flete_base: 50, multiplicador: 1.0 },
  'canelones': { flete_base: 80, multiplicador: 1.2 },
  'maldonado': { flete_base: 120, multiplicador: 1.5 },
  'rivera': { flete_base: 200, multiplicador: 2.0 },
  'artigas': { flete_base: 250, multiplicador: 2.5 }
}
```

### Reglas de Cotización

El sistema incluye reglas inteligentes para:
- Galpones completos
- Solo techos
- Paredes exteriores
- Proyectos especiales

## 🧪 Testing

### Pruebas Automatizadas

```bash
# Ejecutar tests
npm test

# Tests específicos
npm run test:chat
npm run test:parsing
npm run test:sheets
```

### Casos de Prueba

1. **Parsing de consultas** - Diferentes formatos de entrada
2. **Generación de cotizaciones** - Cálculos de precios
3. **Integración Google Sheets** - CRUD operations
4. **Chat en tiempo real** - Flujo completo
5. **Webhook WhatsApp** - Recepción y respuesta

## 🚀 Despliegue

### Vercel (Recomendado)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel

# Configurar variables de entorno
vercel env add OPENAI_API_KEY
vercel env add GOOGLE_SHEET_ID
# ... etc
```

### Variables de Entorno en Producción

```env
OPENAI_API_KEY=sk-...
GOOGLE_SHEET_ID=bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
GOOGLE_SERVICE_ACCOUNT_EMAIL=...
GOOGLE_PRIVATE_KEY=...
MONGODB_URI=...
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
```

## 📞 Soporte

### Contacto Técnico

- **Email**: soporte@bmc-construcciones.com
- **Teléfono**: +598 99 123 456
- **Documentación**: [Link a docs completas]

### Troubleshooting Común

1. **Error de OpenAI** - Verificar API key
2. **Error de Google Sheets** - Verificar permisos
3. **Error de MongoDB** - Verificar conexión
4. **Error de WhatsApp** - Verificar webhook

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🎉 ¡Sistema Listo!

El Sistema BMC de Cotización Inteligente está diseñado para:

✅ **Automatizar** el proceso de cotización
✅ **Mejorar** la experiencia del cliente
✅ **Optimizar** el tiempo de respuesta
✅ **Integrar** todos los canales de comunicación
✅ **Escalar** según las necesidades del negocio

¡Disfruta de tu nuevo sistema de cotización inteligente! 🚀