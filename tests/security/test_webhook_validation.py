#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for webhook validation functionality
"""

import pytest
import hmac
import hashlib
from utils.security.webhook_validation import (
    validate_webhook_signature,
    WhatsAppWebhookValidator,
)


class TestWebhookValidation:
    """Test webhook signature validation"""
    
    def test_valid_signature(self):
        """Test validation with correct signature"""
        payload = b'{"entry": [{"id": "123"}]}'
        secret = "test_secret"
        
        # Compute correct signature
        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert validate_webhook_signature(payload, signature, secret) is True
    
    def test_invalid_signature(self):
        """Test validation with incorrect signature"""
        payload = b'{"entry": [{"id": "123"}]}'
        secret = "test_secret"
        wrong_signature = "sha256=invalid_signature_hash"
        
        assert validate_webhook_signature(payload, wrong_signature, secret) is False
    
    def test_missing_prefix(self):
        """Test validation with missing sha256= prefix"""
        payload = b'{"entry": [{"id": "123"}]}'
        secret = "test_secret"
        signature_no_prefix = "abc123"
        
        assert validate_webhook_signature(payload, signature_no_prefix, secret) is False
    
    def test_empty_signature(self):
        """Test validation with empty signature"""
        payload = b'{"entry": [{"id": "123"}]}'
        secret = "test_secret"
        
        assert validate_webhook_signature(payload, "", secret) is False
    
    def test_modified_payload(self):
        """Test that modified payload fails validation"""
        original_payload = b'{"entry": [{"id": "123"}]}'
        modified_payload = b'{"entry": [{"id": "456"}]}'
        secret = "test_secret"
        
        # Compute signature for original payload
        mac = hmac.new(secret.encode(), msg=original_payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        # Verify with modified payload should fail
        assert validate_webhook_signature(modified_payload, signature, secret) is False


class TestWhatsAppWebhookValidator:
    """Test WhatsAppWebhookValidator class"""
    
    def test_initialization(self):
        """Test validator initialization"""
        validator = WhatsAppWebhookValidator("test_secret")
        assert validator.webhook_secret == "test_secret"
    
    def test_initialization_empty_secret(self):
        """Test that empty secret raises error"""
        with pytest.raises(ValueError):
            WhatsAppWebhookValidator("")
    
    def test_validate_method(self):
        """Test validate method"""
        secret = "test_secret"
        validator = WhatsAppWebhookValidator(secret)
        
        payload = b'{"entry": [{"id": "123"}]}'
        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = f"sha256={mac.hexdigest()}"
        
        assert validator.validate(payload, signature) is True
    
    def test_validate_verification_token(self):
        """Test verification token validation"""
        validator = WhatsAppWebhookValidator("test_secret")
        expected_token = "my_verify_token"
        
        assert validator.validate_verification_token(expected_token, expected_token) is True
        assert validator.validate_verification_token("wrong_token", expected_token) is False
    
    def test_timing_attack_resistance(self):
        """Test that comparison is resistant to timing attacks"""
        validator = WhatsAppWebhookValidator("test_secret")
        expected_token = "a" * 32
        wrong_token = "b" * 32
        
        # Both should take similar time (using constant-time comparison)
        # This is more of a smoke test - actual timing attack testing requires benchmarking
        assert validator.validate_verification_token(wrong_token, expected_token) is False
