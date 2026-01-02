#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the Unified Model Integrator
Run this to verify your API keys and model configurations
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_model_integrator():
    """Test the model integrator with all providers"""
    print("=" * 60)
    print("Testing Unified Model Integrator")
    print("=" * 60)
    
    try:
        from model_integrator import get_model_integrator
        
        # Get integrator
        print("\n1. Initializing model integrator...")
        integrator = get_model_integrator()
        
        # List available models
        print("\n2. Available models:")
        models = integrator.list_available_models()
        if not models:
            print("   ⚠️  No models configured!")
            print("\n   Please set API keys in your .env file:")
            print("   - OPENAI_API_KEY")
            print("   - GROQ_API_KEY")
            print("   - GEMINI_API_KEY")
            return False
        
        enabled_models = [m for m in models if m['enabled']]
        print(f"   ✓ Found {len(enabled_models)} enabled model(s):")
        for model in enabled_models:
            print(f"     - {model['provider']}: {model['model_name']}")
            print(f"       Cost: ${model['cost_input_per_1k']:.6f}/1k input, ${model['cost_output_per_1k']:.6f}/1k output")
            print(f"       Speed: {model['speed_rating']}/10, Quality: {model['quality_rating']}/10")
        
        # Test generation
        print("\n3. Testing model generation...")
        test_prompt = "Hello! Can you help me with a quote for insulation?"
        system_prompt = "You are a helpful assistant for BMC Uruguay, a company that sells thermal insulation products."
        
        print(f"   Prompt: {test_prompt}")
        print("   Generating response...")
        
        response = integrator.generate(
            prompt=test_prompt,
            system_prompt=system_prompt,
            max_tokens=200
        )
        
        if response.get("success"):
            print(f"\n   ✓ Success!")
            print(f"   Model used: {response['model_used']}")
            print(f"   Provider: {response['provider']}")
            print(f"   Response time: {response['response_time']:.2f}s")
            print(f"   Tokens: {response['tokens_input']} input + {response['tokens_output']} output = {response['total_tokens']} total")
            print(f"   Cost: ${response['cost']:.6f}")
            print(f"\n   Response preview:")
            print(f"   {response['content'][:200]}...")
        else:
            print(f"\n   ✗ Error: {response.get('error', 'Unknown error')}")
            return False
        
        # Show usage summary
        print("\n4. Usage summary:")
        summary = integrator.get_usage_summary()
        print(f"   Total requests: {summary['total_requests']}")
        print(f"   Total tokens: {summary['total_tokens']:,}")
        print(f"   Total cost: ${summary['total_cost']:.6f}")
        
        # Save stats
        integrator.save_usage_stats()
        print("\n5. Usage statistics saved to model_usage_stats.json")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        print("\nPlease install required packages:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_model_integrator()
    sys.exit(0 if success else 1)

