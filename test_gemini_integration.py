#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for Gemini integration"""

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

print("=" * 60)
print("Testing Gemini Integration")
print("=" * 60)

# Check if API key is set
if not os.getenv("GEMINI_API_KEY"):
    print("\n❌ GEMINI_API_KEY not found in .env")
    print("\n💡 To set up Gemini:")
    print("   1. Get API key from: https://makersuite.google.com/app/apikey")
    print("   2. Run: python3 setup_gemini.py")
    print("   3. Or add to .env: GEMINI_API_KEY=your-key-here")
    exit(1)

# Initialize integrator
integrator = get_model_integrator()

# List available models
print("\n📋 Available Gemini Models:")
print("-" * 60)
models = integrator.list_available_models()
gemini_models = [m for m in models if m["provider"] == "gemini"]

if not gemini_models:
    print("  ❌ No Gemini models found")
    print("\n💡 Check:")
    print("   - GEMINI_API_KEY is set correctly")
    print("   - google-generativeai package is installed: pip install google-generativeai")
    exit(1)

for model in gemini_models:
    print(f"  ✅ {model['model_id']}: {model['model_name']}")
    print(f"     Speed: {model['speed_rating']}/10, Quality: {model['quality_rating']}/10")

# Test with Gemini
print("\n🧪 Testing Gemini API...")
print("-" * 60)

try:
    # Test with gemini-1.5-flash (fastest)
    response = integrator.generate(
        prompt="Hola, ¿estás usando Gemini? Responde brevemente.",
        system_prompt="Eres un asistente útil",
        model_id="gemini_gemini-2.5-flash",
        temperature=0.7,
        max_tokens=200
    )
    
    print(f"\n✅ Success!")
    print(f"Model used: {response['model_used']}")
    print(f"Provider: {response['provider']}")
    print(f"\n📝 Response:")
    print("-" * 60)
    print(response['content'])
    print("-" * 60)
    print(f"\n📊 Stats:")
    print(f"   Tokens: {response['tokens_input']} input + {response['tokens_output']} output = {response['total_tokens']} total")
    print(f"   Cost: ${response['cost']:.6f}")
    print(f"   Response time: {response['response_time']:.2f}s")
    
    # Test auto-selection
    print("\n🧪 Testing auto-selection (balanced strategy)...")
    print("-" * 60)
    
    response2 = integrator.generate(
        prompt="Explica qué es Python en una frase",
        temperature=0.7,
        max_tokens=100
    )
    
    print(f"✅ Auto-selected model: {response2['model_used']}")
    print(f"Provider: {response2['provider']}")
    print(f"Response: {response2['content'][:100]}...")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Troubleshooting:")
    print("   - Verify API key is correct")
    print("   - Check internet connection")
    print("   - Ensure google-generativeai is installed: pip install google-generativeai")

print("=" * 60)

