import requests
from bs4 import BeautifulSoup

def scrape_url(url: str):
    """
    Fetches the content of a URL and extracts the main text.
    Returns a dictionary with 'title' and 'content' or raises an exception.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Extract title
        title = soup.title.string.strip() if soup.title else url
        
        # Extract text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long (to avoid token limits in AI)
        # 10,000 characters is usually enough for a good summary
        if len(clean_text) > 10000:
             clean_text = clean_text[:10000] + "..."
             
        return {
            "title": title,
            "content": clean_text,
            "url": url
        }
        
    except Exception as e:
        print(f"Scrape Error: {e}")
        return None
