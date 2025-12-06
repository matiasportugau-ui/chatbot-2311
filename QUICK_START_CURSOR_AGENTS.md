# Quick Start: Cursor Multi-Agent Integration

## ✅ What's Included

- **OpenAI** (GPT-4, GPT-3.5)
- **Groq** (Llama, Mixtral - Free tier available!)
- **Google Gemini** (Gemini Pro, Flash)
- **xAI Grok** (grok-4-latest, grok-beta) ✨ NEW!

## 🚀 Setup (2 minutes)

### 1. Add API Keys to `.env`

```bash
# Required: At least one provider
GROK_API_KEY=YOUR_GROK_API_KEY_HERE

# Optional: Add more providers for fallback
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...  # Free tier available!

# Strategy: balanced, cost, speed, or quality
MODEL_STRATEGY=balanced
```

### 2. Install Dependencies

```bash
pip install openai groq google-generativeai python-dotenv
```

Or use the setup script:
```bash
./setup_cursor_agents.sh
```

### 3. Test It

```bash
python3 test_grok_integration.py
```

## 💻 Usage

### Basic Usage

```python
from model_integrator import get_model_integrator

integrator = get_model_integrator()

response = integrator.generate(
    prompt="Write a Python function to sort a list",
    system_prompt="You are a helpful coding assistant",
    temperature=0.7,
    max_tokens=1000
)

print(response["content"])
print(f"Model: {response['model_used']}")
print(f"Cost: ${response['cost']:.6f}")
```

### Using Cursor Agent Wrapper

```python
from cursor_agent_wrapper import get_cursor_agent

agent = get_cursor_agent(strategy="balanced")

messages = [
    {"role": "system", "content": "You are a coding assistant"},
    {"role": "user", "content": "Explain Python decorators"}
]

response = agent.chat(messages)
print(response["content"])
```

### Force Specific Provider

```python
# Use Grok specifically
response = integrator.generate(
    prompt="Hello!",
    model_id="grok_grok-4-latest"
)

# Or use agent with provider preference
agent = get_cursor_agent(provider="grok")
```

## 🎯 Model Selection Strategy

- **`balanced`** (default): Optimizes cost, speed, and quality
- **`cost`**: Minimizes API costs
- **`speed`**: Maximizes response speed
- **`quality`**: Maximizes output quality

## 📊 Available Models

### Grok (xAI)
- `grok-4-latest` - Latest Grok 4 model
- `grok-beta` - Beta model
- `grok-2-1212` - Stable Grok 2
- `grok-2-vision-1212` - Grok 2 with vision

### OpenAI
- `gpt-4o` - Latest GPT-4
- `gpt-4o-mini` - Fast, cost-effective
- `gpt-3.5-turbo` - Budget option

### Groq (Free tier!)
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`

### Gemini (New SDK - google-genai)
- `gemini-2.5-flash` ⭐ **NEW** - Fastest, cost-effective (recommended)
- `gemini-1.5-pro` - Best quality, balanced
- `gemini-3-pro` ⭐ **NEW** - Preview, agentic workflows (if available)
- `gemini-1.5-flash` - Fast, good quality
- `gemini-pro` - Legacy model

## 🔧 Configuration

Set in `.env`:

```bash
# Model lists (comma-separated)
GROK_MODELS=grok-4-latest,grok-beta
OPENAI_MODELS=gpt-4o-mini,gpt-4o
GROQ_MODELS=llama-3.1-70b-versatile
# Recommended: gemini-2.5-flash (fastest), gemini-1.5-pro (best quality), gemini-3-pro (preview)
GEMINI_MODELS=gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro

# Strategy
MODEL_STRATEGY=balanced
```

## 📈 Usage Stats

```python
integrator = get_model_integrator()
stats = integrator.get_usage_summary()

print(f"Total requests: {stats['total_requests']}")
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"By model: {stats['by_model']}")
```

## 🛠️ Troubleshooting

### "Model not available"
- Check API key is set correctly
- Verify model name matches available models
- Check provider is enabled

### Rate limit errors
- Increase rate limits in provider dashboard
- System automatically falls back to other providers
- Use `strategy="cost"` to prefer free/low-cost models

### Import errors
```bash
pip install openai groq google-generativeai python-dotenv
```

## 📚 Files

- `model_integrator.py` - Core integration logic
- `cursor_agent_wrapper.py` - Cursor-compatible wrapper
- `test_grok_integration.py` - Test script
- `setup_cursor_agents.sh` - Setup script
- `CURSOR_AGENT_SETUP.md` - Detailed setup guide

## 🎉 You're Ready!

Your Cursor agent now supports 4 AI providers with automatic fallback and cost optimization!

