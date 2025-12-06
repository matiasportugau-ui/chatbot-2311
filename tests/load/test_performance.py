"""
Performance tests
"""

import os
import statistics

import psutil
import pytest


class TestPerformance:
    @pytest.mark.slow
    def test_response_time_percentiles(self):
        response_times = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        p50 = statistics.median(response_times)
        p95 = (
            statistics.quantiles(response_times, n=20)[18]
            if len(response_times) > 1
            else response_times[-1]
        )
        assert p95 < 0.5, f"p95 response time should be < 500ms, got {p95:.3f}s"

    @pytest.mark.slow
    def test_memory_usage(self):
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        data = [{"id": i, "data": "x" * 100} for i in range(1000)]
        peak_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        assert memory_increase < 1000, f"Memory increase too high: {memory_increase:.2f} MB"
