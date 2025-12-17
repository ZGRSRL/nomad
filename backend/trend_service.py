import re
from collections import Counter
import random

# Common stopwords to ignore
STOPWORDS = {
    'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 
    'with', 'by', 'from', 'as', 'it', 'this', 'that', 'new', 'how', 'why', 'what', 'updates', 'daily',
    'more', 'about', 'can', 'will', 'not', 'be', 'has', 'have', 'news', 'report', 'video', 'post'
}

CRITICAL_KEYWORDS = {'ZERO-DAY', 'RANSOMWARE', 'BREACH', 'VULNERABILITY', 'ATTACK', 'APT', 'MALWARE', 'EXPLOIT'}

def analyze_trends(articles):
    """
    Analyzes a list of articles to find trending keywords and simulate velocity.
    """
    text_blob = ""
    for art in articles:
        text_blob += f" {art.get('title', '')} {art.get('summary', '')}"
    
    # Clean and tokenize
    words = re.findall(r'\b\w+\b', text_blob.lower())
    
    # Filter stopwords and short words
    filtered_words = [w for w in words if w not in STOPWORDS and len(w) > 3]
    
    # Count frequency
    counts = Counter(filtered_words)
    
    # Get top 20
    top_common = counts.most_common(20)
    
    trends = []
    for word, count in top_common:
        # Simulate velocity/trend change for the UI effect since we don't have historical db yet
        # In a real system, this would compare t(now) vs t(yesterday)
        velocity = random.randint(-20, 150)
        direction = 'up' if velocity >= 0 else 'down'
        
        is_critical = word.upper() in CRITICAL_KEYWORDS or velocity > 100
        
        trends.append({
            "topic": word.upper(),
            "count": count,
            "velocity": abs(velocity),
            "direction": direction,
            "is_critical": is_critical
        })
        
    # Always inject a few critical cyber terms if not found (for demo/flavor)
    if not any(t['is_critical'] for t in trends):
        trends.insert(0, {"topic": "ZERO-DAY", "count": 5, "velocity": 85, "direction": "up", "is_critical": True})
        
    return trends[:10]
