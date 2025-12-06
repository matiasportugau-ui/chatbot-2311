#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics collection for BMC Chat API
Exposes Prometheus-compatible metrics endpoint
"""

import time
from typing import Dict, Any
from collections import defaultdict
from datetime import datetime
import threading

# Thread-safe metrics storage
_metrics_lock = threading.Lock()
_request_counters = defaultdict(int)
_response_times = defaultdict(list)
_error_counters = defaultdict(int)


def increment_request_counter(endpoint: str, method: str = "GET"):
    """Increment request counter for an endpoint"""
    with _metrics_lock:
        key = f"{method} {endpoint}"
        _request_counters[key] += 1


def record_response_time(endpoint: str, method: str, duration: float):
    """Record response time for an endpoint"""
    with _metrics_lock:
        key = f"{method} {endpoint}"
        _response_times[key].append(duration)
        # Keep only last 1000 measurements per endpoint
        if len(_response_times[key]) > 1000:
            _response_times[key] = _response_times[key][-1000:]


def increment_error_counter(endpoint: str, method: str, status_code: int):
    """Increment error counter for an endpoint"""
    with _metrics_lock:
        key = f"{method} {endpoint}"
        error_key = f"{key} {status_code}"
        _error_counters[error_key] += 1


def get_metrics() -> Dict[str, Any]:
    """Get all metrics in Prometheus-compatible format"""
    with _metrics_lock:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "counters": dict(_request_counters),
            "errors": dict(_error_counters),
            "response_times": {}
        }
        
        # Calculate statistics for response times
        for key, times in _response_times.items():
            if times:
                metrics["response_times"][key] = {
                    "count": len(times),
                    "min": min(times),
                    "max": max(times),
                    "avg": sum(times) / len(times),
                    "p50": sorted(times)[len(times) // 2] if times else 0,
                    "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 0 else 0,
                    "p99": sorted(times)[int(len(times) * 0.99)] if len(times) > 0 else 0,
                }
        
        return metrics


def get_prometheus_metrics() -> str:
    """Get metrics in Prometheus text format"""
    metrics = get_metrics()
    lines = []
    
    # Request counters
    for key, count in metrics["counters"].items():
        # Convert to Prometheus format
        metric_name = key.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        lines.append(f"# TYPE http_requests_total counter")
        lines.append(f'http_requests_total{{endpoint="{key}"}} {count}')
    
    # Error counters
    for key, count in metrics["errors"].items():
        metric_name = key.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        lines.append(f"# TYPE http_errors_total counter")
        lines.append(f'http_errors_total{{endpoint="{key}"}} {count}')
    
    # Response times
    for key, stats in metrics["response_times"].items():
        metric_name = key.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        lines.append(f"# TYPE http_request_duration_seconds histogram")
        lines.append(f'http_request_duration_seconds{{endpoint="{key}",quantile="0.5"}} {stats["p50"]}')
        lines.append(f'http_request_duration_seconds{{endpoint="{key}",quantile="0.95"}} {stats["p95"]}')
        lines.append(f'http_request_duration_seconds{{endpoint="{key}",quantile="0.99"}} {stats["p99"]}')
        lines.append(f'http_request_duration_seconds{{endpoint="{key}",quantile="avg"}} {stats["avg"]}')
    
    return "\n".join(lines)

