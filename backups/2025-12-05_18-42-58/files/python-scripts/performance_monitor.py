#!/usr/bin/env python3
"""
Performance Monitor with Prometheus Metrics
Tracks response times, error rates, cache hit rates, and other KPIs
"""

import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Prometheus client
try:
    from prometheus_client import Counter, Gauge, Histogram

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available. Metrics will be collected in-memory only.")


class PerformanceMonitor:
    """Performance monitoring with Prometheus metrics support"""

    def __init__(self):
        self.start_time = datetime.now()
        self.response_times = defaultdict(lambda: deque(maxlen=1000))
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.cache_hits = defaultdict(int)
        self.cache_misses = defaultdict(int)
        self.intent_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})

        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
        else:
            self._init_fallback_metrics()

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.response_time_histogram = Histogram(
            "chat_response_time_seconds", "Chat response time in seconds", ["endpoint", "method"]
        )
        self.request_counter = Counter(
            "chat_requests_total", "Total number of chat requests", ["endpoint", "method", "status"]
        )
        self.error_counter = Counter(
            "chat_errors_total", "Total number of errors", ["endpoint", "error_type"]
        )
        self.cache_hit_counter = Counter("cache_hits_total", "Total cache hits", ["cache_type"])
        self.cache_miss_counter = Counter(
            "cache_misses_total", "Total cache misses", ["cache_type"]
        )
        logger.info("Prometheus metrics initialized")

    def _init_fallback_metrics(self):
        """Initialize fallback metrics (in-memory only)"""
        self.response_time_histogram = None
        self.request_counter = None
        self.error_counter = None
        self.cache_hit_counter = None
        self.cache_miss_counter = None
        logger.info("Using in-memory metrics (Prometheus not available)")

    def record_response_time(self, endpoint: str, method: str, duration: float):
        """Record response time for an endpoint"""
        self.response_times[f"{method}:{endpoint}"].append(duration)
        if self.response_time_histogram:
            self.response_time_histogram.labels(endpoint=endpoint, method=method).observe(duration)

    def record_request(self, endpoint: str, method: str, status: int):
        """Record a request"""
        self.request_counts[f"{method}:{endpoint}"] += 1
        if self.request_counter:
            self.request_counter.labels(endpoint=endpoint, method=method, status=str(status)).inc()

    def record_error(self, endpoint: str, method: str, error_type: str):
        """Record an error"""
        self.error_counts[f"{method}:{endpoint}:{error_type}"] += 1
        if self.error_counter:
            self.error_counter.labels(endpoint=endpoint, error_type=error_type).inc()

    def record_cache_hit(self, cache_type: str):
        """Record a cache hit"""
        self.cache_hits[cache_type] += 1
        if self.cache_hit_counter:
            self.cache_hit_counter.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record a cache miss"""
        self.cache_misses[cache_type] += 1
        if self.cache_miss_counter:
            self.cache_miss_counter.labels(cache_type=cache_type).inc()

    def get_cache_hit_rate(self, cache_type: str) -> float:
        """Get cache hit rate for a cache type"""
        hits = self.cache_hits.get(cache_type, 0)
        misses = self.cache_misses.get(cache_type, 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "cache_stats": {
                ct: {
                    "hits": self.cache_hits.get(ct, 0),
                    "misses": self.cache_misses.get(ct, 0),
                    "hit_rate": self.get_cache_hit_rate(ct),
                }
                for ct in set(list(self.cache_hits.keys()) + list(self.cache_misses.keys()))
            },
        }


_performance_monitor: PerformanceMonitor | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create the performance monitor singleton"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
