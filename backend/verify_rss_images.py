import rss_service
import os
from dotenv import load_dotenv

load_dotenv()

def verify_images():
    print("🚀 Verifying RSS Image Extraction...")
    
    # 1. Fetch Feeds
    # Using 'ALL' to test all configured feeds
    print("Fetching feeds from database...")
    articles = rss_service.fetch_feeds("ALL")
    
    if not articles:
        print("❌ No articles found. Check DB connection or Feed URLs.")
        return

    total = len(articles)
    with_image = 0
    
    print(f"\n📊 Analyzed {total} Articles:\n")
    
    for article in articles:
        has_img = article.get('image_url') is not None
        if has_img:
            with_image += 1
            print(f"✅ [IMG] {article['source']}: {article['title'][:50]}...")
            print(f"   -> {article['image_url']}")
        else:
            print(f"⚠️ [NO IMAGE] {article['source']}: {article['title'][:50]}...")
    
    print(f"\n📈 Result: {with_image}/{total} articles have images.")
    
    if with_image == 0:
        print("❌ CRITICAL: No images extracted. Logic needs review.")
    elif with_image < total * 0.5:
        print("⚠️ WARNING: Less than 50% coverage. Might be normal for text-heavy feeds.")
    else:
        print("✅ SUCCESS: Strong visual coverage.")

if __name__ == "__main__":
    verify_images()
