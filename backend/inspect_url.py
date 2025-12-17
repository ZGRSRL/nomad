
import requests



base_url = "https://nomad-backend-xxs2tligqa-ew.a.run.app"
urls = [f"{base_url}/", f"{base_url}/stats"]

for url in urls:
    print(f"GET {url}")
    try:
        r = requests.get(url, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        print(f"Body: {r.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
