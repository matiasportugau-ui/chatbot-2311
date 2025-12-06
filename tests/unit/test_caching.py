"""
Unit tests for caching functionality
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python-scripts"))
from cache_manager import get_cache_manager


class TestCacheManager:
    @pytest.fixture
    def cache(self):
        return get_cache_manager()

    def test_cache_set_get(self, cache):
        cache.set("test_key", {"data": "test_value"})
        retrieved = cache.get("test_key")
        assert retrieved == {"data": "test_value"}

    def test_cache_miss(self, cache):
        assert cache.get("non_existent_key") is None

    def test_cache_ttl(self, cache):
        cache.set("ttl_key", "value", ttl=1)
        assert cache.get("ttl_key") == "value"
        time.sleep(1.1)
        assert cache.get("ttl_key") is None
