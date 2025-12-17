
import json
import os

CREDS_FILE = 'd:\\Nomad\\backend\\credentials.json'

def check_structure():
    if not os.path.exists(CREDS_FILE):
        print("❌ File not found.")
        return

    try:
        with open(CREDS_FILE, 'r') as f:
            data = json.load(f)
        
        required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri']
        missing = [key for key in required_keys if key not in data]
        
        if missing:
            print(f"❌ Invalid JSON Structure. Missing keys: {missing}")
        else:
            print("✅ JSON Structure is valid.")
            print(f"   Project ID: {data.get('project_id')}")
            print(f"   Client Email: {data.get('client_email')}")
            
            pk = data.get('private_key', '')
            print(f"   Private Key Length: {len(pk)}")
            if "-----BEGIN PRIVATE KEY-----" not in pk:
                print("❌ Private Key missing header!")
            if "\\n" in pk and "\n" not in pk:
                print("⚠️ Private Key contains literal '\\n' but no actual newlines. It might need replacement.")
            elif "\n" not in pk:
                print("❌ Private Key has no newlines!")
            else:
                print("✅ Private Key seems to have newlines.")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_structure()
