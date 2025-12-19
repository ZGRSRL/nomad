import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_analyst import analyze_article

print("--- TESTING TURKISH SUMMARY ---")
title = "SpaceX Starship Launch Success"
content = """
SpaceX has successfully launched its massive Starship rocket, marking a major milestone in space exploration. 
The vehicle achieved orbit and completed its objectives. Elon Musk stated this brings Mars colonization close.
Technological advancements in the raptor engines were significant.
"""

print(f"Input Title: {title}")
print("Analyzing...")

try:
    result = analyze_article(title, content)
    print("\n--- RESULT JSON ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Simple validation
    summary = result.get('summary', '')
    print(f"\nSummary Language Check: {summary}")
    
except Exception as e:
    print(f"Error: {e}")
