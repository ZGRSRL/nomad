
import sys
from drive_service import get_drive_service

def check_quota():
    service = get_drive_service()
    if not service:
        print("Failed to authenticate with Drive API.")
        return

    try:
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get('storageQuota', {})
        
        limit = int(quota.get('limit', 0))
        usage = int(quota.get('usage', 0))
        usage_in_drive = int(quota.get('usageInDrive', 0))
        usage_in_trash = int(quota.get('usageInTrash', 0))
        
        limit_gb = limit / (1024**3)
        usage_gb = usage / (1024**3)
        
        print(f"--- Google Drive Storage Diagnostic ---")
        if limit > 0:
            print(f"Total Limit: {limit_gb:.2f} GB")
            print(f"Total Usage: {usage_gb:.2f} GB_")
            print(f"Percent Used: {(usage/limit)*100:.1f}%")
        else:
            print("Total Limit: Unlimited (or unknown)")
            print(f"Total Usage: {usage_gb:.2f} GB")
            
        print(f"Usage details:")
        print(f"  - In Drive: {usage_in_drive / (1024**3):.2f} GB")
        print(f"  - In Trash: {usage_in_trash / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"Error checking quota: {e}")

if __name__ == "__main__":
    check_quota()
