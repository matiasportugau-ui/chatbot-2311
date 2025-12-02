#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test all integrated providers: Grok, Gemini, OpenAI, Groq"""

import os
import sys
from dotenv import load_dotenv

# Force reload
load_dotenv(override=True)

# Clear cached instance
if 'model_integrator' in sys.modules:
    import model_integrator
    model_integrator._integrator_instance = None

from model_integrator import get_model_integrator

print("=" * 60)
print("Multi-Provider Integration Test")
print("=" * 60)

integrator = get_model_integrator()
models = integrator.list_available_models()

# Group by provider
providers = {}
for m in models:
    provider = m['provider']
    if provider not in providers:
        providers[provider] = []
    providers[provider].append(m)

print("\n📋 Available Providers & Models:")
print("-" * 60)
for provider, model_list in providers.items():
    print(f"\n✅ {provider.upper()} ({len(model_list)} model(s)):")
    for m in model_list:
        status = "🟢" if m['enabled'] else "🔴"
        print(f"   {status} {m['model_id']}: {m['model_name']}")

# Test each provider
print("\n🧪 Testing Each Provider:")
print("-" * 60)

test_prompt = "Responde brevemente: ¿Qué modelo de IA eres?"

# Check Gemini SDK version
if "gemini" in providers:
    use_new_sdk = getattr(integrator, 'gemini_use_new_sdk', False)
    print(f"\n📦 Gemini SDK: {'New (google-genai)' if use_new_sdk else 'Old (google-generativeai)'}")

for provider in providers.keys():
    provider_models = [m for m in providers[provider] if m['enabled']]
    if not provider_models:
        print(f"\n⏭️  {provider.upper()}: No enabled models")
        continue
    
    # For Gemini, prefer newer models
    if provider == "gemini":
        # Prefer gemini-2.5-flash, then gemini-1.5-pro, then others
        preferred = [m for m in provider_models if '2.5-flash' in m['model_id']]
        if not preferred:
            preferred = [m for m in provider_models if '1.5-pro' in m['model_id']]
        if preferred:
            test_model = preferred[0]['model_id']
        else:
            test_model = provider_models[0]['model_id']
    else:
        test_model = provider_models[0]['model_id']
    
    print(f"\n🔍 Testing {provider.upper()} with {test_model}...")
    
    try:
        response = integrator.generate(
            prompt=test_prompt,
            model_id=test_model,
            max_tokens=100
        )
        
        if response['success']:
            print(f"   ✅ Success!")
            print(f"   📝 Response: {response['content'][:80]}...")
            print(f"   📊 Tokens: {response['total_tokens']}, Cost: ${response['cost']:.6f}, Time: {response['response_time']:.2f}s")
        else:
            print(f"   ❌ Error: {response.get('error', 'Unknown')[:80]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)[:80]}")

# Summary
print("\n📊 Summary:")
print("-" * 60)
stats = integrator.get_usage_summary()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.6f}")

print("\n✅ Integration test complete!")
print("=" * 60)

