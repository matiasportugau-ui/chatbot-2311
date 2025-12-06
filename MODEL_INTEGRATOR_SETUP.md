# AI Model Integrator Setup Guide

This guide will help you set up and optimize your paid subscriptions for OpenAI, Groq, and Google Gemini.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Key Setup](#api-key-setup)
3. [Configuration Options](#configuration-options)
4. [Cost Optimization Strategies](#cost-optimization-strategies)
5. [Usage Monitoring](#usage-monitoring)
6. [Best Practices](#best-practices)

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `openai` - OpenAI API client
- `groq` - Groq API client (fast inference)
- `google-generativeai` - Google Gemini API client

### Step 2: Set Up Environment Variables

Copy the example environment file:

```bash
cp env.example .env
```

Edit `.env` and add your API keys:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# Groq (Free tier available!)
GROQ_API_KEY=gsk-your-groq-key-here

# Google Gemini
GEMINI_API_KEY=your-gemini-key-here
```

### Step 3: Test the Integration

```python
from model_integrator import get_model_integrator

# Get the integrator
integrator = get_model_integrator()

# List available models
models = integrator.list_available_models()
print("Available models:", models)

# Generate a response
response = integrator.generate(
    prompt="Hello! Can you help me with a quote?",
    system_prompt="You are a helpful assistant for BMC Uruguay."
)

print(response["content"])
print(f"Cost: ${response['cost']:.6f}")
print(f"Model used: {response['model_used']}")
```

## 🔑 API Key Setup

### OpenAI

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key and add it to `.env` as `OPENAI_API_KEY`

**Recommended Models:**
- `gpt-4o-mini` - Best cost/performance ratio ($0.15/$0.60 per 1M tokens)
- `gpt-4o` - Highest quality ($2.50/$10.00 per 1M tokens)
- `gpt-3.5-turbo` - Fast and cheap ($0.50/$1.50 per 1M tokens)

### Groq

1. Go to https://console.groq.com/keys
2. Sign in or create an account
3. Create a new API key
4. Copy the key and add it to `.env` as `GROQ_API_KEY`

**Why Groq?**
- ⚡ **Extremely fast** - Up to 10x faster than other providers
- 💰 **Free tier available** - Great for development and testing
- 🚀 **High throughput** - Perfect for high-volume applications

**Recommended Models:**
- `llama-3.1-70b-versatile` - Best quality (free tier)
- `llama-3.1-8b-instant` - Fastest responses (free tier)
- `mixtral-8x7b-32768` - Good balance (free tier)

### Google Gemini

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to `.env` as `GEMINI_API_KEY`

**Recommended Models:**
- `gemini-1.5-flash` - Fast and cost-effective ($0.075/$0.30 per 1M tokens)
- `gemini-1.5-pro` - Highest quality ($1.25/$5.00 per 1M tokens)

## ⚙️ Configuration Options

### Model Selection Strategy

Set `MODEL_STRATEGY` in your `.env` file:

```bash
# Minimize cost (uses cheapest available models)
MODEL_STRATEGY=cost

# Maximize speed (uses fastest models, like Groq)
MODEL_STRATEGY=speed

# Maximize quality (uses best quality models)
MODEL_STRATEGY=quality

# Balanced approach (default - considers cost, speed, and quality)
MODEL_STRATEGY=balanced
```

### Selecting Specific Models

You can specify which models to enable for each provider:

```bash
# OpenAI - enable multiple models
OPENAI_MODELS=gpt-4o-mini,gpt-4o

# Groq - enable specific models
GROQ_MODELS=llama-3.1-70b-versatile,llama-3.1-8b-instant

# Gemini - enable specific models
GEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro
```

## 💰 Cost Optimization Strategies

### Strategy 1: Use Groq for High-Volume Tasks

Groq offers free tier with excellent performance. Use it for:
- High-frequency queries
- Simple Q&A
- Real-time chat responses
- Development and testing

```python
# Force Groq for a specific request
response = integrator.generate(
    prompt="Quick question...",
    model_id="groq_llama-3.1-8b-instant"  # Specify model directly
)
```

### Strategy 2: Tiered Model Selection

Use different models based on task complexity:

```python
# Simple queries -> Groq (free/fast)
if is_simple_query(prompt):
    model_id = "groq_llama-3.1-8b-instant"
# Complex queries -> GPT-4o-mini (cost-effective)
elif is_complex_query(prompt):
    model_id = "openai_gpt-4o-mini"
# Critical queries -> Best quality
else:
    model_id = "openai_gpt-4o"
```

### Strategy 3: Cost-Based Strategy

Set `MODEL_STRATEGY=cost` to automatically use the cheapest available models:

```bash
MODEL_STRATEGY=cost
```

This will prioritize:
1. Groq (free tier)
2. Gemini Flash (very cheap)
3. GPT-4o-mini (cost-effective)
4. Other models as needed

### Strategy 4: Monitor and Optimize

Regularly check usage statistics:

```python
from model_integrator import get_model_integrator

integrator = get_model_integrator()
summary = integrator.get_usage_summary()

print(f"Total Cost: ${summary['total_cost']:.2f}")
print(f"Total Requests: {summary['total_requests']}")
print(f"Total Tokens: {summary['total_tokens']:,}")

# Per-model breakdown
for model_id, stats in summary['by_model'].items():
    print(f"\n{model_id}:")
    print(f"  Cost: ${stats['total_cost']:.2f}")
    print(f"  Requests: {stats['requests']}")
    print(f"  Avg Response Time: {stats['avg_response_time']:.2f}s")
```

## 📊 Usage Monitoring

### Automatic Usage Tracking

The integrator automatically tracks:
- Token usage (input/output)
- Cost per request
- Response times
- Error rates
- Model selection frequency

Statistics are saved to `model_usage_stats.json` automatically.

### View Usage Statistics

```python
from model_integrator import get_model_integrator

integrator = get_model_integrator()

# Get summary
summary = integrator.get_usage_summary()
print(summary)

# List all available models
models = integrator.list_available_models()
for model in models:
    print(f"{model['model_id']}: {model['provider']} - {model['model_name']}")
```

### Export Usage Data

```python
# Save current stats
integrator.save_usage_stats()

# Stats are saved to model_usage_stats.json
```

## 🎯 Best Practices

### 1. Start with Free/Cheap Models

- Use Groq for development and testing (free tier)
- Use GPT-4o-mini for production (cost-effective)
- Reserve expensive models (GPT-4o, Gemini Pro) for critical tasks

### 2. Implement Fallback Logic

The integrator automatically falls back to alternative models if one fails:

```python
# The integrator will try fallback models automatically
response = integrator.generate(prompt="Your question")
```

### 3. Cache Responses When Possible

For repeated queries, implement caching:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(prompt_hash):
    return integrator.generate(prompt)
```

### 4. Set Token Limits

Control costs by setting appropriate token limits:

```python
# For simple responses
response = integrator.generate(
    prompt="Quick answer",
    max_tokens=500  # Limit response length
)

# For detailed responses
response = integrator.generate(
    prompt="Detailed analysis",
    max_tokens=2000  # Allow longer responses
)
```

### 5. Monitor Costs Regularly

Set up daily/weekly cost monitoring:

```python
import json
from datetime import datetime

def check_daily_costs():
    integrator = get_model_integrator()
    summary = integrator.get_usage_summary()
    
    daily_report = {
        "date": datetime.now().isoformat(),
        "total_cost": summary["total_cost"],
        "total_requests": summary["total_requests"],
        "by_model": summary["by_model"]
    }
    
    with open(f"daily_report_{datetime.now().date()}.json", "w") as f:
        json.dump(daily_report, f, indent=2)
    
    print(f"Daily cost: ${summary['total_cost']:.2f}")
```

## 🔧 Advanced Configuration

### Custom Model Configuration

Create a custom config file `model_config.json`:

```json
{
  "strategy": "balanced",
  "models": {
    "openai_gpt-4o-mini": {
      "enabled": true,
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "groq_llama-3.1-70b-versatile": {
      "enabled": true,
      "temperature": 0.8,
      "max_tokens": 1500
    }
  }
}
```

Load it:

```python
integrator = get_model_integrator(config_file="model_config.json")
```

## 🆘 Troubleshooting

### Issue: "Model not available"

**Solution:** Check that:
1. API key is set correctly in `.env`
2. Required package is installed (`pip install groq` or `pip install google-generativeai`)
3. Model name is correct

### Issue: High costs

**Solution:**
1. Switch to `MODEL_STRATEGY=cost`
2. Use Groq for more requests (free tier)
3. Reduce `max_tokens` in requests
4. Implement response caching

### Issue: Slow responses

**Solution:**
1. Switch to `MODEL_STRATEGY=speed`
2. Use Groq models (fastest)
3. Reduce `max_tokens`
4. Use `gemini-1.5-flash` or `gpt-3.5-turbo`

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Groq API Documentation](https://console.groq.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

## 💡 Tips for Maximizing Your Paid Plans

1. **Use Groq Free Tier First**: Test with Groq before using paid models
2. **Batch Similar Requests**: Group similar queries to optimize token usage
3. **Set Appropriate Temperature**: Lower temperature = more consistent (and cheaper) responses
4. **Monitor Daily**: Check costs daily to catch unexpected usage
5. **Use Right Model for Task**: Don't use GPT-4o for simple questions - use GPT-4o-mini or Groq
6. **Implement Rate Limiting**: Prevent accidental high-volume usage
7. **Cache Common Responses**: Many queries can be cached

---

**Need Help?** Check the code comments in `model_integrator.py` or review the integration examples.

