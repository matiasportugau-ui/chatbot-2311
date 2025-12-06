#!/usr/bin/env python3
"""
Quick script to fix OPENAI_API_KEY in .env file
"""

import os
from pathlib import Path

ENV_FILE = Path(".env")


def main():
    print("=" * 70)
    print("CONFIGURAR OPENAI_API_KEY")
    print("=" * 70)
    print()

    # Check if already set in system environment
    system_key = os.environ.get("OPENAI_API_KEY", "")
    if system_key and not system_key.startswith("your-") and len(system_key) > 10:
        print("✅ Found OPENAI_API_KEY in system environment")
        use_system = input("Use this key? (y/n, default: y): ").strip().lower()
        if use_system != "n":
            update_env_file(system_key)
            return

    # Check current .env value
    current_key = ""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("OPENAI_API_KEY="):
                current_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

    if current_key and not current_key.startswith("your-") and len(current_key) > 10:
        print("✅ Found OPENAI_API_KEY in .env file")
        print("Current value appears to be valid.")
        return

    # Prompt for new key
    print("OPENAI_API_KEY is missing or invalid.")
    print()
    print("Get your API key from: https://platform.openai.com/api-keys")
    print("(The key should start with 'sk-')")
    print()

    new_key = input("Enter your OPENAI_API_KEY: ").strip()

    if not new_key:
        print("❌ No key provided. Exiting.")
        return

    if not new_key.startswith("sk-"):
        print("⚠️  Warning: API keys usually start with 'sk-'. Continue anyway? (y/n): ", end="")
        if input().strip().lower() != "y":
            return

    update_env_file(new_key)
    print()
    print("✅ OPENAI_API_KEY configured successfully!")
    print(f"   Location: {ENV_FILE.resolve()}")


def update_env_file(api_key):
    """Update .env file with new API key"""
    if not ENV_FILE.exists():
        # Create new file
        ENV_FILE.write_text(f"OPENAI_API_KEY={api_key}\n", encoding="utf-8")
        return

    # Update existing file
    lines = []
    key_found = False

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("OPENAI_API_KEY="):
            lines.append(f"OPENAI_API_KEY={api_key}")
            key_found = True
        else:
            lines.append(line)

    if not key_found:
        lines.append(f"OPENAI_API_KEY={api_key}")

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
