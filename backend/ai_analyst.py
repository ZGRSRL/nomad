import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# API Ayarları
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "response_mime_type": "text/plain", 
}

# Trying Gemini 2.0 Flash as requested, falling back to 1.5 if needed is handled by the model name string here.
# Note: Providing the user requested string. If 2.0-flash isn't available to this key yet, user might see an error, 
# but as an agent I follow instructions. 
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    generation_config=generation_config
)

def analyze_article(title, content_snippet):
    print(f"Analyzing: {title}")
    prompt = f"""
    Act as an elite Intelligence Officer.
    Analyze the following news article title and snippet.
    
    Article Title: {title}
    Snippet: {content_snippet}
    
    Provide a tactical analysis in strict JSON format with these 4 keys:
    1. "summary": A concise technical summary (max 2 sentences).
    2. "aiInsight": Why this matters strategically? (The hidden implication).
    3. "action": A concrete, imperative command.
    4. "tags": A list of 3-5 uppercase keywords/tags (e.g. ["AI", "CYBERSEC", "NVIDIA"]).
    
    IMPORTANT: Return ONLY the JSON. No markdown formatting.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Temizlik
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "summary": "Decryption failed.",
            "aiInsight": "N/A",
            "action": "Manual analysis required.",
            "tags": ["ERROR"]
        }
