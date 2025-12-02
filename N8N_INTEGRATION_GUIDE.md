# n8n Integration Guide

## ✅ Credentials Configured

Your n8n API credentials have been set up:

- **API Key (JWT)**: Configured
- **Public Key**: `mvkwbyac`
- **Private Key**: `8d26b5d5-50a3-4439-9b91-d22d16ffe455`
- **Base URL**: `http://localhost:5678` (update if hosted elsewhere)

## 🚀 Quick Start

### 1. Test Connection

```bash
python3 test_n8n_integration.py
```

### 2. Use in Your Code

```python
from n8n_api_client import get_n8n_client

# Get client
client = get_n8n_client()

# List workflows
workflows = client.get_workflows()
print(f"Found {len(workflows)} workflows")

# Trigger webhook
response = client.trigger_workflow_webhook(
    webhook_path="whatsapp",
    data={"message": "Hello from Python!"}
)
```

## 📋 Available Methods

### Workflow Management

```python
# List all workflows
workflows = client.get_workflows()

# Get specific workflow
workflow = client.get_workflow("workflow-id")

# Get active workflows only
active_workflows = client.get_workflows(active_only=True)
```

### Webhook Execution

```python
# Trigger webhook by path
response = client.trigger_workflow_webhook(
    webhook_path="whatsapp",
    data={
        "message": "Test message",
        "from": "+1234567890"
    }
)

# Execute workflow directly
response = client.execute_workflow(
    workflow_id="workflow-id",
    data={"input": "data"}
)
```

### Execution History

```python
# Get recent executions
executions = client.get_executions(limit=50)

# Get executions for specific workflow
workflow_executions = client.get_executions(
    workflow_id="workflow-id",
    limit=20
)
```

### Health Check

```python
# Check n8n status
health = client.health_check()
print(health['status'])  # 'healthy' or 'unhealthy'
```

## 🔧 Configuration

### Update Base URL

If your n8n instance is hosted elsewhere, update `.env`:

```bash
N8N_BASE_URL=https://your-n8n-instance.com
```

### Authentication Methods

The client supports two authentication methods:

1. **JWT Token** (recommended):
   ```bash
   N8N_API_KEY=your-jwt-token
   ```

2. **Public/Private Keys**:
   ```bash
   N8N_PUBLIC_KEY=your-public-key
   N8N_PRIVATE_KEY=your-private-key
   ```

## 🔗 Integration with Model Integrator

You can combine n8n with your AI models:

```python
from model_integrator import get_model_integrator
from n8n_api_client import get_n8n_client

# Get AI response
integrator = get_model_integrator()
ai_response = integrator.generate(
    prompt="User question",
    model_id="grok_grok-4-latest"
)

# Send to n8n workflow
n8n_client = get_n8n_client()
n8n_response = n8n_client.trigger_workflow_webhook(
    webhook_path="process-ai-response",
    data={
        "ai_response": ai_response['content'],
        "model_used": ai_response['model_used']
    }
)
```

## 📝 Common Webhook Paths

Based on your existing setup, common webhook paths:

- `/webhook/whatsapp` - WhatsApp message processing
- `/webhook/chat` - General chat messages
- `/webhook/sheets-sync` - Google Sheets synchronization
- `/webhook/analytics` - Analytics and insights

## 🛠️ Troubleshooting

### Connection Errors

**Error: Connection refused**
- Check if n8n is running: `docker ps` (if using Docker)
- Verify `N8N_BASE_URL` is correct
- Check firewall/network settings

**Error: 401 Unauthorized**
- Verify API credentials in `.env`
- Check if JWT token is expired
- Ensure public/private keys are correct

### Workflow Not Found

**Error: 404 Not Found**
- Verify workflow ID is correct
- Check if workflow is active
- Ensure webhook path matches workflow configuration

### Testing Tips

1. **Health Check First**:
   ```python
   health = client.health_check()
   if health['status'] != 'healthy':
       print("n8n is not accessible")
   ```

2. **List Workflows**:
   ```python
   workflows = client.get_workflows()
   for wf in workflows:
       print(f"{wf['name']}: {wf['id']}")
   ```

3. **Test with Simple Data**:
   ```python
   response = client.trigger_workflow_webhook(
       webhook_path="test",
       data={"test": "data"}
   )
   ```

## 📚 Related Files

- `n8n_api_client.py` - Main API client
- `n8n_integration.py` - Python script integration (for stdin/stdout)
- `n8n-client.ts` - TypeScript client (for Next.js frontend)
- `test_n8n_integration.py` - Test script

## 🎯 Next Steps

1. ✅ Credentials configured
2. ⏭️ Test connection: `python3 test_n8n_integration.py`
3. ⏭️ List your workflows
4. ⏭️ Test webhook triggers
5. ⏭️ Integrate with your AI models


