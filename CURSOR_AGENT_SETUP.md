# Cursor Multi-Agent Integration Setup Guide

## xAI (Grok) API Key Configuration

### Recommended Settings

**Name:**
```
cursor-agent-integration
```
or
```
cursor-multi-agent-grok
```

**Permissions:**
- **Development/Testing:** `All` ✅
- **Production:** `Restricted` (with specific scopes)

**Custom Rate Limits (Recommended):**

For **Development:**
- **TPM (Tokens Per Minute):** `200,000`
- **RPM (Requests Per Minute):** `100`

For **Production/Heavy Usage:**
- **TPM (Tokens Per Minute):** `500,000`
- **RPM (Requests Per Minute):** `200`

### Why These Limits?

- **TPM 200K-500K:** Coding tasks typically use 1K-10K tokens per request. This allows 20-200 requests/minute.
- **RPM 100-200:** Prevents accidental API abuse while allowing concurrent agent operations.

---

## Environment Configuration

Add to your `.env` file:

```bash
# xAI (Grok) Configuration
GROK_API_KEY=xai-your-api-key-here
GROK_MODELS=grok-4-latest,grok-beta,grok-2-1212

# Google Gemini Configuration (uses new google-genai SDK)
GEMINI_API_KEY=your-gemini-api-key
# Recommended: gemini-2.5-flash (fastest, cost-effective), gemini-1.5-pro (best quality), gemini-3-pro (preview, agentic workflows)
GEMINI_MODELS=gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro

# Model Selection Strategy
MODEL_STRATEGY=balanced
```

### Available Grok Models

- `grok-4-latest` - Latest Grok 4 model (recommended)
- `grok-beta` - Beta model
- `grok-2-1212` - Stable Grok 2 model
- `grok-2-vision-1212` - Grok 2 with vision capabilities

### Available Gemini Models (New SDK)

- `gemini-2.5-flash` ⭐ **NEW** - Fastest, most cost-effective (recommended for speed)
- `gemini-1.5-pro` - Best quality, balanced performance
- `gemini-3-pro` ⭐ **NEW** - Preview model, agentic workflows (if available)
- `gemini-1.5-flash` - Fast, good quality
- `gemini-pro` - Legacy model

---

## Complete Multi-Agent Setup

### 1. Install Dependencies

```bash
pip install openai groq google-genai python-dotenv
# Or with fallback:
pip install openai groq google-genai google-generativeai python-dotenv
```

**Note**: The new `google-genai` SDK (2025) is recommended for Gemini. The old `google-generativeai` SDK is kept as fallback for compatibility.

### 2. Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODELS=gpt-4o-mini,gpt-4o

# Groq (Free tier available)
GROQ_API_KEY=gsk_...
GROQ_MODELS=llama-3.1-70b-versatile,llama-3.1-8b-instant

# Google Gemini (uses new google-genai SDK)
GEMINI_API_KEY=...
# Recommended: gemini-2.5-flash (fastest, cost-effective), gemini-1.5-pro (best quality), gemini-3-pro (preview, agentic workflows)
GEMINI_MODELS=gemini-2.5-flash,gemini-1.5-pro,gemini-3-pro

# xAI (Grok)
GROK_API_KEY=xai-...
GROK_MODELS=grok-beta,grok-2-1212

# Strategy: cost, speed, quality, balanced
MODEL_STRATEGY=balanced
```

### 3. Model Strategy Options

- **`balanced`** (Recommended): Optimizes cost, speed, and quality
- **`cost`**: Minimizes API costs
- **`speed`**: Maximizes response speed
- **`quality`**: Maximizes output quality

---

## Usage Example

```python
from model_integrator import get_model_integrator

# Initialize with balanced strategy
integrator = get_model_integrator()

# Generate response (auto-selects best model)
response = integrator.generate(
    prompt="Write a Python function to sort a list",
    system_prompt="You are a helpful coding assistant",
    temperature=0.7,
    max_tokens=1000
)

print(f"Model used: {response['model_used']}")
print(f"Response: {response['content']}")
print(f"Cost: ${response['cost']:.4f}")
print(f"Time: {response['response_time']:.2f}s")
```

---

## Rate Limit Considerations

### xAI (Grok) Default Limits
- Free tier: Limited requests
- Paid tier: Higher limits based on plan

### Best Practices
1. **Start with lower limits** and increase as needed
2. **Monitor usage** via xAI dashboard
3. **Implement retry logic** with exponential backoff
4. **Cache responses** when possible
5. **Use fallback models** if rate limits are hit

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secure key management
3. **Rotate keys regularly**
4. **Use restricted permissions** in production
5. **Monitor API usage** for anomalies

---

## Troubleshooting

### Rate Limit Errors
- Increase TPM/RPM limits in xAI dashboard
- Implement request queuing
- Use fallback to other providers (OpenAI, Gemini, Groq)

### Authentication Errors
- Verify API key format: `xai-...`
- Check key permissions in xAI dashboard
- Ensure key is active and not expired

### Model Not Available
- Check model name spelling
- Verify model is available in your region/plan
- Use fallback model selection

---

## Quick Start

### 1. Set Your API Key

Add to your `.env` file:
```bash
GROK_API_KEY=YOUR_GROK_API_KEY_HERE
GROK_MODELS=grok-4-latest,grok-beta,grok-2-1212
MODEL_STRATEGY=balanced
```

### 2. Run Setup Script

```bash
./setup_cursor_agents.sh
```

### 3. Test Integration

```bash
python3 test_grok_integration.py
```

### 4. Use in Your Code

```python
from cursor_agent_wrapper import get_cursor_agent

# Initialize agent
agent = get_cursor_agent(strategy="balanced")

# Chat
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
]

response = agent.chat(messages)
print(response["content"])
```

## Next Steps

1. ✅ Create xAI API key with recommended settings
2. ✅ Add `GROK_API_KEY` to `.env` file
3. ✅ Update `model_integrator.py` with Grok support
4. ✅ Test integration with sample requests
5. ✅ Monitor usage and adjust rate limits as needed

