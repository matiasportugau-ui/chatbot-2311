#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Logger
JSON-based structured logging for better observability
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger
import structlog
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record"""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add service name
        log_record['service'] = 'bmc-chatbot'
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_record['request_id'] = request_id
        
        # Add severity level
        log_record['severity'] = record.levelname
        
        # Add source location
        log_record['source'] = {
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName
        }


class StructuredLogger:
    """Structured logger with JSON output"""
    
    def __init__(
        self,
        name: str = "bmc-chatbot",
        level: str = "INFO",
        json_format: bool = True
    ):
        """
        Initialize structured logger
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            json_format: Use JSON format (True) or plain text (False)
        """
        self.name = name
        self.level = getattr(logging, level.upper())
        self.json_format = json_format
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        if json_format:
            # Use JSON formatter
            formatter = CustomJsonFormatter(
                '%(timestamp)s %(severity)s %(name)s %(message)s'
            )
        else:
            # Use standard formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra=kwargs)
    
    def log_request(
        self,
        method: str,
        path: str,
        status: int,
        duration: float,
        user_id: Optional[str] = None,
        **kwargs
    ):
        """
        Log HTTP request
        
        Args:
            method: HTTP method
            path: Request path
            status: HTTP status code
            duration: Request duration in seconds
            user_id: User ID (optional)
            **kwargs: Additional fields
        """
        self.info(
            f"{method} {path} {status}",
            http={
                'method': method,
                'path': path,
                'status': status,
                'duration_seconds': duration
            },
            user_id=user_id,
            **kwargs
        )
    
    def log_ai_request(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        duration: float,
        **kwargs
    ):
        """
        Log AI model request
        
        Args:
            model: AI model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost_usd: Cost in USD
            duration: Request duration in seconds
            **kwargs: Additional fields
        """
        self.info(
            f"AI request to {model}",
            ai={
                'model': model,
                'tokens': {
                    'prompt': prompt_tokens,
                    'completion': completion_tokens,
                    'total': prompt_tokens + completion_tokens
                },
                'cost_usd': cost_usd,
                'duration_seconds': duration
            },
            **kwargs
        )
    
    def log_business_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        **kwargs
    ):
        """
        Log business event
        
        Args:
            event_type: Event type (e.g., 'quote_created', 'conversation_started')
            event_data: Event-specific data
            **kwargs: Additional fields
        """
        self.info(
            f"Business event: {event_type}",
            event={
                'type': event_type,
                'data': event_data
            },
            **kwargs
        )
    
    def log_error_with_context(
        self,
        error: Exception,
        context: Dict[str, Any],
        **kwargs
    ):
        """
        Log error with context
        
        Args:
            error: Exception object
            context: Error context
            **kwargs: Additional fields
        """
        self.error(
            f"Error: {str(error)}",
            error={
                'type': type(error).__name__,
                'message': str(error),
                'traceback': self._format_traceback(error)
            },
            context=context,
            **kwargs
        )
    
    def _format_traceback(self, error: Exception) -> Optional[str]:
        """Format exception traceback"""
        import traceback
        if error.__traceback__:
            return ''.join(traceback.format_tb(error.__traceback__))
        return None
    
    def set_request_id(self, request_id: str):
        """Set request ID for current context"""
        request_id_var.set(request_id)
    
    def clear_request_id(self):
        """Clear request ID from current context"""
        request_id_var.set(None)


# Singleton instance
_logger = None


def get_logger(
    name: str = "bmc-chatbot",
    level: str = "INFO",
    json_format: bool = True
) -> StructuredLogger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        level: Log level
        json_format: Use JSON format
        
    Returns:
        StructuredLogger instance
    """
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name, level, json_format)
    return _logger


def configure_structlog():
    """Configure structlog for enhanced logging"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )
