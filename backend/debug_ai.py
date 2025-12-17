import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"FULL_KEY_DUMP:{key}")

if not key:
    print("CRITICAL: No API KEY found in environment!")
    exit(1)

genai.configure(api_key=key)

def test_model(name):
    print(f"\n--- Testing {name} ---")
    try:
        model = genai.GenerativeModel(name)
        response = model.generate_content("Hello, are you online?")
        print(f"SUCCESS. Response: {response.text}")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

test_model("gemini-1.5-flash")
test_model("gemini-2.0-flash")
