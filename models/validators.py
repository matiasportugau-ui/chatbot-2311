#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Validators for Input Data
Implements input validation based on Google Cloud security best practices

Based on Google Cloud Architecture Framework security recommendations
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Set
import re
import html

# Validation patterns
PHONE_PATTERN = re.compile(
    r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{4,6}$'
)
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,128}$')
NAME_PATTERN = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'\-]+$')

# Valid product codes
PRODUCT_CODES: Set[str] = {
    'isodec', 'poliestireno', 'lana_roca', 'poliuretano', 'fibra_vidrio'
}

# Valid thickness values
THICKNESS_VALUES: Set[str] = {
    '25mm', '50mm', '75mm', '100mm', '125mm', '150mm'
}

# Suspicious patterns that could indicate XSS or injection attempts
SUSPICIOUS_PATTERNS = [
    r'<script',
    r'javascript:',
    r'data:text/html',
    r'vbscript:',
    r'onload\s*=',
    r'onerror\s*=',
    r'onclick\s*=',
    r'onmouseover\s*=',
    r'onfocus\s*=',
    r'onblur\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
]


def sanitize_string(value: str, max_length: int = 2000) -> str:
    """
    Sanitize string by removing potentially dangerous content
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return value
    
    # Escape HTML entities
    value = html.escape(value)
    
    # Remove control characters (except newlines and tabs)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
    
    # Limit length
    value = value[:max_length]
    
    return value.strip()


def check_suspicious_content(value: str) -> bool:
    """
    Check if value contains suspicious patterns
    
    Args:
        value: String to check
        
    Returns:
        True if suspicious content found
    """
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


class SecureChatMessage(BaseModel):
    """
    Secure model for chat messages with comprehensive validation
    """
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message content"
    )
    session_id: Optional[str] = Field(
        None,
        max_length=128,
        description="Session identifier for conversation tracking"
    )
    
    @field_validator('message', mode='before')
    @classmethod
    def sanitize_message(cls, v):
        """Sanitize and validate message content"""
        if not isinstance(v, str):
            raise ValueError('El mensaje debe ser texto')
        
        v = sanitize_string(v, max_length=2000)
        
        if not v:
            raise ValueError('El mensaje no puede estar vacío')
        
        if check_suspicious_content(v):
            raise ValueError('El mensaje contiene contenido no permitido')
        
        return v
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v):
        """Validate session ID format"""
        if v is None:
            return v
        
        if not SESSION_ID_PATTERN.match(v):
            raise ValueError('session_id contiene caracteres no permitidos')
        
        return v


class SecureQuoteRequest(BaseModel):
    """
    Secure model for quote requests with comprehensive validation
    """
    
    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Customer full name"
    )
    phone: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Customer phone number"
    )
    product: str = Field(
        ...,
        description="Product type code"
    )
    thickness: str = Field(
        ...,
        description="Product thickness"
    )
    length: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Length in meters"
    )
    width: float = Field(
        ...,
        gt=0,
        le=1000,
        description="Width in meters"
    )
    address: Optional[str] = Field(
        None,
        max_length=200,
        description="Delivery address"
    )
    zone: Optional[str] = Field(
        None,
        max_length=50,
        description="Zone or area"
    )
    observations: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional observations"
    )
    
    @field_validator('customer_name', mode='before')
    @classmethod
    def sanitize_name(cls, v):
        """Sanitize and validate customer name"""
        if not isinstance(v, str):
            raise ValueError('El nombre debe ser texto')
        
        v = sanitize_string(v, max_length=100)
        
        if not v:
            raise ValueError('El nombre no puede estar vacío')
        
        if not NAME_PATTERN.match(v):
            raise ValueError('El nombre contiene caracteres no válidos')
        
        return v.title()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        # Remove formatting characters
        v = re.sub(r'[\s\-\.\(\)]', '', v)
        
        if not PHONE_PATTERN.match(v):
            raise ValueError('Formato de teléfono inválido')
        
        return v
    
    @field_validator('product')
    @classmethod
    def validate_product(cls, v):
        """Validate product code"""
        v = v.lower().strip()
        if v not in PRODUCT_CODES:
            raise ValueError(
                f'Producto no válido. Opciones: {", ".join(sorted(PRODUCT_CODES))}'
            )
        return v
    
    @field_validator('thickness')
    @classmethod
    def validate_thickness(cls, v):
        """Validate thickness value"""
        v = v.lower().strip()
        if v not in THICKNESS_VALUES:
            raise ValueError(
                f'Espesor no válido. Opciones: {", ".join(sorted(THICKNESS_VALUES))}'
            )
        return v
    
    @field_validator('address', 'zone', 'observations', mode='before')
    @classmethod
    def sanitize_optional_fields(cls, v):
        """Sanitize optional text fields"""
        if v is None:
            return v
        if not isinstance(v, str):
            return str(v)
        return sanitize_string(v)
    
    @model_validator(mode='after')
    def validate_dimensions(self):
        """Validate that dimensions are reasonable"""
        area = self.length * self.width
        if area > 10000:
            raise ValueError('El área total excede el máximo permitido (10,000 m²)')
        
        if area < 0.01:
            raise ValueError('El área total es demasiado pequeña')
        
        return self


# Export validators for easy access
__all__ = [
    'SecureChatMessage',
    'SecureQuoteRequest',
    'sanitize_string',
    'check_suspicious_content',
    'PRODUCT_CODES',
    'THICKNESS_VALUES'
]
