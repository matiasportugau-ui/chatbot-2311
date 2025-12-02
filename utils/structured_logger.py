#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Logger
Provides JSON-formatted logging with correlation IDs and OpenAI API metadata.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

from utils.request_tracking import get_request_context


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Includes correlation IDs and request context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string
        """
        # Get request context if available
        request_context = get_request_context()
        
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request context if available
        if request_context:
            log_entry['request_id'] = request_context.get('request_id')
            log_entry['client_request_id'] = request_context.get('client_request_id')
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add any additional fields passed via extra parameter
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'pathname', 'process', 'processName', 'relativeCreated',
                'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                'extra_fields'
            ]:
                if not key.startswith('_'):
                    try:
                        json.dumps(value)  # Test if value is JSON serializable
                        log_entry[key] = value
                    except (TypeError, ValueError):
                        pass  # Skip non-serializable values
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    Structured logger wrapper that adds correlation IDs and metadata.
    """
    
    def __init__(self, name: str, log_level: str = "INFO"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add console handler with structured formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
    
    def _log_with_context(
        self,
        level: int,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log with request context and extra fields.
        
        Args:
            level: Log level
            message: Log message
            extra_fields: Additional fields to include
            **kwargs: Additional keyword arguments
        """
        # Get request context
        request_context = get_request_context()
        
        # Prepare extra dict
        extra = {'extra_fields': extra_fields or {}}
        
        # Add request context to extra fields
        if request_context:
            extra['extra_fields']['request_id'] = request_context.get('request_id')
            extra['extra_fields']['client_request_id'] = request_context.get('client_request_id')
        
        # Add any additional kwargs to extra fields
        if kwargs:
            if 'extra_fields' not in extra:
                extra['extra_fields'] = {}
            extra['extra_fields'].update(kwargs)
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def log_openai_request(
        self,
        model: str,
        provider: str,
        prompt_length: int,
        system_prompt_length: Optional[int] = None,
        request_id: Optional[str] = None,
        client_request_id: Optional[str] = None,
        **kwargs
    ):
        """
        Log OpenAI API request.
        
        Args:
            model: Model name
            provider: Provider name (openai, groq, etc.)
            prompt_length: Length of user prompt
            system_prompt_length: Length of system prompt
            request_id: Server-generated request ID
            client_request_id: Client-provided request ID
            **kwargs: Additional metadata
        """
        extra_fields = {
            'event_type': 'openai_request',
            'model': model,
            'provider': provider,
            'prompt_length': prompt_length,
            'system_prompt_length': system_prompt_length,
            **kwargs
        }
        
        if request_id:
            extra_fields['request_id'] = request_id
        if client_request_id:
            extra_fields['client_request_id'] = client_request_id
        
        self.info(f"OpenAI API request: {provider}/{model}", **extra_fields)
    
    def log_openai_response(
        self,
        model: str,
        provider: str,
        tokens_input: int,
        tokens_output: int,
        response_time: float,
        cost: float,
        request_id: Optional[str] = None,
        client_request_id: Optional[str] = None,
        openai_request_id: Optional[str] = None,
        rate_limit_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log OpenAI API response.
        
        Args:
            model: Model name
            provider: Provider name
            tokens_input: Input tokens used
            tokens_output: Output tokens used
            response_time: Response time in seconds
            cost: Estimated cost
            request_id: Server-generated request ID
            client_request_id: Client-provided request ID
            openai_request_id: OpenAI's x-request-id header value
            rate_limit_info: Rate limit information from headers
            **kwargs: Additional metadata
        """
        extra_fields = {
            'event_type': 'openai_response',
            'model': model,
            'provider': provider,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output,
            'total_tokens': tokens_input + tokens_output,
            'response_time_seconds': response_time,
            'cost': cost,
            **kwargs
        }
        
        if request_id:
            extra_fields['request_id'] = request_id
        if client_request_id:
            extra_fields['client_request_id'] = client_request_id
        if openai_request_id:
            extra_fields['openai_request_id'] = openai_request_id
        if rate_limit_info:
            extra_fields['rate_limit'] = rate_limit_info
        
        self.info(
            f"OpenAI API response: {provider}/{model} "
            f"({tokens_input + tokens_output} tokens, {response_time:.2f}s, ${cost:.4f})",
            **extra_fields
        )
    
    def log_openai_error(
        self,
        model: str,
        provider: str,
        error: str,
        request_id: Optional[str] = None,
        client_request_id: Optional[str] = None,
        openai_request_id: Optional[str] = None,
        response_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """
        Log OpenAI API error.
        
        Args:
            model: Model name
            provider: Provider name
            error: Error message
            request_id: Server-generated request ID
            client_request_id: Client-provided request ID
            openai_request_id: OpenAI's x-request-id header value
            response_headers: Response headers if available
            **kwargs: Additional metadata
        """
        extra_fields = {
            'event_type': 'openai_error',
            'model': model,
            'provider': provider,
            'error': error,
            **kwargs
        }
        
        if request_id:
            extra_fields['request_id'] = request_id
        if client_request_id:
            extra_fields['client_request_id'] = client_request_id
        if openai_request_id:
            extra_fields['openai_request_id'] = openai_request_id
        if response_headers:
            extra_fields['response_headers'] = response_headers
        
        self.error(f"OpenAI API error: {provider}/{model} - {error}", **extra_fields)


def get_structured_logger(name: str, log_level: Optional[str] = None) -> StructuredLogger:
    """
    Get or create a structured logger instance.
    
    Args:
        name: Logger name
        log_level: Optional log level (defaults to INFO)
        
    Returns:
        StructuredLogger instance
    """
    if log_level is None:
        import os
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    return StructuredLogger(name, log_level)

