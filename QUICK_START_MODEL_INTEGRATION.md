# Quick Start: Multi-Provider AI Model Integration

## 🎯 What You Get

You now have a unified system that can use:
- **OpenAI** (GPT-4o, GPT-4o-mini, GPT-3.5-turbo)
- **Groq** (Llama 3.1, Mixtral - FREE tier available!)
- **Google Gemini** (Gemini 1.5 Pro, Gemini 1.5 Flash)

With automatic:
- ✅ Cost optimization
- ✅ Model selection based on your strategy
- ✅ Usage tracking
- ✅ Fallback handling
- ✅ Performance monitoring

## 🚀 3-Step Setup

### Step 1: Install Dependencies

```bash
cd /Users/matias/chatbot2511/chatbot-2311
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI SDK
- `groq` - Groq SDK (fast inference)
- `google-generativeai` - Google Gemini SDK

### Step 2: Configure API Keys

Create or edit your `.env` file:

```bash
# Copy example if you don't have .env
cp env.example .env
```

Add your API keys:

```bash
# OpenAI (required for GPT models)
OPENAI_API_KEY=sk-your-key-here

# Groq (FREE tier - highly recommended!)
GROQ_API_KEY=gsk-your-key-here

# Google Gemini
GEMINI_API_KEY=your-key-here

# Optional: Set strategy
MODEL_STRATEGY=balanced  # Options: cost, speed, quality, balanced
```

**Where to get API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Groq**: https://console.groq.com/keys (FREE tier!)
- **Gemini**: https://aistudio.google.com/app/apikey

### Step 3: Test the Integration

```bash
python test_model_integrator.py
```

This will:
- ✅ Check all API keys
- ✅ List available models
- ✅ Test a sample request
- ✅ Show cost and performance metrics

## 💡 How It Works

### Automatic Model Selection

The system automatically selects the best model based on your strategy:

```python
# In your .env file:
MODEL_STRATEGY=cost      # Minimize costs (uses Groq free tier first)
MODEL_STRATEGY=speed     # Maximize speed (uses Groq)
MODEL_STRATEGY=quality   # Maximize quality (uses GPT-4o, Gemini Pro)
MODEL_STRATEGY=balanced  # Best balance (default)
```

### Usage in Your Code

The integration is already done! Your existing chat system (`ia_conversacional_integrada.py`) now automatically uses the model integrator.

**Manual usage example:**

```python
from model_integrator import get_model_integrator

integrator = get_model_integrator()

# Generate a response
response = integrator.generate(
    prompt="Help me with a quote",
    system_prompt="You are a helpful assistant for BMC Uruguay",
    max_tokens=500
)

print(response["content"])
print(f"Cost: ${response['cost']:.6f}")
print(f"Model: {response['model_used']}")
```

## 💰 Cost Optimization Tips

### 1. Use Groq for High-Volume Tasks

Groq offers a **free tier** with excellent performance. Perfect for:
- Development and testing
- High-frequency queries
- Simple Q&A
- Real-time chat

The system will automatically use Groq when `MODEL_STRATEGY=cost` is set.

### 2. Tiered Usage Strategy

- **Simple queries** → Groq (free/fast)
- **Standard queries** → GPT-4o-mini ($0.15/$0.60 per 1M tokens)
- **Complex queries** → GPT-4o or Gemini Pro

### 3. Monitor Your Usage

Check costs anytime:

```python
from model_integrator import get_model_integrator

integrator = get_model_integrator()
summary = integrator.get_usage_summary()

print(f"Total Cost: ${summary['total_cost']:.2f}")
print(f"Total Requests: {summary['total_requests']}")
```

Stats are automatically saved to `model_usage_stats.json`.

## 📊 Model Comparison

| Provider | Model | Cost (per 1M tokens) | Speed | Quality | Best For |
|----------|-------|---------------------|-------|---------|----------|
| **Groq** | Llama 3.1 70B | **FREE** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | High volume, fast responses |
| **Groq** | Llama 3.1 8B | **FREE** | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Simple queries, instant responses |
| **OpenAI** | GPT-4o-mini | $0.15/$0.60 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Cost-effective production use |
| **OpenAI** | GPT-4o | $2.50/$10.00 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Complex reasoning, high quality |
| **Gemini** | Gemini 1.5 Flash | $0.075/$0.30 | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Fast, cost-effective |
| **Gemini** | Gemini 1.5 Pro | $1.25/$5.00 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks, long context |

## 🎯 Recommended Setup for Your Paid Plans

### For Maximum Value:

1. **Set `MODEL_STRATEGY=cost`** in `.env`
   - Uses Groq free tier first
   - Falls back to cheapest paid models when needed

2. **Enable all providers** in `.env`:
   ```bash
   OPENAI_MODELS=gpt-4o-mini,gpt-4o
   GROQ_MODELS=llama-3.1-70b-versatile,llama-3.1-8b-instant
   GEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro
   ```

3. **Monitor daily**:
   ```bash
   python test_model_integrator.py
   # Check model_usage_stats.json
   ```

### For Best Performance:

1. **Set `MODEL_STRATEGY=balanced`** (default)
   - Automatically balances cost, speed, and quality
   - Uses the best model for each task

2. **Use Groq for real-time chat** (fastest)
3. **Use GPT-4o-mini for standard queries** (cost-effective)
4. **Use GPT-4o or Gemini Pro for complex tasks** (best quality)

## 🔧 Troubleshooting

### "No models configured"

**Solution:** Make sure you have at least one API key set in `.env`:
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`

### "Model not available"

**Solution:** 
1. Check API key is correct
2. Install required package: `pip install groq` or `pip install google-generativeai`
3. Check model name is correct

### High costs

**Solution:**
1. Set `MODEL_STRATEGY=cost` in `.env`
2. Use Groq more (free tier)
3. Reduce `max_tokens` in requests
4. Check `model_usage_stats.json` to see which models are being used

## 📚 Next Steps

1. ✅ Run `python test_model_integrator.py` to verify setup
2. ✅ Check `MODEL_INTEGRATOR_SETUP.md` for detailed documentation
3. ✅ Monitor usage with `model_usage_stats.json`
4. ✅ Adjust `MODEL_STRATEGY` based on your needs

## 🎉 You're All Set!

Your chatbot now automatically uses the best model for each request, optimizing for cost, speed, or quality based on your preferences.

**Questions?** Check the detailed guide in `MODEL_INTEGRATOR_SETUP.md`

