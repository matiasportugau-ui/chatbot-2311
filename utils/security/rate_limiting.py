#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate limiting utilities for BMC Chatbot API
Implements sliding window rate limiting with Redis backend
"""

import os
import time
import logging
from typing import Optional, Tuple
from functools import wraps
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import hashlib

logger = logging.getLogger(__name__)

# Rate limit configuration
DEFAULT_RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
DEFAULT_RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "100"))

# In-memory storage for rate limiting (use Redis in production)
_rate_limit_storage = {}


def get_client_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses IP address or API key if available.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Unique client identifier
    """
    # Check for API key in header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # Hash API key for privacy
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    # Fallback to IP address
    client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    if "," in client_ip:
        # X-Forwarded-For can contain multiple IPs, use the first
        client_ip = client_ip.split(",")[0].strip()
    
    return client_ip


def check_rate_limit(
    client_id: str,
    limit: int = DEFAULT_RATE_LIMIT,
    window: int = 60
) -> Tuple[bool, dict]:
    """
    Check if client has exceeded rate limit using sliding window.
    
    Args:
        client_id: Unique client identifier
        limit: Maximum requests allowed per window
        window: Time window in seconds
        
    Returns:
        Tuple[bool, dict]: (is_allowed, rate_limit_info)
    """
    current_time = time.time()
    key = f"rate_limit:{client_id}"
    
    # Get or initialize request history
    if key not in _rate_limit_storage:
        _rate_limit_storage[key] = []
    
    request_history = _rate_limit_storage[key]
    
    # Remove requests outside the time window
    request_history = [
        timestamp for timestamp in request_history
        if current_time - timestamp < window
    ]
    
    # Check if limit exceeded
    is_allowed = len(request_history) < limit
    
    if is_allowed:
        request_history.append(current_time)
    
    # Update storage
    _rate_limit_storage[key] = request_history
    
    # Calculate rate limit info
    remaining = max(0, limit - len(request_history))
    reset_time = int(current_time + window) if request_history else int(current_time)
    
    rate_limit_info = {
        "limit": limit,
        "remaining": remaining,
        "reset": reset_time,
        "used": len(request_history)
    }
    
    return is_allowed, rate_limit_info


class RateLimiter:
    """
    Rate limiter middleware for FastAPI.
    """
    
    def __init__(
        self,
        requests_per_minute: int = DEFAULT_RATE_LIMIT,
        burst_size: int = DEFAULT_RATE_LIMIT_BURST
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        
    async def __call__(self, request: Request, call_next):
        """
        Middleware to check rate limits.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/route handler
            
        Returns:
            Response or rate limit error
        """
        client_id = get_client_identifier(request)
        
        # Check rate limit
        is_allowed, rate_info = check_rate_limit(
            client_id,
            limit=self.requests_per_minute,
            window=60
        )
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again after {rate_info['reset'] - int(time.time())} seconds.",
                    "rate_limit": rate_info
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["reset"] - int(time.time()))
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response


def rate_limit(
    requests_per_minute: int = DEFAULT_RATE_LIMIT,
    error_message: str = "Rate limit exceeded"
):
    """
    Decorator for rate limiting specific routes.
    
    Args:
        requests_per_minute: Maximum requests per minute
        error_message: Custom error message
        
    Usage:
        @app.post("/api/endpoint")
        @rate_limit(requests_per_minute=10)
        async def endpoint(request: Request):
            return {"message": "success"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_id = get_client_identifier(request)
            is_allowed, rate_info = check_rate_limit(
                client_id,
                limit=requests_per_minute,
                window=60
            )
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {func.__name__}: {client_id}")
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": error_message,
                        "rate_limit": rate_info
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset"]),
                        "Retry-After": str(rate_info["reset"] - int(time.time()))
                    }
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


# Redis-backed rate limiter (production)
class RedisRateLimiter:
    """
    Redis-backed rate limiter for distributed systems.
    """
    
    def __init__(self, redis_client, prefix: str = "rate_limit"):
        """
        Initialize Redis rate limiter.
        
        Args:
            redis_client: Redis client instance
            prefix: Key prefix for rate limit data
        """
        self.redis = redis_client
        self.prefix = prefix
        
    def check_rate_limit(
        self,
        client_id: str,
        limit: int,
        window: int = 60
    ) -> Tuple[bool, dict]:
        """
        Check rate limit using Redis sorted sets.
        
        Args:
            client_id: Client identifier
            limit: Request limit
            window: Time window in seconds
            
        Returns:
            Tuple[bool, dict]: (is_allowed, rate_limit_info)
        """
        key = f"{self.prefix}:{client_id}"
        current_time = time.time()
        window_start = current_time - window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        request_count = self.redis.zcard(key)
        
        # Check limit
        is_allowed = request_count < limit
        
        if is_allowed:
            # Add current request
            self.redis.zadd(key, {str(current_time): current_time})
            # Set expiry
            self.redis.expire(key, window)
        
        remaining = max(0, limit - request_count - (1 if is_allowed else 0))
        reset_time = int(current_time + window)
        
        rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "used": request_count + (1 if is_allowed else 0)
        }
        
        return is_allowed, rate_limit_info
