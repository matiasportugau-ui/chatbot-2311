# WhatsApp Agent Mode Workflow - Overview

This directory contains the complete n8n workflow for the WhatsApp conversational chatbot in agent mode, as specified in the project plan.

## 📁 Files

- **`workflow-whatsapp-agent-mode.json`** - The main n8n workflow file (import this into n8n)
- **`AGENT_MODE_SETUP_GUIDE.md`** - Comprehensive setup and configuration guide
- **`QUICK_START.md`** - Quick 5-minute setup guide
- **`README_AGENT_MODE.md`** - This file (overview)

## 🎯 What This Workflow Does

The workflow implements the complete WhatsApp chatbot pipeline:

1. **Webhook Verification (GET)** - Handles Meta's webhook verification challenge
2. **Message Reception (POST)** - Receives WhatsApp messages from Meta
3. **Security** - Validates X-Hub-Signature-256 and timestamp
4. **Message Extraction** - Parses WhatsApp webhook payload
5. **AI Processing** - Calls Python FastAPI service (`/chat/process`)
6. **Response Routing** - Branches by response type (cotizacion|informacion|pregunta|seguimiento)
7. **Persistence** - Stores transcripts in MongoDB with session tracking
8. **Reply** - Sends formatted response via WhatsApp API
9. **Error Handling** - Dead-letter queue (DLQ) for failed messages

## 🏗️ Workflow Architecture

```
┌─────────────────┐
│  GET Webhook    │ → Verify Webhook → Respond Challenge
└─────────────────┘

┌─────────────────┐
│  POST Webhook   │ → Verify Signature → Extract Message
└─────────────────┘
                        ↓
              Call Python LLM API
                        ↓
              Route by Response Type
                        ↓
              Persist to MongoDB
                        ↓
              Format WhatsApp Response
                        ↓
              Send via WhatsApp API
                        ↓
              Update Transcript
                        ↓
              Respond Success
```

## 🚀 Getting Started

### Quick Start (5 minutes)
See [QUICK_START.md](./QUICK_START.md)

### Full Setup Guide
See [AGENT_MODE_SETUP_GUIDE.md](./AGENT_MODE_SETUP_GUIDE.md)

## 📋 Prerequisites

1. **n8n instance** (self-hosted or cloud)
2. **Meta WhatsApp Business Account** with API access
3. **Python FastAPI service** running (see `api_server.py`)
4. **MongoDB** instance (local or cloud)
5. **Environment variables** configured (see setup guide)

## 🔑 Required Environment Variables

```bash
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_APP_SECRET=your_app_secret
PY_CHAT_SERVICE_URL=http://localhost:8000
```

## 📊 MongoDB Collections

The workflow creates/uses these collections:

- **`whatsapp_transcripts`** - Conversation transcripts with session tracking
- **`whatsapp_dlq`** - Dead-letter queue for failed messages

## 🔄 Workflow Nodes

### Entry Points
- **Webhook Verify (GET)** - Handles webhook verification
- **Webhook Message (POST)** - Receives WhatsApp messages

### Processing Nodes
- **Verify Webhook** - Validates verification token
- **Verify Signature** - Validates X-Hub-Signature-256
- **Extract Message Data** - Parses WhatsApp payload
- **Call Python LLM API** - Processes message with AI
- **Route by Response Type** - Branches by tipo field
- **Format WhatsApp Response** - Formats message for WhatsApp
- **Send WhatsApp Message** - Sends via Meta API

### Persistence Nodes
- **Persist to MongoDB** - Saves transcripts
- **Update Transcript (Sent)** - Updates with WhatsApp response ID

### Error Handling
- **Format Error** - Captures error details
- **Save to DLQ** - Stores failed messages
- **Respond Error** - Returns error response

## 🧪 Testing

### 1. Test Webhook Verification
```bash
curl "https://your-n8n.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=your_token"
# Expected: test123
```

### 2. Test Message Processing
Send a test message from WhatsApp to your business number.

### 3. Verify MongoDB
```javascript
db.whatsapp_transcripts.find().sort({processedAt: -1}).limit(5)
```

## 🔍 Monitoring

- **n8n Executions** - View execution logs in n8n UI
- **MongoDB Queries** - Check transcripts and DLQ
- **Python API Logs** - Monitor FastAPI service logs

## 🐛 Troubleshooting

Common issues and solutions:

1. **Webhook verification fails** → Check `WHATSAPP_VERIFY_TOKEN`
2. **Signature verification fails** → Verify `WHATSAPP_APP_SECRET` and raw body access
3. **Python API timeout** → Check `PY_CHAT_SERVICE_URL` and service status
4. **WhatsApp message not sent** → Verify access token and phone number ID
5. **MongoDB connection fails** → Check credentials and connection string

See [AGENT_MODE_SETUP_GUIDE.md](./AGENT_MODE_SETUP_GUIDE.md) for detailed troubleshooting.

## 🔐 Security Considerations

- ✅ Signature verification on all POST requests
- ✅ Timestamp validation (rejects old requests)
- ✅ Environment variables for secrets
- ✅ Error logging without exposing PII
- ⚠️ **TODO**: Add rate limiting (use n8n Queue node)
- ⚠️ **TODO**: Add IP allowlist for Python API
- ⚠️ **TODO**: Rotate tokens regularly

## 📈 Next Steps

After setup:

1. ✅ Test end-to-end flow
2. ✅ Monitor first conversations
3. ✅ Review MongoDB transcripts
4. ✅ Adjust Python prompts based on responses
5. ✅ Set up alerts for errors
6. ⏳ Configure background agents (optional, phase 3)

## 📚 Related Documentation

- [Project Plan](../../whats.plan.md) - Overall architecture
- [AI Model Integration](../../AI_MODEL_INTEGRATION.md) - Python service setup
- [n8n Documentation](https://docs.n8n.io/)
- [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section in the setup guide
2. Review n8n execution logs
3. Check MongoDB for error details in DLQ
4. Verify Python API is responding correctly

## 📝 Version History

- **v1.0** - Initial workflow implementation
  - Webhook verification (GET/POST)
  - Signature validation
  - Python API integration
  - MongoDB persistence
  - WhatsApp reply
  - Error handling with DLQ

