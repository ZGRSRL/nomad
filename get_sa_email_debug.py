
import os
import json
import base64

filename = 'temp_drive_creds.env'
print(f"Reading {filename}...")

try:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    print(f"File content length: {len(content)}")
    
    if "=" in content:
        key, b64_val = content.split('=', 1)
        b64_val = b64_val.strip()
        print(f"Key: {key}")
        print(f"B64 Val Snippet: {b64_val[:30]}...")
        
        # Fix padding
        missing_padding = len(b64_val) % 4
        if missing_padding:
            b64_val += '=' * (4 - missing_padding)
            
        decoded_bytes = base64.b64decode(b64_val)
        decoded_str = decoded_bytes.decode('utf-8')
        print(f"Decoded snippet: {decoded_str[:50]}...")
        
        creds = json.loads(decoded_str)
        print(f"SERVICE_ACCOUNT_EMAIL: {creds.get('client_email')}")
        
    else:
        print("No '=' found in file.")

except Exception as e:
    print(f"ERROR: {e}")
