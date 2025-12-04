#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for rate limiting functionality
"""

import pytest
import time
from unittest.mock import Mock, MagicMock
from fastapi import Request
from utils.security.rate_limiting import (
    get_client_identifier,
    check_rate_limit,
    RateLimiter,
    _rate_limit_storage,
)


class TestClientIdentifier:
    """Test client identifier extraction"""
    
    def test_identifier_from_api_key(self):
        """Test identifier extraction from API key"""
        request = Mock(spec=Request)
        request.headers = {"X-API-Key": "test_key_123"}
        request.client = None
        
        identifier = get_client_identifier(request)
        assert isinstance(identifier, str)
        assert len(identifier) == 16  # Truncated SHA-256
    
    def test_identifier_from_ip(self):
        """Test identifier extraction from IP"""
        request = Mock(spec=Request)
        request.headers = {}
        mock_client = Mock()
        mock_client.host = "192.168.1.1"
        request.client = mock_client
        
        identifier = get_client_identifier(request)
        assert identifier == "192.168.1.1"
    
    def test_identifier_from_forwarded_header(self):
        """Test identifier from X-Forwarded-For"""
        request = Mock(spec=Request)
        request.headers = {"X-Forwarded-For": "10.0.0.1, 192.168.1.1"}
        request.client = None
        
        identifier = get_client_identifier(request)
        assert identifier == "10.0.0.1"
    
    def test_identifier_fallback(self):
        """Test identifier fallback when no client info"""
        request = Mock(spec=Request)
        request.headers = {}
        request.client = None
        
        identifier = get_client_identifier(request)
        assert identifier == "unknown"


class TestRateLimitChecking:
    """Test rate limit checking logic"""
    
    def setup_method(self):
        """Clear rate limit storage before each test"""
        _rate_limit_storage.clear()
    
    def test_first_request_allowed(self):
        """Test that first request is allowed"""
        is_allowed, info = check_rate_limit("client1", limit=5, window=60)
        
        assert is_allowed is True
        assert info["limit"] == 5
        assert info["remaining"] == 4
        assert info["used"] == 1
    
    def test_within_limit(self):
        """Test requests within limit are allowed"""
        client_id = "client2"
        
        for i in range(5):
            is_allowed, info = check_rate_limit(client_id, limit=5, window=60)
            assert is_allowed is True
            assert info["remaining"] == 5 - i - 1
    
    def test_exceeds_limit(self):
        """Test request exceeding limit is blocked"""
        client_id = "client3"
        limit = 3
        
        # Make 3 requests (at limit)
        for _ in range(limit):
            is_allowed, _ = check_rate_limit(client_id, limit=limit, window=60)
            assert is_allowed is True
        
        # 4th request should be blocked
        is_allowed, info = check_rate_limit(client_id, limit=limit, window=60)
        assert is_allowed is False
        assert info["remaining"] == 0
        assert info["used"] == 3
    
    def test_window_expiration(self):
        """Test that old requests are removed after window expires"""
        client_id = "client4"
        limit = 2
        window = 1  # 1 second window
        
        # Make 2 requests
        check_rate_limit(client_id, limit=limit, window=window)
        check_rate_limit(client_id, limit=limit, window=window)
        
        # Should be at limit
        is_allowed, _ = check_rate_limit(client_id, limit=limit, window=window)
        assert is_allowed is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        is_allowed, info = check_rate_limit(client_id, limit=limit, window=window)
        assert is_allowed is True
        assert info["remaining"] == 1
    
    def test_different_clients_independent(self):
        """Test that different clients have independent limits"""
        limit = 2
        
        # Client 1 makes 2 requests
        check_rate_limit("client_a", limit=limit, window=60)
        check_rate_limit("client_a", limit=limit, window=60)
        
        # Client 1 should be blocked
        is_allowed, _ = check_rate_limit("client_a", limit=limit, window=60)
        assert is_allowed is False
        
        # Client 2 should still be allowed
        is_allowed, _ = check_rate_limit("client_b", limit=limit, window=60)
        assert is_allowed is True
    
    def test_rate_limit_info_accuracy(self):
        """Test rate limit info is accurate"""
        client_id = "client5"
        limit = 10
        
        # Make 3 requests
        for i in range(3):
            is_allowed, info = check_rate_limit(client_id, limit=limit, window=60)
            assert info["limit"] == limit
            assert info["used"] == i + 1
            assert info["remaining"] == limit - i - 1
            assert info["reset"] > time.time()


class TestRateLimiterMiddleware:
    """Test RateLimiter middleware"""
    
    def setup_method(self):
        """Clear rate limit storage before each test"""
        _rate_limit_storage.clear()
    
    @pytest.mark.asyncio
    async def test_middleware_allows_within_limit(self):
        """Test middleware allows requests within limit"""
        rate_limiter = RateLimiter(requests_per_minute=10)
        
        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        mock_client = Mock()
        mock_client.host = "127.0.0.1"
        request.client = mock_client
        
        # Mock response
        async def call_next(req):
            response = Mock()
            response.headers = {}
            return response
        
        response = await rate_limiter(request, call_next)
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
    
    @pytest.mark.asyncio
    async def test_middleware_blocks_over_limit(self):
        """Test middleware blocks requests over limit"""
        rate_limiter = RateLimiter(requests_per_minute=2)
        
        # Mock request
        request = Mock(spec=Request)
        request.headers = {}
        mock_client = Mock()
        mock_client.host = "127.0.0.1"
        request.client = mock_client
        
        # Mock response
        async def call_next(req):
            response = Mock()
            response.headers = {}
            return response
        
        # First 2 requests should succeed
        await rate_limiter(request, call_next)
        await rate_limiter(request, call_next)
        
        # 3rd request should be blocked
        response = await rate_limiter(request, call_next)
        assert response.status_code == 429
