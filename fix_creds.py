import os
import json

source = r"d:\Tuygun\backend\credentials.json"
dest = r"d:\Nomad\backend\credentials.json"

try:
    # Try reading as UTF-16 (common on Windows if created via some tools)
    try:
        with open(source, 'r', encoding='utf-16') as f:
            content = f.read()
        print("Read as UTF-16")
    except:
        # Fallback to default/utf-8 if utf-16 fails
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        print("Read as UTF-8")

    # Clean BOM if present (utf-8-sig handles it but we force strip to be sure)
    msg = content.lstrip('\ufeff')
    
    # Parse to ensure validity
    data = json.loads(msg)
    
    # Write back as clean enc-less UTF-8
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("FIX SUCCESS: Clean JSON written to destination.")

except Exception as e:
    print(f"FIX ERROR: {e}")
