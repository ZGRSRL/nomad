
import os

try:
    # Try utf-16 first as reported
    with open('cloud_env.txt', 'r', encoding='utf-16') as f:
        content = f.read()
except:
    # Fallback to utf-8
    with open('cloud_env.txt', 'r', encoding='utf-8') as f:
        content = f.read()

for line in content.splitlines():
    if "GOOGLE_CREDENTIALS_JSON_B64" in line:
        key, val = line.strip().split('=', 1)
        print(f"{key}={val}")
        # Write to a clean .env file for usage
        with open('temp_drive_creds.env', 'w', encoding='utf-8') as f_out:
            f_out.write(f"{key}={val}\n")
        print("✅ Credentials extracted to temp_drive_creds.env")
