# Quick Start Guide - WhatsApp Agent Mode Workflow

## 🚀 Fast Setup (5 minutes)

### Step 1: Import Workflow
1. Open n8n
2. **Workflows** → **Import from File**
3. Select `workflow-whatsapp-agent-mode.json`
4. Click **Import**

### Step 2: Set Environment Variables
In n8n: **Settings** → **Environment Variables**

```bash
WHATSAPP_VERIFY_TOKEN=your_token_here
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_APP_SECRET=your_app_secret
PY_CHAT_SERVICE_URL=http://localhost:8000
```

### Step 3: Configure MongoDB Credentials
1. **Credentials** → **Add Credential** → **MongoDB**
2. Enter connection string: `mongodb://localhost:27017`
3. Database: `bmc_chatbot`

### Step 4: Get Webhook URL
1. Click **Webhook Message (POST)** node
2. Copy **Production URL**
3. Example: `https://your-n8n.com/webhook/whatsapp`

### Step 5: Configure Meta Webhook
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Your App → **WhatsApp** → **Configuration**
3. **Webhook** → **Edit**
4. URL: `https://your-n8n.com/webhook/whatsapp`
5. Verify Token: (same as `WHATSAPP_VERIFY_TOKEN`)
6. Subscribe to: **messages**
7. **Verify and Save**

### Step 6: Activate Workflow
1. Toggle **Active** switch (top right)
2. Test with a WhatsApp message

## ✅ Test Verification

```bash
# Test GET (webhook verification)
curl "https://your-n8n.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=your_token"
# Should return: test123
```

## 📝 Notes

- **Python Service**: Must be running at `PY_CHAT_SERVICE_URL`
- **MongoDB**: Collections `whatsapp_transcripts` and `whatsapp_dlq` will be created automatically
- **Signature Verification**: Requires raw body - see full guide for advanced configuration

## 🆘 Troubleshooting

**Webhook verification fails?**
- Check `WHATSAPP_VERIFY_TOKEN` matches Meta config

**Signature verification fails?**
- Ensure `WHATSAPP_APP_SECRET` is set correctly
- Check webhook node returns raw body (see full guide)

**Python API timeout?**
- Verify `PY_CHAT_SERVICE_URL` is accessible
- Check Python service is running: `curl http://localhost:8000/health`

For detailed setup, see [AGENT_MODE_SETUP_GUIDE.md](./AGENT_MODE_SETUP_GUIDE.md)

