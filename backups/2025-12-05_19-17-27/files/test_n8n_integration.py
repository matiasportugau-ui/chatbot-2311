#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test n8n API integration"""

import os
import sys
from dotenv import load_dotenv

# Force reload
load_dotenv(override=True)

from n8n_api_client import get_n8n_client

print("=" * 60)
print("n8n API Integration Test")
print("=" * 60)

# Check credentials
api_key = os.getenv("N8N_API_KEY")
public_key = os.getenv("N8N_PUBLIC_KEY")
private_key = os.getenv("N8N_PRIVATE_KEY")
base_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")

if not api_key and not (public_key and private_key):
    print("\n❌ n8n credentials not found in .env")
    print("\n💡 Run: python3 setup_n8n_credentials.py")
    exit(1)

print(f"\n📋 Configuration:")
print(f"   Base URL: {base_url}")
if api_key:
    print(f"   API Key: {api_key[:30]}...")
if public_key:
    print(f"   Public Key: {public_key}")
if private_key:
    print(f"   Private Key: {private_key[:20]}...")

# Initialize client
client = get_n8n_client()

# Health check
print("\n🔍 Health Check:")
print("-" * 60)
health = client.health_check()
print(f"Status: {health['status']}")
if health['status'] != 'healthy':
    print(f"⚠️  Warning: n8n may not be accessible at {base_url}")
    print("   Check if n8n is running and the URL is correct")

# List workflows
print("\n📋 Listing Workflows:")
print("-" * 60)
try:
    workflows = client.get_workflows()
    print(f"Found {len(workflows)} workflow(s)")
    
    if workflows:
        for wf in workflows[:10]:  # Show first 10
            name = wf.get('name', 'Unknown')
            wf_id = wf.get('id', 'N/A')
            active = "🟢 Active" if wf.get('active', False) else "🔴 Inactive"
            print(f"   {active} - {name} (ID: {wf_id})")
    else:
        print("   No workflows found")
        
except Exception as e:
    print(f"❌ Error listing workflows: {e}")
    print("\n💡 Troubleshooting:")
    print("   - Verify n8n is running")
    print("   - Check N8N_BASE_URL is correct")
    print("   - Verify API credentials are valid")

# Test webhook (if you have a webhook workflow)
print("\n🧪 Testing Webhook:")
print("-" * 60)
print("To test a webhook, you need:")
print("  1. A workflow with a webhook trigger")
print("  2. The webhook path (e.g., 'whatsapp')")
print("\nExample:")
print("  client.trigger_workflow_webhook('whatsapp', {'message': 'test'})")

print("\n✅ Integration test complete!")
print("=" * 60)


