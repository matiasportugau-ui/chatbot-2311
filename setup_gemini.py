#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for Gemini integration"""

import os
from pathlib import Path

print("=" * 60)
print("Gemini Integration Setup")
print("=" * 60)
print()

# Check if API key is provided
gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()

if not gemini_key:
    print("\n📋 To get your Gemini API key:")
    print("   1. Visit: https://makersuite.google.com/app/apikey")
    print("   2. Sign in with your Google account")
    print("   3. Click 'Create API Key'")
    print("   4. Copy the key and run this script again")
    print()
    print("   Or manually add to .env:")
    print("   GEMINI_API_KEY=your-api-key-here")
    print("   GEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro")
    exit(0)

env_file = Path(".env")

# Read existing .env or create new
if env_file.exists():
    content = env_file.read_text()
    
    # Check if GEMINI_API_KEY already exists
    if "GEMINI_API_KEY" in content:
        # Update existing key
        lines = content.split('\n')
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("GEMINI_API_KEY=") and not line.strip().startswith("#"):
                lines[i] = f"GEMINI_API_KEY={gemini_key}"
                updated = True
                break
        
        if updated:
            env_file.write_text('\n'.join(lines))
            print("✅ Updated GEMINI_API_KEY in .env")
        else:
            # Add if not found (might be commented)
            env_file.write_text(content + f"\nGEMINI_API_KEY={gemini_key}\nGEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro\n")
            print("✅ Added GEMINI_API_KEY to .env")
    else:
        # Add new key
        env_file.write_text(content + f"\n# Google Gemini Configuration\nGEMINI_API_KEY={gemini_key}\nGEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro\n")
        print("✅ Added GEMINI_API_KEY to .env")
else:
    # Create new .env file
    env_file.write_text(f"""# Google Gemini Configuration
GEMINI_API_KEY={gemini_key}
GEMINI_MODELS=gemini-1.5-flash,gemini-1.5-pro
""")
    print("✅ Created .env file with GEMINI_API_KEY")

print(f"\n📋 Gemini API key configured: {gemini_key[:20]}...{gemini_key[-10:]}")
print("\n✨ You can now test with:")
print("   python3 test_gemini_integration.py")

