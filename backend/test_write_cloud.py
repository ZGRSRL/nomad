
import requests
import json
import time

URL = "https://nomad-backend-49856050254.europe-west1.run.app/save"

payload = {
    "text": "E2E TEST ARTIFACT: Connectivity Verified. Timestamp: " + str(time.time())
}

print(f"Sending Request to: {URL}")
try:
    r = requests.post(URL, json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200 and "id" in r.json():
        print("✅ WRITE SUCCESS: Memory Saved.")
    else:
        print("❌ FAILURE: Write Failed.")

except Exception as e:
    print(f"❌ REQUEST FAILED: {e}")
