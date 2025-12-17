
import requests

urls = [
    "https://nomad-backend-xxs2tligqa-ew.a.run.app",
    "https://nomad-backend-49856050254.europe-west1.run.app"
]

for url in urls:
    print(f"Checking {url}...")
    try:
        r = requests.get(f"{url}/", timeout=5)
        print(f"Root Status: {r.status_code}")
        print(f"Content Type: {r.headers.get('Content-Type')}")
        print(f"Preview: {r.text[:100]}")
        
        r2 = requests.get(f"{url}/stats", timeout=5)
        print(f"/stats Status: {r2.status_code}")
        print(f"/stats Content Type: {r2.headers.get('Content-Type')}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
