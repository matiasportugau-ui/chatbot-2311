# 📊 Guía de Extracción de Datos para Entrenamiento

Este documento explica cómo extraer mensajes de WhatsApp y solicitudes de Mercado Libre para usar en el entrenamiento del chatbot.

## 🚀 Inicio Rápido

### Instalación de Dependencias

```bash
pip install pymongo requests
```

### Extracción Básica

#### 1. Extraer WhatsApp desde MongoDB

```bash
python extraer_datos_entrenamiento.py \
  --whatsapp-mongodb \
  --limite 1000 \
  --salida whatsapp_entrenamiento.json
```

#### 2. Extraer WhatsApp desde Archivo JSON

```bash
python extraer_datos_entrenamiento.py \
  --whatsapp-archivo conversaciones_backup.json \
  --salida whatsapp_entrenamiento.json
```

#### 3. Extraer Mercado Libre desde Archivo

```bash
python extraer_datos_entrenamiento.py \
  --mercado-libre-archivo preguntas_ml.json \
  --salida mercado_libre_entrenamiento.json
```

#### 4. Extraer Mercado Libre desde API

```bash
python extraer_datos_entrenamiento.py \
  --mercado-libre-api \
  --access-token TU_TOKEN_ML \
  --seller-id TU_SELLER_ID \
  --limite 500 \
  --salida mercado_libre_entrenamiento.json
```

## 📋 Opciones Completas

### Parámetros de Extracción

- `--whatsapp-mongodb`: Extrae conversaciones desde MongoDB
- `--whatsapp-archivo ARCHIVO`: Extrae desde archivo JSON de WhatsApp
- `--mercado-libre-archivo ARCHIVO`: Extrae desde archivo JSON/CSV de Mercado Libre
- `--mercado-libre-api`: Extrae desde API de Mercado Libre
- `--access-token TOKEN`: Token de acceso para API de Mercado Libre
- `--seller-id ID`: ID del vendedor en Mercado Libre
- `--fecha-desde YYYY-MM-DD`: Fecha inicial para filtrar
- `--fecha-hasta YYYY-MM-DD`: Fecha final para filtrar
- `--limite N`: Límite de registros a extraer
- `--salida ARCHIVO`: Archivo de salida (default: `datos_entrenamiento.json`)
- `--formato json|csv`: Formato de salida (default: `json`)

## 📁 Estructura de Datos Extraídos

### Formato de WhatsApp

```json
{
  "source": "whatsapp",
  "session_id": "abc123",
  "phone": "59899123456",
  "timestamp": "2024-01-15T10:30:00",
  "message": "Hola, necesito información sobre Isodec",
  "response": "Hola! Te puedo ayudar con información sobre Isodec...",
  "response_type": "text",
  "confidence": 0.95,
  "intent": "consulta_producto",
  "entities": {
    "producto": "Isodec"
  },
  "metadata": {
    "source": "api",
    "original_id": "507f1f77bcf86cd799439011"
  }
}
```

### Formato de Mercado Libre

```json
{
  "source": "mercado_libre",
  "question_id": "MLQ123456",
  "product_id": "MLU123456789",
  "buyer_id": "123456789",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "question": "¿Este producto tiene garantía?",
  "answer": "Sí, tiene garantía de 1 año",
  "status": "ANSWERED",
  "product_title": "Isodec Panel Aislante 100mm",
  "metadata": {
    "source": "api",
    "api_version": "v1"
  }
}
```

## 🔧 Ejemplos de Uso

### Extraer Últimos 30 Días de WhatsApp

```bash
python extraer_datos_entrenamiento.py \
  --whatsapp-mongodb \
  --fecha-desde 2024-01-01 \
  --fecha-hasta 2024-01-31 \
  --salida whatsapp_enero_2024.json
```

### Combinar Múltiples Fuentes

```bash
python extraer_datos_entrenamiento.py \
  --whatsapp-mongodb \
  --mercado-libre-archivo preguntas_ml.json \
  --salida datos_combinados.json \
  --formato json
```

### Exportar a CSV para Análisis

```bash
python extraer_datos_entrenamiento.py \
  --whatsapp-mongodb \
  --limite 5000 \
  --salida datos_entrenamiento.csv \
  --formato csv
```

## 🔐 Configuración de Mercado Libre API

### Obtener Token de Acceso

1. Ve a [Mercado Libre Developers](https://developers.mercadolibre.com/)
2. Crea una aplicación
3. Obtén tu `access_token` y `seller_id`

### Variables de Entorno (Opcional)

Puedes configurar en `.env`:

```env
MONGODB_URI=mongodb://localhost:27017/bmc_chat
MERCADO_LIBRE_ACCESS_TOKEN=TU_TOKEN
MERCADO_LIBRE_SELLER_ID=TU_SELLER_ID
```

## 📊 Formato de Archivos de Entrada

### WhatsApp JSON

```json
[
  {
    "session_id": "abc123",
    "phone": "59899123456",
    "message": "Hola",
    "response": "Hola! ¿Cómo puedo ayudarte?",
    "timestamp": "2024-01-15T10:30:00",
    "intent": "saludo"
  }
]
```

### Mercado Libre JSON

```json
[
  {
    "id": "MLQ123456",
    "item_id": "MLU123456789",
    "text": "¿Tiene garantía?",
    "answer": {
      "text": "Sí, 1 año"
    },
    "date_created": "2024-01-15T10:30:00.000Z",
    "status": "ANSWERED"
  }
]
```

### Mercado Libre CSV

```csv
question_id,item_id,text,answer,date_created,status
MLQ123456,MLU123456789,"¿Tiene garantía?","Sí, 1 año",2024-01-15T10:30:00.000Z,ANSWERED
```

## 🎯 Uso de Datos para Entrenamiento

Los datos extraídos están listos para usar en:

1. **Fine-tuning de modelos**: Formato JSON compatible con OpenAI, HuggingFace, etc.
2. **Análisis de intents**: Datos estructurados con intents y entidades
3. **Mejora de respuestas**: Preguntas y respuestas emparejadas
4. **Análisis de patrones**: Datos históricos para identificar tendencias

### Ejemplo de Uso en Python

```python
import json
from extraer_datos_entrenamiento import ExtractorDatosEntrenamiento

# Crear extractor
extractor = ExtractorDatosEntrenamiento()

# Extraer WhatsApp
datos_wa = extractor.extraer_whatsapp_mongodb(limite=1000)

# Extraer Mercado Libre
datos_ml = extractor.extraer_mercado_libre_archivo("preguntas_ml.json")

# Combinar y guardar
todos_los_datos = datos_wa + datos_ml
extractor.guardar_para_entrenamiento(todos_los_datos, "datos_combinados.json")

# Generar resumen
resumen = extractor.generar_resumen(todos_los_datos)
print(json.dumps(resumen, indent=2))
```

## ⚠️ Notas Importantes

1. **Privacidad**: Los datos extraídos contienen información sensible. Asegúrate de:
   - Anonimizar números de teléfono si es necesario
   - No compartir datos sin consentimiento
   - Cumplir con GDPR/LGPD según corresponda

2. **Límites de API**: La API de Mercado Libre tiene límites de rate. El script respeta estos límites.

3. **Formato de Fechas**: Usa formato `YYYY-MM-DD` para filtros de fecha.

4. **MongoDB**: Asegúrate de que MongoDB esté corriendo y accesible antes de extraer.

## 🐛 Solución de Problemas

### Error: "MongoDB connection failed"

- Verifica que MongoDB esté corriendo
- Revisa la URI de conexión en `MONGODB_URI`
- Verifica credenciales si usas autenticación

### Error: "Archivo no encontrado"

- Verifica la ruta del archivo
- Usa rutas absolutas si es necesario

### Error: "API de Mercado Libre error 401"

- Verifica que el `access_token` sea válido
- El token puede haber expirado, genera uno nuevo

## 📞 Soporte

Para más información, consulta:
- Documentación de MongoDB: https://docs.mongodb.com/
- API de Mercado Libre: https://developers.mercadolibre.com/




