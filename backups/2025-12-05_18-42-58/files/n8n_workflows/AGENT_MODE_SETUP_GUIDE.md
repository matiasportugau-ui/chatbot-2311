# WhatsApp Agent Mode Workflow - Setup Guide

This guide explains how to set up and configure the n8n workflow for the WhatsApp conversational chatbot in agent mode.

## 📋 Overview

This workflow implements the complete WhatsApp chatbot pipeline as specified in `whats.plan.md`:

1. **Webhook Verification** (GET) - Handles Meta's webhook verification
2. **Message Processing** (POST) - Receives and processes WhatsApp messages
3. **Signature Verification** - Validates X-Hub-Signature-256
4. **Message Extraction** - Parses WhatsApp webhook payload
5. **LLM Processing** - Calls Python FastAPI service (`/chat/process`)
6. **Response Routing** - Branches by response type (cotizacion|informacion|pregunta|seguimiento)
7. **MongoDB Persistence** - Stores transcripts with session IDs
8. **WhatsApp Reply** - Sends response via Meta WhatsApp API
9. **Error Handling** - Dead-letter queue (DLQ) for failed messages

## 🔧 Prerequisites

### 1. Environment Variables

Configure these in n8n (Settings → Environment Variables) or in your `.env` file:

```bash
# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=your_verify_token_here
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ID=your_business_id
WHATSAPP_APP_SECRET=your_app_secret

# Python Service
PY_CHAT_SERVICE_URL=http://localhost:8000

# MongoDB (if not using n8n credentials)
MONGODB_URI=mongodb://localhost:27017/bmc_chatbot
```

### 2. n8n Credentials Setup

#### MongoDB Credentials
1. Go to **Credentials** → **Add Credential**
2. Select **MongoDB**
3. Configure:
   - **Connection String**: `mongodb://localhost:27017` (or your MongoDB URI)
   - **Database**: `bmc_chatbot` (or your database name)

#### HTTP Header Auth (for WhatsApp API)
1. Go to **Credentials** → **Add Credential**
2. Select **HTTP Header Auth**
3. Configure:
   - **Name**: `WhatsApp API`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer {{ $env.WHATSAPP_ACCESS_TOKEN }}`

## 📥 Importing the Workflow

### Option 1: Import JSON File
1. Open n8n UI
2. Click **Workflows** → **Import from File**
3. Select `workflow-whatsapp-agent-mode.json`
4. Click **Import**

### Option 2: Copy-Paste JSON
1. Open n8n UI
2. Click **Workflows** → **New Workflow**
3. Click the **⋮** menu → **Import from JSON**
4. Paste the contents of `workflow-whatsapp-agent-mode.json`
5. Click **Import**

## 🔗 Configuring Webhook URLs

### 1. Get Your n8n Webhook URL

After importing the workflow:
1. Click on **Webhook Verify (GET)** node
2. Copy the **Production URL** (e.g., `https://your-n8n-instance.com/webhook/whatsapp`)
3. Do the same for **Webhook Message (POST)** (should be the same URL)

### 2. Configure Meta WhatsApp Webhook

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Select your WhatsApp Business App
3. Go to **WhatsApp** → **Configuration**
4. Under **Webhook**, click **Edit**
5. Enter your webhook URL: `https://your-n8n-instance.com/webhook/whatsapp`
6. Enter your verify token (must match `WHATSAPP_VERIFY_TOKEN`)
7. Subscribe to **messages** field
8. Click **Verify and Save**

## 🎯 Node Configuration Details

### Webhook Nodes

#### Webhook Verify (GET)
- **Path**: `webhook/whatsapp`
- **Method**: GET
- **Response Mode**: Respond to Webhook

#### Webhook Message (POST)
- **Path**: `webhook/whatsapp`
- **Method**: POST
- **Response Mode**: Respond to Webhook

### Verify Signature Node

This node validates the `X-Hub-Signature-256` header using HMAC-SHA256:
- Uses `WHATSAPP_APP_SECRET` for signature calculation
- Rejects requests older than 5 minutes (timestamp check)
- Uses constant-time comparison to prevent timing attacks

**Important Note**: For signature verification to work correctly, the webhook node needs access to the raw request body. The workflow attempts to handle both parsed and raw bodies, but if signature verification consistently fails:

1. Check that `WHATSAPP_APP_SECRET` matches your Meta app secret
2. Verify the webhook node is receiving the raw body (n8n may parse JSON automatically)
3. If needed, you can disable signature verification temporarily for testing by modifying the "Signature Valid?" node to always return `true`

### Extract Message Data Node

This node parses the WhatsApp webhook payload:
- Extracts: `mensaje`, `telefono`, `messageId`, `timestamp`
- Generates consistent `sesionId` (daily session per phone number)
- Handles contact information if available

### Call Python LLM API Node

- **URL**: `{{ $env.PY_CHAT_SERVICE_URL }}/chat/process`
- **Method**: POST
- **Body**:
  ```json
  {
    "mensaje": "{{ $json.mensaje }}",
    "telefono": "{{ $json.telefono }}",
    "sesionId": "{{ $json.sesionId }}"
  }
  ```
- **Timeout**: 30 seconds
- **Retries**: 2 retries on 5xx errors

### Route by Response Type Node

Routes based on `tipo` field from Python API:
- `cotizacion` → Quote handling
- `informacion` → Information response
- `pregunta` → Question response
- `seguimiento` → Follow-up response
- `default` → Generic response

### Persist to MongoDB Node

Stores conversation transcripts:
- **Collection**: `whatsapp_transcripts`
- **Fields**: sessionId, phoneNumber, userMessage, botResponse, responseType, confidence, timestamp, etc.

### Format WhatsApp Response Node

Formats the response message:
- Adds emoji formatting for quotes
- Formats prices with locale (es-UY)
- Structures multi-line responses

### Send WhatsApp Message Node

- **URL**: `https://graph.facebook.com/v19.0/{{ WHATSAPP_PHONE_NUMBER_ID }}/messages`
- **Method**: POST
- **Headers**: Authorization Bearer token
- **Body**:
  ```json
  {
    "messaging_product": "whatsapp",
    "to": "+5989xxxxxxx",
    "type": "text",
    "text": { "body": "Response message" }
  }
  ```
- **Retries**: 3 retries on 429, 5xx errors

### Error Handling

#### Format Error Node
Captures error details for logging

#### Save to DLQ Node
- **Collection**: `whatsapp_dlq`
- Stores failed messages for retry/review
- Includes: error message, stack trace, sessionId, retryable flag

## 🧪 Testing

### 1. Test Webhook Verification (GET)

```bash
curl "https://your-n8n-instance.com/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=your_verify_token"
```

Expected response: `test123`

### 2. Test Message Processing (POST)

```bash
curl -X POST https://your-n8n-instance.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "59891234567",
            "id": "wamid.test123",
            "timestamp": "1234567890",
            "type": "text",
            "text": { "body": "Hola, necesito una cotización" }
          }],
          "contacts": [{
            "profile": { "name": "Test User" }
          }],
          "metadata": {
            "phone_number_id": "your_phone_id"
          }
        }
      }]
    }]
  }'
```

### 3. Verify MongoDB Collections

Check that transcripts are being saved:
```javascript
// In MongoDB shell or Compass
db.whatsapp_transcripts.find().sort({timestamp: -1}).limit(5)
db.whatsapp_dlq.find().sort({timestamp: -1}).limit(5)
```

## 🔍 Monitoring & Debugging

### 1. n8n Execution Logs

- Go to **Executions** tab
- Filter by workflow name
- Check execution details for errors

### 2. MongoDB Queries

```javascript
// Recent transcripts
db.whatsapp_transcripts.find().sort({processedAt: -1}).limit(10)

// Failed messages
db.whatsapp_dlq.find({retryable: true, retryCount: {$lt: 3}})

// Session history
db.whatsapp_transcripts.find({sessionId: "wa_59891234567_12345"})
```

### 3. Python API Logs

Check your FastAPI service logs for:
- Request/response details
- LLM processing times
- Error messages

## 🚀 Production Checklist

- [ ] Set `WHATSAPP_VERIFY_TOKEN` to a strong random value
- [ ] Store `WHATSAPP_ACCESS_TOKEN` securely (rotate regularly)
- [ ] Configure `WHATSAPP_APP_SECRET` for signature verification
- [ ] Set `PY_CHAT_SERVICE_URL` to production URL
- [ ] Enable MongoDB authentication
- [ ] Configure n8n webhook to use HTTPS
- [ ] Set up monitoring/alerts for DLQ
- [ ] Test rate limiting (n8n Queue node if needed)
- [ ] Enable request ID tracking
- [ ] Set up log aggregation

## 🔄 Workflow Activation

1. Click **Active** toggle in n8n (top right)
2. Verify webhook is accessible
3. Test with Meta's webhook verification
4. Send a test message from WhatsApp

## 📊 Expected Flow

```
WhatsApp Message
    ↓
Meta Webhook → n8n Webhook (POST)
    ↓
Verify Signature ✓
    ↓
Extract Message Data
    ↓
Call Python API (/chat/process)
    ↓
Route by Type (cotizacion|informacion|pregunta|seguimiento)
    ↓
Persist to MongoDB
    ↓
Format Response
    ↓
Send via WhatsApp API
    ↓
Update Transcript (sent)
    ↓
Respond Success
```

## 🐛 Troubleshooting

### Issue: Webhook verification fails
- Check `WHATSAPP_VERIFY_TOKEN` matches Meta configuration
- Verify webhook URL is accessible
- Check n8n webhook node is active

### Issue: Signature verification fails
- Verify `WHATSAPP_APP_SECRET` is correct
- Check timestamp is within 5 minutes
- Ensure raw body is used for signature calculation

### Issue: Python API timeout
- Check `PY_CHAT_SERVICE_URL` is correct
- Verify Python service is running
- Check network connectivity between n8n and Python service
- Increase timeout in HTTP Request node

### Issue: WhatsApp message not sent
- Verify `WHATSAPP_ACCESS_TOKEN` is valid
- Check `WHATSAPP_PHONE_NUMBER_ID` is correct
- Verify phone number format (include country code)
- Check Meta API rate limits

### Issue: MongoDB connection fails
- Verify MongoDB credentials in n8n
- Check MongoDB is accessible from n8n
- Verify database and collection names
- Check MongoDB connection string format

## 📚 Additional Resources

- [Meta WhatsApp Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [n8n Documentation](https://docs.n8n.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Node.js Driver](https://www.mongodb.com/docs/drivers/node/current/)

## 🔐 Security Notes

1. **Never commit secrets** to version control
2. **Rotate tokens** regularly (every 90 days)
3. **Use HTTPS** for all webhook URLs
4. **Validate signatures** on every request
5. **Sanitize logs** (mask phone numbers, PII)
6. **Rate limit** webhook endpoints
7. **Monitor DLQ** for suspicious patterns

## 📝 Next Steps

After setup:
1. Test end-to-end flow
2. Monitor first few conversations
3. Review MongoDB transcripts
4. Adjust Python prompts based on responses
5. Set up alerts for errors
6. Configure background agents (optional, phase 3)

