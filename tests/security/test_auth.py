#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for authentication functionality
"""

import pytest
import os
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from utils.security.auth import (
    create_access_token,
    verify_jwt_token,
    hash_api_key,
    verify_api_key_hash,
    SECRET_KEY,
    ALGORITHM,
)


class TestJWTAuthentication:
    """Test JWT token creation and validation"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "user123", "scopes": ["read", "write"]}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode to verify contents
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user123"
        assert payload["scopes"] == ["read", "write"]
        assert "exp" in payload
    
    def test_create_token_with_custom_expiry(self):
        """Test token creation with custom expiration"""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Should expire in approximately 30 minutes
        time_diff = exp_time - now
        assert 29 <= time_diff.total_seconds() / 60 <= 31
    
    def test_verify_valid_token(self):
        """Test verification of valid JWT token"""
        data = {"sub": "user123", "scopes": ["read"]}
        token = create_access_token(data)
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        token_data = verify_jwt_token(credentials)
        assert token_data.username == "user123"
        assert token_data.scopes == ["read"]
    
    def test_verify_invalid_token(self):
        """Test verification of invalid JWT token"""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_expired_token(self):
        """Test verification of expired JWT token"""
        data = {"sub": "user123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(credentials)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_token_missing_sub(self):
        """Test verification of token without subject"""
        # Manually create token without 'sub' claim
        data = {"other": "data"}
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=encoded_jwt
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(credentials)
        
        assert exc_info.value.status_code == 401


class TestAPIKeyAuthentication:
    """Test API key hashing and validation"""
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        api_key = "my_secret_key_123"
        hashed = hash_api_key(api_key)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 produces 64 character hex string
        assert hashed != api_key  # Hash should be different from original
    
    def test_hash_consistency(self):
        """Test that same key produces same hash"""
        api_key = "my_secret_key_123"
        hash1 = hash_api_key(api_key)
        hash2 = hash_api_key(api_key)
        
        assert hash1 == hash2
    
    def test_verify_api_key_hash_valid(self):
        """Test verification of valid API key"""
        api_key = "my_secret_key_123"
        hashed = hash_api_key(api_key)
        
        assert verify_api_key_hash(api_key, hashed) is True
    
    def test_verify_api_key_hash_invalid(self):
        """Test verification of invalid API key"""
        api_key = "my_secret_key_123"
        wrong_key = "wrong_key_456"
        hashed = hash_api_key(api_key)
        
        assert verify_api_key_hash(wrong_key, hashed) is False
    
    def test_different_keys_different_hashes(self):
        """Test that different keys produce different hashes"""
        key1 = "key_1"
        key2 = "key_2"
        
        hash1 = hash_api_key(key1)
        hash2 = hash_api_key(key2)
        
        assert hash1 != hash2
