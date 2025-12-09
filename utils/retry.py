#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retry with Exponential Backoff
Implements reliable retry logic based on Google Cloud best practices

Based on Google Cloud Architecture Framework reliability recommendations
"""

import asyncio
import random
from functools import wraps
from typing import Callable, Type, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class RetryExhausted(Exception):
    """All retry attempts exhausted"""
    
    def __init__(self, message: str, attempts: int, last_exception: Exception = None):
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(message)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Decorator for retrying functions with exponential backoff
    
    This implements the exponential backoff pattern recommended by Google Cloud
    for handling transient failures in distributed systems.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Base for exponential calculation (default: 2.0)
        jitter: Add random variation to delay (default: True)
        retry_exceptions: Tuple of exceptions that trigger retry (default: Exception)
        on_retry: Optional callback called on each retry (attempt, exception)
    
    Returns:
        Decorated function with retry logic
    
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        async def call_external_api():
            # API call that may fail
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except retry_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Retry exhausted for {func.__name__} "
                            f"after {max_retries + 1} attempts: {e}"
                        )
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for "
                        f"{func.__name__}: {e}. Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_error:
                            logger.warning(f"on_retry callback failed: {callback_error}")
                    
                    await asyncio.sleep(delay)
            
            raise RetryExhausted(
                f"Function {func.__name__} failed after {max_retries + 1} attempts",
                attempts=max_retries + 1,
                last_exception=last_exception
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return asyncio.get_event_loop().run_until_complete(
                async_wrapper(*args, **kwargs)
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Pre-configured retry decorators for common use cases

def retry_for_api_calls(func):
    """
    Retry configuration for external API calls
    
    - 3 retries with 1s base delay
    - Max 30s delay
    - Handles connection and timeout errors
    """
    return retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        jitter=True,
        retry_exceptions=(ConnectionError, TimeoutError, Exception)
    )(func)


def retry_for_database(func):
    """
    Retry configuration for database operations
    
    - 2 retries with 0.5s base delay
    - Max 10s delay
    - Handles connection errors
    """
    return retry_with_backoff(
        max_retries=2,
        base_delay=0.5,
        max_delay=10.0,
        jitter=True,
        retry_exceptions=(ConnectionError, TimeoutError)
    )(func)


def retry_for_ai_services(func):
    """
    Retry configuration for AI service calls (OpenAI, Vertex AI, etc.)
    
    - 3 retries with 2s base delay (AI services may need more time)
    - Max 60s delay
    - Full exception handling
    """
    return retry_with_backoff(
        max_retries=3,
        base_delay=2.0,
        max_delay=60.0,
        jitter=True,
        retry_exceptions=(Exception,)
    )(func)


def retry_for_webhooks(func):
    """
    Retry configuration for webhook calls
    
    - 5 retries with 1s base delay
    - Max 120s delay (webhooks may have longer processing times)
    """
    return retry_with_backoff(
        max_retries=5,
        base_delay=1.0,
        max_delay=120.0,
        jitter=True,
        retry_exceptions=(ConnectionError, TimeoutError, Exception)
    )(func)


# Export
__all__ = [
    'retry_with_backoff',
    'RetryExhausted',
    'retry_for_api_calls',
    'retry_for_database',
    'retry_for_ai_services',
    'retry_for_webhooks'
]
