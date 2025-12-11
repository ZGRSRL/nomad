import psycopg2

# Görseldeki connection string'i buraya uyarladık
conn_string = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"

try:
    print("🔌 Veritabanına bağlanılıyor...")
    connection = psycopg2.connect(conn_string)
    cursor = connection.cursor()
    
    # Basit bir sorgu ile test edelim
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    
    print(f"✅ Başarılı! Bağlandığın sürüm: {record[0]}")
    
    cursor.close()
    connection.close()
    
except Exception as error:
    print(f"❌ Hata oluştu: {error}")
