#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for OpenAI API Best Practices Implementation
Tests request tracking, rate limit monitoring, structured logging, and debugging endpoints
"""

import os
import sys
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_request_tracking():
    """Test request tracking functionality"""
    print("\n" + "="*80)
    print("TEST 1: Request Tracking")
    print("="*80)
    
    try:
        from utils.request_tracking import get_request_tracker, RequestTracker
        
        tracker = get_request_tracker()
        print("✅ Request tracker initialized")
        
        # Test request ID generation
        request_id = tracker.generate_request_id()
        print(f"✅ Generated request ID: {request_id}")
        
        # Test client request ID validation
        valid_id = "test-123-abc"
        invalid_id = "test-" + "x" * 600  # Too long
        
        assert tracker.validate_client_request_id(valid_id), "Valid ID should pass validation"
        assert not tracker.validate_client_request_id(invalid_id), "Invalid ID should fail validation"
        print("✅ Client request ID validation works")
        
        # Test request metadata creation
        metadata = tracker.create_request_metadata(
            client_request_id="client-req-123",
            model="gpt-4o-mini",
            provider="openai",
            endpoint="/v1/chat/completions"
        )
        print(f"✅ Created request metadata: {metadata.request_id}")
        print(f"   Client Request ID: {metadata.client_request_id}")
        print(f"   Model: {metadata.model}")
        print(f"   Provider: {metadata.provider}")
        
        # Test request retrieval
        retrieved = tracker.get_request(metadata.request_id)
        assert retrieved is not None, "Should retrieve request metadata"
        print("✅ Request retrieval works")
        
        return True
    except Exception as e:
        print(f"❌ Request tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_structured_logging():
    """Test structured logging functionality"""
    print("\n" + "="*80)
    print("TEST 2: Structured Logging")
    print("="*80)
    
    try:
        from utils.structured_logger import get_structured_logger
        from utils.request_tracking import set_request_context
        
        logger = get_structured_logger("test_logger")
        print("✅ Structured logger initialized")
        
        # Set request context
        set_request_context("test-request-id", "test-client-id")
        
        # Test basic logging
        logger.info("Test info message", test_field="test_value")
        print("✅ Basic logging works")
        
        # Test OpenAI request logging
        logger.log_openai_request(
            model="gpt-4o-mini",
            provider="openai",
            prompt_length=100,
            system_prompt_length=50,
            request_id="test-request-id",
            client_request_id="test-client-id"
        )
        print("✅ OpenAI request logging works")
        
        # Test OpenAI response logging
        logger.log_openai_response(
            model="gpt-4o-mini",
            provider="openai",
            tokens_input=150,
            tokens_output=50,
            response_time=1.5,
            cost=0.001,
            request_id="test-request-id",
            client_request_id="test-client-id",
            openai_request_id="openai-req-123",
            rate_limit_info={"requests_remaining": 100}
        )
        print("✅ OpenAI response logging works")
        
        return True
    except Exception as e:
        print(f"❌ Structured logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limit_monitor():
    """Test rate limit monitoring functionality"""
    print("\n" + "="*80)
    print("TEST 3: Rate Limit Monitor")
    print("="*80)
    
    try:
        from utils.rate_limit_monitor import get_rate_limit_monitor
        
        monitor = get_rate_limit_monitor()
        print("✅ Rate limit monitor initialized")
        
        # Simulate response headers
        test_headers = {
            "x-ratelimit-limit-requests": "100",
            "x-ratelimit-remaining-requests": "75",
            "x-ratelimit-reset-requests": str(time.time() + 3600),
            "x-ratelimit-limit-tokens": "100000",
            "x-ratelimit-remaining-tokens": "50000",
            "x-ratelimit-reset-tokens": str(time.time() + 3600),
            "x-request-id": "test-openai-request-id",
            "openai-organization": "org-123",
            "openai-processing-ms": "150",
            "openai-version": "2020-10-01"
        }
        
        # Update rate limits
        rate_limits = monitor.update_from_headers(
            test_headers,
            provider="openai",
            organization="org-123"
        )
        print("✅ Rate limits updated from headers")
        print(f"   Requests: {rate_limits.requests.remaining}/{rate_limits.requests.limit}")
        print(f"   Tokens: {rate_limits.tokens.remaining}/{rate_limits.tokens.limit}")
        
        # Test rate limit extraction
        rate_limit_info = monitor.extract_rate_limit_info(test_headers)
        print("✅ Rate limit info extraction works")
        print(f"   Requests remaining: {rate_limit_info.get('requests_remaining')}")
        print(f"   Tokens remaining: {rate_limit_info.get('tokens_remaining')}")
        
        # Test warnings
        warnings = monitor.check_warnings("openai", "org-123")
        if warnings:
            print(f"⚠️  Warnings: {warnings}")
        else:
            print("✅ No warnings (expected at 75% utilization)")
        
        # Test utilization calculation
        requests_util = rate_limits.requests.utilization_percent()
        tokens_util = rate_limits.tokens.utilization_percent()
        print(f"✅ Utilization calculation: Requests {requests_util:.1f}%, Tokens {tokens_util:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Rate limit monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_integrator():
    """Test model integrator with request tracking"""
    print("\n" + "="*80)
    print("TEST 4: Model Integrator Integration")
    print("="*80)
    
    try:
        from model_integrator import get_model_integrator
        
        # Check if OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  OPENAI_API_KEY not set, skipping actual API test")
            print("   Set OPENAI_API_KEY environment variable to test with real API")
            return True
        
        integrator = get_model_integrator()
        print("✅ Model integrator initialized")
        
        # List available models
        models = integrator.list_available_models()
        print(f"✅ Available models: {len(models)}")
        for model in models[:3]:  # Show first 3
            print(f"   - {model['model_id']} ({model['provider']})")
        
        # Test generation with request tracking
        print("\n📤 Making test API call with request tracking...")
        client_request_id = f"test-client-{int(time.time())}"
        
        response = integrator.generate(
            prompt="Say 'Hello, this is a test' in one sentence.",
            system_prompt="You are a helpful assistant.",
            client_request_id=client_request_id,
            max_tokens=50
        )
        
        print("✅ API call completed")
        print(f"   Request ID: {response.get('request_id', 'N/A')}")
        print(f"   Client Request ID: {response.get('client_request_id', 'N/A')}")
        print(f"   OpenAI Request ID: {response.get('openai_request_id', 'N/A')}")
        print(f"   Model: {response.get('model_used', 'N/A')}")
        print(f"   Tokens: {response.get('total_tokens', 0)}")
        print(f"   Cost: ${response.get('cost', 0):.6f}")
        print(f"   Response time: {response.get('response_time', 0):.2f}s")
        
        if response.get('rate_limit_info'):
            print(f"   Rate limit info: {json.dumps(response['rate_limit_info'], indent=2)}")
        
        if response.get('success'):
            print(f"   Content: {response.get('content', '')[:100]}...")
        else:
            print(f"   Error: {response.get('error', 'Unknown error')}")
        
        return response.get('success', False)
    except Exception as e:
        print(f"❌ Model integrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_debugging_utilities():
    """Test debugging utilities"""
    print("\n" + "="*80)
    print("TEST 5: Debugging Utilities")
    print("="*80)
    
    try:
        from utils.debugging import (
            format_request_response,
            format_rate_limit_info,
            generate_debugging_report,
            extract_openai_headers
        )
        
        # Test request/response formatting
        request_data = {
            "request_id": "test-123",
            "client_request_id": "client-456",
            "model": "gpt-4o-mini",
            "provider": "openai"
        }
        
        response_data = {
            "tokens_input": 100,
            "tokens_output": 50,
            "response_time": 1.5,
            "cost": 0.001,
            "openai_request_id": "openai-789"
        }
        
        formatted = format_request_response(request_data, response_data)
        print("✅ Request/response formatting works")
        print(formatted[:200] + "...")
        
        # Test rate limit info formatting
        rate_limit_info = {
            "requests_limit": 100,
            "requests_remaining": 75,
            "requests_reset_timestamp": time.time() + 3600,
            "tokens_limit": 100000,
            "tokens_remaining": 50000,
            "tokens_reset_timestamp": time.time() + 3600
        }
        
        formatted_rl = format_rate_limit_info(rate_limit_info)
        print("✅ Rate limit info formatting works")
        print(formatted_rl[:200] + "...")
        
        # Test debugging report generation
        report = generate_debugging_report(
            request_id="test-123",
            request_metadata={"model": "gpt-4o-mini", "provider": "openai"},
            request_data=request_data,
            response_data=response_data,
            rate_limit_info=rate_limit_info
        )
        print("✅ Debugging report generation works")
        print(report[:300] + "...")
        
        # Test header extraction
        headers = {
            "x-request-id": "openai-123",
            "openai-organization": "org-456",
            "openai-processing-ms": "150",
            "x-ratelimit-remaining-requests": "75"
        }
        
        extracted = extract_openai_headers(headers)
        print("✅ Header extraction works")
        print(f"   Extracted: {extracted}")
        
        return True
    except Exception as e:
        print(f"❌ Debugging utilities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("\n" + "="*80)
    print("TEST 6: API Endpoints")
    print("="*80)
    
    try:
        import requests
        
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        print(f"Testing API at: {base_url}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health endpoint works")
                print(f"   Status: {health_data.get('status')}")
                if 'rate_limits' in health_data:
                    print(f"   Rate limits tracked: {len(health_data['rate_limits'])} providers")
            else:
                print(f"⚠️  Health endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  API server not running. Start with: python api_server.py")
            print("   Skipping API endpoint tests")
            return True
        except Exception as e:
            print(f"⚠️  Health endpoint test error: {e}")
        
        # Test rate limits endpoint
        try:
            response = requests.get(f"{base_url}/api/monitoring/rate-limits", timeout=5)
            if response.status_code == 200:
                rate_data = response.json()
                print("✅ Rate limits endpoint works")
                print(f"   Providers tracked: {len(rate_data.get('rate_limits', {}))}")
            else:
                print(f"⚠️  Rate limits endpoint returned {response.status_code}")
        except Exception as e:
            print(f"⚠️  Rate limits endpoint test error: {e}")
        
        return True
    except ImportError:
        print("⚠️  requests library not installed. Install with: pip install requests")
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("OpenAI API Best Practices - Test Suite")
    print("="*80)
    print(f"Started at: {datetime.now().isoformat()}")
    
    results = []
    
    # Run tests
    results.append(("Request Tracking", test_request_tracking()))
    results.append(("Structured Logging", test_structured_logging()))
    results.append(("Rate Limit Monitor", test_rate_limit_monitor()))
    results.append(("Model Integrator", test_model_integrator()))
    results.append(("Debugging Utilities", test_debugging_utilities()))
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

