#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook Signature Validation Utilities
Implements HMAC SHA256 validation for WhatsApp and n8n webhooks
"""

import hmac
import hashlib
import os
from typing import Optional
from flask import Request


def verify_whatsapp_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Verify WhatsApp webhook signature using HMAC SHA256.

    Args:
        payload: Raw request body as bytes
        signature: Signature from X-Hub-Signature-256 header
        secret: Webhook secret/verify token

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False

    # WhatsApp sends signature as "sha256=<hash>"
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)


def verify_n8n_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Verify n8n webhook signature using HMAC SHA256.

    Args:
        payload: Raw request body as bytes
        signature: Signature from X-n8n-signature header
        secret: Webhook secret

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not secret:
        return False

    # Calculate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected_signature)


def get_webhook_secret(service: str) -> Optional[str]:
    """
    Get webhook secret from environment variables.

    Args:
        service: Service name ('whatsapp' or 'n8n')

    Returns:
        Secret string or None if not found
    """
    env_var_map = {
        'whatsapp': 'WHATSAPP_WEBHOOK_SECRET',
        'n8n': 'N8N_WEBHOOK_SECRET'
    }

    env_var = env_var_map.get(service.lower())
    if not env_var:
        return None

    return os.getenv(env_var)


def validate_webhook_request(
    request: Request,
    service: str = 'whatsapp'
) -> tuple[bool, Optional[str]]:
    """
    Validate webhook request signature.

    Args:
        request: Flask request object
        service: Service name ('whatsapp' or 'n8n')

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get secret from environment
    secret = get_webhook_secret(service)
    if not secret:
        return False, f"Webhook secret not configured for {service}"

    # Get signature from headers
    if service.lower() == 'whatsapp':
        signature_header = 'X-Hub-Signature-256'
    elif service.lower() == 'n8n':
        signature_header = 'X-n8n-signature'
    else:
        return False, f"Unknown service: {service}"

    signature = request.headers.get(signature_header)
    if not signature:
        return False, f"Missing {signature_header} header"

    # Get raw payload
    try:
        payload = request.get_data()
    except Exception as e:
        return False, f"Error reading request payload: {str(e)}"

    # Verify signature
    if service.lower() == 'whatsapp':
        is_valid = verify_whatsapp_webhook_signature(payload, signature, secret)
    else:
        is_valid = verify_n8n_webhook_signature(payload, signature, secret)

    if not is_valid:
        return False, "Invalid webhook signature"

    return True, None



