#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for structured logging with correlation IDs
Verifies that logs include request IDs and are properly formatted
"""

import os
import sys
import json
import io
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))

def capture_log_output(func):
    """Capture log output to string"""
    f = io.StringIO()
    with redirect_stdout(f):
        func()
    return f.getvalue()


def test_correlation_ids_in_logs():
    """Test that correlation IDs appear in structured logs"""
    print("\n" + "="*80)
    print("Correlation ID Logging Test")
    print("="*80)
    
    try:
        from utils.structured_logger import get_structured_logger
        from utils.request_tracking import set_request_context, clear_request_context
        
        logger = get_structured_logger("test_correlation")
        
        # Test without request context
        print("\n1. Testing logs without request context:")
        output = capture_log_output(
            lambda: logger.info("Test message without context", test_field="value1")
        )
        log_entry = json.loads(output.strip())
        assert 'request_id' not in log_entry or log_entry.get('request_id') is None, \
            "Log without context should not have request_id"
        print("✅ Log without context works correctly")
        
        # Test with request context
        print("\n2. Testing logs with request context:")
        set_request_context("test-request-123", "test-client-456")
        
        output = capture_log_output(
            lambda: logger.info("Test message with context", test_field="value2")
        )
        log_entry = json.loads(output.strip())
        
        assert log_entry.get('request_id') == "test-request-123", \
            "Log should include request_id from context"
        assert log_entry.get('client_request_id') == "test-client-456", \
            "Log should include client_request_id from context"
        print("✅ Log with context includes correlation IDs")
        print(f"   Request ID: {log_entry.get('request_id')}")
        print(f"   Client Request ID: {log_entry.get('client_request_id')}")
        
        # Test OpenAI-specific logging
        print("\n3. Testing OpenAI request logging:")
        output = capture_log_output(
            lambda: logger.log_openai_request(
                model="gpt-4o-mini",
                provider="openai",
                prompt_length=100,
                system_prompt_length=50,
                request_id="test-request-123",
                client_request_id="test-client-456"
            )
        )
        log_entry = json.loads(output.strip())
        
        assert log_entry.get('event_type') == 'openai_request', \
            "Should have event_type for OpenAI request"
        assert log_entry.get('model') == 'gpt-4o-mini', \
            "Should include model name"
        assert log_entry.get('request_id') == "test-request-123", \
            "Should include request_id"
        print("✅ OpenAI request logging includes all fields")
        print(f"   Event type: {log_entry.get('event_type')}")
        print(f"   Model: {log_entry.get('model')}")
        print(f"   Provider: {log_entry.get('provider')}")
        
        # Test OpenAI response logging
        print("\n4. Testing OpenAI response logging:")
        output = capture_log_output(
            lambda: logger.log_openai_response(
                model="gpt-4o-mini",
                provider="openai",
                tokens_input=150,
                tokens_output=50,
                response_time=1.5,
                cost=0.001,
                request_id="test-request-123",
                client_request_id="test-client-456",
                openai_request_id="openai-req-789",
                rate_limit_info={"requests_remaining": 100}
            )
        )
        log_entry = json.loads(output.strip())
        
        assert log_entry.get('event_type') == 'openai_response', \
            "Should have event_type for OpenAI response"
        assert log_entry.get('tokens_input') == 150, \
            "Should include tokens_input"
        assert log_entry.get('openai_request_id') == "openai-req-789", \
            "Should include OpenAI request ID"
        assert 'rate_limit' in log_entry, \
            "Should include rate limit info"
        print("✅ OpenAI response logging includes all fields")
        print(f"   Tokens: {log_entry.get('tokens_input')} in, {log_entry.get('tokens_output')} out")
        print(f"   Cost: ${log_entry.get('cost')}")
        print(f"   OpenAI Request ID: {log_entry.get('openai_request_id')}")
        
        clear_request_context()
        print("\n✅ All correlation ID logging tests passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Correlation ID logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_format_consistency():
    """Test that all logs follow consistent JSON format"""
    print("\n" + "="*80)
    print("Log Format Consistency Test")
    print("="*80)
    
    try:
        from utils.structured_logger import get_structured_logger
        from utils.request_tracking import set_request_context
        
        logger = get_structured_logger("test_format")
        set_request_context("format-test-123", "format-client-456")
        
        log_types = [
            ("debug", lambda: logger.debug("Debug message")),
            ("info", lambda: logger.info("Info message")),
            ("warning", lambda: logger.warning("Warning message")),
            ("error", lambda: logger.error("Error message")),
        ]
        
        required_fields = ['timestamp', 'level', 'logger', 'message']
        
        for log_type, log_func in log_types:
            output = capture_log_output(log_func)
            log_entry = json.loads(output.strip())
            
            # Check required fields
            for field in required_fields:
                assert field in log_entry, \
                    f"{log_type} log should have {field} field"
            
            # Check JSON is valid
            assert isinstance(log_entry, dict), \
                "Log entry should be a dictionary"
            
            print(f"✅ {log_type.capitalize()} log format is valid")
        
        print("\n✅ All log formats are consistent")
        return True
        
    except Exception as e:
        print(f"\n❌ Log format consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_logging():
    """Test end-to-end logging through model integrator"""
    print("\n" + "="*80)
    print("End-to-End Logging Test")
    print("="*80)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set, skipping end-to-end test")
        return True
    
    try:
        from model_integrator import get_model_integrator
        from utils.request_tracking import get_request_tracker
        
        integrator = get_model_integrator()
        tracker = get_request_tracker()
        
        print("Making API call and checking logs...")
        
        # Create request metadata
        metadata = tracker.create_request_metadata(
            client_request_id="e2e-test-123",
            model="gpt-4o-mini",
            provider="openai"
        )
        
        # Make API call
        response = integrator.generate(
            prompt="Say 'test' in one word.",
            client_request_id=metadata.client_request_id,
            max_tokens=10
        )
        
        # Verify request was tracked
        retrieved = tracker.get_request(metadata.request_id)
        assert retrieved is not None, "Request should be tracked"
        assert retrieved.status == "completed" or retrieved.status == "failed", \
            "Request should have status"
        
        print("✅ Request tracking works end-to-end")
        print(f"   Request ID: {metadata.request_id}")
        print(f"   Status: {retrieved.status}")
        if retrieved.response_time:
            print(f"   Response time: {retrieved.response_time:.2f}s")
        
        # Verify response includes request IDs
        assert response.get('request_id') == metadata.request_id, \
            "Response should include request_id"
        
        print("✅ Response includes request tracking information")
        
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-end logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Structured Logging Test Suite")
    print("="*80)
    
    results = []
    results.append(("Correlation IDs", test_correlation_ids_in_logs()))
    results.append(("Format Consistency", test_log_format_consistency()))
    results.append(("End-to-End", test_end_to_end_logging()))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

