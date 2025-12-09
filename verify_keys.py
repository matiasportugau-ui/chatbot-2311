import os
import sys
from openai import OpenAI

def test_key(key, source):
    print(f"Testing key from {source}: {key[:10]}...{key[-5:]}")
    client = OpenAI(api_key=key)
    try:
        client.models.list()
        print("✅ Key is VALID.")
        return True
    except Exception as e:
        print(f"❌ Key is INVALID: {e}")
        return False

# 1. Check Env Var (inherited)
env_key = os.environ.get("OPENAI_API_KEY")
if env_key:
    test_key(env_key, "Environment Variable")
else:
    print("⚠️  OPENAI_API_KEY not set in environment.")

# 2. Check keys from files
files = [".env.unified", ".env", ".env.local"]
for fname in files:
    if os.path.exists(fname):
        with open(fname, "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    val = line.strip().split("=", 1)[1]
                    # Strip quotes if present
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    test_key(val, fname)
