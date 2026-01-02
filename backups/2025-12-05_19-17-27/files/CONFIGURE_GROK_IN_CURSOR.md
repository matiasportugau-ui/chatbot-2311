# How to Configure Grok in Cursor

## Method 1: Using Cursor Settings UI (Recommended)

### Step 1: Enable OpenAI API Key
1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Navigate to **AI Models** or **API Keys** section
3. Find **"OpenAI API Key"** section
4. **Enable the toggle** (green switch)
5. Enter your Grok API key: `YOUR_GROK_API_KEY_HERE`

### Step 2: Override Base URL
1. Find **"Override OpenAI Base URL"** section
2. **Enable the toggle** (turn it green)
3. Enter the xAI API endpoint: `https://api.x.ai/v1`

### Step 3: Use Grok Models
Now you can use Grok models in Cursor:
- `grok-4-latest`
- `grok-beta`
- `grok-2-1212`
- `grok-2-vision-1212`

## Method 2: Using Environment Variables

Add to your `.env` file or Cursor's environment:

```bash
OPENAI_API_KEY=YOUR_GROK_API_KEY_HERE
OPENAI_BASE_URL=https://api.x.ai/v1
```

## Method 3: Using Cursor Config File

If Cursor supports a config file, you can add:

```json
{
  "openai": {
    "apiKey": "YOUR_GROK_API_KEY_HERE",
    "baseURL": "https://api.x.ai/v1"
  }
}
```

## Quick Setup Checklist

- [ ] Enable OpenAI API Key toggle in Cursor settings
- [ ] Enter Grok API key: `YOUR_GROK_API_KEY_HERE`
- [ ] Enable "Override OpenAI Base URL" toggle
- [ ] Set Base URL to: `https://api.x.ai/v1`
- [ ] Test by asking Cursor a question

## Testing

After configuration, test it by:
1. Opening Cursor chat (Cmd/Ctrl + L)
2. Asking: "Hello, are you using Grok?"
3. Or specify model: "Use grok-4-latest to explain Python decorators"

## Important Notes

⚠️ **When using Grok via OpenAI Base URL override:**
- Your OpenAI API key field will be used for Grok
- You won't be able to use regular OpenAI models simultaneously
- To switch back to OpenAI, disable the Base URL override

💡 **Alternative Approach:**
- Use the `model_integrator.py` we created for multi-provider support
- This allows using Grok, OpenAI, Gemini, and Groq simultaneously
- See `QUICK_START_CURSOR_AGENTS.md` for details

## Troubleshooting

**"Invalid API key" error:**
- Verify the API key starts with `xai-`
- Check the key is active in xAI dashboard
- Ensure no extra spaces in the key

**"Model not found" error:**
- Use exact model names: `grok-4-latest`, `grok-beta`, etc.
- Check xAI dashboard for available models

**Base URL not working:**
- Ensure the toggle is enabled (green)
- Verify URL is exactly: `https://api.x.ai/v1`
- Try restarting Cursor

