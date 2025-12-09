#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Circuit Breaker Pattern Implementation
Protects the system from cascading failures

Based on Google Cloud Architecture Framework reliability recommendations
"""

import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional, Tuple, Type
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation - requests pass through
    OPEN = "open"           # Failing - requests are rejected immediately
    HALF_OPEN = "half_open" # Testing - limited requests to check recovery


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""
    
    def __init__(self, message: str, circuit_name: str = "unknown"):
        self.circuit_name = circuit_name
        super().__init__(message)


class CircuitBreaker:
    """
    Circuit Breaker for protecting calls to external services
    
    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service has recovered
    
    Configuration:
    - failure_threshold: Number of failures before opening circuit
    - success_threshold: Number of successes in half-open to close
    - timeout: Time in seconds before attempting recovery
    """
    
    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0,
        expected_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exceptions = expected_exceptions
        
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        return self._state
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self._state == CircuitState.OPEN
    
    async def _transition_to(self, new_state: CircuitState):
        """Transition to a new state"""
        old_state = self._state
        self._state = new_state
        
        logger.info(
            f"Circuit breaker '{self.name}' state change: "
            f"{old_state.value} -> {new_state.value}"
        )
        
        if new_state == CircuitState.CLOSED:
            self._failures = 0
            self._successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._successes = 0
    
    async def _handle_success(self):
        """Handle a successful call"""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._successes += 1
                if self._successes >= self.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._failures = 0
    
    async def _handle_failure(self):
        """Handle a failed call"""
        async with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failures >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)
    
    async def _should_allow(self) -> bool:
        """Check if a call should be allowed"""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if (self._last_failure_time and 
                    time.time() - self._last_failure_time >= self.timeout):
                    await self._transition_to(CircuitState.HALF_OPEN)
                    return True
                return False
            
            # HALF_OPEN - allow test requests
            return True
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker
        
        Args:
            func: Function to execute (sync or async)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception if call fails
        """
        if not await self._should_allow():
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. Service unavailable.",
                circuit_name=self.name
            )
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._handle_success()
            return result
            
        except self.expected_exceptions as e:
            await self._handle_failure()
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Use circuit breaker as a decorator"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.get_event_loop().run_until_complete(
                self.call(func, *args, **kwargs)
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self._state.value,
            "failures": self._failures,
            "successes": self._successes,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "timeout_seconds": self.timeout,
            "last_failure_time": self._last_failure_time,
            "time_since_last_failure": (
                time.time() - self._last_failure_time 
                if self._last_failure_time else None
            )
        }
    
    async def reset(self):
        """Manually reset circuit breaker to closed state"""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failures = 0
            self._successes = 0
            self._last_failure_time = None
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED")


# Pre-configured circuit breakers for common services
openai_circuit = CircuitBreaker(
    name="openai",
    failure_threshold=3,
    success_threshold=2,
    timeout=60.0,
    expected_exceptions=(Exception,)
)

mongodb_circuit = CircuitBreaker(
    name="mongodb",
    failure_threshold=5,
    success_threshold=3,
    timeout=30.0,
    expected_exceptions=(ConnectionError, TimeoutError, Exception)
)

whatsapp_circuit = CircuitBreaker(
    name="whatsapp",
    failure_threshold=5,
    success_threshold=2,
    timeout=120.0,
    expected_exceptions=(Exception,)
)

external_api_circuit = CircuitBreaker(
    name="external_api",
    failure_threshold=5,
    success_threshold=3,
    timeout=60.0,
    expected_exceptions=(ConnectionError, TimeoutError, Exception)
)


def get_all_circuit_status() -> dict:
    """Get status of all circuit breakers"""
    return {
        "circuits": {
            "openai": openai_circuit.get_status(),
            "mongodb": mongodb_circuit.get_status(),
            "whatsapp": whatsapp_circuit.get_status(),
            "external_api": external_api_circuit.get_status()
        }
    }


# Export
__all__ = [
    'CircuitBreaker',
    'CircuitBreakerError',
    'CircuitState',
    'openai_circuit',
    'mongodb_circuit',
    'whatsapp_circuit',
    'external_api_circuit',
    'get_all_circuit_status'
]
