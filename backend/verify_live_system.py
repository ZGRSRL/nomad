import requests
import json

BASE_URL = "https://nomad-backend-49856050254.europe-west1.run.app"

def check_stats():
    print("\n[ CHECKING /stats ]")
    try:
        r = requests.get(f"{BASE_URL}/stats", timeout=10)
        data = r.json()
        print(f"Status Code: {r.status_code}")
        print(f"System Status: {data.get('system_status')} (Expected: OPTIMIZED)")
        print(f"Top Trend: {data.get('top_trend')}")
        print(f"Total Sources: {data.get('total_sources')}")
        return data.get('system_status') == "OPTIMIZED"
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_feeds():
    print("\n[ CHECKING /feeds ]")
    try:
        r = requests.get(f"{BASE_URL}/feeds", timeout=15)
        # Handle potential empty list or error dict
        data = r.json()
        count = len(data) if isinstance(data, list) else 0
        print(f"Status Code: {r.status_code}")
        print(f"Feeds Retrieved: {count}")
        if count > 0:
            print(f"Sample: {data[0].get('title', 'No Title')} ({data[0].get('source')})")
        return count > 0
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    stats_ok = check_stats()
    feeds_ok = check_feeds()
    
    print("\n--- REPORT ---")
    if stats_ok:
        print("✅ Backend Optimization: ACTIVE (Running SQL Analysis)")
    else:
        print("❌ Backend Optimization: INACTIVE or FAILED")
        
    if feeds_ok:
        print("✅ RSS Feed Service: REPAIRED (Fetching Live Data)")
    else:
        print("❌ RSS Feed Service: EMPTY (Still having connection/parse issues)")
