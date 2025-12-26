#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Middleware
FastAPI middleware for JWT and API Key authentication
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
import logging
from .jwt_manager import get_jwt_manager
from .api_key_manager import get_api_key_manager
from .models import TokenData, APIKey

logger = logging.getLogger(__name__)

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self, db_connection=None):
        """
        Initialize authentication middleware
        
        Args:
            db_connection: Database connection for API key validation
        """
        self.jwt_manager = get_jwt_manager()
        self.api_key_manager = get_api_key_manager(db_connection)
    
    async def verify_jwt_token(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> TokenData:
        """
        Verify JWT token from Authorization header
        
        Args:
            request: FastAPI request object
            credentials: HTTPBearer credentials
            
        Returns:
            TokenData if valid
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        token_data = self.jwt_manager.verify_token(token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Store token data in request state
        request.state.user = token_data
        
        return token_data
    
    async def verify_api_key(self, request: Request) -> APIKey:
        """
        Verify API key from X-API-Key header
        
        Args:
            request: FastAPI request object
            
        Returns:
            APIKey if valid
            
        Raises:
            HTTPException: If API key is invalid or missing
        """
        api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key",
                headers={"WWW-Authenticate": 'ApiKey realm="API Key required"'},
            )
        
        key_data = await self.api_key_manager.verify_api_key(api_key)
        
        if not key_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
                headers={"WWW-Authenticate": 'ApiKey realm="Invalid API key"'},
            )
        
        # Store API key data in request state
        request.state.api_key = key_data
        
        return key_data
    
    async def verify_either(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> tuple[Optional[TokenData], Optional[APIKey]]:
        """
        Verify either JWT token or API key
        
        Args:
            request: FastAPI request object
            credentials: HTTPBearer credentials (optional)
            
        Returns:
            Tuple of (TokenData, APIKey) - one will be None
            
        Raises:
            HTTPException: If both authentication methods fail
        """
        # Try JWT first
        if credentials:
            try:
                token_data = await self.verify_jwt_token(request, credentials)
                return token_data, None
            except HTTPException:
                pass  # Try API key
        
        # Try API key
        try:
            api_key = await self.verify_api_key(request)
            return None, api_key
        except HTTPException:
            pass  # Both failed
        
        # Both authentication methods failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide either JWT token or API key.",
            headers={"WWW-Authenticate": 'Bearer, ApiKey'},
        )
    
    def require_role(self, *allowed_roles: str) -> Callable:
        """
        Decorator to require specific user roles
        
        Args:
            *allowed_roles: Allowed role names
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, request: Request = None, **kwargs):
                if not request:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Request object not available"
                    )
                
                # Get user from request state
                user = getattr(request.state, "user", None)
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Check role
                if user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
                    )
                
                return await func(*args, request=request, **kwargs)
            
            return wrapper
        return decorator
    
    def require_scope(self, *required_scopes: str) -> Callable:
        """
        Decorator to require specific API key scopes
        
        Args:
            *required_scopes: Required scope names
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, request: Request = None, **kwargs):
                if not request:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Request object not available"
                    )
                
                # Get API key from request state
                api_key = getattr(request.state, "api_key", None)
                
                if not api_key:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key required"
                    )
                
                # Check scopes
                missing_scopes = set(required_scopes) - set(api_key.scopes)
                if missing_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required scopes: {', '.join(missing_scopes)}"
                    )
                
                return await func(*args, request=request, **kwargs)
            
            return wrapper
        return decorator


# Singleton instance
_auth_middleware = None


def get_auth_middleware(db_connection=None) -> AuthMiddleware:
    """Get singleton auth middleware instance"""
    global _auth_middleware
    if _auth_middleware is None:
        _auth_middleware = AuthMiddleware(db_connection)
    return _auth_middleware
