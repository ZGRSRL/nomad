
# Merge env vars safely in python
import os

# Base vars
env_content = """DB_HOST=db.twfyvroqefyhhlasdkdn.supabase.co
DB_USER=postgres
DB_PASSWORD=Fm5%g69!jnnVgQn
DB_NAME=postgres
DB_URL=postgresql://postgres:Fm5%g69!jnnVgQn@db.twfyvroqefyhhlasdkdn.supabase.co:5432/postgres?sslmode=require
GEMINI_API_KEY=AIzaSyD9hWJ3U3kQ_ySRHjVRXN9Ng4iOk4UsYFM
"""

# Read drive creds
try:
    with open('temp_drive_creds.env', 'r', encoding='utf-8') as f:
        drive_creds = f.read()
    
    # Combine
    full_content = env_content.strip() + "\n" + drive_creds.strip()
    
    with open('temp_clean.env', 'w', encoding='utf-8') as f:
        f.write(full_content)
        
    print("✅ Created temp_clean.env")
except Exception as e:
    print(f"Error: {e}")
