import sys
import os

# Add backend directory to path so we can import drive_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from drive_service import upload_html_as_doc, get_drive_service

print("--- Starting Drive Permission Test ---")

# 1. Test Service/Auth first
service = get_drive_service()
if not service:
    print("FATAL: Could not authenticate.")
    sys.exit(1)

# 2. Get About info to see email
try:
    about = service.about().get(fields="user").execute()
    email = about['user']['emailAddress']
    print(f"Authenticated as: {email}")
except Exception as e:
    print(f"Could not get user info: {e}")

# 3. Try Upload
title = "ANTIGRAVITY_PERMISSION_TEST"
content = "<h1>Hello</h1><p>This is a test upload to verify permissions.</p>"

print(f"Attempting upload to hardcoded folder...")
result = upload_html_as_doc(title, content)

print("--- Result ---")
print(result)

if result['status'] == 'success':
    print("\nSUCCESS: Permissions are correct! Review content in Drive.")
else:
    print("\nFAILURE: Still encountering issues.")
