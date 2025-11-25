# 🤖 Configuración de OpenAI para el Chatbot BMC

## Estado Actual

El sistema **SÍ tiene integración con OpenAI**, pero actualmente está funcionando en modo **pattern matching** porque:

1. ✅ El código de integración está completo
2. ⚠️ El paquete `openai` puede no estar instalado
3. ⚠️ La variable de entorno `OPENAI_API_KEY` no está configurada

## ¿Qué significa esto?

### Modo Actual: Pattern Matching
- ✅ Funciona sin OpenAI
- ✅ Respuestas basadas en patrones predefinidos
- ✅ Base de conocimiento integrada
- ⚠️ Respuestas más limitadas y menos flexibles

### Modo con OpenAI: IA Avanzada
- ✅ Respuestas más naturales y contextuales
- ✅ Mejor comprensión de intenciones complejas
- ✅ Manejo de errores de tipeo y variaciones
- ✅ Function calling para acciones automáticas
- ⚠️ Requiere API key de OpenAI (tiene costo)

## Cómo Activar OpenAI

### Paso 1: Instalar el Paquete

```bash
pip install openai>=1.0.0
```

O instalar todas las dependencias:

```bash
pip install -r requirements.txt
```

### Paso 2: Obtener API Key de OpenAI

1. Ve a: https://platform.openai.com/api-keys
2. Inicia sesión o crea una cuenta
3. Crea una nueva API key
4. Copia la clave (empieza con `sk-...`)

### Paso 3: Configurar la Variable de Entorno

#### Opción A: Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-tu-api-key-aqui"
```

#### Opción B: Windows (CMD)
```cmd
set OPENAI_API_KEY=sk-tu-api-key-aqui
```

#### Opción C: Crear archivo .env (Recomendado)
Crea un archivo `.env` en la raíz del proyecto:

```
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
```

Y el sistema lo cargará automáticamente.

### Paso 4: Verificar la Configuración

Ejecuta el chatbot y deberías ver:

```
✅ OpenAI integration enabled
```

En lugar de:

```
⚠️ OPENAI_API_KEY not set, using pattern matching only
```

## Funcionalidades con OpenAI

Cuando OpenAI está activo, el sistema puede:

1. **Function Calling**:
   - Crear cotizaciones automáticamente
   - Validar datos de cotización
   - Consultar estado de cotizaciones
   - Actualizar base de conocimiento
   - Enviar mensajes por WhatsApp

2. **Comprensión Avanzada**:
   - Entender intenciones complejas
   - Manejar errores de tipeo
   - Contexto de conversación mejorado
   - Respuestas más naturales

3. **Modelo Configurable**:
   - Por defecto: `gpt-4o-mini` (económico)
   - Configurable con: `OPENAI_MODEL=gpt-4` (más potente)

## Costos de OpenAI

- **gpt-4o-mini**: ~$0.15 por 1M tokens de entrada, ~$0.60 por 1M tokens de salida
- **gpt-4**: Más costoso pero más potente
- Para un chatbot de cotizaciones, el costo es muy bajo (centavos por conversación)

## Verificación Rápida

Para verificar si OpenAI está funcionando:

```python
python -c "from ia_conversacional_integrada import IAConversacionalIntegrada; ia = IAConversacionalIntegrada(); print('OpenAI activo' if ia.use_ai else 'OpenAI NO activo')"
```

## Recomendación

Para desarrollo y pruebas:
- ✅ Usa **pattern matching** (gratis, suficiente para la mayoría de casos)

Para producción:
- ✅ Activa **OpenAI** para mejor experiencia de usuario
- ✅ Usa `gpt-4o-mini` para balance costo/calidad

## Nota Importante

El sistema funciona perfectamente **sin OpenAI**. La integración es opcional y mejora la experiencia, pero no es requerida para el funcionamiento básico.

