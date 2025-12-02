#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick script to set up Grok API key in .env file"""

import os
from pathlib import Path

# Your Grok API key
GROK_API_KEY = "YOUR_GROK_API_KEY_HERE"  # Replace with your actual Grok API key

env_file = Path(".env")

# Read existing .env or create new
if env_file.exists():
    content = env_file.read_text()
    
    # Check if GROK_API_KEY already exists
    if "GROK_API_KEY" in content:
        # Update existing key
        lines = content.split('\n')
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GROK_API_KEY="):
                lines[i] = f"GROK_API_KEY={GROK_API_KEY}"
                updated = True
                break
        
        if updated:
            env_file.write_text('\n'.join(lines))
            print("✅ Updated GROK_API_KEY in .env")
        else:
            # Add if not found (might be commented)
            env_file.write_text(content + f"\nGROK_API_KEY={GROK_API_KEY}\n")
            print("✅ Added GROK_API_KEY to .env")
    else:
        # Add new key
        env_file.write_text(content + f"\n# xAI (Grok) Configuration\nGROK_API_KEY={GROK_API_KEY}\nGROK_MODELS=grok-4-latest,grok-beta,grok-2-1212\n")
        print("✅ Added GROK_API_KEY to .env")
else:
    # Create new .env file
    env_file.write_text(f"""# xAI (Grok) Configuration
GROK_API_KEY={GROK_API_KEY}
GROK_MODELS=grok-4-latest,grok-beta,grok-2-1212

# Model Selection Strategy
MODEL_STRATEGY=balanced
""")
    print("✅ Created .env file with GROK_API_KEY")

print("\n📋 Current GROK_API_KEY configuration:")
print(f"   {GROK_API_KEY[:20]}...{GROK_API_KEY[-10:]}")
print("\n✨ You can now test with:")
print("   python3 test_grok_quick.py")

