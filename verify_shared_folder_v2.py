
import os
import sys
import json
import base64

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Manually load the B64 creds to ensure we use the right account
# (Bypassing dotenv issues)
try:
    with open('cloud_env.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    with open('cloud_env.txt', 'r', encoding='utf-8') as f:
        content = f.read()

b64_val = None
for line in content.splitlines():
    if "GOOGLE_CREDENTIALS_JSON_B64" in line:
        parts = line.strip().split('=', 1)
        if len(parts) == 2:
            b64_val = parts[1]
            break

if b64_val:
    # Fix padding
    missing = len(b64_val) % 4
    if missing: b64_val += '=' * (4 - missing)
    os.environ["GOOGLE_CREDENTIALS_JSON_B64"] = b64_val
else:
    print("WARNING: Could not load B64 creds from file")

from backend import drive_service

SHARED_FOLDER_ID = "1LmySDiVGHRasi2R6zGwz3ijcsHiox0rG"

print(f"--- VERIFYING ACCESS TO FOLDER: {SHARED_FOLDER_ID} ---")

try:
    service = drive_service.get_drive_service()
    if not service:
        print("Failed to get service")
        sys.exit(1)

    # Confirm Identity
    about = service.about().get(fields="user").execute()
    email = about['user']['emailAddress']
    print(f"🔍 Authenticated as: {email}")

    # 1. Check Metadata (Read Access)
    print("Checking folder access...")
    try:
        f = service.files().get(fileId=SHARED_FOLDER_ID, fields="id, name, capabilities").execute()
        print(f"✅ Folder Found: '{f.get('name')}'")
        print(f"   Capabilities: {f.get('capabilities', {})}")
        
        can_add = f.get('capabilities', {}).get('canAddChildren')
        if not can_add:
            print("❌ PERMISSION ERROR: Service Account cannot add files. Needs 'Editor' role.")
        else:
             print("✅ PERMISSION OK: Can add children.")
             
             # 2. Add Test File
             file_metadata = {'name': 'ACCESS_TEST_V2.txt', 'parents': [SHARED_FOLDER_ID]}
             from googleapiclient.http import MediaIoBaseUpload
             import io
             media = MediaIoBaseUpload(io.BytesIO(b"Access Granted V2"), mimetype='text/plain')
             new_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
             print(f"✅ WRITE SUCCESS! Created file ID: {new_file.get('id')}")
             service.files().delete(fileId=new_file.get('id')).execute()
             
    except Exception as e:
        print(f"❌ API Error: {e}")
        
except Exception as e:
    print(f"❌ System Error: {e}")
