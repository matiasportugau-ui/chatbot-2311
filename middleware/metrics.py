#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics Middleware for FastAPI
Implements the Four Golden Signals from Google SRE practices

Based on Google Cloud Architecture Framework operational excellence recommendations
"""

import time
from typing import Callable, Dict, Any
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects application metrics based on the Four Golden Signals:
    - Latency: Time to serve requests
    - Traffic: Request volume
    - Errors: Error rate
    - Saturation: Resource utilization
    """
    
    def __init__(self):
        self.request_count: Dict[str, Dict[str, int]] = {}
        self.error_count: Dict[str, int] = {}
        self.latency_sum: Dict[str, float] = {}
        self.latency_count: Dict[str, int] = {}
        self.latency_buckets: Dict[str, Dict[str, int]] = {}
        self.active_requests = 0
        self.start_time = datetime.utcnow()
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        status: int,
        latency: float
    ):
        """Record metrics for a completed request"""
        key = f"{method}:{endpoint}"
        
        # Request count by status
        if key not in self.request_count:
            self.request_count[key] = {}
        status_key = str(status)
        self.request_count[key][status_key] = self.request_count[key].get(status_key, 0) + 1
        
        # Latency tracking
        if key not in self.latency_sum:
            self.latency_sum[key] = 0.0
            self.latency_count[key] = 0
            self.latency_buckets[key] = {
                "0-50ms": 0,
                "50-100ms": 0,
                "100-250ms": 0,
                "250-500ms": 0,
                "500-1000ms": 0,
                "1000ms+": 0
            }
        
        self.latency_sum[key] += latency
        self.latency_count[key] += 1
        
        # Bucket the latency
        if latency < 50:
            self.latency_buckets[key]["0-50ms"] += 1
        elif latency < 100:
            self.latency_buckets[key]["50-100ms"] += 1
        elif latency < 250:
            self.latency_buckets[key]["100-250ms"] += 1
        elif latency < 500:
            self.latency_buckets[key]["250-500ms"] += 1
        elif latency < 1000:
            self.latency_buckets[key]["500-1000ms"] += 1
        else:
            self.latency_buckets[key]["1000ms+"] += 1
        
        # Error count
        if status >= 400:
            self.error_count[key] = self.error_count.get(key, 0) + 1
    
    def get_metrics(self) -> dict:
        """Get all collected metrics"""
        total_requests = sum(
            sum(statuses.values())
            for statuses in self.request_count.values()
        )
        total_errors = sum(self.error_count.values())
        
        latency_avg = {}
        for key in self.latency_count:
            if self.latency_count[key] > 0:
                latency_avg[key] = round(
                    self.latency_sum[key] / self.latency_count[key], 2
                )
        
        return {
            "summary": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": round(total_errors / max(total_requests, 1) * 100, 2),
                "active_requests": self.active_requests,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            },
            "endpoints": {
                "requests_by_status": self.request_count,
                "errors": self.error_count,
                "latency_avg_ms": latency_avg,
                "latency_distribution": self.latency_buckets
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def reset(self):
        """Reset all metrics (useful for testing)"""
        self.request_count = {}
        self.error_count = {}
        self.latency_sum = {}
        self.latency_count = {}
        self.latency_buckets = {}


# Global metrics collector instance
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect metrics for all requests
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        metrics_collector.active_requests += 1
        
        try:
            response = await call_next(request)
            
            # Calculate latency in milliseconds
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Record metrics
            metrics_collector.record_request(
                endpoint=request.url.path,
                method=request.method,
                status=response.status_code,
                latency=latency_ms
            )
            
            # Add timing headers
            response.headers["X-Response-Time"] = f"{latency_ms:.2f}ms"
            
            # Structured logging
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"status={response.status_code} latency={latency_ms:.2f}ms"
            )
            
            return response
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            metrics_collector.record_request(
                endpoint=request.url.path,
                method=request.method,
                status=500,
                latency=latency_ms
            )
            
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"error={type(e).__name__}: {str(e)}"
            )
            raise
            
        finally:
            metrics_collector.active_requests -= 1


def setup_metrics(app: FastAPI):
    """
    Configure metrics collection on the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(MetricsMiddleware)
    
    @app.get("/metrics", tags=["Monitoring"])
    async def get_metrics():
        """
        Get application metrics
        
        Returns metrics based on the Four Golden Signals:
        - Latency
        - Traffic
        - Errors
        - Saturation
        """
        return metrics_collector.get_metrics()
    
    @app.get("/metrics/health", tags=["Monitoring"])
    async def metrics_health():
        """Quick health check based on metrics"""
        metrics = metrics_collector.get_metrics()
        summary = metrics["summary"]
        
        status = "healthy"
        issues = []
        
        if summary["error_rate"] > 5:
            status = "degraded"
            issues.append(f"High error rate: {summary['error_rate']}%")
        
        if summary["active_requests"] > 100:
            status = "degraded"
            issues.append(f"High active requests: {summary['active_requests']}")
        
        return {
            "status": status,
            "error_rate": summary["error_rate"],
            "active_requests": summary["active_requests"],
            "issues": issues
        }
    
    logger.info("✅ Metrics collection configurado correctamente")
