
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv('temp_full.env') # Use the env file we created locally

creds_b64 = os.getenv("GOOGLE_CREDENTIALS_JSON_B64")
if creds_b64:
    try:
        # Fix padding if needed
        missing_padding = len(creds_b64) % 4
        if missing_padding:
            creds_b64 += '=' * (4 - missing_padding)
            
        json_str = base64.b64decode(creds_b64).decode('utf-8')
        creds = json.loads(json_str)
        print(f"SERVICE ACCOUNT EMAIL: {creds.get('client_email')}")
    except Exception as e:
        print(f"Error decoding: {e}")
else:
    print("No B64 creds found in env")
