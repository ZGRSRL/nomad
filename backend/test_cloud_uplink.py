import requests
import json
import sys

CLOUD_URL = "https://nomad-backend-xxs2tligqa-ew.a.run.app"
ENDPOINT = f"{CLOUD_URL}/upload-report"

print(f"--- TESTING CLOUD UPLINK: {CLOUD_URL} ---")

payload = {
    "title": "Nomad Cloud Verification (Live)",
    "content": """
    <h1>Cloud System Verification</h1>
    <p>This report confirms that the <b>Cloud Production Environment</b> has been successfully updated with the new OAuth credentials.</p>
    <ul>
        <li><b>Target:</b> nomad-backend-xxs2tligqa-ew.a.run.app</li>
        <li><b>Auth Method:</b> User OAuth (Env Vars)</li>
        <li><b>Status:</b> SUCCESS</li>
    </ul>
    """
}

try:
    print("Sending POST request...")
    response = requests.post(ENDPOINT, json=payload, headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS: Cloud Uplink Established!")
        print(f"Response: {json.dumps(data, indent=2)}")
        if data.get("status") == "success":
             print(f"\nDocument Link: {data.get('link')}")
        else:
             print("\n⚠️ API returned 200 but status != success")
    else:
        print(f"\n❌ FAILED: Uplink Rejected (Status {response.status_code})")
        print(f"Details: {response.text}")

except Exception as e:
    print(f"\n❌ CONNECTION ERROR: {e}")
