import requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret[:5]}...{client_secret[-5:]}")
print(f"Refresh Token: {refresh_token[:10]}...")

url = "https://oauth2.googleapis.com/token"
data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token,
    "grant_type": "refresh_token",
    "redirect_uri": "http://localhost:8081/"
}

print("\nSending POST request to Google...")
response = requests.post(url, data=data)

print(f"Status Code: {response.status_code}")
print("Response Body:")
print(response.text)
