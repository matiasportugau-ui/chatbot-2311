# Guía de Integración de Conocimiento

Esta guía explica cómo funciona la integración del conocimiento entrenado en el chatbot BMC.

## Descripción General

El sistema de conocimiento del chatbot se carga automáticamente al iniciar la aplicación. El conocimiento incluye:
- Interacciones previas con clientes
- Patrones de venta exitosos
- Conocimiento sobre productos
- Insights automáticos generados

## Carga Automática de Conocimiento

### Orden de Prioridad

El sistema intenta cargar conocimiento desde archivos JSON en el siguiente orden:

1. `base_conocimiento_final.json` - Base de conocimiento final (más completa)
2. `conocimiento_completo.json` - Conocimiento completo exportado
3. `base_conocimiento_exportada.json` - Base exportada
4. `base_conocimiento_demo.json` - Versión demo
5. `conocimiento_completo_demo.json` - Conocimiento demo

El sistema carga el **primer archivo encontrado** en este orden.

### Carga desde MongoDB (Opcional)

Si no se encuentra ningún archivo JSON, el sistema intenta cargar desde MongoDB si:
- La variable de entorno `MONGODB_URI` está configurada
- MongoDB está disponible y accesible

El sistema carga interacciones desde la colección `kb_interactions`.

## Estructura de Archivos de Conocimiento

Los archivos JSON de conocimiento deben tener la siguiente estructura:

```json
{
  "interacciones": [
    {
      "id": "unique_id",
      "timestamp": "2025-10-24T04:27:53",
      "cliente_id": "cliente_id",
      "tipo_interaccion": "consulta|cotizacion|venta",
      "mensaje_cliente": "Mensaje del cliente",
      "respuesta_agente": "Respuesta del agente",
      "contexto": {},
      "resultado": "exitoso|fallido|pendiente",
      "valor_cotizacion": null,
      "valor_venta": null,
      "satisfaccion_cliente": 1-5
    }
  ],
  "patrones_venta": [
    {
      "id": "patron_id",
      "nombre": "Nombre del patrón",
      "descripcion": "Descripción",
      "frecuencia": 10,
      "tasa_exito": 0.85,
      "factores_clave": ["factor1", "factor2"],
      "productos_asociados": ["isodec"],
      "estrategia_recomendada": "Estrategia recomendada"
    }
  ],
  "conocimiento_productos": {
    "isodec": {
      "producto_id": "isodec",
      "nombre": "Isodec",
      "caracteristicas_base": {},
      "caracteristicas_aprendidas": {},
      "objeciones_comunes": [],
      "respuestas_efectivas": []
    }
  },
  "metricas_evolucion": {},
  "insights_automaticos": []
}
```

## Cómo Agregar Nuevo Conocimiento

### Método 1: Exportar desde el Sistema

El sistema puede exportar conocimiento automáticamente:

```python
from base_conocimiento_dinamica import BaseConocimientoDinamica

base = BaseConocimientoDinamica()
base.exportar_conocimiento("mi_conocimiento.json")
```

### Método 2: Crear Manualmente

Puedes crear un archivo JSON siguiendo la estructura descrita arriba.

### Método 3: Usar el Script de Consolidación

Si tienes múltiples archivos de conocimiento, puedes consolidarlos:

```bash
python consolidar_conocimiento.py
```

Esto generará `conocimiento_consolidado.json` con todo el conocimiento combinado.

## Consolidación de Conocimiento

El script `consolidar_conocimiento.py` permite:

- **Combinar múltiples archivos**: Une todos los archivos de conocimiento en uno
- **Evitar duplicados**: Identifica y elimina interacciones duplicadas
- **Fusionar productos**: Combina conocimiento de productos de múltiples fuentes
- **Validar integridad**: Verifica que los datos sean válidos

### Uso

```bash
python consolidar_conocimiento.py
```

El script:
1. Busca todos los archivos de conocimiento
2. Consolida interacciones (evita duplicados)
3. Consolida patrones de venta
4. Fusiona conocimiento de productos
5. Valida la integridad
6. Guarda en `conocimiento_consolidado.json`

## Validación

### Validar Carga de Conocimiento

Para verificar que el conocimiento se carga correctamente:

```bash
python validar_integracion.py
```

Este script verifica:
- Que el conocimiento se carga al inicio
- Número de interacciones cargadas
- Número de patrones disponibles
- Productos disponibles
- Que las respuestas usan el conocimiento

### Usar el Chatbot con Conocimiento Cargado

**Opción A: API Server (recomendado)**
```bash
python api_server.py
```
El conocimiento se carga automáticamente al inicializar.

**Opción B: Chat Interactivo Simple**
```bash
python chat_interactivo.py
```
Usa una versión simplificada sin IA completa.

**Opción C: Chat Interactivo con IA Completa**
```bash
# En Windows PowerShell:
$env:CHAT_USE_FULL_IA="true"
python chat_interactivo.py

# En Linux/Mac:
CHAT_USE_FULL_IA=true python chat_interactivo.py
```
Usa la IA completa con conocimiento cargado.

### Probar Respuestas

Para probar que las respuestas mejoran con el conocimiento:

```bash
python test_respuestas_chatbot.py
```

Este script:
- Ejecuta preguntas de prueba comunes
- Analiza la calidad de las respuestas
- Genera un reporte de satisfacción

## Configuración

Puedes configurar el comportamiento de carga editando `config_conocimiento.json`:

```json
{
  "carga_conocimiento": {
    "habilitada": true,
    "archivos_prioridad": [...],
    "cargar_primer_archivo_encontrado": true,
    "intentar_mongodb": true
  }
}
```

## Análisis de Conocimiento

### Analizar Archivos Existentes

Para analizar qué archivos de conocimiento tienes y cuál es el más completo:

```bash
python analizar_conocimiento.py
```

Esto genera:
- `reporte_analisis_conocimiento.json` - Reporte detallado
- `reporte_analisis_conocimiento.txt` - Reporte en texto

### Analizar Escenarios de Prueba

Para ver qué escenarios de prueba están disponibles:

```bash
python analizar_escenarios.py
```

## Solución de Problemas

### El conocimiento no se carga

1. Verifica que existe al menos un archivo JSON de conocimiento
2. Verifica que el archivo tiene el formato correcto
3. Ejecuta `validar_integracion.py` para ver errores específicos

### Las respuestas son genéricas

1. Verifica que el conocimiento se cargó (ver logs al inicio)
2. Ejecuta `test_respuestas_chatbot.py` para ver qué preguntas fallan
3. Asegúrate de que el conocimiento tiene interacciones relevantes

### Hay duplicados

1. Usa `consolidar_conocimiento.py` para eliminar duplicados
2. Revisa los archivos fuente para identificar la fuente de duplicados

## Mejores Prácticas

1. **Exportar regularmente**: Exporta el conocimiento periódicamente para tener backups
2. **Consolidar antes de usar**: Si tienes múltiples archivos, consolida primero
3. **Validar después de cambios**: Siempre valida después de agregar nuevo conocimiento
4. **Mantener un archivo principal**: Usa `base_conocimiento_final.json` como archivo principal
5. **Documentar cambios**: Mantén notas sobre qué conocimiento agregaste y cuándo

## Próximos Pasos

Después de integrar el conocimiento:

1. Ejecuta `validar_integracion.py` para verificar que todo funciona
2. Ejecuta `test_respuestas_chatbot.py` para probar las respuestas
3. Prueba el chatbot con preguntas reales
4. Monitorea las respuestas y ajusta el conocimiento según sea necesario

