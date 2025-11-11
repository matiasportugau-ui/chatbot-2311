# Quick Start: Simulated Workflow Testing

## 🚀 Fastest Way to Start Testing

### Option 1: Use the Start Script (Recommended)

```bash
./start_simulator.sh
```

This script will:
- Check if API server is running
- Start it if needed
- Give you options to choose from

### Option 2: Manual Start

#### Step 1: Start API Server

```bash
python api_server.py
```

Keep this terminal open. The server runs on `http://localhost:8000`

#### Step 2: In a New Terminal, Start Simulator

**Enhanced CLI (Recommended):**
```bash
python simulate_chat_cli.py
```

**Simple Simulator:**
```bash
python simulate_chat.py
```

**Populate Knowledge Base:**
```bash
python populate_kb.py
```

## 📱 Testing from Cursor

You can send messages directly from Cursor by:

1. **Using the CLI in terminal:**
   ```bash
   cd /path/to/05_dashboard_ui
   python simulate_chat_cli.py
   ```

2. **Using the Web UI:**
   - Start Next.js: `npm run dev`
   - Open: `http://localhost:3000/simulator`
   - Type messages and see responses

## 💬 Example Conversation

```
👤 You: Hola, necesito información sobre Isodec

🤖 Bot: ¡Hola! Soy tu asistente de cotizaciones de BMC Uruguay...
   Tipo: informacion
   Confianza: 95%

👤 You: Quiero cotizar para mi casa, 10 metros por 5 metros

🤖 Bot: ¡Perfecto! Vamos a crear tu cotización paso a paso...
   Tipo: cotizacion
   Confianza: 90%
   Necesita datos: espesor, color

👤 You: 100mm, blanco

🤖 Bot: 🎉 ¡COTIZACIÓN LISTA!
   Tipo: cotizacion
   Confianza: 95%
```

## 🎯 What Gets Tested

- ✅ Real chatbot logic (`ia_conversacional_integrada.py`)
- ✅ Real OpenAI API (if key provided) or pattern matching
- ✅ Real quote generation (`sistema_cotizaciones.py`)
- ✅ Real knowledge base updates (MongoDB)
- ✅ Real conversation context and sessions

## 📊 Knowledge Base Population

Run test scenarios to build knowledge base:

```bash
python populate_kb.py
```

This will:
- Run all scenarios from `test_scenarios/`
- Save conversations to MongoDB
- Generate knowledge base insights
- Export results for analysis

## 🔄 Development Workflow

1. **Test**: Send message via CLI/UI
2. **Review**: Check response quality
3. **Adjust**: Edit prompts in `ia_conversacional_integrada.py`
4. **Restart**: Restart API server
5. **Test Again**: Same input, compare responses
6. **Iterate**: Repeat until satisfied

## 📝 CLI Commands

When using `simulate_chat_cli.py`:

- `/help` - Show commands
- `/new` - New session
- `/phone <num>` - Set phone
- `/history` - Show history
- `/export` - Export conversation
- `/stats` - KB statistics
- `/exit` - Quit

## 🐛 Troubleshooting

**API not running:**
```bash
python api_server.py
```

**MongoDB not available:**
- System will continue without persistence
- Or start MongoDB: `docker-compose up -d mongodb`

**OpenAI errors:**
- System automatically falls back to pattern matching
- Check API key in `.env`

## 📚 Next Steps

- Test different conversation flows
- Populate knowledge base
- Iterate on prompts
- Export conversations for analysis
- Compare OpenAI vs pattern matching

For more details, see `README_SIMULATOR.md`

