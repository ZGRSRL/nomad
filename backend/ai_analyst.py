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
    Analyze this article for a tech-savvy user interested in AI, Science, and Global Innovation.
    
    Article Title: {title}
    Snippet: {content_snippet}
    
    Determine the 'Impact Score' (0-100) based on:
    1. Innovation: Is this a scientific/tech breakthrough?
    2. Scale: Does it affect a large industry or population?
    3. Longevity: Is this a fleeting hype or a long-term shift?

    Provide the analysis in strict JSON format with these keys:
    1. "summary": Concise technical summary (max 2 sentences).
    2. "aiInsight": Why does this matter? (The hidden implication or opportunity).
    3. "action": A strategic recommendation (e.g. "Investigate", "Monitor", "Ignore").
    4. "tags": List of 3-5 uppercase keywords.
    5. "impact_score": Integer 0-100. (80+ = Global Shift, 50-79 = Industry Update, <50 = Niche).
    6. "trend_label": Short badge text (e.g. "GLOBAL SHIFT", "HYPE", "SIGNAL", "NOISE").
    7. "one_line_hook": A catchy, single-sentence hook about the core value.
    
    IMPORTANT: Return ONLY the JSON.
    """
    
    try:
        # Use the exact same model that works in rag_service.py
        # rag_service.py successfully uses: models/gemini-2.5-flash
        model_name = "models/gemini-2.5-flash"
        
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
