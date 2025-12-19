
import os
import json
import base64

# Manual parsing of cloud_env.txt to avoid dotenv issues
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
    try:
        # Fix padding
        missing_padding = len(b64_val) % 4
        if missing_padding:
            b64_val += '=' * (4 - missing_padding)
            
        json_str = base64.b64decode(b64_val).decode('utf-8')
        creds = json.loads(json_str)
        print(f"SERVICE_ACCOUNT_EMAIL: {creds.get('client_email')}")
    except Exception as e:
        print(f"Error decoding: {e}")
else:
    print("Could not find GOOGLE_CREDENTIALS_JSON_B64 in cloud_env.txt")
