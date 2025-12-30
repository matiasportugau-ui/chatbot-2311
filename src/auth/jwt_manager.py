#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Manager
Handles JWT token creation, validation, and refresh
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .models import TokenData, UserRole
import logging

logger = logging.getLogger(__name__)


class JWTManager:
    """JWT token manager"""
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7
    ):
        """
        Initialize JWT manager
        
        Args:
            secret_key: Secret key for JWT encoding (defaults to env var)
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION")
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        
        # Warn if using default secret key
        if self.secret_key == "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION":
            logger.warning(
                "⚠️  Using default JWT secret key! "
                "Set JWT_SECRET_KEY environment variable in production!"
            )
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID
            username: Username
            email: User email
            role: User role
            expires_delta: Custom expiration delta (optional)
            
        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": user_id,
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role.value if isinstance(role, UserRole) else role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(f"Created access token for user: {username}")
        return encoded_jwt
    
    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token
        
        Args:
            user_id: User ID
            expires_delta: Custom expiration delta (optional)
            
        Returns:
            JWT refresh token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": user_id,
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.debug(f"Created refresh token for user_id: {user_id}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """
        Verify JWT token and extract payload
        
        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
                return None
            
            # Extract token data
            if token_type == "access":
                token_data = TokenData(
                    user_id=payload.get("user_id"),
                    username=payload.get("username"),
                    email=payload.get("email"),
                    role=UserRole(payload.get("role")),
                    exp=payload.get("exp"),
                    iat=payload.get("iat")
                )
                return token_data
            else:
                # For refresh tokens, return minimal data
                return {
                    "user_id": payload.get("user_id"),
                    "exp": payload.get("exp"),
                    "iat": payload.get("iat")
                }
        
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def decode_token_no_verify(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging only)
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None
        """
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None


# Singleton instance
_jwt_manager = None


def get_jwt_manager() -> JWTManager:
    """Get singleton JWT manager instance"""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager()
    return _jwt_manager


# Convenience functions
def create_access_token(user_id: str, username: str, email: str, role: UserRole) -> str:
    """Create access token (convenience function)"""
    manager = get_jwt_manager()
    return manager.create_access_token(user_id, username, email, role)


def verify_token(token: str) -> Optional[TokenData]:
    """Verify token (convenience function)"""
    manager = get_jwt_manager()
    return manager.verify_token(token)
