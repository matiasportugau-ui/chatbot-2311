# 🤖 Multimodal Training System - User Guide

## Overview

The Multimodal Training System transforms the BMC Uruguay chatbot into an intelligent, self-learning sales assistant that can process audio, images, documents, and text while continuously improving through agent feedback.

## Architecture

### 1. Dynamic Truth Layer (Priority-based Knowledge)

```
┌─────────────────────────────────────┐
│  Level 1: dynamic_knowledge.json   │  ← PRIORITY
│  - Agent corrections                │
│  - Real-time updates                │
│  - Conflict resolution              │
└─────────────────────────────────────┘
           ↓ (if no match)
┌─────────────────────────────────────┐
│  Level 2: Static Knowledge Base     │
│  - conocimiento_consolidado.json    │
│  - Original product manuals         │
│  - Historical interactions          │
└─────────────────────────────────────┘
```

**Rule**: The system ALWAYS searches Level 1 first. If there's a contradiction, Level 1 WINS.

### 2. Multimodal Pipeline

```
Input → MultimodalProcessor
  ├── 🎤 Audio → Whisper (OpenAI) → Text transcription
  ├── 📷 Image → GPT-4o Vision → Analysis & description
  ├── 📄 Document (PDF/TXT) → Text extraction
  └── 💬 Text → Direct processing
```

### 3. Human-in-the-Loop Training

```
Agent sends message
   ↓
Check for training commands
   ├── "MODO ENTRENAMIENTO" → Activate training mode
   ├── "MODO PRODUCCIÓN" → Deactivate training mode
   ↓
Check for correction emojis
   ├── ❌ → Capture correction
   ├── ✅ → Approve correction
   ├── ⚠️ → Flag uncertainty
   ↓
Process with bot logic
   ↓
Calculate confidence score
   ├── < 0.8 → Trigger doubt gate
   └── ≥ 0.8 → Direct response
   ↓
Update dynamic_knowledge.json
```

## Installation

### Prerequisites

1. Python 3.8 or higher
2. OpenAI API key (for multimodal processing)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-4o"  # or gpt-4o-mini

# Verify installation
python3 test_multimodal_integration.py
```

## Usage

### Basic Text Chat

```python
from ia_conversacional_integrada import IAConversacionalIntegrada

ia = IAConversacionalIntegrada()

# Process a message
respuesta = ia.procesar_mensaje(
    mensaje="¿Cuál es el precio del Isodec?",
    cliente_id="agent_001",
    sesion_id="session_123"
)

print(respuesta.mensaje)
print(f"Confidence: {respuesta.confianza}")
```

### Multimodal Processing

```python
# Text message
respuesta = ia.procesar_mensaje_multimodal(
    mensaje="¿Qué productos tienen?",
    cliente_id="agent_001",
    sesion_id="session_123",
    mensaje_tipo="text"
)

# Audio message (WhatsApp voice note)
respuesta = ia.procesar_mensaje_multimodal(
    mensaje=audio_bytes,  # or path to audio file
    cliente_id="agent_001",
    sesion_id="session_123",
    mensaje_tipo="audio"
)

# Image message (product photo)
respuesta = ia.procesar_mensaje_multimodal(
    mensaje=image_bytes,  # or path to image file
    cliente_id="agent_001",
    sesion_id="session_123",
    mensaje_tipo="image"
)

# Document (PDF technical specs)
respuesta = ia.procesar_mensaje_multimodal(
    mensaje="path/to/document.pdf",
    cliente_id="agent_001",
    sesion_id="session_123",
    mensaje_tipo="document"
)
```

### Training Mode

#### 1. Activate Training Mode

Agent sends: `MODO ENTRENAMIENTO`

Bot responds:
```
🎓 Modo de entrenamiento activado. 
Puedes corregir mis respuestas usando ❌ 
o diciéndome la información correcta.
```

#### 2. Make a Correction

**Agent conversation:**
- Agent: "¿Cuál es el precio del Isodec 100mm?"
- Bot: "El precio es 1200 UYU por m²"
- Agent: "❌ El precio correcto es 1500 UYU por m²"
- Bot: 
  ```
  📝 Corrección recibida:
  
  El precio correcto es 1500 UYU por m²
  
  ¿Deseas que actualice mi base de conocimiento 
  con esta información? Responde ✅ para aprobar 
  o ❌ para cancelar.
  ```

#### 3. Approve Correction

Agent sends: `✅`

Bot responds:
```
✅ ¡Perfecto! He actualizado mi base de 
conocimiento con esta corrección. 
Gracias por ayudarme a mejorar.
```

#### 4. Voice Corrections

Agent sends audio: *"No, el precio es mil quinientos pesos"*

Bot will:
1. Transcribe the audio using Whisper
2. Extract the correction (precio = 1500)
3. Ask for approval
4. Update the knowledge base

### Doubt Gate (Automatic Verification)

When confidence is low (< 0.8), the bot automatically asks for verification:

```
⚠️ Verificando con mi base de entrenamiento...

[Bot's response]

¿Esta información es correcta? Si no lo es, 
indícamelo con ❌ y dime cuál es la respuesta correcta.
```

## Benchmark System

### Running Benchmarks

```python
from benchmark_system import BenchmarkSystem
from ia_conversacional_integrada import IAConversacionalIntegrada

# Initialize
benchmark = BenchmarkSystem()
ia = IAConversacionalIntegrada()

# Run all tests
results = benchmark.run_benchmark(ia)

# Run specific tests
results = benchmark.run_benchmark(
    ia, 
    test_cases=["test_001_isodec_price", "test_002_isodec_specs"]
)
```

### Benchmark Output

```
============================================================
🎯 RUNNING BENCHMARK TESTS
============================================================

▶️  Running: test_001_isodec_price (quotation)
   Input: ¿Cuál es el precio del Isodec de 100mm?
   ✅ PASS - Score: 85.5/100 - Confidence: 0.90
   Keywords: 80% - Source: dynamic

============================================================
📊 BENCHMARK SUMMARY
============================================================
Total Tests: 5
Passed: 4 | Failed: 1
Pass Rate: 80.0%
Average Score: 78.2/100
Average Confidence: 0.82
Keyword Coverage: 75.0%

📚 Knowledge Sources:
   Dynamic: 3 (60.0%)
   Static: 2 (40.0%)

📈 Learning Metrics:
   Score Improvement: +12.3 (+15.7%)
   Dynamic Usage Improvement: +25.0%
   Historical Runs: 3
============================================================
```

### Learning Rate Metrics

The benchmark tracks:
- **Score Improvement**: How much better the bot performs over time
- **Dynamic Knowledge Usage**: % of responses using agent corrections vs static knowledge
- **Historical Comparison**: Performance trend across multiple runs

## Dynamic Knowledge Structure

### dynamic_knowledge.json

```json
{
  "metadata": {
    "version": "1.0.0",
    "total_corrections": 15,
    "total_conflicts": 2
  },
  "corrections": {
    "prices": {
      "isodec_100mm": {
        "product": "Isodec",
        "thickness": "100mm",
        "price_per_m2": 1500.00,
        "currency": "UYU",
        "last_updated": "2025-12-21T10:30:00",
        "source_agent": "agent_001",
        "keywords": ["isodec", "precio", "100mm"]
      }
    },
    "technical_specs": {},
    "procedures": {},
    "responses": {}
  },
  "conflicts": [
    {
      "correction_id": "isodec_100mm",
      "existing_data": {...},
      "new_data": {...},
      "status": "pending_resolution"
    }
  ],
  "learning_history": [...]
}
```

## Conflict Resolution

When two agents provide different corrections:

```python
from dynamic_knowledge_manager import DynamicKnowledgeManager

manager = DynamicKnowledgeManager()

# View pending conflicts
stats = manager.get_statistics()
pending = stats['dynamic']['pending_conflicts']

# Resolve conflict
manager.resolve_conflict(
    conflict_index=0,
    resolution="use_new"  # or "keep_existing" or "merge"
)
```

## WhatsApp Integration

### Setup

```python
from integracion_whatsapp import IntegracionWhatsApp

# Initialize with multimodal support
whatsapp = IntegracionWhatsApp(ia)

# The webhook will automatically handle:
# - Text messages → Direct processing
# - Audio messages → Whisper transcription
# - Image messages → GPT-4o Vision analysis
# - Training emojis → Correction capture
```

### Message Flow

```
WhatsApp Business API
   ↓
Webhook receives message
   ↓
Detect message type (text/audio/image)
   ↓
Process with procesar_mensaje_multimodal()
   ↓
Check for training feedback
   ↓
Generate response
   ↓
Send back to WhatsApp
```

## Best Practices

### For Sales Agents

1. **Always use training mode** when testing new products or prices
2. **Be specific** in corrections: Include units, context, and details
3. **Use voice corrections** for complex information - it's faster
4. **Review the bot's response** before approving corrections
5. **Use emojis consistently**:
   - ❌ for corrections
   - ✅ for approval
   - ⚠️ when unsure

### For System Administrators

1. **Run benchmarks regularly** to track improvement
2. **Review conflicts daily** and resolve them promptly
3. **Monitor dynamic_knowledge.json** size - archive old corrections
4. **Set up automated backups** of the knowledge base
5. **Check learning_history** to understand what agents are teaching

## Troubleshooting

### Issue: Multimodal processing not working

**Solution**: Check that OPENAI_API_KEY is set:
```bash
echo $OPENAI_API_KEY
```

### Issue: Corrections not persisting

**Solution**: Check file permissions on dynamic_knowledge.json:
```bash
chmod 664 dynamic_knowledge.json
```

### Issue: Low confidence scores

**Solution**: 
1. Run benchmark to identify weak areas
2. Add more agent corrections for those topics
3. Review and improve static knowledge base

### Issue: Conflicts not resolving

**Solution**: Use the conflict resolution API:
```python
manager = DynamicKnowledgeManager()
stats = manager.get_statistics()
print(f"Pending conflicts: {stats['dynamic']['pending_conflicts']}")

# Review and resolve
manager.resolve_conflict(0, "use_new")
```

## API Reference

### procesar_mensaje_multimodal()

```python
def procesar_mensaje_multimodal(
    self,
    mensaje: Any,              # Text, bytes, or file path
    cliente_id: str,           # Agent/client ID
    sesion_id: str = None,     # Session ID (auto-generated if None)
    mensaje_tipo: str = "text",# "text", "audio", "image", "document", "auto"
    metadata: Optional[dict] = None  # Additional metadata
) -> RespuestaIA
```

### HumanInLoopTrainer.process_message()

```python
def process_message(
    self,
    agent_id: str,              # Agent ID
    message: str,               # Message content
    message_type: str = "text", # Message type
    previous_response: Optional[str] = None  # Previous bot response
) -> dict[str, Any]  # Returns action, response, and metadata
```

### DynamicKnowledgeManager.add_correction()

```python
def add_correction(
    self,
    correction_type: str,    # "products", "prices", "technical_specs", etc.
    correction_id: str,      # Unique ID
    correction_data: dict,   # Correction data
    source_agent: str        # Agent who made the correction
) -> bool  # Returns True if successful
```

## Performance Metrics

### Expected Performance

- **Text Processing**: < 100ms
- **Audio Transcription**: 1-3 seconds (depends on audio length)
- **Image Analysis**: 2-5 seconds
- **Document Processing**: 0.5-2 seconds (depends on PDF size)
- **Knowledge Query**: < 50ms

### Confidence Thresholds

- **≥ 0.9**: High confidence - direct response
- **0.8-0.9**: Good confidence - response with minor doubt
- **< 0.8**: Low confidence - triggers doubt gate

### Learning Rate

Expected improvement per 100 corrections:
- **Score**: +10-15%
- **Dynamic Usage**: +20-30%
- **Confidence**: +0.05-0.10

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run integration tests: `python3 test_multimodal_integration.py`
3. Review benchmark results for specific failures
4. Check logs in the console output

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-21  
**Status**: ✅ Production Ready
