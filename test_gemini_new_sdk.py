#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for Gemini New SDK Integration
Tests gemini-2.5-flash, gemini-1.5-pro, and gemini-3-pro
"""

import os
import sys
from dotenv import load_dotenv

# Force reload environment
load_dotenv(override=True)

# Clear cached instance
if 'model_integrator' in sys.modules:
    import model_integrator
    model_integrator._integrator_instance = None

from model_integrator import get_model_integrator

print("=" * 70)
print("Gemini New SDK Integration Test Suite")
print("=" * 70)

# Check if API key is set
if not os.getenv("GEMINI_API_KEY"):
    print("\n❌ GEMINI_API_KEY not found in .env")
    print("\n💡 To set up Gemini:")
    print("   1. Get API key from: https://makersuite.google.com/app/apikey")
    print("   2. Add to .env: GEMINI_API_KEY=your-key-here")
    sys.exit(1)

# Initialize integrator
integrator = get_model_integrator()

# Check SDK version being used
use_new_sdk = getattr(integrator, 'gemini_use_new_sdk', False)
print(f"\n📦 SDK Version: {'New (google-genai)' if use_new_sdk else 'Old (google-generativeai)'}")

# List available Gemini models
print("\n📋 Available Gemini Models:")
print("-" * 70)
models = integrator.list_available_models()
gemini_models = [m for m in models if m["provider"] == "gemini"]

if not gemini_models:
    print("  ❌ No Gemini models found")
    print("\n💡 Check:")
    print("   - GEMINI_API_KEY is set correctly")
    print("   - google-genai or google-generativeai package is installed")
    sys.exit(1)

for model in gemini_models:
    status = "🟢" if model['enabled'] else "🔴"
    print(f"  {status} {model['model_id']}: {model['model_name']}")
    print(f"     Speed: {model['speed_rating']}/10, Quality: {model['quality_rating']}/10")
    print(f"     Cost: ${model['cost_input_per_1k']:.6f} input / ${model['cost_output_per_1k']:.6f} output per 1K tokens")

# Test each Gemini model
print("\n🧪 Testing Each Gemini Model:")
print("=" * 70)

test_cases = [
    {
        "name": "Simple Question",
        "prompt": "What is Python? Answer in one sentence.",
        "system_prompt": "You are a helpful assistant.",
        "max_tokens": 50
    },
    {
        "name": "Code Generation",
        "prompt": "Write a Python function to calculate factorial.",
        "system_prompt": "You are a coding assistant.",
        "max_tokens": 200
    },
    {
        "name": "Spanish Response",
        "prompt": "Explica qué es Python en una frase.",
        "system_prompt": "Eres un asistente útil.",
        "max_tokens": 50
    }
]

results = {}

for model_info in gemini_models:
    if not model_info['enabled']:
        continue
    
    model_id = model_info['model_id']
    model_name = model_info['model_name']
    
    print(f"\n🔍 Testing {model_name} ({model_id})...")
    print("-" * 70)
    
    model_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {test_case['name']}")
        try:
            response = integrator.generate(
                prompt=test_case['prompt'],
                system_prompt=test_case['system_prompt'],
                model_id=model_id,
                temperature=0.7,
                max_tokens=test_case['max_tokens']
            )
            
            if response['success']:
                print(f"    ✅ Success")
                print(f"    📝 Response: {response['content'][:100]}...")
                print(f"    📊 Tokens: {response['tokens_input']} input + {response['tokens_output']} output = {response['total_tokens']} total")
                print(f"    💰 Cost: ${response['cost']:.6f}")
                print(f"    ⏱️  Time: {response['response_time']:.2f}s")
                
                model_results.append({
                    "test": test_case['name'],
                    "success": True,
                    "tokens": response['total_tokens'],
                    "cost": response['cost'],
                    "time": response['response_time']
                })
            else:
                print(f"    ❌ Failed: {response.get('error', 'Unknown error')}")
                model_results.append({
                    "test": test_case['name'],
                    "success": False,
                    "error": response.get('error', 'Unknown error')
                })
        except Exception as e:
            print(f"    ❌ Exception: {str(e)[:100]}")
            model_results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    results[model_name] = model_results

# Summary
print("\n" + "=" * 70)
print("📊 Test Summary")
print("=" * 70)

for model_name, model_results in results.items():
    print(f"\n{model_name}:")
    successful = sum(1 for r in model_results if r['success'])
    total = len(model_results)
    print(f"  Tests passed: {successful}/{total}")
    
    if successful > 0:
        avg_tokens = sum(r['tokens'] for r in model_results if r['success']) / successful
        avg_cost = sum(r['cost'] for r in model_results if r['success']) / successful
        avg_time = sum(r['time'] for r in model_results if r['success']) / successful
        print(f"  Avg tokens: {avg_tokens:.0f}")
        print(f"  Avg cost: ${avg_cost:.6f}")
        print(f"  Avg time: {avg_time:.2f}s")

# Test SDK fallback
print("\n" + "=" * 70)
print("🔄 Testing SDK Fallback")
print("=" * 70)

print("\nTesting error handling and fallback...")
try:
    # Try with invalid model to test error handling
    response = integrator.generate(
        prompt="Test",
        model_id="gemini_invalid-model",
        max_tokens=10
    )
    if not response['success']:
        print("✅ Error handling works correctly")
    else:
        print("⚠️  Unexpected success with invalid model")
except Exception as e:
    print(f"✅ Exception handling works: {type(e).__name__}")

# Test token counting accuracy
print("\n" + "=" * 70)
print("🔢 Testing Token Counting Accuracy")
print("=" * 70)

if gemini_models:
    test_model = gemini_models[0]['model_id']
    print(f"\nTesting with {test_model}...")
    
    test_prompt = "Count the tokens in this message: " + "word " * 20
    response = integrator.generate(
        prompt=test_prompt,
        model_id=test_model,
        max_tokens=50
    )
    
    if response['success']:
        estimated = len(test_prompt) // 4
        actual = response['tokens_input']
        print(f"  Estimated tokens: {estimated}")
        print(f"  Actual tokens: {actual}")
        if actual > 0:
            diff = abs(estimated - actual) / actual * 100
            print(f"  Difference: {diff:.1f}%")
            if diff < 50:
                print("  ✅ Token counting appears accurate")
            else:
                print("  ⚠️  Token counting may need adjustment")

print("\n" + "=" * 70)
print("✅ Test Suite Complete")
print("=" * 70)


