# Simulated Workflow Testing Mode

## Overview

This simulated workflow allows you to test the chatbot locally without any external WhatsApp integration. It uses the **actual chatbot logic and workflows** to process messages, populate the knowledge base, and iterate on prompts rapidly.

## Quick Start

### 1. Start Required Services

```bash
# Start MongoDB (if using Docker)
docker-compose up -d mongodb

# Start Python API server
python api_server.py
```

### 2. Test with CLI

```bash
# Interactive chat
python simulate_chat_cli.py

# Or simple simulator
python simulate_chat.py
```

### 3. Test with Web UI

```bash
# Start Next.js app (if not already running)
npm run dev

# Open simulator
http://localhost:3000/simulator
```

## Features

### Interactive CLI (`simulate_chat_cli.py`)

Enhanced command-line interface with commands:

- `/help` - Show available commands
- `/new` - Start new session
- `/phone <num>` - Set phone number
- `/history` - Show conversation history
- `/export` - Export conversation to JSON
- `/load <file>` - Load conversation from JSON
- `/stats` - Show knowledge base statistics
- `/clear` - Clear screen
- `/exit` or `/quit` - Exit chat

### Simple Simulator (`simulate_chat.py`)

Basic interactive chat:

```bash
python simulate_chat.py
```

Or batch mode:

```bash
python simulate_chat.py --batch test_scenarios/quote_request.json
```

### Knowledge Base Populator (`populate_kb.py`)

Run multiple scenarios to populate the knowledge base:

```bash
# Populate with all scenarios
python populate_kb.py

# Use specific directory
python populate_kb.py --scenarios test_scenarios/

# Quiet mode
python populate_kb.py --quiet
```

## Test Scenarios

Pre-defined test scenarios in `test_scenarios/`:

- `quote_request.json` - Complete quote flows
- `product_info.json` - Product information requests
- `multi_turn.json` - Multi-turn conversations
- `edge_cases.json` - Error handling and edge cases

## Configuration

Edit `simulate_config.json`:

```json
{
  "api_url": "http://localhost:8000",
  "mongodb_uri": "mongodb://localhost:27017/bmc_chat",
  "use_real_openai": true,
  "use_pattern_matching_fallback": true,
  "persist_to_kb": true,
  "session_timeout": 3600,
  "default_phone": "+59891234567"
}
```

## Development Workflow

1. **Start services**: MongoDB and Python API
2. **Test conversation**: Use CLI or web UI
3. **Review response**: Check type, confidence, actions
4. **Adjust prompts**: Edit `ia_conversacional_integrada.py`
5. **Restart API**: `python api_server.py`
6. **Test again**: Same input, compare responses
7. **Populate KB**: Run scenarios to build knowledge base
8. **Iterate**: Repeat until satisfied

## Example Session

```bash
$ python simulate_chat_cli.py

🤖 BMC Chatbot Simulator - Enhanced CLI
======================================================================
API: http://localhost:8000
Phone: +59891234567

✅ API server is running

📱 Started new session: sim_20240101_120000_abc12345
   Phone: +59891234567

👤 You: Hola, necesito información sobre Isodec

🤖 Bot: ¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay...
   Tipo: informacion
   Confianza: 0.95

👤 You: Quiero cotizar para mi casa

🤖 Bot: ¡Perfecto! Vamos a crear tu cotización paso a paso...
   Tipo: cotizacion
   Confianza: 0.90
   Necesita datos: producto, dimensiones, espesor

👤 You: 10 metros por 5 metros, Isodec, 100mm

🤖 Bot: 🎉 ¡COTIZACIÓN LISTA!...
   Tipo: cotizacion
   Confianza: 0.95

👤 You: /export
💾 Conversation exported to: conversation_sim_20240101_120000_abc12345.json
```

## Knowledge Base Population

Run scenarios to build the knowledge base:

```bash
$ python populate_kb.py

📚 Knowledge Base Populator
======================================================================
Scenarios directory: test_scenarios
API URL: http://localhost:8000
MongoDB URI: mongodb://localhost:27017/bmc_chat

✅ Loaded 3 scenarios from quote_request.json
✅ Loaded 3 scenarios from product_info.json
✅ Loaded 2 scenarios from multi_turn.json
✅ Loaded 5 scenarios from edge_cases.json

📋 Found 13 scenarios to run

[1/13] Running scenario...
📋 Scenario: Complete Quote Request Flow
...

📊 Population Summary
======================================================================
Total scenarios: 13
Total messages: 45
Successful: 43
Failed: 2
Conversations created: 13

📚 Knowledge Base Statistics:
   Total interactions: 43
   By type:
     - cotizacion: 25
     - informacion: 15
     - general: 3
```

## Benefits

1. **Rapid Iteration**: Test changes immediately
2. **Real Logic**: Uses actual chatbot code
3. **Knowledge Base**: Populates real database
4. **Cost Effective**: No WhatsApp API costs
5. **Development Friendly**: No external dependencies
6. **Architecture Validation**: Test workflow logic
7. **Prompt Tuning**: Iterate on prompts quickly
8. **Regression Testing**: Replay conversations

## Troubleshooting

### API Connection Error

```
❌ Cannot connect to API. Is the server running?
   Try: python api_server.py
```

**Solution**: Start the API server first

### MongoDB Connection Error

```
⚠️ MongoDB connection failed: ...
   Continuing without MongoDB persistence
```

**Solution**: Start MongoDB or check connection string

### OpenAI API Error

The system will automatically fallback to pattern matching if OpenAI fails.

## Next Steps

- Test different conversation flows
- Populate knowledge base with scenarios
- Iterate on prompts and responses
- Export conversations for analysis
- Compare OpenAI vs pattern matching

