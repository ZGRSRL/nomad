import subprocess
import requests

try:
    # Get URL
    url = subprocess.check_output(
        'gcloud run services describe nomad-backend --region europe-west1 --format "value(status.url)"',
        shell=True, cwd=r'd:\Nomad'
    ).decode().strip()
    
    print(f"CAPTURED URL: {url}")
    
    # Verify
    try:
        r = requests.get(f"{url}/stats", timeout=10)
        print(f"HEALTH CHECK: {r.status_code}")
        print(f"STATS: {r.json()}")
    except Exception as e:
        print(f"HEALTH CHECK FAILED: {e}")
        
    # Save for reading
    with open("cloud_url.txt", "w") as f:
        f.write(url)

except Exception as e:
    print(f"ERROR: {e}")
