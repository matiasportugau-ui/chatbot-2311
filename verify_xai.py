#!/usr/bin/env python3
"""
Script to verify xAI API connectivity.
"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_xai_connection():
    api_key = os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("xai-"):
        print("Using xAI key found in environment.")
    elif api_key and api_key.startswith("sk-") and not os.getenv("XAI_API_KEY"):
        print("Warning: Using OpenAI key format (sk-...) but testing xAI. This might fail if not using a proxy or if XAI_API_KEY is not set.")
    base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
    model = os.getenv("XAI_MODEL", "grok-beta") # Or gork-4

    print(f"Testing xAI Connection...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")

    if not api_key:
        print("Error: XAI_API_KEY environment variable not set.")
        print("Please export XAI_API_KEY='your-key-here'")
        return

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you Grok?"},
            ],
        )

        print("\nSuccess! Response from xAI:")
        print("-" * 20)
        print(response.choices[0].message.content)
        print("-" * 20)

    except Exception as e:
        print(f"\nFailed to connect/generate: {e}")

if __name__ == "__main__":
    test_xai_connection()
