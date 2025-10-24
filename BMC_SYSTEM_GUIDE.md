# 🏗️ Sistema BMC de Cotización Inteligente

## Descripción General

Sistema completo de cotización automática para BMC Construcciones que integra:
- **Motor de IA** para parsing de consultas
- **Base de conocimiento** de productos BMC
- **Integración Google Sheets** para gestión de cotizaciones
- **Chat inteligente** con respuestas contextuales
- **Dashboard** para monitoreo y gestión

## 🚀 Instalación Rápida

### 1. Configurar Variables de Entorno

```bash
# Ejecutar script de configuración
./setup-bmc-system.sh

# Editar .env.local con tus credenciales
nano .env.local
```

### 2. Credenciales Requeridas

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

### 3. Ejecutar Sistema

```bash
npm run dev
# Navegar a http://localhost:3000
```

## 🧠 Motor de Cotización

### Base de Conocimiento de Productos

El sistema incluye una base de conocimiento completa con:

#### Productos Principales
- **Isodec EPS** - Paneles aislantes (50, 100, 150, 200mm)
- **Isoroof** - Paneles para techos (30, 50, 80mm)
- **Isopanel** - Paneles de uso general (50-250mm)
- **Isowall** - Paneles para paredes exteriores (50-150mm)
- **Chapas Galvanizadas** - Acero galvanizado (0.30-0.50mm)
- **Calamería** - Estructura metálica (1.5-2.5mm)

#### Servicios Adicionales
- **Instalación** - Precio base + por m²
- **Flete** - Según zona geográfica
- **Accesorios** - Babetas, goteros, remates, juntas

### Motor de Respuestas Inteligentes

El sistema puede responder a:

1. **Cotizaciones** - Genera presupuestos automáticos
2. **Información** - Detalles de productos y servicios
3. **Preguntas Frecuentes** - Respuestas a consultas comunes
4. **Soporte** - Ayuda con el proceso de cotización

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

### API Endpoints

#### Sincronización con Sheets
```typescript
// Leer todas las cotizaciones
GET /api/sheets/sync

// Agregar nueva cotización
POST /api/sheets/sync
{
  "action": "add_quote",
  "data": { ... }
}

// Mover cotización entre pestañas
POST /api/sheets/sync
{
  "action": "move_to_enviados",
  "data": { "rowNumber": 123 }
}
```

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

## 🎯 Motor de Parsing IA

### Extracción de Datos

El sistema utiliza OpenAI para extraer información estructurada de consultas:

```typescript
interface ParsedQuote {
  producto: {
    tipo: string
    grosor?: string
    color?: string
    cantidad?: number
    unidad?: string
  }
  dimensiones?: {
    largo?: number
    ancho?: number
    alto?: number
    area_m2?: number
  }
  servicios: {
    flete: boolean
    instalacion: boolean
    accesorios: boolean
  }
  estado_info: 'completo' | 'pendiente_info' | 'ver_plano'
  confianza: number
}
```

### Ejemplos de Parsing

**Entrada**: "Isodec 100mm / 8 p de 10 m / paneles blancos / completo + flete"

**Salida**:
```json
{
  "producto": {
    "tipo": "Isodec",
    "grosor": "100mm",
    "color": "blancos",
    "cantidad": 8,
    "unidad": "paneles"
  },
  "dimensiones": {
    "largo": 10,
    "area_m2": 80
  },
  "servicios": {
    "flete": true,
    "instalacion": true,
    "accesorios": false
  },
  "estado_info": "completo",
  "confianza": 0.95
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

### Modelos

```typescript
interface Quote {
  _id?: string
  arg: string
  estado: 'Pendiente' | 'Adjunto' | 'Listo' | 'Enviado' | 'Asignado' | 'Confirmado'
  fecha: string
  cliente: string
  origen: 'WA' | 'LO' | 'EM' | 'CL'
  telefono: string
  direccion: string
  consulta: string
  parsed?: ParsedQuote
  createdAt: Date
  updatedAt: Date
}
```

## 📊 Dashboard de Gestión

### Pestañas Disponibles

1. **Cotizaciones** - Gestión de cotizaciones en tiempo real
2. **Context Management** - Gestión de contexto de conversaciones
3. **Live Chat** - Chat inteligente con motor de cotización
4. **Analytics** - Métricas y estadísticas
5. **Settings** - Configuración del sistema

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

## 📈 Monitoreo y Analytics

### Métricas Clave

- **Tasa de conversión** - Consultas a cotizaciones
- **Tiempo de respuesta** - Latencia del sistema
- **Precisión del parsing** - Exactitud de extracción
- **Satisfacción del usuario** - Feedback de clientes

### Logs y Debugging

```bash
# Ver logs en desarrollo
npm run dev

# Logs en producción
vercel logs

# Debug específico
DEBUG=bmc:* npm run dev
```

## 🔒 Seguridad

### Medidas Implementadas

1. **Autenticación** - API keys y tokens
2. **Validación** - Input sanitization
3. **Rate Limiting** - Protección contra spam
4. **Cifrado** - Datos sensibles encriptados
5. **Auditoría** - Logs de todas las operaciones

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

## 🎉 ¡Sistema Listo!

El Sistema BMC de Cotización Inteligente está diseñado para:

✅ **Automatizar** el proceso de cotización
✅ **Mejorar** la experiencia del cliente
✅ **Optimizar** el tiempo de respuesta
✅ **Integrar** todos los canales de comunicación
✅ **Escalar** según las necesidades del negocio

¡Disfruta de tu nuevo sistema de cotización inteligente! 🚀
