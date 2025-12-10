#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse

def parse_env_file(filepath=".env"):
    """Reads .env file and returns a dictionary of valid keys."""
    env_vars = {}
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} not found.")
        return env_vars
    
    # Critical keys that MUST be synced for the app to work
    CRITICAL_KEYS = [
        "OPENAI_API_KEY",
        "MONGODB_URI",
        "GOOGLE_SHEET_ID",
        "GOOGLE_PROJECT_ID",
        "GOOGLE_SERVICE_ACCOUNT_EMAIL",
        "GOOGLE_PRIVATE_KEY",
        "SHOPIFY_ACCESS_TOKEN",
        "SHOPIFY_SHOP_DOMAIN",
        "FE_EMISOR_ID",
        "FE_USERNAME",
        "FE_PASSWORD_HASH"
    ]
        
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Check if this key is critical
                if key in CRITICAL_KEYS:
                     if "\\n" in value:
                         value = value.replace("\\n", "\n")
                     env_vars[key] = value
                
    return env_vars

def custom_env_add(key, value):
    """Adds env var to Vercel using stdin."""
    print(f"   Setting {key}...")
    try:
        # echo value | vercel env add KEY production --force
        process = subprocess.Popen(
            ["vercel", "env", "add", key, "production", "--force"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=value)
        if process.returncode != 0:
            print(f"   ❌ Failed to set {key}: {stderr.strip()}")
        else:
            print(f"   ✅ Set {key}")
    except Exception as e:
        print(f"   ❌ Exception setting {key}: {e}")

def deploy_vercel(backend_url=None):
    print("🚀 Preparing to deploy chatbot-frontend to Vercel...")
    
    # 1. Check Vercel CLI
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ 'vercel' CLI is not operating correctly.")
        sys.exit(1)
        
    # 2. Sync Env Vars
    print("\n🔄 Syncing Environment Variables from .env to Vercel Production...")
    env_vars = parse_env_file(".env")
    
    for key, value in env_vars.items():
        custom_env_add(key, value)
        
    if backend_url:
        custom_env_add("NEXT_PUBLIC_API_URL", backend_url)
        
    # 3. Deploy
    print("\n📦 Triggering Vercel Deployment...")
    # vercel --prod
    try:
        subprocess.run(["vercel", "--prod"], check=True)
        print("\n✅ Vercel Deployment triggered successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Frontend to Vercel")
    parser.add_argument("--backend-url", help="URL of the Python Backend (Cloud Run)")
    args = parser.parse_args()
    
    deploy_vercel(args.backend_url)
