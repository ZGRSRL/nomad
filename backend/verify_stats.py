import requests
import json

try:
    r = requests.get("https://nomad-backend-49856050254.europe-west1.run.app/stats", timeout=10)
    data = r.json()
    print("--- STATS VERIFICATION ---")
    print(f"Sources: {data.get('total_sources')}")
    print(f"Trend:   {data.get('top_trend')}")
    print(f"Status:  {data.get('system_status')}")
    print("--------------------------")
except Exception as e:
    print(f"FAIL: {e}")
