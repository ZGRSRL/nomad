import feedparser
import requests

url = "https://evrimagaci.org/kategori/kriminoloji-396/rss.xml"
print(f"Testing URL: {url}")

try:
    # 1. Standard Feedparser
    print("\n--- Method 1: Standard feedparser ---")
    feed = feedparser.parse(url)
    print(f"Bozo (Error): {feed.bozo}")
    if feed.bozo:
        print(f"Bozo Exception: {feed.bozo_exception}")
    print(f"Entries: {len(feed.entries)}")
    if feed.entries:
        print(f"First Entry: {feed.entries[0].title}")

    # 2. Requests with User-Agent
    print("\n--- Method 2: Requests with User-Agent ---")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        feed2 = feedparser.parse(response.content)
        print(f"Entries: {len(feed2.entries)}")
    else:
        print("Failed to fetch via requests")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
