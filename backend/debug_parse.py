from urllib.parse import urlparse

url = "postgresql://postgres:Fm5%g69!jnnVgQn]@db.supabase.co:5432/postgres"

try:
    print(f"Parsing: {url}")
    result = urlparse(url)
    print(f"Password: {result.password}")
except Exception as e:
    print(f"Error: {e}")
