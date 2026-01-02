# Language Module - Quick Reference Guide

## Quick Start

### Basic Usage

```python
from language_processor import get_language_processor

# Get processor instance
processor = get_language_processor()

# Process a message
result = processor.process_message(
    "Hola, necesito cotizar Isodec 100mm para 50m2",
    session_id="user_123"
)

# Access results
print(f"Language: {result.language.value}")      # "es"
print(f"Intent: {result.intent.value}")          # "cotizacion"
print(f"Confidence: {result.confidence}")        # 0.85
print(f"Entities: {result.entities}")            # {...}
```

## API Reference

### LanguageProcessor

#### `process_message(message: str, session_id: Optional[str] = None) -> ProcessedMessage`

Process a message and return structured result.

**Parameters:**
- `message`: Input text to process
- `session_id`: Optional session ID for context management

**Returns:** `ProcessedMessage` object

**Example:**
```python
result = processor.process_message("Cotizar Isodec", "session_1")
```

### ProcessedMessage

Result object containing:
- `original`: Original input text
- `normalized`: Normalized text
- `language`: Detected language (Language enum)
- `intent`: Classified intent (Intent enum)
- `entities`: Extracted entities (dict)
- `confidence`: Confidence score (0.0-1.0)
- `timestamp`: Processing timestamp
- `session_id`: Session ID
- `context`: Conversation context (if available)

### Intent Enum

Available intents:
- `Intent.SALUDO` - Greeting
- `Intent.DESPEDIDA` - Farewell
- `Intent.COTIZACION` - Quote request
- `Intent.INFORMACION` - Information request
- `Intent.PREGUNTA` - Question
- `Intent.PRODUCTO` - Product inquiry
- `Intent.INSTALACION` - Installation inquiry
- `Intent.SERVICIO` - Service inquiry
- `Intent.OBJECION` - Objection handling
- `Intent.GENERAL` - General/unknown
- `Intent.ERROR` - Error state

### Language Enum

Supported languages:
- `Language.SPANISH` - Spanish ("es")
- `Language.ENGLISH` - English ("en")
- `Language.PORTUGUESE` - Portuguese ("pt")
- `Language.UNKNOWN` - Unknown language

### Entities Structure

```python
{
    'products': [
        {
            'id': 'isodec',
            'name': 'isodec',
            'confidence': 0.9
        }
    ],
    'dimensions': {
        'largo': 10.0,
        'ancho': 5.0,
        'confidence': 0.8
    },
    'thickness': {
        'value': '100mm',
        'confidence': 0.9
    },
    'color': {
        'value': 'blanco',
        'confidence': 0.8
    },
    'phone': {
        'value': '+59812345678',
        'confidence': 0.9
    },
    'services': {
        'flete': False,
        'instalacion': False,
        'accesorios': False
    }
}
```

## Common Patterns

### 1. Intent-Based Routing

```python
result = processor.process_message(message, session_id)

if result.intent == Intent.COTIZACION:
    # Handle quote request
    handle_quote(result)
elif result.intent == Intent.INFORMACION:
    # Handle information request
    handle_info(result)
elif result.intent == Intent.SALUDO:
    # Handle greeting
    handle_greeting(result)
```

### 2. Entity Extraction

```python
result = processor.process_message(message, session_id)

# Check for products
if result.entities.get('products'):
    product = result.entities['products'][0]['id']
    print(f"Product detected: {product}")

# Check for dimensions
if result.entities.get('dimensions'):
    dims = result.entities['dimensions']
    if 'largo' in dims and 'ancho' in dims:
        area = dims['largo'] * dims['ancho']
        print(f"Area: {area}m²")
```

### 3. Context-Aware Processing

```python
# First message
result1 = processor.process_message("Hola", "session_1")
# result1.intent = Intent.SALUDO

# Follow-up message (uses context)
result2 = processor.process_message("Quiero cotizar", "session_1")
# result2.context contains previous intent
# Better classification due to context
```

### 4. Confidence-Based Handling

```python
result = processor.process_message(message, session_id)

if result.confidence > 0.8:
    # High confidence - proceed automatically
    process_automatically(result)
elif result.confidence > 0.5:
    # Medium confidence - ask for confirmation
    ask_confirmation(result)
else:
    # Low confidence - ask for clarification
    ask_clarification(result)
```

### 5. Language-Specific Handling

```python
result = processor.process_message(message, session_id)

if result.language == Language.SPANISH:
    response = generate_spanish_response(result)
elif result.language == Language.ENGLISH:
    response = generate_english_response(result)
elif result.language == Language.PORTUGUESE:
    response = generate_portuguese_response(result)
```

## Integration Examples

### With Existing Chat System

```python
from language_processor import get_language_processor
from chat_interactivo import AgenteInteractivo

class EnhancedAgent:
    def __init__(self):
        self.agent = AgenteInteractivo()
        self.processor = get_language_processor()
    
    def process(self, message: str, session_id: str):
        # Pre-process with language module
        processed = self.processor.process_message(message, session_id)
        
        # Use extracted entities for better processing
        if processed.intent == Intent.COTIZACION:
            # Enhance message with extracted entities
            enhanced = self._enhance_message(processed)
            return self.agent.procesar_mensaje(enhanced)
        else:
            return self.agent.procesar_mensaje(message)
```

### With API Endpoint

```python
from fastapi import FastAPI
from language_processor import get_language_processor

app = FastAPI()
processor = get_language_processor()

@app.post("/api/process")
async def process_message(message: str, session_id: str):
    result = processor.process_message(message, session_id)
    return {
        'intent': result.intent.value,
        'confidence': result.confidence,
        'entities': result.entities,
        'language': result.language.value
    }
```

## Performance Tips

1. **Use Caching**: The processor caches results automatically
   ```python
   # Same message processed twice - second time uses cache
   result1 = processor.process_message("Hola", "session_1")
   result2 = processor.process_message("Hola", "session_2")  # Uses cache
   ```

2. **Reuse Processor Instance**: Don't create new instances
   ```python
   # Good
   processor = get_language_processor()
   result1 = processor.process_message(msg1)
   result2 = processor.process_message(msg2)
   
   # Bad
   processor1 = LanguageProcessor()
   processor2 = LanguageProcessor()  # Creates new cache
   ```

3. **Use Session IDs**: Enables context management
   ```python
   # With context (better)
   result = processor.process_message(msg, session_id="user_123")
   
   # Without context (no conversation history)
   result = processor.process_message(msg)
   ```

## Troubleshooting

### Low Confidence Scores

**Problem:** Confidence < 0.5

**Solutions:**
- Check if message is too short
- Verify language detection is correct
- Add more keywords to intent patterns
- Use context from previous messages

### Missing Entities

**Problem:** Entities not extracted

**Solutions:**
- Check if product names match patterns
- Verify dimension format (e.g., "10m x 5m")
- Check if text normalization is working
- Review entity extraction patterns

### Language Detection Issues

**Problem:** Wrong language detected

**Solutions:**
- Use longer messages (more context)
- Consider using `langdetect` library
- Add language hints if available
- Check language patterns

## Statistics & Monitoring

```python
# Get processing statistics
stats = processor.export_stats()
print(f"Cache size: {stats['cache_size']}")
print(f"Active sessions: {stats['context_sessions']}")
```

## Migration Checklist

- [ ] Install language processor module
- [ ] Replace keyword matching with `process_message()`
- [ ] Update intent detection to use `result.intent`
- [ ] Replace entity extraction with `result.entities`
- [ ] Add session IDs for context management
- [ ] Update error handling
- [ ] Add monitoring/logging
- [ ] Test with real messages
- [ ] Monitor performance metrics

## Next Steps

1. Review `LANGUAGE_MODULE_ANALYSIS.md` for detailed analysis
2. Review `LANGUAGE_MODULE_BEST_PRACTICES.md` for best practices
3. Check `language_processor_integration_example.py` for integration examples
4. Test with your messages
5. Integrate gradually (start with 10% of traffic)
