import psycopg2
import os
import random
from dotenv import load_dotenv
from pathlib import Path

# Load env from backend folder
env_path = Path('backend/.env').absolute()
load_dotenv(dotenv_path=env_path)

def connect_db():
    try:
        db_url = os.getenv("DB_URL")
        # Force sslmode disable for local local hack
        if "sslmode=disable" not in db_url and "localhost" in db_url:
             db_url += "?sslmode=disable"
        
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"Connect error: {e}")
        return None

def populate_memory():
    conn = connect_db()
    if not conn:
        print("DB Connection failed")
        return

    cur = conn.cursor()
    
    # Check if empty
    cur.execute("SELECT COUNT(*) FROM agent_memory")
    count = cur.fetchone()[0]
    
    if count > 5:
        print(f"DB already has {count} memories. Skipping population.")
        return

    print("Populating synthetic memories...")
    
    memories = [
        "Analysis of OpenAI o1 model architecture | Tags: AI, MODEL, LLM | Insight: New reasoning capabilities surpass CoT.",
        "SpaceX Starship orbital test success | Tags: SPACE, FUTURE, TECH | Insight: Significant reduction in payload cost to LEO.",
        "Quantum computing breakthrough in error correction | Tags: QUANTUM, PHYSICS, TECH | Insight: 99.9% fidelity reached in 2-qubit gates.",
        "Cybersecurity report: rise of AI-driven phishing | Tags: SECURITY, CYBER, AI | Insight: Automated social engineering at scale.",
        "New battery tech doubles EV range | Tags: ENERGY, TECH, FUTURE | Insight: Solid state batteries nearing production readiness.",
        "Google Deepmind releases Gemini 2.0 technical report | Tags: AI, MODEL, GOOGLE | Insight: Multimodal capabilities expanded.",
        "Zero-day exploit found in popular web server | Tags: SECURITY, ZERO-DAY, EXPLOIT | Insight: Immediate patching required globally.",
        "NASA announces new lunar outpost plans | Tags: SPACE, NASA, FUTURE | Insight: Permanent human presence on Moon by 2030."
    ]

    for mem in memories:
        cur.execute("INSERT INTO agent_memory (content, embedding) VALUES (%s, %s)", (mem, "[0.1, 0.2]"))
    
    conn.commit()
    print("Added 8 synthetic memory nodes.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    populate_memory()
