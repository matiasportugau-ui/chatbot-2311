"""
Unit tests for rate limiting
"""

import time
from collections import defaultdict

import pytest


class SimpleRateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        self.requests[key] = [
            req_time for req_time in self.requests[key] if now - req_time < window_seconds
        ]
        if len(self.requests[key]) >= max_requests:
            return False
        self.requests[key].append(now)
        return True


class TestRateLimiting:
    @pytest.fixture
    def limiter(self):
        return SimpleRateLimiter()

    def test_rate_limit_allows_requests(self, limiter):
        for i in range(5):
            assert limiter.is_allowed("test_key", 5, 60)

    def test_rate_limit_blocks_excess(self, limiter):
        for i in range(3):
            assert limiter.is_allowed("test_key", 3, 60)
        assert not limiter.is_allowed("test_key", 3, 60)
