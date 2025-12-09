import os
import sys
import re
import socket
from dotenv import load_dotenv

def check_socket(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        try:
            s.connect((host, port))
            return True
        except:
            return False

def main():
    print("🔍 Inspecting Configuration...")
    load_dotenv(override=True)
    
    # 1. Check OpenAI Key
    key = os.getenv("OPENAI_API_KEY", "")
    print(f"\n🔑 OPENAI_API_KEY: {key[:10]}...{key[-5:] if len(key)>5 else ''}")
    if key.startswith("sk-"):
        print("   ✅ Format looks correct (starts with sk-)")
    elif key.startswith("ey"):
        print("   ❌ ERROR: This looks like a JWT/Token (e.g. from n8n), NOT an OpenAI API Key.")
        print("      Please get a key from https://platform.openai.com/api-keys")
    else:
        print("   ⚠️ WARNING: Does not start with 'sk-'. Might be invalid.")

    # 2. Check MongoDB URI
    uri = os.getenv("MONGODB_URI", "")
    print(f"\n🍃 MONGODB_URI: {uri}")
    
    if "localhost" in uri or "127.0.0.1" in uri:
        print("   ⚠️ Configured for LOCALHOST.")
        print("   Checking if MongoDB is running locally on port 27017...")
        if check_socket("localhost", 27017):
            print("   ✅ Local MongoDB is responding.")
        else:
            print("   ❌ ERROR: Local MongoDB is NOT running.")
            print("      (Since Docker is down, you probably need to start it or use a Cloud URI)")
            
    elif "mongodb+srv://" in uri:
        print("   ✅ Configured for Atlas (Cloud).")
    else:
        print("   ⚠️ Unknown URI format.")

    # 3. Docker Check
    print("\n🐳 Docker Status:")
    if os.system("docker ps > /dev/null 2>&1") == 0:
         print("   ✅ Docker is running.")
    else:
         print("   ❌ Docker is NOT running (or not accessible).")

    print("\n" + "="*40)
    print("CONCLUSION:")
    if not key.startswith("sk-"):
        print("1. Update OPENAI_API_KEY in .env with a valid 'sk-...' key.")
    if "localhost" in uri and not check_socket("localhost", 27017):
        print("2. You have two choices for Database:")
        print("   a) Use CLOUD: Update MONGODB_URI to an Atlas connection string.")
        print("   b) Use LOCAL: Start Docker Desktop so local DB can run.")
    print("="*40)

if __name__ == "__main__":
    main()
