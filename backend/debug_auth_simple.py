
import os
from pathlib import Path
from google.oauth2 import service_account
import traceback

# Hardcode for safety
CREDS_FILE = Path(r"d:\Nomad\backend\credentials.json")
SCOPES = ['https://www.googleapis.com/auth/drive']

print(f"Path: {CREDS_FILE}")
print(f"Exists: {CREDS_FILE.exists()}")

try:
    print("Attempting to load credentials...")
    creds = service_account.Credentials.from_service_account_file(
        str(CREDS_FILE), scopes=SCOPES)
    print("✅ Success!")
    print(f"Service Account Email: {creds.service_account_email}")
except Exception:
    print("❌ Failed!")
    traceback.print_exc()
