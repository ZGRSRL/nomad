import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env yükle (API anahtarı için)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # Eğer doğrudan çalıştırılırsa ve env yüklü değilse uyarı ver
    # ama modül olarak import edilirse çağıranın yüklemesi beklenir.
    print("UYARI: Embedding servisi için API Key bulunamadı.")

else:
    genai.configure(api_key=API_KEY)

def generate_embedding(text: str):
    """
    Verilen metnin Gemini text-embedding-004 modelini kullanarak
    vektör karşılığını (embedding) döndürür.
    """
    try:
        if not API_KEY:
            raise ValueError("API Key eksik.")
            
        # text-embedding-004 modeli, retrieval_document task type'ı ile dökümanları vektörleştirir.
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
            title="Nomad Memory"
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding Üretme Hatası: {e}")
        return None

if __name__ == "__main__":
    # Test Bloğu
    print("🌉 Babil Kulesi (Embedding Bridge) Test Ediliyor...")
    test_metni = "Yapay zeka geleceği şekillendiriyor."
    
    print(f"Metin: {test_metni}")
    vector = generate_embedding(test_metni)
    
    if vector:
        print(f"✅ Başarılı! Vektör üretildi.")
        print(f"📏 Boyut: {len(vector)} (Standart Gemini Boyutu)")
        print(f"🔢 İlk 5 değer: {vector[:5]}")
    else:
        print("❌ Başarısız. API Key veya Model hatası olabilir.")
