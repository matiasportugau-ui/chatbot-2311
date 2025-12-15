import os
import subprocess
import json
from dotenv import load_dotenv

load_dotenv()

SECRETS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "XAI_API_KEY": os.getenv("XAI_API_KEY"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "DROPBOX_API_KEY": os.getenv("DROPBOX_API_KEY"),
}

# Special case for file content
try:
    with open("credentials.json", "r") as f:
        SECRETS["GOOGLE_SHEETS_CREDENTIALS"] = f.read()
except FileNotFoundError:
    print("❌ Error: credentials.json not found!")
    exit(1)

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result

print("🚀 Setting up Google Cloud Secrets...")

for name, value in SECRETS.items():
    if not value:
        print(f"⚠️ Skipping {name} (Value not found in environment)")
        continue

    print(f"🔹 Processing {name}...")
    
    # 1. Create Secret (idempotent-ish, ignore error if exists)
    create_cmd = f"gcloud secrets create {name} --replication-policy=automatic"
    res = run_cmd(create_cmd)
    
    if res.returncode != 0 and "already exists" not in res.stderr:
        print(f"   ❌ Failed to create secret: {res.stderr}")
    
    # 2. Add Version
    # Use subprocess input to avoid exposing secret in command line logs
    proc = subprocess.Popen(
        f"gcloud secrets versions add {name} --data-file=-", 
        shell=True, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = proc.communicate(input=value)
    
    if proc.returncode == 0:
        print(f"   ✅ Version added successfully.")
    else:
        print(f"   ❌ Failed to add version: {stderr}")

print("🎉 Secrets Setup Complete!")
