# Secrets Management Migration Guide

## Overview

This guide explains how to migrate from `.env` files to Docker secrets for production deployment.

## Current State

- Development: Uses `.env` files (acceptable for local development)
- Production: Should use Docker secrets or external secret management (HashiCorp Vault, AWS Secrets Manager, etc.)

## Migration Steps

### Step 1: Create Secrets Directory

```bash
mkdir -p secrets
chmod 700 secrets
```

### Step 2: Create Secret Files

Create individual secret files (one per secret):

```bash
# OpenAI API Key
echo "your-openai-api-key" > secrets/openai_api_key.txt
chmod 600 secrets/openai_api_key.txt

# Qdrant API Key (if using authentication)
echo "your-qdrant-api-key" > secrets/qdrant_api_key.txt
chmod 600 secrets/qdrant_api_key.txt

# WhatsApp Token
echo "your-whatsapp-token" > secrets/whatsapp_token.txt
chmod 600 secrets/whatsapp_token.txt

# WhatsApp Phone ID
echo "your-phone-id" > secrets/whatsapp_phone_id.txt
chmod 600 secrets/whatsapp_phone_id.txt

# WhatsApp Webhook Secret
echo "your-webhook-secret" > secrets/whatsapp_webhook_secret.txt
chmod 600 secrets/whatsapp_webhook_secret.txt

# n8n Auth Password
echo "your-n8n-password" > secrets/n8n_auth_password.txt
chmod 600 secrets/n8n_auth_password.txt
```

### Step 3: Update Application Code

The application code needs to read secrets from files when `*_FILE` environment variables are set:

```python
# Example: Reading OpenAI API key
import os

openai_key_file = os.getenv("OPENAI_API_KEY_FILE")
if openai_key_file:
    with open(openai_key_file, 'r') as f:
        OPENAI_API_KEY = f.read().strip()
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Step 4: Deploy with Production Compose

```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## Alternative: HashiCorp Vault

For more advanced secret management:

1. Install and configure Vault
2. Store secrets in Vault
3. Use Vault agent or API to retrieve secrets at runtime
4. Update application to use Vault client

## Security Best Practices

1. **Never commit secrets to Git**
   - Add `secrets/` to `.gitignore`
   - Add `*.txt` in secrets directory to `.gitignore`

2. **Rotate secrets regularly**
   - Set up rotation schedule
   - Update secret files
   - Restart services

3. **Use different secrets per environment**
   - Development secrets
   - Staging secrets
   - Production secrets

4. **Limit access to secrets**
   - Use file permissions (chmod 600)
   - Use directory permissions (chmod 700)
   - Restrict access to production servers

## Secret Rotation Strategy

1. Generate new secret
2. Update secret file
3. Restart affected services
4. Verify functionality
5. Remove old secret

## Troubleshooting

### Issue: Service cannot read secret file

**Solution:** Check file permissions and path
```bash
ls -la secrets/
chmod 600 secrets/*.txt
```

### Issue: Secret not found

**Solution:** Verify secret file exists and path is correct
```bash
docker-compose -f docker-compose.prod.yml config
```

### Issue: Service fails to start

**Solution:** Check logs for secret-related errors
```bash
docker-compose -f docker-compose.prod.yml logs chat-api
```

