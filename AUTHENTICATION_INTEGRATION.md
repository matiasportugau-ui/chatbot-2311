# 🔒 Authentication Integration Guide

## Overview

This guide covers the newly integrated authentication system for the BMC Chatbot, including JWT tokens for user authentication and API keys for webhook/service authentication.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐         ┌──────────────┐                   │
│  │   Client    │────────▶│   Login      │                   │
│  │  (Web/App)  │         │   Endpoint   │                   │
│  └─────────────┘         └──────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│                         ┌────────────────┐                   │
│                         │  JWT Manager   │                   │
│                         │  - Validate    │                   │
│                         │  - Generate    │                   │
│                         └────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│                         ┌────────────────┐                   │
│                         │  JWT Token     │                   │
│                         │  (HTTP-Only)   │                   │
│                         └────────┬───────┘                   │
│                                  │                           │
│  ┌─────────────┐                │         ┌──────────────┐  │
│  │  Protected  │◀───────────────┴────────▶│ Middleware   │  │
│  │  Endpoints  │                          │ - Verify JWT │  │
│  └─────────────┘                          │ - Check Role │  │
│                                           └──────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               API Key Authentication Flow                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐         ┌──────────────┐                   │
│  │  Webhook    │────────▶│  Protected   │                   │
│  │  Provider   │  X-API- │  Endpoint    │                   │
│  │ (WhatsApp)  │   Key   │              │                   │
│  └─────────────┘         └──────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│                         ┌────────────────┐                   │
│                         │ API Key Mgr    │                   │
│                         │ - Validate     │                   │
│                         │ - Check Scope  │                   │
│                         │ - Rate Limit   │                   │
│                         └────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│                         ┌────────────────┐                   │
│                         │  Process       │                   │
│                         │  Request       │                   │
│                         └────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. JWT Manager (`src/auth/jwt_manager.py`)

**Purpose:** Generate and validate JWT tokens for user authentication

**Features:**
- Access token generation (60 min default)
- Refresh token generation (7 days default)
- Token validation and parsing
- Role-based authorization

**Usage:**

```python
from src.auth import create_access_token, verify_token, UserRole

# Create token
token = create_access_token(
    user_id="user123",
    username="john_doe",
    email="john@example.com",
    role=UserRole.USER
)

# Verify token
token_data = verify_token(token)
if token_data:
    print(f"User: {token_data.username}, Role: {token_data.role}")
```

### 2. API Key Manager (`src/auth/api_key_manager.py`)

**Purpose:** Manage API keys for webhook and service authentication

**Features:**
- Secure key generation (`bmc_` prefix)
- Key hashing (SHA256)
- Scope-based authorization
- Per-key rate limiting
- Key rotation
- Expiration management

**Usage:**

```python
from src.auth import APIKeyManager, APIKeyCreate

manager = APIKeyManager(db_connection)

# Create API key
key_data = APIKeyCreate(
    name="WhatsApp Webhook",
    scopes=["webhook:read", "webhook:write"],
    rate_limit=100,
    expires_in_days=90
)

api_key_response = await manager.create_api_key(
    owner_id="user123",
    key_data=key_data
)

# Save the plain text key - shown only once!
print(f"API Key: {api_key_response.key}")

# Verify API key
key = await manager.verify_api_key("bmc_xxxxxxxxxxxxx")
if key:
    print(f"Valid key: {key.name}, Scopes: {key.scopes}")
```

### 3. Authentication Middleware (`src/auth/middleware.py`)

**Purpose:** Protect endpoints with authentication

**Features:**
- JWT token validation
- API key validation
- Either/or authentication (JWT or API key)
- Role-based access control (RBAC)
- Scope-based access control

**Usage:**

```python
from fastapi import Depends, Request
from src.auth import AuthMiddleware, bearer_scheme

auth = AuthMiddleware(db_connection)

# Protect with JWT
@app.get("/api/user/profile")
async def get_profile(
    request: Request,
    credentials = Depends(bearer_scheme)
):
    token_data = await auth.verify_jwt_token(request, credentials)
    return {"user": token_data.username}

# Protect with API key
@app.post("/api/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    api_key = await auth.verify_api_key(request)
    # Process webhook
    return {"status": "ok"}

# Protect with either JWT or API key
@app.post("/api/chat")
async def chat(
    request: Request,
    credentials = Depends(bearer_scheme)
):
    token_data, api_key = await auth.verify_either(request, credentials)
    # Process chat request
    return {"response": "Hello!"}
```

### 4. Password Utilities (`src/auth/password_utils.py`)

**Purpose:** Secure password hashing and validation

**Features:**
- Bcrypt password hashing (12 rounds)
- Password verification
- Password strength validation

**Usage:**

```python
from src.auth.password_utils import (
    hash_password,
    verify_password,
    validate_password_strength
)

# Hash password
hashed = hash_password("SecurePass123!")

# Verify password
if verify_password("SecurePass123!", hashed):
    print("Password correct")

# Validate strength
is_valid, message = validate_password_strength("weakpass")
if not is_valid:
    print(f"Weak password: {message}")
```

---

## Integration with Existing API

### Step 1: Initialize Authentication

```python
# In sistema_completo_integrado.py or api_server.py

from src.auth import AuthMiddleware, get_jwt_manager
from pymongo import MongoClient

# Initialize database connection
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["bmc_chatbot"]

# Initialize authentication
auth = AuthMiddleware(db)
jwt_manager = get_jwt_manager()
```

### Step 2: Add User Login Endpoint

```python
from src.auth import UserLogin, Token
from src.auth.password_utils import verify_password

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """User login endpoint"""
    
    # Find user in database
    user = await db["users"].find_one({
        "$or": [
            {"username": user_login.username},
            {"email": user_login.username}
        ]
    })
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Generate tokens
    access_token = jwt_manager.create_access_token(
        user_id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user["role"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600  # 60 minutes
    )
```

### Step 3: Protect Endpoints

```python
from fastapi import Depends

# Protect chat endpoint
@app.post("/api/chat")
async def chat(
    message: ChatMessage,
    request: Request,
    credentials = Depends(bearer_scheme)
):
    # Verify authentication
    token_data, api_key = await auth.verify_either(request, credentials)
    
    # Process chat
    response = process_chat(message.message)
    
    return {"response": response}

# Protect admin endpoints
@app.get("/api/admin/users")
async def list_users(
    request: Request,
    credentials = Depends(bearer_scheme)
):
    # Verify JWT token
    token_data = await auth.verify_jwt_token(request, credentials)
    
    # Check admin role
    if token_data.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # List users
    users = await db["users"].find().to_list(100)
    return {"users": users}
```

### Step 4: Add API Key Management Endpoints

```python
from src.auth import APIKeyCreate, APIKeyResponse

@app.post("/api/auth/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    request: Request,
    credentials = Depends(bearer_scheme)
):
    """Create new API key"""
    
    # Verify user authentication
    token_data = await auth.verify_jwt_token(request, credentials)
    
    # Create API key
    from src.auth import get_api_key_manager
    manager = get_api_key_manager(db)
    
    api_key = await manager.create_api_key(
        owner_id=token_data.user_id,
        key_data=key_data
    )
    
    return api_key

@app.get("/api/auth/api-keys")
async def list_api_keys(
    request: Request,
    credentials = Depends(bearer_scheme)
):
    """List user's API keys"""
    
    token_data = await auth.verify_jwt_token(request, credentials)
    
    from src.auth import get_api_key_manager
    manager = get_api_key_manager(db)
    
    keys = await manager.list_api_keys(token_data.user_id)
    return {"keys": keys}

@app.delete("/api/auth/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    request: Request,
    credentials = Depends(bearer_scheme)
):
    """Revoke API key"""
    
    token_data = await auth.verify_jwt_token(request, credentials)
    
    from src.auth import get_api_key_manager
    manager = get_api_key_manager(db)
    
    success = await manager.revoke_api_key(key_id, token_data.user_id)
    
    if success:
        return {"message": "API key revoked"}
    else:
        raise HTTPException(status_code=404, detail="API key not found")
```

---

## Environment Variables

Add these to your `.env` file:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Requirements
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true

# API Key Configuration
API_KEY_PREFIX=bmc
API_KEY_LENGTH=32
API_KEY_DEFAULT_RATE_LIMIT=100
```

---

## Security Best Practices

### 1. JWT Secret Key
- **Never commit the secret key** to version control
- Use a strong, random secret key (at least 32 characters)
- Rotate keys periodically (every 90 days)
- Use different keys for staging and production

### 2. Password Storage
- Always hash passwords with bcrypt (12 rounds minimum)
- Never store plain text passwords
- Implement password strength requirements
- Consider implementing password expiration

### 3. API Keys
- Generate keys using cryptographically secure random
- Hash keys before storing in database
- Implement per-key rate limiting
- Support key rotation
- Set expiration dates

### 4. Token Management
- Use HTTP-only cookies for web applications
- Implement token refresh mechanism
- Add token to revocation list on logout
- Keep token expiration short (60 minutes)

### 5. HTTPS Only
- Always use HTTPS in production
- Set `Secure` flag on cookies
- Enable HSTS headers

---

## Testing

### Unit Tests

```python
# tests/unit/test_auth.py

import pytest
from src.auth import JWTManager, APIKeyManager, UserRole
from src.auth.password_utils import hash_password, verify_password

def test_jwt_creation():
    """Test JWT token creation"""
    manager = JWTManager()
    
    token = manager.create_access_token(
        user_id="test123",
        username="testuser",
        email="test@example.com",
        role=UserRole.USER
    )
    
    assert token is not None
    assert isinstance(token, str)

def test_jwt_verification():
    """Test JWT token verification"""
    manager = JWTManager()
    
    token = manager.create_access_token(
        user_id="test123",
        username="testuser",
        email="test@example.com",
        role=UserRole.USER
    )
    
    token_data = manager.verify_token(token)
    
    assert token_data is not None
    assert token_data.username == "testuser"
    assert token_data.role == UserRole.USER

def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

@pytest.mark.asyncio
async def test_api_key_generation():
    """Test API key generation"""
    manager = APIKeyManager()
    
    key = manager.generate_api_key()
    
    assert key.startswith("bmc_")
    assert len(key) > 32
```

### Integration Tests

```python
# tests/integration/test_auth_endpoints.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login_success():
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "Test123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrong"
    })
    
    assert response.status_code == 401

def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    response = client.get("/api/user/profile")
    
    assert response.status_code == 401

def test_protected_endpoint_with_auth():
    """Test accessing protected endpoint with authentication"""
    # Login first
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "Test123!"
    })
    
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
```

---

## Migration Guide

### Migrating Existing Endpoints

1. **Identify public vs protected endpoints**
2. **Add authentication to protected endpoints**
3. **Create default admin user**
4. **Generate API keys for webhooks**
5. **Update documentation**

### Example Migration

**Before:**
```python
@app.post("/api/chat")
async def chat(message: ChatMessage):
    response = process_chat(message.message)
    return {"response": response}
```

**After:**
```python
from fastapi import Depends
from src.auth import AuthMiddleware, bearer_scheme

@app.post("/api/chat")
async def chat(
    message: ChatMessage,
    request: Request,
    credentials = Depends(bearer_scheme)
):
    # Verify authentication (JWT or API key)
    token_data, api_key = await auth.verify_either(request, credentials)
    
    # Track user/key for analytics
    user_id = token_data.user_id if token_data else api_key.owner_id
    
    # Process chat
    response = process_chat(message.message, user_id)
    
    return {"response": response}
```

---

## Troubleshooting

### Common Issues

**1. "Invalid or expired token"**
- Check JWT_SECRET_KEY is set correctly
- Verify token hasn't expired
- Ensure token format is correct

**2. "Missing API key"**
- Check X-API-Key header is set
- Verify header name (case-insensitive)
- Ensure key format: `bmc_xxxxx`

**3. "Insufficient permissions"**
- Check user role matches required role
- Verify API key has required scopes
- Review role/scope configuration

**4. Database connection errors**
- Verify MONGODB_URI is set
- Check database connectivity
- Ensure indexes are created

---

## Next Steps

1. **Create admin user** - Use script to create initial admin
2. **Generate webhook API keys** - For WhatsApp, n8n, etc.
3. **Update frontend** - Add login page and token storage
4. **Add refresh token endpoint** - For token renewal
5. **Implement token revocation** - Logout functionality
6. **Add audit logging** - Track authentication events

---

**Related Documentation:**
- [MASSIVE_INTEGRATION_PLAN.md](./MASSIVE_INTEGRATION_PLAN.md)
- [MONITORING_INTEGRATION.md](./MONITORING_INTEGRATION.md)
- [SECURITY_GUIDE.md](./SECURITY_GUIDE.md)
