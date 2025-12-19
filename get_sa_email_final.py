
import os
import json
import base64
import ast

print("Extracting Service Account Email with AST...")

# Read original source to be safe
try:
    with open('cloud_env.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    with open('cloud_env.txt', 'r', encoding='utf-8') as f:
        content = f.read()

found_creds = False
for line in content.splitlines():
    line = line.strip()
    if "GOOGLE_CREDENTIALS_JSON_B64" in line:
        try:
            # Try to parse as python dict literal
            data = ast.literal_eval(line)
            if isinstance(data, dict) and data.get('name') == 'GOOGLE_CREDENTIALS_JSON_B64':
                b64_val = data.get('value')
                print("Found B64 via AST.")
                found_creds = True
                break
        except:
            # Fallback for simple KEY=VALUE
            if "=" in line:
                 parts = line.split("=", 1)
                 b64_val = parts[1].strip()
                 print("Found B64 via Split.")
                 found_creds = True
                 break

if found_creds and b64_val:
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
    print("Could not find/parse credentials.")
