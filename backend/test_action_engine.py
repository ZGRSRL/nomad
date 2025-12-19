
import requests
import json
import time

# Use Cloud URL since we want to test the deployed logic after we deploy (or local if testing locally)
# Since we haven't deployed the new main.py yet, we must first deploy or run locally.
# Assuming we will deploy first.

URL = "https://nomad-backend-49856050254.europe-west1.run.app/analyze"
# NOTE: The above URL is the LIVE one. It does NOT have the Action Engine code yet until we push and deploy.
# So this test will FAIL to show the action engine results until deployment.

print("To verify Action Engine, we must first deploy the changes.")
print("This script is ready for post-deployment verification.")

payload = {
    "title": "BREAKING: Artificial General Intelligence (AGI) Achieved in Lab",
    "content": "Scientists confirm the first instance of self-improving AI that surpasses human intelligence in all domains. Global markets react wildly. Governments convene emergency summits."
}

def verify():
    print(f"Sending CRITICAL Request to: {URL}")
    try:
        r = requests.post(URL, json=payload, timeout=30)
        data = r.json()
        
        print(f"Impact Score: {data.get('impact_score')} (Type: {type(data.get('impact_score'))})")
        print("Raw Data:", json.dumps(data, indent=2))
        print(f"Action Taken: {data.get('action_taken', 'NONE')}")
        
        if data.get('action_taken') == "IMMEDIATE_REPORT_GENERATED":
            print("✅ SUCCESS: Action Engine Triggered!")
            print(f"Report Link: {data.get('report_link')}")
        else:
            print("❌ FAILURE: Action Engine did NOT trigger (or code not deployed).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
