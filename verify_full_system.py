
import requests
import json
import random
import time

BASE_URL = "https://nomad-backend-49856050254.europe-west1.run.app"

def print_step(name):
    print(f"\n👉 {name}...")

def run_test():
    print(f"🚀 STARTING LIVE SYSTEM INTEGRITY CHECK: {BASE_URL}")

    # 1. DB SYNC
    print_step("1. Veritabanı Senkronizasyonu (/admin/init-db)")
    try:
        r = requests.get(f"{BASE_URL}/admin/init-db", timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # 2. ANALYZE (Zero-Day Scenario)
    print_step("2. AI Analiz Testi (High Impact)")
    payload = {
        "title": "GLOBAL MARKET CRASH: All Indices Down 20% in Single Session",
        "content": "Unprecedented sell-off triggered by quantum computing breakthrough decrypting major banking protocols. Central banks panic. Gold spikes."
    }
    analysis_result = None
    try:
        r = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=60)
        if r.status_code == 200:
            analysis_result = r.json()
            score = analysis_result.get('impact_score', 0)
            print(f"✅ Analysis Successful. Impact Score: {score}")
            print(f"Action Taken: {analysis_result.get('action_taken')}")
            
            # Check JSON keys
            print("Keys:", list(analysis_result.keys()))
        else:
            print(f"❌ Analysis Failed: {r.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. MEMORY SAVE
    if analysis_result:
        print_step("3. Hafıza Testi (/save)")
        try:
            save_payload = {
                "title": payload["title"],
                "url": "http://test-source.com/market-crash",
                "ai_insight": analysis_result.get("aiInsight"),
                "impact_score": analysis_result.get("impact_score"),
                "category": "Economy", # Testing prompt category
                "tags": analysis_result.get("tags")
            }
            # Adjust payload keys to match what /save expects if different
            # Looking at code might be needed or trial. Assuming standard keys.
            
            r = requests.post(f"{BASE_URL}/save", json=save_payload, timeout=10)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.json()}")
        except Exception as e:
            print(f"❌ Save Error: {e}")

    # 4. DASHBOARD STATS
    print_step("4. Dashboard Doğrulaması (/stats)")
    try:
        r = requests.get(f"{BASE_URL}/stats", timeout=10)
        data = r.json()
        print(f"Total Processed: {data.get('total_processed')}")
        print(f"Dominant Trend: {data.get('dominant_trend')}")
        print(f"High Impact Count: {data.get('high_impact_count')}")
        
        # Verify categoryvb logic didn't break trends
        trends = data.get('dominant_trend', [])
        if trends:
            print("✅ Trends Data Found (categoryvb works)")
        else:
            print("⚠️ No trends data (might be empty DB or standard mismatch)")
            
    except Exception as e:
        print(f"❌ Stats Error: {e}")

if __name__ == "__main__":
    run_test()
