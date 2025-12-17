import requests
import json
import time

URL = "https://nomad-backend-49856050254.europe-west1.run.app/analyze"

# Using a clear tech innovation example to trigger 'High Impact' logic
payload = {
    "title": "Universal Quantum Computer Breakthrough Announced by Google",
    "content": "Google researchers have achieved quantum supremacy with a new stable qubit processor that solves problems in seconds that would take supercomputers millennia. This marks a paradigm shift in computing."
}

print(f"Testing TREND RADAR Logic at: {URL}")
try:
    r = requests.post(URL, json=payload, timeout=45)
    data = r.json()
    
    print(f"Status: {r.status_code}")
    print("KEYS RECEIVED:", list(data.keys()))
    
    # Validation Checklist
    has_score = "impact_score" in data
    has_label = "trend_label" in data
    has_hook = "one_line_hook" in data
    
    if has_score and has_label and has_hook:
        print("\n✅ SUCCESS: New Trend Radar Logic is ACTIVE.")
        print(f"🌍 Trend Label: {data['trend_label']}")
        print(f"⚡ Impact Score: {data['impact_score']}")
        print(f"🎣 Hook: {data['one_line_hook']}")
        
        if data['impact_score'] > 80:
            print("🚀 Logic Check: High Impact correctly identified.")
        else:
            print(f"⚠ Note: Score {data['impact_score']} is lower than expected for Quantum Supremacy, but format is correct.")
            
    else:
        print("\n❌ FAIL: Old Logic Detected or Keys Missing.")
        print(f"Missing: {[k for k in ['impact_score', 'trend_label', 'one_line_hook'] if k not in data]}")

except Exception as e:
    print(f"❌ ERROR: {e}")
