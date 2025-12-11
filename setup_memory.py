import psycopg2
import sys

# Bağlantı ayarları
conn_string = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"

try:
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # 1. Eski Tabloyu Temizle (Drop)
    # Şema değiştiği için eskisini siliyoruz.
    drop_query = "DROP TABLE IF EXISTS agent_memory;"
    cursor.execute(drop_query)
    print("🗑️ Eski tablo silindi (varsa).")

    # 2. Yeni Tabloyu Oluştur (768 Boyutlu)
    # text-embedding-004 = 768 dimensions
    create_table_query = """
    CREATE TABLE agent_memory (
        id bigserial PRIMARY KEY,
        content text,
        embedding vector(768),
        created_at timestamp DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    print("✅ 'agent_memory' tablosu YENİDEN oluşturuldu (vector(768)).")

    conn.commit()
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Hata: {e}")
    sys.exit(1)
