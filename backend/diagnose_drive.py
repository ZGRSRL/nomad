import sys
import os
import json
from googleapiclient.errors import HttpError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from drive_service import get_drive_service, SHARED_FOLDER_ID

service = get_drive_service()
if not service:
    print("No service.")
    sys.exit(1)

print("\n--- 1. Checking About Info ---")
try:
    about = service.about().get(fields="user, storageQuota").execute()
    print(json.dumps(about, indent=2))
except Exception as e:
    print(f"About Error: {e}")

print("\n--- 2. Checking Shared Folder Access ---")
try:
    f = service.files().get(fileId=SHARED_FOLDER_ID, fields="id, name, capabilities, owners").execute()
    print(json.dumps(f, indent=2))
except Exception as e:
    print(f"Shared Folder Error: {e}")

print("\n--- 3. Test Upload to ROOT ---")
try:
    file_metadata = {'name': 'TEST_ROOT_UPLOAD', 'mimeType': 'application/vnd.google-apps.document'}
    file = service.files().create(body=file_metadata, fields='id').execute()
    print(f"ROOT Upload Success: {file.get('id')}")
    # Cleanup
    service.files().delete(fileId=file.get('id')).execute()
    print("ROOT Cleanup Success")
except Exception as e:
    print(f"ROOT Upload Failed: {e}")

print("\n--- 4. Test Upload to Shared Folder ---")
try:
    file_metadata = {
        'name': 'TEST_SHARED_UPLOAD', 
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [SHARED_FOLDER_ID]
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    print(f"SHARED Upload Success: {file.get('id')}")
    # Cleanup
    service.files().delete(fileId=file.get('id')).execute()
    print("SHARED Cleanup Success")
except Exception as e:
    print(f"SHARED Upload Failed: {e}")
