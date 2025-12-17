import requests
import psycopg2

BASE_URL = "http://127.0.0.1:8001"
DB_CONN = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"

def test_integration():
    test_text = "Entegrasyon testi için özel veri."
    
    # 1. Test /summarize
    print("Testing /summarize...")
    try:
        resp = requests.post(f"{BASE_URL}/summarize", json={"text": test_text})
        if resp.status_code == 200:
            print(f"✅ /summarize successful. Summary: {resp.json().get('summary')[:50]}...")
        else:
            print(f"❌ /summarize failed: {resp.text}")
    except Exception as e:
        print(f"❌ /summarize connection error: {e}")

    # 2. Test /save
    print("\nTesting /save...")
    try:
        resp = requests.post(f"{BASE_URL}/save", json={"text": test_text})
        if resp.status_code == 200:
            print(f"✅ /save successful. ID: {resp.json().get('id')}")
        else:
            print(f"❌ /save failed: {resp.text}")
    except Exception as e:
         print(f"❌ /save connection error: {e}")

    # 3. Verify DB
    print("\nVerifying Database Content...")
    try:
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute("SELECT content, embedding FROM agent_memory ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        
        if row and row[0] == test_text:
            print(f"✅ Database Verification Successful!")
            print(f"   Content: {row[0]}")
            # Check embedding dimension
            embedding_str = row[1]
            # pgvector returns string like "[0.01, ...]"
            # rough check
            dim = embedding_str.count(',') + 1
            print(f"   Embedding Dimension ~ {dim}")
            if dim == 768:
                print("   ✅ Dimension matches 768.")
            else:
                print(f"   ⚠️ Dimension mismatch? ({dim})")
        else:
            print(f"❌ Database verification failed. Last row: {row}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Error: {e}")

if __name__ == "__main__":
    test_integration()
