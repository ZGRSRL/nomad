
import os
import sys
import json
import base64
import ast
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("--- VERIFYING ACCESS V3 (AST PARSING) ---")

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

if not b64_val:
    print("❌ Failed to find B64 creds")
    sys.exit(1)

# Fix padding
missing = len(b64_val) % 4
if missing: b64_val += '=' * (4 - missing)

creds_json = base64.b64decode(b64_val).decode('utf-8')
creds_dict = json.loads(creds_json)
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/drive'])

print(f"🔍 Authenticated as: {creds_dict.get('client_email')}")

# 2. CHECK FOLDER
SHARED_FOLDER_ID = "1LmySDiVGHRasi2R6zGwz3ijcsHiox0rG"
service = build('drive', 'v3', credentials=creds)

try:
    f = service.files().get(fileId=SHARED_FOLDER_ID, fields="id, name, capabilities").execute()
    print(f"✅ FOLDER ACCESSIBLE: '{f.get('name')}'")
    
    if f.get('capabilities', {}).get('canAddChildren'):
        print("✅ PERMISSIONS: Write Access Confirmed.")
    else:
        print("❌ PERMISSIONS: Read Only. Need Editor Access.")

except Exception as e:
    print(f"❌ ACCESS DENIED: {e}")
