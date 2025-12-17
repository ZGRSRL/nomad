import requests
import json

url = "https://nomad-backend-49856050254.europe-west1.run.app/feeds/add"
payload = {
    "url": "https://evrimagaci.org/kategori/muhendislik-839/rss.xml",
    "category": "SCIENCE",
    "source_name": "Evrim Agaci Test"
}

print(f"Sending request to {url}...")
try:
    r = requests.post(url, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"CRITICAL FAIL: {e}")
