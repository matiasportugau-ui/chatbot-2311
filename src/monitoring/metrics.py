#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prometheus Metrics Collector
Comprehensive metrics for monitoring and observability
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from prometheus_client.multiprocess import MultiProcessCollector
from functools import wraps
import time
import os
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Centralized metrics collection for BMC Chatbot"""
    
    def __init__(self):
        """Initialize Prometheus metrics"""
        
        # ============================================================================
        # REQUEST METRICS
        # ============================================================================
        
        self.requests_total = Counter(
            'chatbot_requests_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'chatbot_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.requests_in_progress = Gauge(
            'chatbot_requests_in_progress',
            'Number of requests currently being processed',
            ['endpoint']
        )
        
        # ============================================================================
        # AI/ML METRICS
        # ============================================================================
        
        self.ai_requests_total = Counter(
            'chatbot_ai_requests_total',
            'Total number of AI model requests',
            ['model', 'status']
        )
        
        self.ai_tokens_used = Counter(
            'chatbot_ai_tokens_used_total',
            'Total tokens consumed',
            ['model', 'type']  # type: prompt, completion, total
        )
        
        self.ai_cost_usd = Counter(
            'chatbot_ai_cost_usd_total',
            'Total AI cost in USD',
            ['model']
        )
        
        self.ai_response_time = Histogram(
            'chatbot_ai_response_time_seconds',
            'AI model response time in seconds',
            ['model'],
            buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
        )
        
        # ============================================================================
        # BUSINESS METRICS
        # ============================================================================
        
        self.quotes_created = Counter(
            'chatbot_quotes_created_total',
            'Total number of quotes created',
            ['product_type', 'status']
        )
        
        self.conversations_started = Counter(
            'chatbot_conversations_started_total',
            'Total number of conversations started',
            ['channel']  # whatsapp, web, api
        )
        
        self.conversations_active = Gauge(
            'chatbot_conversations_active',
            'Number of currently active conversations'
        )
        
        self.conversion_rate = Gauge(
            'chatbot_conversion_rate',
            'Conversation to quote conversion rate',
            ['product_type']
        )
        
        self.user_satisfaction = Histogram(
            'chatbot_user_satisfaction',
            'User satisfaction score',
            buckets=[1, 2, 3, 4, 5]
        )
        
        # ============================================================================
        # DATABASE METRICS
        # ============================================================================
        
        self.db_queries_total = Counter(
            'chatbot_db_queries_total',
            'Total number of database queries',
            ['operation', 'collection', 'status']
        )
        
        self.db_query_duration = Histogram(
            'chatbot_db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'collection'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
        )
        
        self.db_connections_active = Gauge(
            'chatbot_db_connections_active',
            'Number of active database connections'
        )
        
        # ============================================================================
        # CACHE METRICS
        # ============================================================================
        
        self.cache_hits = Counter(
            'chatbot_cache_hits_total',
            'Total number of cache hits',
            ['cache_type']
        )
        
        self.cache_misses = Counter(
            'chatbot_cache_misses_total',
            'Total number of cache misses',
            ['cache_type']
        )
        
        self.cache_size = Gauge(
            'chatbot_cache_size_bytes',
            'Cache size in bytes',
            ['cache_type']
        )
        
        # ============================================================================
        # ERROR METRICS
        # ============================================================================
        
        self.errors_total = Counter(
            'chatbot_errors_total',
            'Total number of errors',
            ['error_type', 'severity']
        )
        
        self.rate_limit_hits = Counter(
            'chatbot_rate_limit_hits_total',
            'Total number of rate limit hits',
            ['endpoint', 'limit_type']
        )
        
        # ============================================================================
        # SYSTEM METRICS
        # ============================================================================
        
        self.system_info = Info(
            'chatbot_system_info',
            'System information'
        )
        
        self.uptime_seconds = Gauge(
            'chatbot_uptime_seconds',
            'System uptime in seconds'
        )
        
        # Set system info
        self.system_info.info({
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'python_version': os.sys.version.split()[0]
        })
        
        logger.info("✅ Metrics collector initialized")
    
    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """
        Track HTTP request metrics
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            status: HTTP status code
            duration: Request duration in seconds
        """
        self.requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def track_ai_request(
        self,
        model: str,
        status: str,
        duration: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        cost_usd: float = 0
    ):
        """
        Track AI model request metrics
        
        Args:
            model: AI model name
            status: Request status (success, error)
            duration: Request duration in seconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_usd: Cost in USD
        """
        self.ai_requests_total.labels(model=model, status=status).inc()
        self.ai_response_time.labels(model=model).observe(duration)
        
        if prompt_tokens > 0:
            self.ai_tokens_used.labels(model=model, type='prompt').inc(prompt_tokens)
        if completion_tokens > 0:
            self.ai_tokens_used.labels(model=model, type='completion').inc(completion_tokens)
        
        total_tokens = prompt_tokens + completion_tokens
        if total_tokens > 0:
            self.ai_tokens_used.labels(model=model, type='total').inc(total_tokens)
        
        if cost_usd > 0:
            self.ai_cost_usd.labels(model=model).inc(cost_usd)
    
    def track_quote_created(self, product_type: str, status: str = "created"):
        """Track quote creation"""
        self.quotes_created.labels(product_type=product_type, status=status).inc()
    
    def track_conversation(self, channel: str, action: str = "started"):
        """Track conversation events"""
        if action == "started":
            self.conversations_started.labels(channel=channel).inc()
            self.conversations_active.inc()
        elif action == "ended":
            self.conversations_active.dec()
    
    def track_error(self, error_type: str, severity: str = "error"):
        """Track error"""
        self.errors_total.labels(error_type=error_type, severity=severity).inc()
    
    def track_rate_limit_hit(self, endpoint: str, limit_type: str = "global"):
        """Track rate limit hit"""
        self.rate_limit_hits.labels(endpoint=endpoint, limit_type=limit_type).inc()
    
    def get_metrics(self) -> bytes:
        """
        Get current metrics in Prometheus format
        
        Returns:
            Metrics in Prometheus exposition format
        """
        return generate_latest(REGISTRY)


# Singleton instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


# Decorator functions
def track_request(func: Callable) -> Callable:
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        collector = get_metrics_collector()
        endpoint = func.__name__
        
        # Get request object from kwargs
        request = kwargs.get('request')
        method = request.method if request else "UNKNOWN"
        
        # Track in-progress
        collector.requests_in_progress.labels(endpoint=endpoint).inc()
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            status = getattr(result, 'status_code', 200)
            return result
        except Exception as e:
            status = 500
            collector.track_error(type(e).__name__)
            raise
        finally:
            duration = time.time() - start_time
            collector.track_request(method, endpoint, status, duration)
            collector.requests_in_progress.labels(endpoint=endpoint).dec()
    
    return wrapper


def track_ai_usage(model: str = "gpt-4o-mini"):
    """Decorator to track AI usage metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract token usage from result if available
                prompt_tokens = getattr(result, 'prompt_tokens', 0)
                completion_tokens = getattr(result, 'completion_tokens', 0)
                
                collector.track_ai_request(
                    model=model,
                    status="success",
                    duration=duration,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                collector.track_ai_request(
                    model=model,
                    status="error",
                    duration=duration
                )
                raise
        
        return wrapper
    return decorator


def track_business_event(event_type: str):
    """Decorator to track business events"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            
            result = await func(*args, **kwargs)
            
            if event_type == "quote_created":
                product_type = kwargs.get('product_type', 'unknown')
                collector.track_quote_created(product_type)
            elif event_type == "conversation_started":
                channel = kwargs.get('channel', 'unknown')
                collector.track_conversation(channel, "started")
            
            return result
        
        return wrapper
    return decorator
