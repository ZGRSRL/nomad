import requests
import json
import time

URL = "https://nomad-backend-49856050254.europe-west1.run.app/analyze"

payload = {
    "title": "New Zero-Day Vulnerability Found in OpenSSH",
    "content": "A critical vulnerability has been discovered in OpenSSH allowing remote code execution. Security experts advise immediate patching."
}

print(f"Sending Request to: {URL}")
start = time.time()
try:
    r = requests.post(URL, json=payload, timeout=30)
    duration = time.time() - start
    print(f"Time Taken: {duration:.2f}s")

    print(f"Status: {r.status_code}")
    try:
        data = r.json()
        print("Response Keys:", data.keys())
        
        if "summary" in data and "impact_score" in data:
            print("\n✅ AI ANALYSIS SUCCESS!")
            print(f"Score: {data['impact_score']}")
            print(f"Insight: {data.get('aiInsight', 'N/A')}")
            
            if "Decryption failed" in data.get('summary', ''):
                 print("\n❌ FAILURE: Still seeing Decryption Failed message.")
            else:
                 print("\n✅ API Key & Model are working correctly.")
        else:
             print("\n❌ FAIL: Invalid Response Structure")
             print(data)
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Response Text: {r.text[:500]}")


except Exception as e:
    print(f"\n❌ REQUEST FAILED: {e}")
