import psycopg2
import sys
from urllib.parse import quote_plus

# Raw Credentials
DB_HOST = "db.twfyvroqefyhhlasdkdn.supabase.co"
DB_PASS = "Fm5%g69!jnnVgQn]"
DB_USER = "postgres"
DB_NAME = "postgres"

# Construct URI with correct escaping
encoded_pass = quote_plus(DB_PASS)
uri = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:5432/{DB_NAME}?sslmode=require"

print(f"Testing connection with URI...")
# Do not print URI to avoid leaking encoded password if sensitive, but here needed for debug
print(f"User: {DB_USER}")
print(f"Pass Encoded: {encoded_pass}")

try:
    conn = psycopg2.connect(uri)
    print("SUCCESS: Connection established.")
    conn.close()
except Exception as e:
    print("FAILED:")
    print(e)
