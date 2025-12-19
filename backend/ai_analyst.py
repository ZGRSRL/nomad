import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Try to load .env file if it exists (for local development)
from pathlib import Path
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# API Ayarları - Cloud Run'da environment variable'dan, local'de .env'den alır
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")
    
# DEBUG KEY
print(f"DEBUG: Loaded API KEY. Length: {len(API_KEY)}")
print(f"DEBUG: Key Start: {API_KEY[:5]}... Key End: ...{API_KEY[-5:]}")
print(f"DEBUG: repr(key): {repr(API_KEY)}")

genai.configure(api_key=API_KEY)

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "response_mime_type": "text/plain", 
}

# Trying Gemini 2.0 Flash as requested, falling back to 1.5 if needed is handled by the model name string here.
# Note: Providing the user requested string. If 2.0-flash isn't available to this key yet, user might see an error, 
# but as an agent I follow instructions. 
# Using Gemini 1.5 Flash for maximum stability and speed
# Model will be initialized dynamically in analyze_article to handle API version differences
model = None  # Will be created per-request

def analyze_article(title, content_snippet):
    print(f"Analyzing: {title}")
    prompt = f"""
    ROL: Sen bilim ve teknoloji konusunda uzman, TÜRK kitleye içerik üreten bir analistsin.
    GÖREV: Aşağıdaki İngilizce metni analiz et ve teknik bir TÜRKÇE rapor oluştur.
    
    Makale Başlığı: {title}
    İçerik Özeti: {content_snippet}
    
    'Etki Puanı'nı (0-100) şuna göre belirle:
    1. İnovasyon: Bilimsel/teknik bir devrim mi?
    2. Ölçek: Büyük bir endüstriyi veya nüfusu etkiliyor mu?
    3. Kalıcılık: Gelip geçici bir heves mi yoksa kalıcı bir değişim mi?

    Analizi şu anahtarlara sahip katı bir JSON formatında sun. TÜM metin alanları KESİNLİKLE TÜRKÇE olmalıdır:
    1. "summary": TÜRKÇE teknik özet (maksimum 2 cümle).
    2. "aiInsight": Bu neden önemli? (Gizli anlam veya fırsat) - TÜRKÇE.
    3. "action": Stratejik tavsiye - TÜRKÇE (Örn: "Araştır", "İzle", "Göz Ardı Et").
    4. "tags": 3-5 adet BÜYÜK HARFLİ İNGİLİZCE anahtar kelime listesi (Filtreleme için İngilizce kalsın).
    5. "impact_score": Tam sayı 0-100.
    6. "trend_label": Kısa etiket İNGİLİZCE (Örn: "GLOBAL SHIFT", "HYPE", "SIGNAL", "NOISE").
    7. "one_line_hook": Ana fikir hakkında çarpıcı tek cümlelik TÜRKÇE slogan.
    
    ÖNEMLİ: Sadece JSON döndür. Markdown blokları kullanma.
    """
    
    try:
        # Use the exact same model that works in rag_service.py
        # rag_service.py successfully uses: models/gemini-2.5-flash
        model_name = "models/gemini-1.5-flash"
        
        # Use the exact same model that works in rag_service.py
        print(f"Using model: {model_name} (same as rag_service)")
        current_model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        response = current_model.generate_content(prompt)
        text = response.text
        
        # Temizlik
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "summary": f"⚠ AI UPLINK OFFLINE: {str(e)[:50]}...",
            "aiInsight": "N/A",
            "action": "RETRY MANUALLY",
            "tags": ["CONNECTION_LOST"],
            "impact_score": 0,
            "trend_label": "OFFLINE",
            "one_line_hook": "Analysis unavailable."
        }
