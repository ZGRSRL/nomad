import feedparser
from datetime import datetime
import time

# Kaynak Listesi
RSS_FEEDS = {
    "AI / TECH": [
        "https://www.wired.com/feed/category/ai/latest/rss",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/index.xml"
    ],
    "SCIENCE": [
        "https://www.sciencedaily.com/rss/top/science.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"
    ],
    "CYBERSEC": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://krebsonsecurity.com/feed/"
    ]
}

def fetch_feeds(category="ALL"):
    articles = []
    
    target_feeds = []
    if category == "ALL":
        for cat in RSS_FEEDS:
            target_feeds.extend([(url, cat) for url in RSS_FEEDS[cat]])
    elif category in RSS_FEEDS:
        target_feeds = [(url, category) for url in RSS_FEEDS[category]]
    
    # Hepsini çek (Gerçek hayatta async olması daha iyi olur ama şimdilik basit tutuyoruz)
    for url, cat in target_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]: # Her kaynaktan en son 3 haberi al
                
                # Tarih formatlama
                published = entry.get("published", "Just now")
                
                articles.append({
                    "id": entry.get("id", entry.link),
                    "source": feed.feed.get("title", "Unknown Source")[:15].upper(), # Kısa isim
                    "category": cat,
                    "title": entry.title,
                    "link": entry.link,
                    "time": published[:16], # Sadece tarihi al, saati kırp
                    "summary": entry.get("summary", "")[:200] + "...", # Ön izleme
                    "isLive": True
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            
    return articles
