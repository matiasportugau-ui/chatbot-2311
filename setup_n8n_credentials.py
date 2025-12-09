#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup n8n API credentials"""

from pathlib import Path

# Your n8n credentials
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkODVlMjVjNi1mMzJjLTQ1NWQtODUzOC02ODU3YjMyYzE5NDQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYyNjczMTQ1fQ.syR-zNunh3r2C6JwE4sNGBsqyaJYqbEzFTpUSMqiwVI"
N8N_PUBLIC_KEY = "mvkwbyac"
N8N_PRIVATE_KEY = "8d26b5d5-50a3-4439-9b91-d22d16ffe455"
N8N_BASE_URL = "http://localhost:5678"  # Update if your n8n is hosted elsewhere

env_file = Path(".env")

# Read existing .env or create new
if env_file.exists():
    content = env_file.read_text()
    lines = content.split('\n')
    
    # Update or add n8n credentials
    updated_keys = {
        "N8N_API_KEY": N8N_API_KEY,
        "N8N_PUBLIC_KEY": N8N_PUBLIC_KEY,
        "N8N_PRIVATE_KEY": N8N_PRIVATE_KEY,
        "N8N_BASE_URL": N8N_BASE_URL
    }
    
    # Update existing or add new
    for key, value in updated_keys.items():
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}=") and not line.strip().startswith("#"):
                lines[i] = f"{key}={value}"
                found = True
                break
        
        if not found:
            # Add new key
            if not any(line.startswith("N8N_") for line in lines):
                # Add n8n section
                lines.append("\n# n8n Configuration")
            lines.append(f"{key}={value}")
    
    env_file.write_text('\n'.join(lines))
    print("✅ Updated n8n credentials in .env")
else:
    # Create new .env file
    env_file.write_text(f"""# n8n Configuration
N8N_API_KEY={N8N_API_KEY}
N8N_PUBLIC_KEY={N8N_PUBLIC_KEY}
N8N_PRIVATE_KEY={N8N_PRIVATE_KEY}
N8N_BASE_URL={N8N_BASE_URL}
""")
    print("✅ Created .env with n8n credentials")

print(f"\n📋 n8n Configuration:")
print(f"   API Key: {N8N_API_KEY[:30]}...")
print(f"   Public Key: {N8N_PUBLIC_KEY}")
print(f"   Private Key: {N8N_PRIVATE_KEY[:20]}...")
print(f"   Base URL: {N8N_BASE_URL}")
print("\n✨ You can now test with:")
print("   python3 test_n8n_integration.py")


