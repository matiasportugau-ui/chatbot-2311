#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook Signature Validator
Validates webhook signatures from WhatsApp, n8n, and other services
"""

import hmac
import hashlib
import base64
from typing import Optional
from fastapi import Request, HTTPException, status
import logging

logger = logging.getLogger(__name__)


class WebhookValidator:
    """Webhook signature validator"""
    
    def __init__(self, secret: Optional[str] = None):
        """
        Initialize webhook validator
        
        Args:
            secret: Webhook secret for signature validation
        """
        self.secret = secret
    
    def validate_whatsapp_signature(
        self,
        payload: bytes,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate WhatsApp webhook signature
        
        Args:
            payload: Raw request body
            signature: X-Hub-Signature-256 header value
            secret: App secret (optional, uses instance secret if not provided)
            
        Returns:
            True if signature is valid
        """
        secret_to_use = secret or self.secret
        
        if not secret_to_use:
            logger.error("WhatsApp webhook secret not configured")
            return False
        
        if not signature:
            logger.warning("Missing X-Hub-Signature-256 header")
            return False
        
        # WhatsApp uses SHA256 HMAC
        expected_signature = hmac.new(
            secret_to_use.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Signature format: sha256=<hex_digest>
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning("Invalid WhatsApp webhook signature")
        
        return is_valid
    
    def validate_n8n_signature(
        self,
        payload: bytes,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate n8n webhook signature
        
        Args:
            payload: Raw request body
            signature: n8n-signature header value
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        secret_to_use = secret or self.secret
        
        if not secret_to_use:
            logger.error("n8n webhook secret not configured")
            return False
        
        if not signature:
            logger.warning("Missing n8n-signature header")
            return False
        
        # n8n uses SHA256 HMAC
        expected_signature = hmac.new(
            secret_to_use.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning("Invalid n8n webhook signature")
        
        return is_valid
    
    def validate_generic_signature(
        self,
        payload: bytes,
        signature: str,
        secret: Optional[str] = None,
        algorithm: str = "sha256"
    ) -> bool:
        """
        Validate generic webhook signature
        
        Args:
            payload: Raw request body
            signature: Signature to validate
            secret: Webhook secret
            algorithm: Hash algorithm (sha256, sha1, sha512)
            
        Returns:
            True if signature is valid
        """
        secret_to_use = secret or self.secret
        
        if not secret_to_use:
            logger.error("Webhook secret not configured")
            return False
        
        if not signature:
            logger.warning("Missing signature")
            return False
        
        # Select hash algorithm
        if algorithm == "sha256":
            hash_func = hashlib.sha256
        elif algorithm == "sha1":
            hash_func = hashlib.sha1
        elif algorithm == "sha512":
            hash_func = hashlib.sha512
        else:
            logger.error(f"Unsupported algorithm: {algorithm}")
            return False
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret_to_use.encode('utf-8'),
            payload,
            hash_func
        ).hexdigest()
        
        # Handle different signature formats
        if signature.startswith(f'{algorithm}='):
            signature = signature[len(algorithm)+1:]
        
        is_valid = hmac.compare_digest(expected_signature, signature)
        
        if not is_valid:
            logger.warning(f"Invalid webhook signature (algorithm: {algorithm})")
        
        return is_valid
    
    async def validate_request(
        self,
        request: Request,
        webhook_type: str = "whatsapp",
        secret: Optional[str] = None
    ):
        """
        Validate webhook request
        
        Args:
            request: FastAPI request object
            webhook_type: Type of webhook (whatsapp, n8n, generic)
            secret: Optional webhook secret
            
        Raises:
            HTTPException: If signature is invalid
        """
        # Read raw body
        body = await request.body()
        
        # Get signature header
        if webhook_type == "whatsapp":
            signature = request.headers.get("X-Hub-Signature-256")
            is_valid = self.validate_whatsapp_signature(body, signature, secret)
        elif webhook_type == "n8n":
            signature = request.headers.get("n8n-signature")
            is_valid = self.validate_n8n_signature(body, signature, secret)
        else:
            signature = request.headers.get("X-Signature")
            is_valid = self.validate_generic_signature(body, signature, secret)
        
        if not is_valid:
            logger.error(f"Invalid {webhook_type} webhook signature from {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )


# Singleton instance
_webhook_validator = None


def get_webhook_validator(secret: Optional[str] = None) -> WebhookValidator:
    """Get singleton webhook validator instance"""
    global _webhook_validator
    if _webhook_validator is None:
        _webhook_validator = WebhookValidator(secret)
    return _webhook_validator


# Convenience function
async def validate_whatsapp_signature(
    request: Request,
    secret: Optional[str] = None
):
    """
    Validate WhatsApp webhook signature (convenience function)
    
    Args:
        request: FastAPI request
        secret: WhatsApp app secret
        
    Raises:
        HTTPException: If signature invalid
    """
    validator = get_webhook_validator(secret)
    await validator.validate_request(request, "whatsapp", secret)
