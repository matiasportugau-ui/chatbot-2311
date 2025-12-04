# Docker Secrets Setup Guide

This guide explains how to securely manage secrets for the BMC Chatbot System in production.

## Overview

Docker secrets provide a secure way to store sensitive data like passwords, API keys, and tokens. Unlike environment variables, secrets:
- Are encrypted at rest
- Are only available to services that need them
- Are mounted in memory (tmpfs) instead of being stored on disk
- Are never logged or visible in `docker inspect`

## Quick Setup

### 1. Create Secrets Directory

```bash
mkdir -p secrets
chmod 700 secrets
```

### 2. Create Secret Files

```bash
# OpenAI API Key
echo "sk-your-openai-api-key" > secrets/openai_api_key.txt

# JWT Secret (generate with: openssl rand -hex 32)
openssl rand -hex 32 > secrets/jwt_secret_key.txt

# WhatsApp Webhook Secret
echo "your-whatsapp-webhook-secret" > secrets/whatsapp_webhook_secret.txt

# API Keys (comma-separated)
echo "key1,key2,key3" > secrets/api_keys.txt

# n8n Credentials
echo "admin" > secrets/n8n_user.txt
echo "$(openssl rand -base64 32)" > secrets/n8n_password.txt

# MongoDB Credentials
echo "mongoroot" > secrets/mongo_root_username.txt
echo "$(openssl rand -base64 32)" > secrets/mongo_root_password.txt

# Qdrant API Key
echo "$(openssl rand -hex 32)" > secrets/qdrant_api_key.txt
```

### 3. Secure the Files

```bash
chmod 600 secrets/*.txt
```

### 4. Add to .gitignore

The `secrets/` directory should already be in .gitignore. Verify:

```bash
echo "secrets/" >> .gitignore
```

## Usage

### Development (docker-compose.yml)

For development, use environment variables from `.env` file:

```bash
cp .env.example .env
# Edit .env with your values
docker-compose up -d
```

### Production (docker-compose.prod.yml)

For production, use Docker secrets:

```bash
# 1. Set up secrets (see above)
# 2. Set environment variables for non-sensitive config
export CORS_ALLOWED_ORIGINS="https://yourdomain.com"
export WEBHOOK_URL="https://yourdomain.com/webhook"
export N8N_PROTOCOL="https"

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Docker Swarm (Recommended for Production)

For Docker Swarm, use built-in secrets management:

```bash
# Create secrets in Swarm
echo "sk-your-key" | docker secret create openai_api_key -
docker secret create jwt_secret_key secrets/jwt_secret_key.txt

# Deploy stack
docker stack deploy -c docker-compose.prod.yml bmc
```

## Reading Secrets in Application Code

### Python Example

```python
import os

def get_secret(secret_name, default=None):
    """Read secret from file or environment variable"""
    # Try Docker secret file first
    secret_file = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_file):
        with open(secret_file) as f:
            return f.read().strip()
    
    # Fallback to environment variable
    env_file_var = f"{secret_name.upper()}_FILE"
    secret_path = os.getenv(env_file_var)
    if secret_path and os.path.exists(secret_path):
        with open(secret_path) as f:
            return f.read().strip()
    
    # Fallback to regular environment variable
    return os.getenv(secret_name.upper(), default)

# Usage
OPENAI_API_KEY = get_secret("openai_api_key")
JWT_SECRET_KEY = get_secret("jwt_secret_key")
```

## Security Best Practices

1. **Never commit secrets to version control**
   - Add `secrets/` to `.gitignore`
   - Use `.env.example` for templates only

2. **Rotate secrets regularly**
   - Change secrets every 90 days
   - Rotate immediately if compromised

3. **Use strong, random values**
   - Generate with `openssl rand -hex 32` or similar
   - Minimum 32 characters for keys

4. **Limit secret access**
   - Only grant access to services that need them
   - Use principle of least privilege

5. **Monitor secret usage**
   - Log secret access attempts
   - Alert on suspicious activity

## Migrating from Environment Variables

If you're currently using environment variables in `.env`:

1. **Create secret files** from your `.env` values:
   ```bash
   grep "OPENAI_API_KEY" .env | cut -d'=' -f2 > secrets/openai_api_key.txt
   ```

2. **Update docker-compose** to use `docker-compose.prod.yml`

3. **Remove secrets from `.env`** (keep non-sensitive config)

4. **Restart services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Troubleshooting

### Secret not found error

```bash
# Check if secret file exists
ls -la secrets/

# Check file permissions
chmod 600 secrets/*.txt

# Verify secret is mounted in container
docker exec bmc-chat-api-prod ls -la /run/secrets/
```

### Permission denied

```bash
# Fix directory permissions
chmod 700 secrets/
chmod 600 secrets/*.txt
```

### Empty secret value

```bash
# Check for newlines or extra whitespace
cat -A secrets/openai_api_key.txt

# Recreate without newline
echo -n "your-secret" > secrets/openai_api_key.txt
```

## Environment-Specific Configurations

### Development
- Use `.env` file with environment variables
- OK to use simple passwords
- Docker Compose without secrets

### Staging
- Use Docker secrets
- Test secret rotation process
- Same setup as production

### Production
- **Must** use Docker secrets or similar
- Strong, random passwords (32+ chars)
- Docker Swarm or Kubernetes secrets
- Regular rotation schedule
- Monitoring and alerting

## Additional Resources

- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [12-Factor App Config](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
