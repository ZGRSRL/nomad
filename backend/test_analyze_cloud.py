
import requests

url = "https://nomad-backend-xxs2tligqa-ew.a.run.app/analyze"
payload = {
    "title": "Test Article",
    "content": "This is a test article content to verify AI connectivity."
}

print(f"POST {url}")
try:
    r = requests.post(url, json=payload, timeout=20)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
