#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Grok (xAI) integration
"""

import os
from dotenv import load_dotenv
from model_integrator import get_model_integrator

# Load environment variables
load_dotenv()

def test_grok_integration():
    """Test Grok integration with the model integrator"""
    print("=" * 60)
    print("Testing Grok (xAI) Integration")
    print("=" * 60)
    
    # Initialize integrator
    integrator = get_model_integrator()
    
    # List available models
    print("\n📋 Available Models:")
    print("-" * 60)
    models = integrator.list_available_models()
    for model in models:
        if model["provider"] == "grok":
            print(f"✅ {model['model_id']}: {model['model_name']} (Provider: {model['provider']})")
            print(f"   Speed: {model['speed_rating']}/10, Quality: {model['quality_rating']}/10")
    
    # Test with Grok
    print("\n🧪 Testing Grok API...")
    print("-" * 60)
    
    try:
        # Test with grok-4-latest (from your curl example)
        response = integrator.generate(
            prompt="Testing. Just say hi and hello world and nothing else.",
            system_prompt="You are a test assistant.",
            model_id="grok_grok-4-latest",  # Use specific model
            temperature=0,
            max_tokens=100
        )
        
        print(f"✅ Success!")
        print(f"Model used: {response['model_used']}")
        print(f"Provider: {response['provider']}")
        print(f"Response: {response['content']}")
        print(f"Tokens: {response['tokens_input']} input + {response['tokens_output']} output = {response['total_tokens']} total")
        print(f"Cost: ${response['cost']:.6f}")
        print(f"Response time: {response['response_time']:.2f}s")
        
        # Test auto-selection with balanced strategy
        print("\n🧪 Testing auto-selection (balanced strategy)...")
        print("-" * 60)
        
        response2 = integrator.generate(
            prompt="Write a Python function to calculate fibonacci numbers",
            system_prompt="You are a helpful coding assistant",
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"✅ Auto-selected model: {response2['model_used']}")
        print(f"Provider: {response2['provider']}")
        print(f"Response preview: {response2['content'][:200]}...")
        print(f"Tokens: {response2['total_tokens']}, Cost: ${response2['cost']:.6f}, Time: {response2['response_time']:.2f}s")
        
        # Show usage summary
        print("\n📊 Usage Summary:")
        print("-" * 60)
        summary = integrator.get_usage_summary()
        print(f"Total requests: {summary['total_requests']}")
        print(f"Total tokens: {summary['total_tokens']}")
        print(f"Total cost: ${summary['total_cost']:.6f}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GROK_API_KEY"):
        print("⚠️  Warning: GROK_API_KEY not found in environment")
        print("Please set it in your .env file:")
        print("GROK_API_KEY=xai-your-api-key-here")
    else:
        test_grok_integration()

