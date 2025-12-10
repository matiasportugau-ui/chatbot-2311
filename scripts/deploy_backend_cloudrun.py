#!/usr/bin/env python3
import os
import subprocess
import sys

def parse_env_file(filepath=".env"):
    """Reads .env file and returns a dictionary of valid keys."""
    env_vars = {}
    if not os.path.exists(filepath):
        print(f"⚠️  {filepath} not found. Deploying without local env vars (expecting Cloud Run already configured).")
        return env_vars
        
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Basic splitting for KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Handle double-escaped newlines in private keys if present
                if "\\n" in value:
                     value = value.replace("\\n", "\n")

                env_vars[key] = value
                
    return env_vars

def deploy_to_cloud_run():
    print("🚀 Preparing to deploy chatbot-backend to Google Cloud Run...")
    
    # 1. Check if gcloud is installed
    try:
        subprocess.run(["gcloud", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("❌ 'gcloud' CLI is not installed or not in PATH.")
        sys.exit(1)
        
    # 2. Get Project ID (optional verification)
    project_id = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True).stdout.strip()
    print(f"ℹ️  Target Project: {project_id}")
    
    # 3. Read Env Vars
    env_vars = parse_env_file(".env")
    env_flags = []
    
    # Exclude Vercel-specific or local-only vars if needed, but for now we pass all
    # Cloud Run doesn't like keys with special chars prefix, but standard keys are fine.
    
    # We construct the comma-separated list. 
    # WARNING: Comma-separated list for --set-env-vars breaks if values contain commas.
    # Better to use repeated --set-env-vars for safety involves shell tricks, but python subprocess allows passing list of args?
    # No, gcloud expects "KEY1=VAL1,KEY2=VAL2" or repeated flags?
    # Recent gcloud supports repeated flags? It says "KEY=VALUE,..."
    # If values contain commas, we must escape them.
    
    # Safer Strategy: Generate a yaml file and use --env-vars-file? No, not standard.
    # Strategy: Use update-env-vars after deploy? OR
    # Just format carefully.
    
    # Let's try to verify if values have commas.
    safe_vars = []
    for k, v in env_vars.items():
        # Escape commas in value
        v_escaped = v.replace(",", "\,") 
        safe_vars.append(f"{k}={v_escaped}")
    
    env_String = ",".join(safe_vars)
    
    command = [
        "gcloud", "run", "deploy", "chatbot-backend",
        "--source", ".",
        "--platform", "managed",
        "--region", "us-central1",
        "--allow-unauthenticated", # Public API? Yes, for Vercel consumption.
        "--quiet",
    ]
    
    if safe_vars:
        command.extend(["--set-env-vars", env_String])
        
    print("📦 Deploying... This may take a few minutes.")
    
    # Execute
    try:
        subprocess.run(command, check=True)
        print("\n✅ Deployment Command Finished.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_cloud_run()
