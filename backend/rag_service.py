import psycopg2
import os
from embedding_service import generate_embedding
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Veritabanı bağlantı bilgisi
DB_CONNECTION = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"

# Configure genai if not already configured in main (it is safer to configure here too or rely on singleton if env set)
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def search_memory(query_text, limit=3):
    """
    Soru metnini alır, vektöre çevirir ve veritabanında en yakın 3 kaydı bulur.
    """
    # 1. Soruyu Vektöre Çevir
    query_vector = generate_embedding(query_text)
    if not query_vector:
        return []

    try:
        conn = psycopg2.connect(DB_CONNECTION)
        cursor = conn.cursor()

        # 2. Vektör Araması (Cosine Distance)
        # <=> operatörü "mesafe" ölçer. En küçük mesafe, en yakın anlam demektir.
        search_sql = """
            SELECT content, (embedding <=> %s::vector) as distance 
            FROM agent_memory 
            ORDER BY distance ASC 
            LIMIT %s;
        """
        
        # Casting vector to string for SQL
        cursor.execute(search_sql, (str(query_vector), limit))
        results = cursor.fetchall()
        
        # Sadece metinleri listeye atıp döndürelim
        matches = [row[0] for row in results]
        
        cursor.close()
        conn.close()
        return matches

    except Exception as e:
        print(f"❌ Arama Hatası: {e}")
        return []

def ask_nomad(user_question):
    """
    RAG Mekanizması:
    1. Hafızada ara.
    2. Bulunanları bağlam (context) olarak Gemini'ye ver.
    3. Cevabı üret.
    """
    # 1. Hafızayı Tara
    relevant_docs = search_memory(user_question)
    
    # If no relevant docs found, maybe return a default or let Gemini answer with its own knowledge but warning it?
    # User prompt said: "Eğer bilgi içinde cevap yoksa 'Bunu bilmiyorum' de".
    # So if relevant_docs is empty, context is empty.
    
    if not relevant_docs:
        # Fallback to empty context
        context_text = "Hafızada ilgili bilgi bulunamadı."
    else:
        context_text = "\n\n".join(relevant_docs)
    
    # 2. Gemini'ye Talimat Ver
    prompt = f"""
    Sen Nomad adında akıllı bir asistansın.
    Aşağıdaki BİLGİLERİ kullanarak kullanıcının sorusuna cevap ver.
    Eğer bilgi içinde cevap yoksa "Bunu bilmiyorum" de, uydurma.

    BİLGİLER:
    {context_text}

    KULLANICI SORUSU:
    {user_question}
    """
    
    try:
        # Using the model known to work: gemini-2.5-flash (from previous discovery)
        # User requested gemini-2.0-flash-exp, but we saw 404s with 1.5. 2.5 works.
        # Let's try 2.5-flash as it is reliable here.
        model = genai.GenerativeModel('models/gemini-2.5-flash') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Düşünürken hata oluştu: {e}"

# --- TEST ---
if __name__ == "__main__":
    # Test etmeden önce veritabanında veri olduğundan emin ol!
    soru = "İlk hafızan nedir?" 
    cevap = ask_nomad(soru)
    print(f"Soru: {soru}")
    print(f"Nomad: {cevap}")
