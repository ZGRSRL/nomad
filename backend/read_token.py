import pickle
import os
import sys

# Define path
token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.pickle')

if not os.path.exists(token_path):
    print("FATAL: token.pickle not found.")
    sys.exit(1)

try:
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
        
    print(f"Refresh Token: {creds.refresh_token}")
except Exception as e:
    print(f"Error reading token: {e}")
