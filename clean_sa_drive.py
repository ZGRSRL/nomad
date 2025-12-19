
import os
import sys
import json
import base64
import ast
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("--- CLEANING SERVICE ACCOUNT DRIVE ---")

# 1. LOAD CREDS
try:
    with open('cloud_env.txt', 'r', encoding='utf-16') as f: content = f.read()
except:
    with open('cloud_env.txt', 'r', encoding='utf-8') as f: content = f.read()

b64_val = None
for line in content.splitlines():
    if "GOOGLE_CREDENTIALS_JSON_B64" in line:
        try:
            data = ast.literal_eval(line.strip())
            if isinstance(data, dict): b64_val = data.get('value')
        except:
            if "=" in line: b64_val = line.split("=", 1)[1].strip()

# Fix padding
missing = len(b64_val) % 4
if missing: b64_val += '=' * (4 - missing)
creds_json = base64.b64decode(b64_val).decode('utf-8')
creds = service_account.Credentials.from_service_account_info(json.loads(creds_json), scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# 2. LIST FILES
print("Listing files owned by me...")
try:
    # 'me' refers to the Service Account
    results = service.files().list(
        q="'me' in owners and trashed=false",
        pageSize=50,
        fields="files(id, name, size, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    print(f"Found {len(files)} files.")
    
    total_size = 0
    for f in files:
        size = int(f.get('size', 0))
        total_size += size
        print(f"[{f['id']}] {f['name']} ({size/1024/1024:.2f} MB)")
        
        # Deleting old reports automatically
        if "ALERT:" in f['name'] or "Test" in f['name']:
             print(f"   Deleting {f['name']}...")
             service.files().delete(fileId=f['id']).execute()

    print(f"Total Size of 50 items: {total_size/1024/1024:.2f} MB")
    
except Exception as e:
    print(f"Error: {e}")
