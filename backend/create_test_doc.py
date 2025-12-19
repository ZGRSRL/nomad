import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from drive_service import upload_html_as_doc
from dotenv import load_dotenv

load_dotenv()

print("--- UPLOADING TEST ARTICLE ---")
title = "Nomad Intelligence: Test Report (User OAuth)"
content = """
<h1>Nomad System Verification</h1>
<p>This document confirms that the Nomad Intelligence system can now successfully create reports in your Google Drive.</p>
<ul>
    <li><b>Auth Method:</b> OAuth 2.0 (User Quota)</li>
    <li><b>Status:</b> Operational</li>
    <li><b>Timestamp:</b> 2025-12-18</li>
</ul>
<p>End of report.</p>
"""

result = upload_html_as_doc(title, content)
print("\n--- RESULT ---")
print(result)
