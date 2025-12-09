import requests
import time
import sys

URL = "https://web-production-b896.up.railway.app/health"
TARGET_SERVICE = "BMC Quote System API"
TIMEOUT = 300  # 5 minutes
INTERVAL = 10  # 10 seconds

print(f"🔍 Monitoring deployment at {URL}...")
print(f"   Target Service: '{TARGET_SERVICE}'")
print(f"   Timeout: {TIMEOUT}s")
print("-" * 50)

start_time = time.time()

while time.time() - start_time < TIMEOUT:
    try:
        response = requests.get(URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_service = data.get("service")
            
            if current_service == TARGET_SERVICE:
                print(f"\n✅ DEPLOYMENT SUCCESSFUL!")
                print(f"   Service: {current_service}")
                print(f"   Time taken: {int(time.time() - start_time)}s")
                sys.exit(0)
            else:
                elapsed = int(time.time() - start_time)
                print(f"⏳ Waiting... Current: '{current_service}' ({elapsed}s)")
        else:
            print(f"⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Connection error: {e}")
        
    time.sleep(INTERVAL)

print("\n❌ TIMEOUT: Deployment verification failed.")
sys.exit(1)
