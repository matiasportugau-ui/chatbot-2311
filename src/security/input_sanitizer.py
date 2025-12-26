#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input Sanitizer
Validates and sanitizes user input to prevent injection attacks
"""

import re
import html
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Input validation and sanitization"""
    
    # Common injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\b(TABLE|DATABASE)\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--\s|#|\/\*|\*\/)",  # SQL comments
        r"(\b(AND|OR)\b.*=)",
    ]
    
    NOSQL_INJECTION_PATTERNS = [
        r"(\$where|\$regex|\$ne|\$gt|\$lt)",
        r"(\.find\(|\.aggregate\(|\.mapReduce\()",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",
    ]
    
    def __init__(self, strict: bool = False):
        """
        Initialize input sanitizer
        
        Args:
            strict: Enable strict mode (more aggressive sanitization)
        """
        self.strict = strict
    
    def sanitize_string(
        self,
        value: str,
        max_length: Optional[int] = None,
        allow_html: bool = False
    ) -> str:
        """
        Sanitize string input
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            allow_html: Allow HTML tags (will escape if False)
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Enforce max length
        if max_length and len(value) > max_length:
            logger.warning(f"Input truncated from {len(value)} to {max_length} characters")
            value = value[:max_length]
        
        # Escape HTML if not allowed
        if not allow_html:
            value = html.escape(value)
        
        # Check for XSS patterns
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential XSS pattern detected: {pattern}")
                if self.strict:
                    raise ValueError("Input contains potentially malicious content")
                # Remove the pattern
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return value
    
    def sanitize_phone(self, value: str) -> str:
        """
        Sanitize phone number
        
        Args:
            value: Phone number string
            
        Returns:
            Sanitized phone number (digits only, with optional + prefix)
        """
        # Remove all non-digit characters except +
        sanitized = re.sub(r'[^\d+]', '', value)
        
        # Ensure + is only at the beginning
        if '+' in sanitized:
            parts = sanitized.split('+')
            sanitized = '+' + ''.join(parts)
        
        return sanitized
    
    def sanitize_email(self, value: str) -> str:
        """
        Sanitize email address
        
        Args:
            value: Email address
            
        Returns:
            Sanitized email
            
        Raises:
            ValueError: If email format is invalid
        """
        value = value.strip().lower()
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")
        
        return value
    
    def sanitize_dict(
        self,
        data: Dict[str, Any],
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sanitize dictionary input
        
        Args:
            data: Input dictionary
            schema: Optional schema for validation
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = self.sanitize_string(str(key), max_length=100)
            
            # Check for NoSQL injection in keys
            for pattern in self.NOSQL_INJECTION_PATTERNS:
                if re.search(pattern, safe_key, re.IGNORECASE):
                    logger.warning(f"Potential NoSQL injection in key: {safe_key}")
                    if self.strict:
                        raise ValueError(f"Invalid key: {safe_key}")
                    continue
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[safe_key] = self.sanitize_list(value)
            else:
                sanitized[safe_key] = value
        
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """
        Sanitize list input
        
        Args:
            data: Input list
            
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    def check_sql_injection(self, value: str) -> bool:
        """
        Check for SQL injection patterns
        
        Args:
            value: String to check
            
        Returns:
            True if potential SQL injection detected
        """
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True
        return False
    
    def check_nosql_injection(self, value: str) -> bool:
        """
        Check for NoSQL injection patterns
        
        Args:
            value: String to check
            
        Returns:
            True if potential NoSQL injection detected
        """
        for pattern in self.NOSQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential NoSQL injection detected: {pattern}")
                return True
        return False
    
    def validate_and_sanitize(
        self,
        value: Any,
        value_type: str = "string",
        **kwargs
    ) -> Any:
        """
        Validate and sanitize input based on type
        
        Args:
            value: Input value
            value_type: Type of value (string, phone, email, dict, list)
            **kwargs: Additional arguments for sanitization
            
        Returns:
            Sanitized value
            
        Raises:
            ValueError: If validation fails
        """
        if value_type == "string":
            return self.sanitize_string(value, **kwargs)
        elif value_type == "phone":
            return self.sanitize_phone(value)
        elif value_type == "email":
            return self.sanitize_email(value)
        elif value_type == "dict":
            return self.sanitize_dict(value, **kwargs)
        elif value_type == "list":
            return self.sanitize_list(value)
        else:
            raise ValueError(f"Unsupported value type: {value_type}")


# Singleton instance
_input_sanitizer = None


def get_input_sanitizer(strict: bool = False) -> InputSanitizer:
    """Get singleton input sanitizer instance"""
    global _input_sanitizer
    if _input_sanitizer is None:
        _input_sanitizer = InputSanitizer(strict)
    return _input_sanitizer


# Convenience function
def sanitize_input(
    value: Any,
    value_type: str = "string",
    **kwargs
) -> Any:
    """
    Sanitize input (convenience function)
    
    Args:
        value: Input value
        value_type: Type of value
        **kwargs: Additional arguments
        
    Returns:
        Sanitized value
    """
    sanitizer = get_input_sanitizer()
    return sanitizer.validate_and_sanitize(value, value_type, **kwargs)
