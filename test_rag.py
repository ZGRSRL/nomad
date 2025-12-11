import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_rag():
    print("🧠 RAG Testi Başlıyor...")
    
    # 1. Bilgi Ekle (Hafızaya At)
    fact = "Nomad'ın yaratıcısı Kaptan Özgür'dür."
    print(f"💾 Kaydediliyor: '{fact}'")
    try:
        resp = requests.post(f"{BASE_URL}/save", json={"text": fact})
        if resp.status_code == 200:
            print("✅ Bilgi hafızaya atıldı.")
        else:
            print(f"❌ Kayıt hatası: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # Biraz bekle (Embedding + DB işlemi için)
    time.sleep(1)

    # 2. Soru Sor (Hafızadan Çağır)
    question = "Senin yaratıcın kim?"
    print(f"❓ Soru Soruluyor: '{question}'")
    try:
        resp = requests.post(f"{BASE_URL}/ask", json={"question": question})
        if resp.status_code == 200:
            answer = resp.json().get("answer")
            print(f"🗣️ Nomad Cevabı: {answer}")
            
            if "Kaptan Özgür" in answer:
                print("✅ TEST BAŞARILI! Doğru ismi hatırladı.")
            else:
                print(f"⚠️ Cevap geldi ama beklenen isim yok gibi: {answer}")
        else:
            print(f"❌ Soru sorma hatası: {resp.text}")
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")

if __name__ == "__main__":
    test_rag()
