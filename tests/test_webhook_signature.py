#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Webhook Signature Validation
"""

import unittest
import importlib.util
import sys
import os
import hmac
import hashlib

# Ensure we can import from utils - assumes we are running from project root or inside tests/
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.security.webhook_validation import verify_whatsapp_webhook_signature, verify_n8n_webhook_signature

class TestWebhookSignature(unittest.TestCase):
    
    def setUp(self):
        self.secret = "test_secret_12345"
        self.payload = b'{"object":"whatsapp_business_account","entry":[{"id":"123","changes":[{"value":{"messaging_product":"whatsapp","messages":[{"from":"123456789","text":{"body":"Hello"}}]},"field":"messages"}]}]}'
        
        # Calculate valid signature
        self.valid_signature = hmac.new(
            self.secret.encode('utf-8'),
            self.payload,
            hashlib.sha256
        ).hexdigest()
        
    def test_whatsapp_valid_signature(self):
        """Test that a valid WhatsApp signature is accepted"""
        # WhatsApp usually validates against the raw signature (without sha256= prefix in the utility call if stripped or with it if not)
        # The utility strips 'sha256=' if present.
        
        # Case 1: Signature with prefix
        self.assertTrue(verify_whatsapp_webhook_signature(
            self.payload,
            f"sha256={self.valid_signature}",
            self.secret
        ))
        
        # Case 2: Signature without prefix (if somehow passed that way)
        self.assertTrue(verify_whatsapp_webhook_signature(
            self.payload,
            self.valid_signature,
            self.secret
        ))

    def test_whatsapp_invalid_signature(self):
        """Test that an invalid WhatsApp signature is rejected"""
        invalid_sig = "a" * 64
        self.assertFalse(verify_whatsapp_webhook_signature(
            self.payload,
            f"sha256={invalid_sig}",
            self.secret
        ))

    def test_whatsapp_tampered_payload(self):
        """Test that a modified payload with original signature is rejected"""
        tampered_payload = self.payload + b" "
        self.assertFalse(verify_whatsapp_webhook_signature(
            tampered_payload,
            f"sha256={self.valid_signature}",
            self.secret
        ))
        
    def test_whatsapp_wrong_secret(self):
        """Test that validating with the wrong secret fails"""
        wrong_secret = "wrong_secret"
        self.assertFalse(verify_whatsapp_webhook_signature(
            self.payload,
            f"sha256={self.valid_signature}",
            wrong_secret
        ))

    def test_n8n_validation(self):
        """Test n8n signature validation"""
        # n8n uses X-n8n-signature, usually no prefix, but logic is similar HMAC SHA256
        self.assertTrue(verify_n8n_webhook_signature(
            self.payload,
            self.valid_signature,
            self.secret
        ))

if __name__ == '__main__':
    unittest.main()
