
import os
import sys
import json
import base64
import ast
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("--- EMPTYING TRASH FOR SERVICE ACCOUNT ---")

# 1. LOAD CREDS (Simplified for brevity)
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
        except: pass

missing = len(b64_val) % 4
if missing: b64_val += '=' * (4 - missing)
creds_json = base64.b64decode(b64_val).decode('utf-8')
creds = service_account.Credentials.from_service_account_info(json.loads(creds_json), scopes=['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

try:
    print("Emptying trash...")
    service.files().emptyTrash().execute()
    print("✅ Trash emptied.")
except Exception as e:
    print(f"Trash Error: {e}")

try:
    # Check About
    about = service.about().get(fields="storageQuota").execute()
    quota = about.get('storageQuota', {})
    limit = int(quota.get('limit', 0))
    usage = int(quota.get('usage', 0))
    print(f"Quota Limit: {limit/1024/1024:.2f} MB")
    print(f"Quota Usage: {usage/1024/1024:.2f} MB")
except Exception as e:
    print(f"About Error: {e}")
