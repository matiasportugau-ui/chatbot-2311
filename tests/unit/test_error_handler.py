"""
Unit tests for error handling
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python-scripts"))
from error_handler import get_error_handler, safe_execute


class TestErrorHandler:
    @pytest.fixture
    def handler(self):
        return get_error_handler()

    def test_error_logging(self, handler):
        try:
            raise ValueError("Test error")
        except Exception as e:
            handler.log_error(e)
        stats = handler.get_stats()
        assert stats["total_errors"] > 0

    def test_safe_execute_success(self, handler):
        def success_func():
            return "success"

        result = safe_execute(success_func, fallback="fallback")
        assert result == "success"

    def test_safe_execute_failure(self, handler):
        def fail_func():
            raise ValueError("Test error")

        result = safe_execute(fail_func, fallback="fallback")
        assert result == "fallback"
