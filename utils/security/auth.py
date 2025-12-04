#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication utilities for BMC Chatbot API
Implements JWT token authentication and API key validation
"""

import os
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Security schemes
security_bearer = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []


class TokenData(BaseModel):
    """JWT token data model"""
    username: Optional[str] = None
    scopes: list[str] = []
    exp: Optional[datetime] = None


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token({"sub": "user123", "scopes": ["read", "write"]})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer)
) -> TokenData:
    """
    Verify and decode JWT token from Authorization header.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        TokenData: Decoded token data
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scopes: list = payload.get("scopes", [])
        
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(
            username=username,
            scopes=scopes,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
        
        return token_data
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Verify API key from X-API-Key header.
    
    Args:
        api_key: API key from header
        
    Returns:
        str: Valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Validate API key using constant-time comparison
    is_valid = any(hmac.compare_digest(api_key, valid_key) for valid_key in API_KEYS)
    
    if not is_valid:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        str: SHA-256 hash of the API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key_hash(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        api_key: Plain text API key to verify
        hashed_key: Stored hash to compare against
        
    Returns:
        bool: True if API key matches hash
    """
    computed_hash = hash_api_key(api_key)
    return hmac.compare_digest(computed_hash, hashed_key)


# Dependency for protecting routes
async def require_auth(
    token_data: TokenData = Depends(verify_jwt_token)
) -> TokenData:
    """
    Dependency to require JWT authentication on routes.
    
    Usage:
        @app.get("/protected", dependencies=[Depends(require_auth)])
        async def protected_route():
            return {"message": "Access granted"}
    """
    return token_data


async def require_api_key(
    api_key: str = Depends(verify_api_key)
) -> str:
    """
    Dependency to require API key authentication on routes.
    
    Usage:
        @app.post("/webhook", dependencies=[Depends(require_api_key)])
        async def webhook_endpoint():
            return {"status": "ok"}
    """
    return api_key
