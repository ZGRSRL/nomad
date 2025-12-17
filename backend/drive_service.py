import os
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from pathlib import Path

# Setup Paths
BASE_DIR = Path(__file__).parent.resolve()
CREDS_FILE = BASE_DIR / 'credentials.json'
print(f"DEBUG: Looking for credentials at: {CREDS_FILE}")

SCOPES = ['https://www.googleapis.com/auth/drive']
VAULT_FOLDER_NAME = "Nomad Intelligence"

def get_drive_service():
    """Authenticates and returns the Drive service."""
    creds = None
    
    # 0. Try OAuth 2.0 (User's personal Drive - 5TB)
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if refresh_token and client_id and client_secret:
        try:
            creds = OAuthCredentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            # Access token al
            creds.refresh(Request())
            print(f"✅ Using OAuth 2.0 (User's personal Drive - 5TB)")
        except Exception as e:
            print(f"⚠️ Failed to use OAuth 2.0: {e}")
            creds = None
    
    # 1. Try environment variable (Cloud Run) - Base64 encoded
    google_creds_b64 = os.getenv("GOOGLE_CREDENTIALS_JSON_B64")
    if google_creds_b64:
        try:
            import base64
            # Trim whitespace and fix padding if needed
            google_creds_b64 = google_creds_b64.strip()
            # Fix padding if needed
            missing_padding = len(google_creds_b64) % 4
            if missing_padding:
                google_creds_b64 += '=' * (4 - missing_padding)
            google_creds_json = base64.b64decode(google_creds_b64).decode('utf-8')
            creds_dict = json.loads(google_creds_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES)
            print(f"✅ Using credentials from GOOGLE_CREDENTIALS_JSON_B64 (Service Account: {creds_dict.get('client_email', 'unknown')})")
        except Exception as e:
            print(f"⚠️ Failed to parse GOOGLE_CREDENTIALS_JSON_B64: {e}")
            import traceback
            print(traceback.format_exc())
    
    # 1b. Try environment variable (Cloud Run) - Direct JSON
    if not creds:
        google_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if google_creds_json:
            try:
                creds_dict = json.loads(google_creds_json)
                creds = service_account.Credentials.from_service_account_info(
                    creds_dict, scopes=SCOPES)
                print("✅ Using credentials from GOOGLE_CREDENTIALS_JSON environment variable")
            except Exception as e:
                print(f"⚠️ Failed to parse GOOGLE_CREDENTIALS_JSON: {e}")
    
    # 2. Try credentials.json file (local development)
    if not creds and CREDS_FILE.exists():
        try:
            creds = service_account.Credentials.from_service_account_file(
                str(CREDS_FILE), scopes=SCOPES)
            print("✅ Using credentials from credentials.json file")
        except Exception as e:
            print(f"⚠️ Failed to load credentials.json: {e}")
    
    # 3. Try default credentials (Cloud Run default service account)
    if not creds:
        try:
            from google.auth import default
            creds, _ = default(scopes=SCOPES)
            print("✅ Using default Cloud Run service account")
        except Exception as e:
            print(f"⚠️ Failed to use default credentials: {e}")
    
    if not creds:
        print(f"❌ CRITICAL: No Google Drive credentials found")
        print(f"   Options:")
        print(f"   1. Set GOOGLE_CREDENTIALS_JSON environment variable")
        print(f"   2. Place credentials.json at {CREDS_FILE}")
        print(f"   3. Use Cloud Run default service account with Drive API enabled")
        return None
    
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return None

def get_or_create_vault(service):
    """Finds or creates the 'Nomad Intelligence' folder."""
    try:
        # Search for existing folder
        query = f"mimeType='application/vnd.google-apps.folder' and name='{VAULT_FOLDER_NAME}' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            # Create if not found
            file_metadata = {
                'name': VAULT_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = service.files().create(body=file_metadata, fields='id').execute()
            print(f"Vault Created: {file.get('id')}")
            return file.get('id')
        else:
            # Return first match
            return items[0]['id']
            
    except Exception as e:
        print(f"Folder Error: {e}")
        return None

def upload_html_as_doc(title, html_content):
    """
    Uploads HTML content as a native Google Doc into the Vault folder.
    """
    print(f"📤 Starting upload: {title}")
    service = get_drive_service()
    if not service:
        error_msg = "Drive Authentication Failed. Check GOOGLE_CREDENTIALS_JSON_B64 or credentials.json"
        print(f"❌ {error_msg}")
        return {"status": "error", "message": error_msg}

    print("✅ Drive service authenticated")
    folder_id = get_or_create_vault(service)
    if not folder_id:
        # Fallback to root if folder creation fails
        folder_id = None 
        print("⚠️ Warning: Could not resolve Vault folder, uploading to root.")
    else:
        print(f"✅ Vault folder ID: {folder_id}")

    try:
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Create media from string
        media = MediaIoBaseUpload(
            io.BytesIO(html_content.encode('utf-8')),
            mimetype='text/html',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return {
            "status": "success", 
            "id": file.get('id'), 
            "link": file.get('webViewLink'),
            "message": f"Report securely archived in {VAULT_FOLDER_NAME}"
        }

    except Exception as e:
        print(f"Upload Error: {e}")
        return {"status": "error", "message": str(e)}
