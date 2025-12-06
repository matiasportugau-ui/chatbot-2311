#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test of Grok integration"""

from model_integrator import get_model_integrator

integrator = get_model_integrator()

response = integrator.generate(
    prompt="hola estas usando grok? ",
    model_id="grok_grok-4-latest"
)

print("=" * 60)
print("Grok Integration Test")
print("=" * 60)
print(f"\n✅ Model used: {response['model_used']}")
print(f"✅ Provider: {response['provider']}")
print(f"✅ Success: {response['success']}")
print(f"\n📝 Response:")
print("-" * 60)
print(response['content'])
print("-" * 60)
print(f"\n📊 Stats:")
print(f"   Tokens: {response['tokens_input']} input + {response['tokens_output']} output = {response['total_tokens']} total")
print(f"   Cost: ${response['cost']:.6f}")
print(f"   Time: {response['response_time']:.2f}s")
print("=" * 60)

