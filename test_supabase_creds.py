
import psycopg2
import sys

# Combinations to test
host = "db.twfyvroqefyhhlasdkdn.supabase.co"
user = "postgres"
pwd = "Fm5%g69!jnnVgQn"
dbs = ["postgres"]

print(f"--- TESTING VERIFIED HOST: {host} ---")
try:
    print(f"Attempting connection to {dbs[0]}...")
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=pwd,
        dbname=dbs[0],
        port=5432,
        connect_timeout=10,
        sslmode='require'
    )
    print(f"✅ SUCCESS! Connected.")
    conn.close()
    
    # Write valid config
    with open("valid_cloud_config.txt", "w") as f:
        f.write(f"DB_HOST={host}\nDB_USER={user}\nDB_PASSWORD={pwd}\nDB_NAME={dbs[0]}")
    sys.exit(0)

except Exception as e:
    # Safe error printing
    print(f"❌ Failed: {repr(e)}")
    sys.exit(1)
