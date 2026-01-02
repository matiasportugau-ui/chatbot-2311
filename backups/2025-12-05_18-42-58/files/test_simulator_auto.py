#!/usr/bin/env python3
"""
Automated test script for simulator
Tests the complete flow without interactive input
"""

import sys
import time

import requests

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_chat_process(message, expected_type=None):
    """Test chat process endpoint"""
    print(f"\n💬 Testing message: '{message}'")
    try:
        response = requests.post(
            f"{API_URL}/chat/process",
            json={"mensaje": message, "telefono": "+59891234567", "sesionId": "test_session_123"},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Response received")
            print(f"   Message: {data.get('mensaje', '')[:100]}...")
            print(f"   Type: {data.get('tipo', 'unknown')}")
            print(f"   Confidence: {data.get('confianza', 0):.2%}")

            if expected_type and data.get("tipo") != expected_type:
                print(f"⚠️  Expected type '{expected_type}', got '{data.get('tipo')}'")

            return True, data
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None


def test_conversation_flow():
    """Test complete conversation flow"""
    print("\n" + "=" * 70)
    print("🧪 Testing Complete Conversation Flow")
    print("=" * 70)

    messages = [
        ("Hola", "informacion"),
        ("Quiero cotizar Isodec", "cotizacion"),
        ("10 metros por 5 metros", "cotizacion"),
        ("100mm", "cotizacion"),
        ("Blanco", "cotizacion"),
    ]

    results = []
    for message, expected_type in messages:
        success, data = test_chat_process(message, expected_type)
        results.append((success, message))
        time.sleep(1)  # Small delay between messages

    return results


def main():
    """Main test function"""
    print("=" * 70)
    print("🚀 Automated Simulator Test")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print()

    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed. Is the API server running?")
        print("   Start it with: python api_server.py")
        return 1

    # Test 2: Single message
    print("\n" + "=" * 70)
    print("📝 Test 1: Single Message")
    print("=" * 70)
    success, _ = test_chat_process("Hola")

    if not success:
        print("\n❌ Single message test failed")
        return 1

    # Test 3: Conversation flow
    print("\n" + "=" * 70)
    print("📝 Test 2: Conversation Flow")
    print("=" * 70)
    results = test_conversation_flow()

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)

    passed = sum(1 for success, _ in results if success)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
