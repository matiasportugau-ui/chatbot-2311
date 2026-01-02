#!/usr/bin/env python3
"""
Script to update API keys and start the API server
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def update_env_file(env_file='.env.local'):
    """Update API keys in .env.local file"""
    env_path = Path(env_file)

    if not env_path.exists():
        print(f"❌ File {env_file} not found!")
        return False

    # Read current content
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Get API keys from user
    print("\n" + "="*60)
    print("API KEY CONFIGURATION")
    print("="*60)
    print("\nEnter your API keys (press Enter to skip and keep current value):\n")

    openai_key = input("OpenAI API Key: ").strip()
    grok_key = input("GROK/xAI API Key: ").strip()

    # Update lines
    updated = False
    new_lines = []
    xai_key_found = False  # Track if we found XAI_API_KEY in the file
    grok_key_found = False  # Track if we found GROK_API_KEY in the file

    # First pass: identify existing keys
    for line in lines:
        if line.startswith('XAI_API_KEY='):
            xai_key_found = True
        elif line.startswith('GROK_API_KEY='):
            grok_key_found = True

    # Second pass: process and update lines
    for line in lines:
        if line.startswith('OPENAI_API_KEY='):
            if openai_key:
                new_lines.append(f'OPENAI_API_KEY={openai_key}\n')
                updated = True
                print("✅ OpenAI API Key updated")
            else:
                new_lines.append(line)
        elif line.startswith('XAI_API_KEY='):
            # Always replace XAI_API_KEY if new key provided, otherwise keep existing
            if grok_key:
                new_lines.append(f'XAI_API_KEY={grok_key}\n')
                updated = True
                print("✅ XAI_API_KEY updated")
            else:
                new_lines.append(line)
        elif line.startswith('GROK_API_KEY='):
            # If we have a new key, replace GROK_API_KEY with XAI_API_KEY
            # If no new key, keep GROK_API_KEY only if XAI_API_KEY doesn't exist
            if grok_key:
                # Replace GROK_API_KEY with XAI_API_KEY (preferred format)
                if not xai_key_found:
                    # Only add XAI_API_KEY if it wasn't already in the file
                    new_lines.append(f'XAI_API_KEY={grok_key}\n')
                    updated = True
                    print("✅ GROK_API_KEY replaced with XAI_API_KEY")
                # Skip the old GROK_API_KEY line (don't append it)
            else:
                # No new key provided, keep GROK_API_KEY only if XAI_API_KEY doesn't exist
                if not xai_key_found:
                    new_lines.append(line)
                # If XAI_API_KEY exists, skip GROK_API_KEY to avoid duplicates
        else:
            new_lines.append(line)

    # Add XAI_API_KEY if it doesn't exist and we have a new key
    if grok_key and not xai_key_found and not grok_key_found:
        new_lines.append(f'XAI_API_KEY={grok_key}\n')
        updated = True
        print("✅ XAI_API_KEY added")

    # Write back
    if updated or openai_key or grok_key:
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        print(f"\n✅ Configuration saved to {env_file}")
        return True
    else:
        print("\n⚠️  No changes made")
        return False

def check_api_running(port=8000):
    """Check if API server is running"""
    try:
        import requests
        response = requests.get(f'http://localhost:{port}/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server"""
    print("\n" + "="*60)
    print("STARTING API SERVER")
    print("="*60)

    # Check if already running
    if check_api_running():
        print("✅ API Server is already running on http://localhost:8000")
        return True

    print("\n🚀 Starting API server...")
    print("   Command: python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload")
    print("\n   Press Ctrl+C to stop the server\n")

    try:
        # Start API server
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "api_server:app",
             "--host", "0.0.0.0", "--port", "8000", "--reload"]
        )
    except KeyboardInterrupt:
        print("\n\n✅ API Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting API server: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("API KEYS & SERVER SETUP")
    print("="*60)

    # Step 1: Update API keys
    update_env_file()

    # Step 2: Ask if user wants to start server
    print("\n" + "="*60)
    response = input("\nDo you want to start the API server now? (y/n): ").strip().lower()

    if response == 'y':
        start_api_server()
    else:
        print("\n💡 To start the API server manually, run:")
        print("   python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload")
        print("\n   Or run this script again and choose 'y'")

if __name__ == "__main__":
    main()

