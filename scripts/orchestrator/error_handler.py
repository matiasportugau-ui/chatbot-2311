"""
Error Handler
Catches, classifies errors and determines retry strategy
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum
import traceback


class ErrorType(Enum):
    """Error classification types"""
    TRANSIENT = "transient"  # Retryable errors
    PERMANENT = "permanent"  # Requires manual intervention
    DEPENDENCY = "dependency"  # Wait for dependency
    CONFIGURATION = "configuration"  # Fix configuration
    UNKNOWN = "unknown"  # Unknown error type


class ErrorHandler:
    """Handles and classifies errors"""
    
    # Transient error patterns (retryable)
    TRANSIENT_PATTERNS = [
        "TimeoutError",
        "ConnectionError",
        "ConnectionRefusedError",
        "timeout",
        "temporary",
        "rate limit",
        "503",
        "502",
        "504"
    ]
    
    # Permanent error patterns (not retryable)
    PERMANENT_PATTERNS = [
        "SyntaxError",
        "TypeError",
        "AttributeError",
        "KeyError",
        "ValueError",
        "FileNotFoundError",
        "PermissionError",
        "401",
        "403",
        "404"
    ]
    
    # Dependency error patterns
    DEPENDENCY_PATTERNS = [
        "dependency",
        "prerequisite",
        "missing dependency",
        "not found"
    ]
    
    # Configuration error patterns
    CONFIGURATION_PATTERNS = [
        "configuration",
        "config",
        "environment",
        "missing",
        "invalid"
    ]
    
    def classify_error(self, error: Exception) -> Tuple[ErrorType, str]:
        """
        Classify an error and determine retry strategy
        Returns: (error_type, error_message)
        """
        error_message = str(error)
        error_type_name = type(error).__name__
        error_str = f"{error_type_name}: {error_message}"
        
        # Check transient patterns
        if any(pattern.lower() in error_str.lower() for pattern in self.TRANSIENT_PATTERNS):
            return ErrorType.TRANSIENT, error_str
        
        # Check permanent patterns
        if any(pattern.lower() in error_str.lower() for pattern in self.PERMANENT_PATTERNS):
            return ErrorType.PERMANENT, error_str
        
        # Check dependency patterns
        if any(pattern.lower() in error_str.lower() for pattern in self.DEPENDENCY_PATTERNS):
            return ErrorType.DEPENDENCY, error_str
        
        # Check configuration patterns
        if any(pattern.lower() in error_str.lower() for pattern in self.CONFIGURATION_PATTERNS):
            return ErrorType.CONFIGURATION, error_str
        
        # Default to unknown
        return ErrorType.UNKNOWN, error_str
    
    def is_retryable(self, error: Exception) -> bool:
        """Check if error is retryable"""
        error_type, _ = self.classify_error(error)
        return error_type == ErrorType.TRANSIENT
    
    def get_error_context(self, error: Exception) -> Dict[str, Any]:
        """Get full error context including stack trace"""
        error_type, error_message = self.classify_error(error)
        
        return {
            "error_type": error_type.value,
            "error_message": error_message,
            "error_class": type(error).__name__,
            "is_retryable": self.is_retryable(error),
            "stack_trace": traceback.format_exc(),
            "traceback": traceback.format_tb(error.__traceback__)
        }
    
    def should_retry(self, error: Exception, retry_count: int, max_retries: int = 3) -> bool:
        """Determine if error should be retried"""
        if retry_count >= max_retries:
            return False
        
        return self.is_retryable(error)
    
    def get_retry_delay(self, error: Exception, retry_count: int, 
                       initial_delay: int = 60, backoff_multiplier: int = 2) -> int:
        """Calculate retry delay with exponential backoff"""
        if not self.is_retryable(error):
            return 0
        
        return initial_delay * (backoff_multiplier ** retry_count)
    
    def format_error_for_logging(self, error: Exception, phase: int) -> Dict[str, Any]:
        """Format error for logging"""
        context = self.get_error_context(error)
        context["phase"] = phase
        return context

