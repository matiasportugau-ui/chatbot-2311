# Step-by-Step Testing Guide: Functionality Evaluation Without Integrations

## Overview

This guide enables testing the chatbot's core functionality using real logic but without external integrations (WhatsApp, n8n). Uses actual `ia_conversacional_integrada.py`, `sistema_cotizaciones.py`, FastAPI endpoints, and MongoDB.

## Quick Start (One Command!)

**Fastest way to start testing:**

```bash
./run_simulation.sh
```

This single command will:
- ✅ Check and install dependencies
- ✅ Set up environment
- ✅ Start MongoDB (if Docker available)
- ✅ Start API server
- ✅ Launch interactive CLI simulator

**That's it!** You'll be chatting with the bot in seconds.

---

### Alternative: Manual Quick Start (5 Minutes)

If you prefer manual steps:

```bash
# 1. Start MongoDB (Docker)
docker run -d -p 27017:27017 --name bmc-mongodb mongo:7.0

# 2. Start API Server (in one terminal)
python api_server.py

# 3. Test via CLI (in another terminal)
python simulate_chat_cli.py

# 4. Type a test message
> Hola, necesito información sobre Isodec
```

Continue reading for comprehensive testing details.

## Prerequisites

### Required Software

- Python 3.8+ installed
- MongoDB (local or Docker)
- Node.js 18+ (for web UI, optional)
- pip package manager

### Required Files (verify existence)

- `api_server.py` - FastAPI server
- `ia_conversacional_integrada.py` - Core chatbot logic
- `sistema_cotizaciones.py` - Quote generation
- `simulate_chat.py` - Simulated chat wrapper
- `simulate_chat_cli.py` - CLI interface
- `populate_kb.py` - Knowledge base populator
- `test_scenarios/` - Test scenario files

**Verification:**
```bash
# Check all files exist
ls -la api_server.py ia_conversacional_integrada.py sistema_cotizaciones.py
ls -la simulate_chat.py simulate_chat_cli.py populate_kb.py
ls -la test_scenarios/
```

## Step 1: Environment Setup

### 1.1 Install Python Dependencies

```bash
cd Dashboard-bmc/proyecto-cotizacion-whatsapp/05_dashboard_ui
pip install -r requirements.txt
```

Key dependencies:

- fastapi
- uvicorn
- pymongo
- openai (optional, for real AI)
- requests

**Verify installation:**
```bash
pip list | grep -E "fastapi|uvicorn|pymongo|openai"
```

### 1.2 Configure Environment Variables

Create `.env` file (or use existing):

```bash
# Minimal configuration for testing
MONGODB_URI=mongodb://localhost:27017/bmc_chat
PY_CHAT_SERVICE_URL=http://localhost:8000
OPENAI_API_KEY=your_key_here  # Optional, will use pattern matching if not set
```

**From template:**
```bash
cp env.example .env
# Edit .env with your values
```

### 1.3 Start MongoDB

**Option A: Local MongoDB**

```bash
# If MongoDB installed locally
mongod --dbpath /path/to/data
```

**Option B: Docker MongoDB**

```bash
docker run -d -p 27017:27017 --name bmc-mongodb mongo:7.0
```

**Option C: Docker Compose (MongoDB only)**

```bash
docker-compose up mongodb -d
```

**Verify MongoDB is running:**

```bash
mongosh mongodb://localhost:27017 --eval "db.adminCommand('ping')"
```

Or with Docker:
```bash
docker ps | grep mongo
```

## Step 2: Start Python API Server

### 2.1 Start FastAPI Server

```bash
python api_server.py
```

Or with uvicorn directly:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2.2 Verify API Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "service": "bmc-chat-api"
}
```

**Alternative verification:**
```bash
# Using Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## Step 3: Test via Command Line Interface

### 3.1 Start CLI Simulator

```bash
python simulate_chat_cli.py
```

You should see:
```
🚀 BMC Chat Simulator
📱 Phone: +59891234567
💬 Type a message or /help for commands
>
```

### 3.2 Basic Chat Test

In CLI, type messages:

```
> Hola
> Necesito información sobre Isodec
> Quiero cotizar 10 metros por 5 metros
> 100mm de espesor
```

### 3.3 CLI Commands

Available commands:

- `/help` - Show commands
- `/new` - Start new session
- `/phone <number>` - Set phone number
- `/history` - Show conversation history
- `/export` - Export conversation to JSON
- `/stats` - Show knowledge base statistics
- `/exit` - Exit

**Example session:**
```
> /help
📖 Available Commands:
  /help          - Show this help
  /new           - Start new session
  ...

> Hola
🤖 Bot: [Response from chatbot]

> /history
📜 Conversation History:
  1. User: Hola
     Bot: [Response]
```

### 3.4 Evaluate Response Quality

Check for:

- Response type (cotizacion|informacion|pregunta|seguimiento)
- Confidence score
- Actions suggested
- Message clarity
- Quote accuracy (if cotizacion)

**Example evaluation:**
```
Response Type: cotizacion ✓
Confidence: 0.85 ✓
Message: Clear and helpful ✓
Quote: Accurate pricing ✓
```

## Step 4: Test via Web UI (Optional)

### 4.1 Start Next.js Development Server

```bash
npm install  # If not done
npm run dev
```

### 4.2 Access Simulator

Open browser:

```
http://localhost:3000/simulator
```

### 4.3 Test in Web UI

- Enter phone number (default: +59891234567)
- Type messages in chat interface
- View response metadata (type, confidence, actions)
- Review conversation history
- Export conversations

### 4.4 Evaluate in Web UI

Check:

- Response display formatting
- Metadata visibility
- Conversation persistence
- UI responsiveness

## Step 5: Test with Pre-defined Scenarios

### 5.1 Review Test Scenarios

Located in `test_scenarios/`:

- `quote_request.json` - Quote request flows
- `product_info.json` - Product information requests
- `multi_turn.json` - Multi-turn conversations
- `edge_cases.json` - Edge cases and errors

**View a scenario:**
```bash
cat test_scenarios/quote_request.json | python -m json.tool
```

### 5.2 Run Single Scenario

```bash
python simulate_chat.py --scenario test_scenarios/quote_request.json
```

**Or using populate_kb.py:**
```bash
python populate_kb.py --scenarios test_scenarios/quote_request.json
```

### 5.3 Run All Scenarios

```bash
python populate_kb.py --scenarios test_scenarios/
```

**With verbose output:**
```bash
python populate_kb.py --scenarios test_scenarios/ --verbose
```

### 5.4 Evaluate Scenario Results

Check:

- All messages processed successfully
- Expected response types returned
- Conversation flow maintained
- Knowledge base updated
- No errors in logs

**Expected output:**
```
✅ Scenario 1: Complete Quote Request Flow
   Messages: 6/6 processed
   Response Type: cotizacion ✓
   Confidence: 0.92 ✓

✅ Scenario 2: Quick Quote Request
   Messages: 1/1 processed
   Response Type: cotizacion ✓
```

## Step 6: Populate Knowledge Base

### 6.1 Run Knowledge Base Populator

```bash
python populate_kb.py --scenarios test_scenarios/ --verbose
```

This will:
- Run all test scenarios
- Store conversations in MongoDB
- Update knowledge base
- Generate statistics

### 6.2 Verify MongoDB Data

```bash
mongosh mongodb://localhost:27017/bmc_chat
```

In MongoDB shell:

```javascript
// Check conversations
db.conversations.countDocuments({})

// Check knowledge base interactions
db.kb_interactions.countDocuments({})

// View recent conversation
db.conversations.find().sort({timestamp: -1}).limit(1).pretty()

// Get statistics
db.conversations.aggregate([
  {
    $group: {
      _id: "$response_type",
      count: { $sum: 1 },
      avg_confidence: { $avg: "$confidence" }
    }
  }
])
```

### 6.3 Evaluate Knowledge Base

Check:

- Conversations stored correctly
- Session IDs maintained
- Phone numbers tracked
- Response metadata saved
- Knowledge base learning active

## Step 7: Functionality Evaluation Checklist

### 7.1 Core Chatbot Functionality

- [ ] Message processing works
- [ ] Response generation works
- [ ] Session management works
- [ ] Context retention works
- [ ] Error handling works

**Test commands:**
```bash
# Test message processing
python -c "from simulate_chat import SimulatedChat; c = SimulatedChat(); print(c.send_message('Hola'))"

# Test session management
python simulate_chat_cli.py
> /new
> Hola
> /history
```

### 7.2 Quote Generation

- [ ] Quote requests detected
- [ ] Product information extracted
- [ ] Dimensions parsed correctly
- [ ] Prices calculated accurately
- [ ] Quote format correct

**Test quote:**
```
> Quiero cotizar Isodec 10x5 100mm blanco
```

**Expected:**
- Response type: `cotizacion`
- Product: Isodec
- Dimensions: 10m x 5m
- Thickness: 100mm
- Price calculated

### 7.3 Response Types

- [ ] cotizacion type works
- [ ] informacion type works
- [ ] pregunta type works
- [ ] seguimiento type works

**Test each type:**
```
# Quote
> Quiero cotizar Isodec 10x5

# Information
> ¿Qué productos tienen disponibles?

# Question
> ¿Cuál es la diferencia entre 75mm y 100mm?

# Follow-up
> Perfecto, me parece bien el precio
```

### 7.4 Knowledge Base

- [ ] Conversations saved to MongoDB
- [ ] Knowledge base updates
- [ ] Patterns learned
- [ ] Insights generated

**Verify:**
```bash
mongosh mongodb://localhost:27017/bmc_chat --eval "db.conversations.countDocuments({})"
```

### 7.5 API Endpoints

- [ ] `/health` responds
- [ ] `/chat/process` works
- [ ] `/quote/create` works (if implemented)
- [ ] Error responses correct

**Test endpoints:**
```bash
# Health
curl http://localhost:8000/health

# Chat process
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola", "telefono": "+59891234567"}'
```

## Step 8: Iterative Testing & Prompt Tuning

### 8.1 Test Prompt Variations

1. Edit `ia_conversacional_integrada.py`
2. Modify system prompts or instructions
3. Restart API server: `python api_server.py`
4. Test same input again
5. Compare responses

**Example prompt edit:**
```python
# In ia_conversacional_integrada.py
# Find system prompt and modify
system_prompt = """
Eres un asistente experto en ventas de productos de construcción (BMC Uruguay).
[Your modifications here]
"""
```

### 8.2 Test Different Inputs

- Short messages: "Hola"
- Long messages: Detailed quote requests
- Ambiguous messages: "Quiero algo para mi casa"
- Multi-language: Mix Spanish/English
- Special characters: Emojis, punctuation

**Test cases:**
```
> Hola
> Necesito cotizar para mi casa que tiene 10 metros de largo por 5 de ancho y quiero usar Isodec de 100mm de espesor en color blanco con terminación frontal estándar
> Quiero algo para mi casa
> Hello, I need a quote
> 😊 Hola, necesito información
```

### 8.3 Compare OpenAI vs Pattern Matching

If OpenAI key not set, system uses pattern matching:

- Test with OpenAI: Set `OPENAI_API_KEY`
- Test without OpenAI: Unset key
- Compare response quality
- Evaluate when to use each

**Test both modes:**
```bash
# With OpenAI
export OPENAI_API_KEY=your_key
python api_server.py
# Test conversation

# Without OpenAI
unset OPENAI_API_KEY
python api_server.py
# Test same conversation
# Compare responses
```

## Step 9: Export & Analyze Results

### 9.1 Export Conversations

From CLI:

```
/export conversation_2024.json
```

From code:

```python
from simulate_chat import SimulatedChat
chat = SimulatedChat()
chat.export_conversation('output.json')
```

### 9.2 Analyze MongoDB Data

```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client.bmc_chat

# Get statistics
stats = {
    'total_conversations': db.conversations.count_documents({}),
    'quote_requests': db.conversations.count_documents({'response_type': 'cotizacion'}),
    'info_requests': db.conversations.count_documents({'response_type': 'informacion'}),
    'avg_confidence': list(db.conversations.aggregate([
        {'$group': {'_id': None, 'avg': {'$avg': '$confidence'}}}
    ]))[0]['avg'] if db.conversations.count_documents({}) > 0 else 0
}

print(f"Statistics: {stats}")
```

### 9.3 Generate Test Report

Create evaluation report:

- Total tests run
- Success rate
- Response type distribution
- Average confidence scores
- Common issues found
- Recommendations

**Example report template:**
```python
report = {
    "test_date": "2024-12-19",
    "total_scenarios": 10,
    "successful": 9,
    "failed": 1,
    "response_types": {
        "cotizacion": 5,
        "informacion": 3,
        "pregunta": 1,
        "seguimiento": 1
    },
    "avg_confidence": 0.87,
    "issues": [
        "Ambiguous messages sometimes misclassified",
        "Long messages occasionally timeout"
    ],
    "recommendations": [
        "Improve ambiguity detection",
        "Add message length limits"
    ]
}
```

## Step 10: Troubleshooting

### 10.1 API Server Not Starting

**Symptoms:**
- Port already in use error
- Import errors
- Module not found errors

**Solutions:**

1. **Check port availability:**
   ```bash
   lsof -i :8000
   # Or
   netstat -an | grep 8000
   ```

2. **Kill process using port:**
   ```bash
   # Find PID
   lsof -ti :8000
   # Kill it
   kill -9 $(lsof -ti :8000)
   ```

3. **Check Python dependencies:**
   ```bash
   pip list | grep -E "fastapi|uvicorn"
   # If missing:
   pip install fastapi uvicorn
   ```

4. **Check for errors in api_server.py:**
   ```bash
   python -c "import api_server"
   ```

5. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

### 10.2 MongoDB Connection Failed

**Symptoms:**
- Connection refused errors
- Timeout errors
- Authentication errors

**Solutions:**

1. **Verify MongoDB running:**
   ```bash
   # Docker
   docker ps | grep mongo
   
   # Local
   ps aux | grep mongod
   ```

2. **Check connection string:**
   ```bash
   # In .env file
   MONGODB_URI=mongodb://localhost:27017/bmc_chat
   ```

3. **Test connection:**
   ```bash
   mongosh mongodb://localhost:27017 --eval "db.adminCommand('ping')"
   ```

4. **Check network connectivity:**
   ```bash
   telnet localhost 27017
   ```

5. **Restart MongoDB:**
   ```bash
   # Docker
   docker restart bmc-mongodb
   
   # Local
   sudo systemctl restart mongod
   ```

### 10.3 No Responses from Chatbot

**Symptoms:**
- Empty responses
- Error messages
- Timeout errors

**Solutions:**

1. **Check API server logs:**
   ```bash
   # Look for errors in terminal running api_server.py
   ```

2. **Verify ia_conversacional_integrada.py imports:**
   ```bash
   python -c "from ia_conversacional_integrada import IAConversacionalIntegrada; print('OK')"
   ```

3. **Check OpenAI API key (if using OpenAI):**
   ```bash
   echo $OPENAI_API_KEY
   # Or check .env file
   ```

4. **Verify pattern matching fallback:**
   ```bash
   # Unset OpenAI key and test
   unset OPENAI_API_KEY
   python api_server.py
   # Test again
   ```

5. **Check system prompts:**
   ```python
   # In ia_conversacional_integrada.py
   # Verify system prompts are defined
   ```

### 10.4 Knowledge Base Not Updating

**Symptoms:**
- Conversations not saved
- No data in MongoDB
- Collection not found

**Solutions:**

1. **Check MongoDB connection:**
   ```bash
   mongosh mongodb://localhost:27017/bmc_chat --eval "db.conversations.countDocuments({})"
   ```

2. **Verify collection names:**
   ```python
   # Should be: conversations, kb_interactions
   ```

3. **Check write permissions:**
   ```bash
   # MongoDB should allow writes by default
   # Check if read-only mode
   ```

4. **Review populate_kb.py logs:**
   ```bash
   python populate_kb.py --scenarios test_scenarios/ --verbose
   # Look for error messages
   ```

5. **Check database name:**
   ```bash
   # In .env: MONGODB_URI=mongodb://localhost:27017/bmc_chat
   # Database name should be: bmc_chat
   ```

### 10.5 Import Errors

**Symptoms:**
- ModuleNotFoundError
- ImportError
- AttributeError

**Solutions:**

1. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

2. **Install missing packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check file locations:**
   ```bash
   ls -la api_server.py ia_conversacional_integrada.py
   ```

4. **Use absolute imports:**
   ```python
   # Instead of: from ia_conversacional_integrada import ...
   # Use: from .ia_conversacional_integrada import ...
   ```

### 10.6 Slow Response Times

**Symptoms:**
- Long delays before responses
- Timeout errors
- High CPU usage

**Solutions:**

1. **Check OpenAI API (if using):**
   ```bash
   # OpenAI API can be slow
   # Consider using faster model: gpt-4o-mini
   ```

2. **Check MongoDB queries:**
   ```bash
   # Slow queries can cause delays
   # Add indexes if needed
   ```

3. **Check system resources:**
   ```bash
   # CPU, memory usage
   top
   # Or
   htop
   ```

4. **Use pattern matching for faster responses:**
   ```bash
   # Pattern matching is faster than OpenAI
   unset OPENAI_API_KEY
   ```

### 10.7 Web UI Not Loading

**Symptoms:**
- Page not found
- Connection refused
- API errors

**Solutions:**

1. **Check Next.js server:**
   ```bash
   npm run dev
   # Should start on http://localhost:3000
   ```

2. **Check API URL:**
   ```bash
   # In .env or environment
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Check CORS:**
   ```python
   # In api_server.py
   # CORS should allow localhost:3000
   ```

4. **Check browser console:**
   ```javascript
   // Open browser DevTools
   // Look for errors in Console tab
   ```

## Step 11: Next Steps After Testing

### 11.1 Refine Prompts

Based on test results:

- Adjust system prompts in `ia_conversacional_integrada.py`
- Improve product information extraction
- Enhance quote generation logic
- Better error messages

**Example improvements:**
```python
# Better prompt for quote extraction
system_prompt = """
Eres un asistente experto en ventas de productos de construcción (BMC Uruguay).

Cuando un cliente solicita una cotización:
1. Extrae: producto, dimensiones (largo x ancho), espesor, color
2. Si falta información, pregunta específicamente
3. Calcula precio usando sistema_cotizaciones
4. Presenta cotización de forma clara y profesional
"""
```

### 11.2 Add More Test Scenarios

Create new scenarios in `test_scenarios/`:

- Edge cases found during testing
- Real-world conversation patterns
- Error recovery scenarios
- Multi-product quotes

**Example new scenario:**
```json
{
  "name": "Multi-Product Quote",
  "phone": "+59891234567",
  "messages": [
    "Necesito cotizar Isodec y Isoroof",
    "Isodec: 10x5 100mm",
    "Isoroof: 8x4 50mm"
  ],
  "expected_type": "cotizacion",
  "description": "Quote request with multiple products"
}
```

### 11.3 Prepare for Integration

Once functionality validated:

- Test with n8n workflow (import workflow)
- Test with WhatsApp webhook (dev number)
- Test end-to-end flow
- Monitor production metrics

**Integration checklist:**
- [ ] n8n workflow imported
- [ ] WhatsApp credentials configured
- [ ] Webhook URL verified
- [ ] End-to-end test successful
- [ ] Monitoring set up

## Quick Reference Commands

```bash
# Start MongoDB
docker run -d -p 27017:27017 --name bmc-mongodb mongo:7.0

# Start API Server
python api_server.py

# Test via CLI
python simulate_chat_cli.py

# Test via Web UI
npm run dev
# Open http://localhost:3000/simulator

# Run scenarios
python populate_kb.py --scenarios test_scenarios/

# Verify setup
python verify_setup.py

# Check MongoDB
mongosh mongodb://localhost:27017/bmc_chat

# Test API endpoint
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola", "telefono": "+59891234567"}'
```

## Files Reference

- **API Server**: `api_server.py`
- **Chatbot Logic**: `ia_conversacional_integrada.py`
- **Quote System**: `sistema_cotizaciones.py`
- **CLI Simulator**: `simulate_chat_cli.py`
- **Web Simulator**: `src/app/simulator/page.tsx`
- **KB Populator**: `populate_kb.py`
- **Test Scenarios**: `test_scenarios/*.json`
- **Verification**: `verify_setup.py`

## Functionality Evaluation Checklist Template

Use this checklist to track your testing progress:

```markdown
## Testing Session: [Date]

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] MongoDB running
- [ ] .env configured
- [ ] API server started

### Basic Functionality
- [ ] CLI simulator works
- [ ] Web UI works (optional)
- [ ] Messages processed
- [ ] Responses generated
- [ ] Session management works

### Quote Generation
- [ ] Quote requests detected
- [ ] Product info extracted
- [ ] Dimensions parsed
- [ ] Prices calculated
- [ ] Quote format correct

### Response Types
- [ ] cotizacion works
- [ ] informacion works
- [ ] pregunta works
- [ ] seguimiento works

### Knowledge Base
- [ ] Conversations saved
- [ ] KB updates
- [ ] Patterns learned

### Scenarios
- [ ] quote_request.json passed
- [ ] product_info.json passed
- [ ] multi_turn.json passed
- [ ] edge_cases.json passed

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

## Additional Resources

- **Installation Guide**: See `INSTALLATION_REVIEW.md`
- **n8n Workflow Setup**: See `n8n_workflows/AGENT_MODE_SETUP_GUIDE.md`
- **Project Plan**: See `whats.plan.md`
- **API Documentation**: See `api_server.py` docstrings

---

**Happy Testing!** 🚀

If you encounter issues not covered here, check the troubleshooting section or review the logs for detailed error messages.

