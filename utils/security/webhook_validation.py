#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Webhook Signature Validation
Implements HMAC-SHA256 signature validation for WhatsApp Business API webhooks
"""

import hmac
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def validate_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Validate WhatsApp webhook signature using HMAC-SHA256.
    
    Args:
        payload: The raw request body as bytes
        signature: The signature from X-Hub-Signature-256 header (format: "sha256=...")
        secret: The webhook secret configured in Meta dashboard
        
    Returns:
        bool: True if signature is valid, False otherwise
        
    Example:
        >>> payload = b'{"entry": [...]}'
        >>> signature = "sha256=abc123..."
        >>> secret = "my_webhook_secret"
        >>> validate_webhook_signature(payload, signature, secret)
        True
    """
    if not signature or not signature.startswith('sha256='):
        logger.warning("Invalid signature format - must start with 'sha256='")
        return False
    
    # Extract the signature hash (remove 'sha256=' prefix)
    expected_signature = signature[7:]
    
    # Compute HMAC-SHA256
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()
    
    # Compare signatures using constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(computed_signature, expected_signature)
    
    if not is_valid:
        logger.warning("Webhook signature validation failed")
    
    return is_valid


class WhatsAppWebhookValidator:
    """
    WhatsApp webhook validator with configuration management.
    """
    
    def __init__(self, webhook_secret: str):
        """
        Initialize the validator with a webhook secret.
        
        Args:
            webhook_secret: The webhook secret from Meta dashboard
        """
        if not webhook_secret:
            raise ValueError("Webhook secret cannot be empty")
        self.webhook_secret = webhook_secret
        
    def validate(self, payload: bytes, signature: str) -> bool:
        """
        Validate webhook signature.
        
        Args:
            payload: The raw request body as bytes
            signature: The signature from X-Hub-Signature-256 header
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        return validate_webhook_signature(payload, signature, self.webhook_secret)
    
    def validate_verification_token(self, token: str, expected_token: str) -> bool:
        """
        Validate webhook verification token during initial setup.
        
        Args:
            token: The token provided in the request
            expected_token: The expected verification token
            
        Returns:
            bool: True if tokens match, False otherwise
        """
        # Use constant-time comparison
        is_valid = hmac.compare_digest(token, expected_token)
        
        if not is_valid:
            logger.warning("Webhook verification token validation failed")
            
        return is_valid
