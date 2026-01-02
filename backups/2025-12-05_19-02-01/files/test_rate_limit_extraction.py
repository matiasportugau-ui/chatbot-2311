#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script specifically for rate limit header extraction
Verifies that rate limit headers are correctly parsed and monitored
"""

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

def test_rate_limit_header_extraction():
    """Test extraction of rate limit headers from OpenAI responses"""
    print("\n" + "="*80)
    print("Rate Limit Header Extraction Test")
    print("="*80)
    
    try:
        from utils.rate_limit_monitor import get_rate_limit_monitor
        
        monitor = get_rate_limit_monitor()
        
        # Simulate various header scenarios
        test_cases = [
            {
                "name": "Full headers with reset timestamps",
                "headers": {
                    "x-ratelimit-limit-requests": "100",
                    "x-ratelimit-remaining-requests": "75",
                    "x-ratelimit-reset-requests": str(int(time.time()) + 3600),
                    "x-ratelimit-limit-tokens": "100000",
                    "x-ratelimit-remaining-tokens": "50000",
                    "x-ratelimit-reset-tokens": str(int(time.time()) + 3600),
                }
            },
            {
                "name": "Headers without reset timestamps",
                "headers": {
                    "x-ratelimit-limit-requests": "200",
                    "x-ratelimit-remaining-requests": "150",
                    "x-ratelimit-limit-tokens": "200000",
                    "x-ratelimit-remaining-tokens": "100000",
                }
            },
            {
                "name": "Partial headers (only requests)",
                "headers": {
                    "x-ratelimit-limit-requests": "50",
                    "x-ratelimit-remaining-requests": "25",
                    "x-ratelimit-reset-requests": str(int(time.time()) + 1800),
                }
            },
            {
                "name": "Low remaining (should trigger warning)",
                "headers": {
                    "x-ratelimit-limit-requests": "100",
                    "x-ratelimit-remaining-requests": "10",  # 90% used
                    "x-ratelimit-reset-requests": str(int(time.time()) + 3600),
                    "x-ratelimit-limit-tokens": "100000",
                    "x-ratelimit-remaining-tokens": "5000",  # 95% used
                    "x-ratelimit-reset-tokens": str(int(time.time()) + 3600),
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['name']}")
            print("-" * 80)
            
            # Update rate limits
            rate_limits = monitor.update_from_headers(
                test_case['headers'],
                provider="openai",
                organization=f"org-test-{i}"
            )
            
            # Extract info
            info = monitor.extract_rate_limit_info(test_case['headers'])
            
            # Display results
            print(f"Requests: {rate_limits.requests.remaining}/{rate_limits.requests.limit}")
            if rate_limits.requests.reset_timestamp:
                time_until_reset = rate_limits.requests.time_until_reset()
                print(f"  Reset in: {time_until_reset:.0f} seconds")
            
            print(f"Tokens: {rate_limits.tokens.remaining}/{rate_limits.tokens.limit}")
            if rate_limits.tokens.reset_timestamp:
                time_until_reset = rate_limits.tokens.time_until_reset()
                print(f"  Reset in: {time_until_reset:.0f} seconds")
            
            # Check utilization
            requests_util = rate_limits.requests.utilization_percent()
            tokens_util = rate_limits.tokens.utilization_percent()
            if requests_util is not None:
                print(f"Requests utilization: {requests_util:.1f}%")
            if tokens_util is not None:
                print(f"Tokens utilization: {tokens_util:.1f}%")
            
            # Check warnings
            warnings = monitor.check_warnings("openai", f"org-test-{i}")
            if warnings:
                print("⚠️  Warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
            else:
                print("✅ No warnings")
            
            # Verify extraction
            assert 'requests_limit' in info or 'requests_remaining' in info, \
                "Should extract at least one requests field"
            print("✅ Header extraction verified")
        
        print("\n" + "="*80)
        print("✅ All rate limit header extraction tests passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Rate limit header extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_api_call_headers():
    """Test with actual OpenAI API call to verify header extraction"""
    print("\n" + "="*80)
    print("Real API Call Header Extraction Test")
    print("="*80)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set, skipping real API test")
        return True
    
    try:
        from model_integrator import get_model_integrator
        from utils.rate_limit_monitor import get_rate_limit_monitor
        
        integrator = get_model_integrator()
        monitor = get_rate_limit_monitor()
        
        print("Making API call to OpenAI...")
        response = integrator.generate(
            prompt="Say 'test' in one word.",
            max_tokens=10
        )
        
        if response.get('success'):
            print("✅ API call successful")
            
            # Check if rate limit info was captured
            rate_limit_info = response.get('rate_limit_info')
            if rate_limit_info:
                print("\n📊 Rate Limit Information Captured:")
                print(f"   Requests remaining: {rate_limit_info.get('requests_remaining', 'N/A')}")
                print(f"   Tokens remaining: {rate_limit_info.get('tokens_remaining', 'N/A')}")
                if 'requests_time_until_reset' in rate_limit_info:
                    print(f"   Requests reset in: {rate_limit_info['requests_time_until_reset']:.0f}s")
                if 'tokens_time_until_reset' in rate_limit_info:
                    print(f"   Tokens reset in: {rate_limit_info['tokens_time_until_reset']:.0f}s")
            else:
                print("⚠️  Rate limit info not captured (headers may not be available)")
            
            # Check OpenAI request ID
            openai_request_id = response.get('openai_request_id')
            if openai_request_id:
                print(f"✅ OpenAI Request ID captured: {openai_request_id}")
            else:
                print("⚠️  OpenAI Request ID not captured")
            
            # Check request IDs
            request_id = response.get('request_id')
            client_request_id = response.get('client_request_id')
            print(f"✅ Request ID: {request_id}")
            if client_request_id:
                print(f"✅ Client Request ID: {client_request_id}")
            
            return True
        else:
            print(f"❌ API call failed: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Real API call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Rate Limit Header Extraction Test Suite")
    print("="*80)
    print(f"Started at: {datetime.now().isoformat()}")
    
    results = []
    results.append(("Header Extraction", test_rate_limit_header_extraction()))
    results.append(("Real API Call", test_real_api_call_headers()))
    
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

