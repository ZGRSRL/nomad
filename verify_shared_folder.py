
import os
import sys
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from dotenv import load_dotenv
load_dotenv('temp_drive_creds.env') # Use the creds we have

from backend import drive_service

SHARED_FOLDER_ID = "1LmySDiVGHRasi2R6zGwz3ijcsHiox0rG"

print(f"--- VERIFYING ACCESS TO FOLDER: {SHARED_FOLDER_ID} ---")

try:
    service = drive_service.get_drive_service()
    if not service:
        print("Failed to get service")
        sys.exit(1)

    # 1. Check Metadata (Read Access)
    print("Checking metadata...")
    f = service.files().get(fileId=SHARED_FOLDER_ID, fields="id, name, capabilities").execute()
    print(f"✅ Folder Found: '{f.get('name')}'")
    print(f"   Capabilities: {f.get('capabilities')}")
    
    can_add = f.get('capabilities', {}).get('canAddChildren')
    if not can_add:
        print("❌ CRITICAL: Service Account cannot add files to this folder. Did you give 'Editor' permission?")
        sys.exit(1)
        
    # 2. Try Writing a Test File (Write Access)
    print("Attempting to write test file...")
    file_metadata = {
        'name': 'ACCESS_TEST.txt',
        'parents': [SHARED_FOLDER_ID]
    }
    from googleapiclient.http import MediaIoBaseUpload
    import io
    media = MediaIoBaseUpload(io.BytesIO(b"Access Granted"), mimetype='text/plain')
    
    new_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ WRITE SUCCESS! Created file ID: {new_file.get('id')}")
    
    # Cleanup
    print("Cleaning up test file...")
    service.files().delete(fileId=new_file.get('id')).execute()
    print("Cleanup done.")
    
except Exception as e:
    print(f"❌ Error: {e}")
