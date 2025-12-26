#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Rate Limiter
Multi-tier rate limiting with sliding window and token bucket algorithms
"""

import time
from typing import Dict, Optional, Tuple
from collections import deque
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens consumed successfully
        """
        # Refill tokens based on elapsed time
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now
        
        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_time(self, tokens: int = 1) -> float:
        """
        Calculate wait time until tokens available
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Wait time in seconds
        """
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class SlidingWindow:
    """Sliding window rate limiter"""
    
    def __init__(self, limit: int, window_seconds: int):
        """
        Initialize sliding window
        
        Args:
            limit: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()
    
    def is_allowed(self) -> Tuple[bool, Optional[float]]:
        """
        Check if request is allowed
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests
        while self.requests and self.requests[0] < window_start:
            self.requests.popleft()
        
        # Check limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True, None
        else:
            # Calculate retry after
            oldest_request = self.requests[0]
            retry_after = oldest_request + self.window_seconds - now
            return False, max(0, retry_after)


class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        """Initialize rate limiter"""
        # Storage for rate limit state per key
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindow] = {}
        
        # Default limits (can be overridden per endpoint)
        self.default_limits = {
            'global': {'limit': 1000, 'window': 60},  # 1000 req/min
            'per_ip': {'limit': 100, 'window': 60},   # 100 req/min per IP
            'per_user': {'limit': 50, 'window': 60},  # 50 req/min per user
        }
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            '/api/chat': {'limit': 20, 'window': 60},
            '/api/quotes': {'limit': 10, 'window': 60},
            '/api/whatsapp/webhook': {'limit': 100, 'window': 60},
        }
    
    def _get_key(self, scope: str, identifier: str) -> str:
        """Generate rate limit key"""
        return f"{scope}:{identifier}"
    
    def check_rate_limit(
        self,
        scope: str,
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> Tuple[bool, Optional[float], Dict[str, any]]:
        """
        Check rate limit using sliding window
        
        Args:
            scope: Rate limit scope (e.g., 'ip', 'user', 'endpoint')
            identifier: Unique identifier (IP, user_id, etc.)
            limit: Maximum requests
            window_seconds: Window size in seconds
            
        Returns:
            Tuple of (is_allowed, retry_after, headers)
        """
        key = self._get_key(scope, identifier)
        
        # Get or create sliding window
        if key not in self.sliding_windows:
            self.sliding_windows[key] = SlidingWindow(limit, window_seconds)
        
        window = self.sliding_windows[key]
        is_allowed, retry_after = window.is_allowed()
        
        # Calculate remaining requests
        remaining = max(0, limit - len(window.requests))
        
        # Prepare headers
        headers = {
            'X-RateLimit-Limit': str(limit),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(int(time.time() + window_seconds))
        }
        
        if not is_allowed and retry_after:
            headers['Retry-After'] = str(int(retry_after) + 1)
        
        return is_allowed, retry_after, headers
    
    def check_token_bucket(
        self,
        scope: str,
        identifier: str,
        capacity: int,
        refill_rate: float,
        tokens: int = 1
    ) -> Tuple[bool, float]:
        """
        Check rate limit using token bucket
        
        Args:
            scope: Rate limit scope
            identifier: Unique identifier
            capacity: Bucket capacity
            refill_rate: Tokens per second
            tokens: Tokens to consume
            
        Returns:
            Tuple of (is_allowed, wait_time)
        """
        key = self._get_key(scope, identifier)
        
        # Get or create token bucket
        if key not in self.token_buckets:
            self.token_buckets[key] = TokenBucket(capacity, refill_rate)
        
        bucket = self.token_buckets[key]
        is_allowed = bucket.consume(tokens)
        wait_time = bucket.wait_time(tokens) if not is_allowed else 0
        
        return is_allowed, wait_time
    
    async def check_request(
        self,
        request: Request,
        endpoint: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Check rate limits for incoming request
        
        Args:
            request: FastAPI request object
            endpoint: Endpoint path (optional, extracted from request if not provided)
            
        Returns:
            Rate limit headers
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        endpoint = endpoint or request.url.path
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user ID from request state (if authenticated)
        user_id = getattr(request.state, "user", {}).get("user_id") if hasattr(request.state, "user") else None
        
        # Get endpoint-specific limits or use defaults
        endpoint_config = self.endpoint_limits.get(endpoint, self.default_limits['per_ip'])
        
        # Check global rate limit
        global_allowed, global_retry, global_headers = self.check_rate_limit(
            'global',
            'all',
            self.default_limits['global']['limit'],
            self.default_limits['global']['window']
        )
        
        if not global_allowed:
            logger.warning(f"Global rate limit exceeded")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Global rate limit exceeded",
                headers=global_headers
            )
        
        # Check per-IP rate limit
        ip_allowed, ip_retry, ip_headers = self.check_rate_limit(
            'ip',
            client_ip,
            self.default_limits['per_ip']['limit'],
            self.default_limits['per_ip']['window']
        )
        
        if not ip_allowed:
            logger.warning(f"IP rate limit exceeded: {client_ip}")
            # Track rate limit hit in metrics
            from src.monitoring import get_metrics_collector
            collector = get_metrics_collector()
            collector.track_rate_limit_hit(endpoint, "ip")
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded for your IP address",
                headers=ip_headers
            )
        
        # Check per-user rate limit (if authenticated)
        if user_id:
            user_allowed, user_retry, user_headers = self.check_rate_limit(
                'user',
                user_id,
                self.default_limits['per_user']['limit'],
                self.default_limits['per_user']['window']
            )
            
            if not user_allowed:
                logger.warning(f"User rate limit exceeded: {user_id}")
                from src.monitoring import get_metrics_collector
                collector = get_metrics_collector()
                collector.track_rate_limit_hit(endpoint, "user")
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for your account",
                    headers=user_headers
                )
            
            return user_headers
        
        return ip_headers


# Singleton instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get singleton rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Decorator for rate limiting
def rate_limit(
    limit: int = 60,
    window: int = 60,
    scope: str = "endpoint"
):
    """
    Rate limit decorator
    
    Args:
        limit: Maximum requests
        window: Window size in seconds
        scope: Rate limit scope
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            if not request:
                return await func(*args, request=request, **kwargs)
            
            limiter = get_rate_limiter()
            
            # Override endpoint limits temporarily
            endpoint = request.url.path
            limiter.endpoint_limits[endpoint] = {'limit': limit, 'window': window}
            
            # Check rate limit
            await limiter.check_request(request, endpoint)
            
            # Call original function
            return await func(*args, request=request, **kwargs)
        
        return wrapper
    return decorator
