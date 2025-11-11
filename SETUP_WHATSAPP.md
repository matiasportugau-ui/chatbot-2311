# WhatsApp Integration Setup Guide

This guide walks you through setting up the complete WhatsApp conversational chatbot system.

## Prerequisites

- Docker and Docker Compose installed
- Meta Developer Account
- OpenAI API Key
- MongoDB (included in docker-compose)

## Step 1: Configure Environment Variables

Copy `env.example` to `.env` and fill in the required values:

```bash
cp env.example .env
```

Required variables:

### WhatsApp Configuration
- `WHATSAPP_VERIFY_TOKEN`: Token for webhook verification (create a secure random string)
- `WHATSAPP_ACCESS_TOKEN`: Your WhatsApp Business API access token
- `WHATSAPP_PHONE_NUMBER_ID`: Your WhatsApp phone number ID
- `WHATSAPP_BUSINESS_ID`: Your WhatsApp Business ID

### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)

### Service URLs
- `PY_CHAT_SERVICE_URL`: URL of Python API (default: `http://localhost:8000`)
- `N8N_WEBHOOK_URL_EXTERNAL`: External URL for n8n webhook (use ngrok in dev)

## Step 2: Set Up Meta WhatsApp Business API

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use existing
3. Add "WhatsApp" product to your app
4. Get your Phone Number ID and Access Token
5. Configure webhook:
   - Webhook URL: `https://your-domain.com/webhook/whatsapp` (or ngrok URL for dev)
   - Verify Token: Use the same value as `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to `messages` field

## Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f chat-api
docker-compose logs -f n8n
docker-compose logs -f mongodb
```

## Step 4: Import n8n Workflow

1. Access n8n at `http://localhost:5678`
2. Login with credentials (default: admin/bmc2024)
3. Import workflow from `n8n_workflows/workflow-whatsapp-complete.json`
4. Configure credentials:
   - MongoDB credentials
   - WhatsApp API credentials (HTTP Header Auth)
5. Activate the workflow

## Step 5: Test the Integration

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Process Message
```bash
curl -X POST http://localhost:8000/chat/process \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Hola, necesito información sobre Isodec",
    "telefono": "+59891234567"
  }'
```

### Test 3: E2E Test
```bash
./scripts/test-e2e-whatsapp.sh
```

## Step 6: Access Simulator

1. Start Next.js app (if not already running)
2. Navigate to `http://localhost:3000/simulator`
3. Test conversations without WhatsApp integration

## Step 7: Set Up Background Agents (Optional)

For automated follow-ups:

```bash
# Run once
python background_agent_followup.py

# Run continuously
python background_agent_followup.py --continuous
```

Or add to cron:
```bash
# Run every hour
0 * * * * cd /path/to/project && python background_agent_followup.py
```

## Step 8: Monitoring and Observability

### Check MongoDB Collections
```bash
# Connect to MongoDB
docker exec -it bmc-mongodb mongosh

# Check conversations
use bmc_chat
db.conversations.find().limit(5)

# Check error logs
db.error_logs.find().limit(5)
```

### View API Logs
```bash
docker-compose logs -f chat-api | grep -E "Request|Response|Error"
```

### n8n Execution Logs
- Access n8n UI
- Go to Executions tab
- View workflow execution history

## Troubleshooting

### Webhook Verification Fails
- Check that `WHATSAPP_VERIFY_TOKEN` matches in both Meta and your `.env`
- Ensure webhook URL is accessible (use ngrok for local dev)

### Python API Not Responding
- Check logs: `docker-compose logs chat-api`
- Verify MongoDB connection
- Check OpenAI API key is valid

### Messages Not Being Sent
- Verify WhatsApp credentials in n8n
- Check n8n workflow is activated
- Review error logs in MongoDB `error_logs` collection

### OpenAI Errors
- Verify API key is set correctly
- Check API quota/limits
- System will fallback to pattern matching if OpenAI fails

## Production Deployment

1. Use production-grade secrets management
2. Set up proper SSL/TLS for webhook
3. Configure rate limiting
4. Set up monitoring and alerts
5. Use production MongoDB (not local)
6. Configure backup strategy
7. Set up log aggregation
8. Enable request ID tracking for debugging

## Security Checklist

- [ ] Webhook signature verification enabled
- [ ] Tokens stored in secure vault (not in code)
- [ ] API access restricted (IP allowlist or auth token)
- [ ] PII data masked in logs
- [ ] Rate limiting configured
- [ ] HTTPS enabled for all endpoints
- [ ] Regular security updates

## Next Steps

- Fine-tune OpenAI prompts based on conversations
- Add more conversation types
- Implement analytics dashboard
- Set up automated testing
- Configure alerts for errors

