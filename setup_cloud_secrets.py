"""
Secrets Exporter for Cloud Deployment
Reads your local .env file and prints a format you can copy-paste
into Railway, Render, or other cloud dashboards.
"""

import os

def main():
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ No .env file found!")
        return

    print("=== COPY THE BELOW INTO YOUR CLOUD PROVIDER CONFIG ===")
    print("# (Do not share this output publicly)")
    print("")
    
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Basic validation
            if "=" in line:
                print(line)
                
    print("")
    print("====================================================")
    print("Instructions:")
    print("1. Go to your Cloud Dashboard (e.g. Railway -> Variables).")
    print("2. Paste the above content.")
    print("3. Deploy using the Dockerfile.")

if __name__ == "__main__":
    main()
