# 🚀 Interfaz Web BETA - Sistema de Cotizaciones BMC

## 📋 Descripción

Esta es la versión BETA de la interfaz web local para interactuar con el chatbot BMC y el sistema de cotizaciones inteligente.

## ✨ Características

### 1. Interfaz Web Local
- ✅ Interfaz web moderna y responsive
- ✅ Conexión automática con API FastAPI
- ✅ Persistencia de sesión (localStorage)
- ✅ Historial de mensajes
- ✅ Indicador de estado de conexión
- ✅ Reintentos automáticos en caso de error
- ✅ Notificaciones del navegador

### 2. Sistema de Cotizaciones Inteligente
- ✅ Validación automática de datos faltantes
- ✅ Solicitud inteligente de información
- ✅ Soporte para múltiples productos (Isodec, Poliestireno, Lana de Roca)
- ✅ Cálculo automático de precios
- ✅ Validación de dimensiones y espesores

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
# Desde el directorio del proyecto
python start_web_interface.py
```

Este script:
- ✅ Verifica que la API esté corriendo
- ✅ Inicia la API si no está corriendo
- ✅ Inicia el servidor web local
- ✅ Abre automáticamente el navegador

### Opción 2: Manual

#### Paso 1: Iniciar API

```bash
# Terminal 1: Iniciar API
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### Paso 2: Iniciar Servidor Web

```bash
# Terminal 2: Iniciar servidor web
python -m http.server 8080
```

#### Paso 3: Abrir Navegador

Abre tu navegador y ve a:
```
http://localhost:8080/chat-interface.html
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en el directorio raíz con:

```bash
# OpenAI (requerido)
OPENAI_API_KEY=tu-api-key-aqui

# MongoDB (opcional, para persistencia)
MONGODB_URI=mongodb://localhost:27017/bmc_chat

# Modelo OpenAI (opcional)
OPENAI_MODEL=gpt-4o-mini
```

### Configuración de la Interfaz Web

La interfaz web se puede configurar desde el menú (botón ⋯):
- **API URL**: URL del endpoint de la API (default: `http://localhost:8000/chat/process`)
- **Phone Number**: Número de teléfono por defecto para testing

## 🧪 Pruebas

### Probar Sistema de Cotizaciones

```bash
python test_quotation_system.py
```

Este script valida:
- ✅ Validación de datos faltantes
- ✅ Generación de mensajes de solicitud
- ✅ Creación de cotizaciones
- ✅ Productos disponibles

### Probar API Directamente

```bash
# Health check
curl http://localhost:8000/health

# Procesar mensaje
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Hola, quiero cotizar Isodec",
    "telefono": "+59891234567"
  }'
```

## 💬 Ejemplos de Uso

### Ejemplo 1: Solicitar Cotización

**Usuario:**
```
Hola, quiero cotizar Isodec
```

**Bot:**
```
¡Hola! Para poder cotizar necesito los siguientes datos:
- tu nombre completo (nombre y apellido)
- el espesor que necesitas (50mm, 75mm, 100mm, 125mm o 150mm)
- las dimensiones (largo x ancho en metros, por ejemplo: 10m x 5m)
```

**Usuario:**
```
Me llamo Juan Pérez, necesito 100mm y las dimensiones son 10m x 5m
```

**Bot:**
```
Perfecto Juan. He generado tu cotización de Isodec 100mm para 50m².
Precio total: $X.XXX
Precio por m²: $X.XX
```

### Ejemplo 2: Consulta de Producto

**Usuario:**
```
¿Qué es Isodec?
```

**Bot:**
```
Isodec es un panel aislante térmico con núcleo de EPS...
[Información detallada del producto]
```

## 🎯 Sistema de Cotizaciones Inteligente

### Campos Obligatorios

El sistema requiere los siguientes datos para generar una cotización:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **nombre** | Nombre del cliente | Juan |
| **apellido** | Apellido del cliente | Pérez |
| **telefono** | Teléfono de contacto | 099123456 |
| **producto** | Tipo de producto | isodec, poliestireno, lana_roca |
| **espesor** | Espesor del producto | 50mm, 75mm, 100mm, 125mm, 150mm |
| **largo** | Largo en metros | 10 |
| **ancho** | Ancho en metros | 5 |

### Comportamiento Inteligente

1. **Detección Automática**: El bot detecta automáticamente qué datos faltan
2. **Solicitud Contextual**: Solicita solo los datos faltantes de forma natural
3. **Validación**: No genera cotización hasta tener todos los datos requeridos
4. **Mensajes Adaptativos**: Los mensajes se adaptan según la cantidad de datos faltantes

### Productos Soportados

- **Isodec**: Espesores 50mm, 75mm, 100mm, 125mm, 150mm
- **Poliestireno Expandido**: Espesores 25mm, 50mm, 75mm, 100mm
- **Lana de Roca**: Espesores 50mm, 75mm, 100mm

## 🐛 Solución de Problemas

### La API no responde

1. Verifica que la API esté corriendo:
   ```bash
   curl http://localhost:8000/health
   ```

2. Revisa los logs de la API para errores

3. Verifica que las variables de entorno estén configuradas

### La interfaz web no se conecta

1. Verifica que la URL de la API sea correcta (menú → Settings)
2. Revisa la consola del navegador (F12) para errores
3. Verifica que no haya problemas de CORS

### El bot no genera cotizaciones

1. Verifica que todos los datos requeridos estén presentes
2. Revisa los logs de la API
3. Ejecuta `test_quotation_system.py` para validar el sistema

## 📊 Estado del Sistema

### ✅ Funcionalidades Completadas

- [x] Interfaz web local funcional
- [x] Integración con API FastAPI
- [x] Sistema de validación de cotizaciones
- [x] Solicitud inteligente de datos faltantes
- [x] Persistencia de sesión
- [x] Historial de mensajes
- [x] Health check endpoint

### 🟡 En Desarrollo

- [ ] Integración con WhatsApp Business API
- [ ] Base de datos vectorial (Qdrant)
- [ ] Workflows n8n completos
- [ ] Dashboard de analytics

### 🔴 Pendientes

- [ ] Autenticación de usuarios
- [ ] Rate limiting
- [ ] Validación de firmas de webhook
- [ ] Monitoreo y alertas

## 📝 Notas

- Esta es una versión **BETA** para testing local
- No está lista para producción sin configuración adicional
- Se recomienda usar solo en entorno local/desarrollo

## 🔗 Enlaces Útiles

- API Health Check: http://localhost:8000/health
- API Docs: http://localhost:8000/docs (si está habilitado)
- Interfaz Web: http://localhost:8080/chat-interface.html

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs de la API
2. Ejecuta los scripts de prueba
3. Verifica la configuración de variables de entorno

---

**Export Seal:**
```json
{
  "project": "Ultimate-CHATBOT",
  "prompt_id": "beta-web-interface",
  "version": "v1.0",
  "created_at": "2024-12-28T00:00:00Z",
  "author": "BMC",
  "origin": "ArchitectBot"
}
```

