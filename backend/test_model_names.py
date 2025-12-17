
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY not found in env.")
    exit(1)

genai.configure(api_key=API_KEY)

model_names = [
    "models/gemini-2.5-flash",
    "gemini-2.5-flash",
    "models/gemini-2.0-flash-exp",
    "gemini-2.0-flash-exp",
    "models/gemini-1.5-flash",
    "gemini-1.5-flash",
    "models/gemini-pro",
    "gemini-pro"
]


print(f"Testing models with API Key ending in ...{API_KEY[-4:]}")

with open("model_test_result.txt", "w", encoding="utf-8") as f:
    f.write(f"Testing models with API Key ending in ...{API_KEY[-4:]}\n")
    
    for model_name in model_names:
        print(f"Testing model: {model_name}")
        f.write(f"\nTesting model: {model_name}\n")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"SUCCESS: {model_name}")
            f.write(f"SUCCESS: {model_name} works!\n")
        except Exception as e:
            print(f"FAILED: {model_name}")
            f.write(f"FAILED: {model_name} - {e}\n")

