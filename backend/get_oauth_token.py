#!/usr/bin/env python3
"""
OAuth 2.0 Refresh Token almak için script
Bir kere çalıştır, refresh token'ı kopyala
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# OAuth 2.0 Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_refresh_token():
    """OAuth flow ile refresh token al"""
    creds = None
    
    # Token dosyası varsa yükle
    token_file = 'token.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh token yoksa veya geçersizse yeni al
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # OAuth credentials dosyası gerekli
            client_secrets_file = 'oauth_credentials.json'
            
            if not os.path.exists(client_secrets_file):
                print("❌ oauth_credentials.json bulunamadı!")
                print("\nOAuth credentials oluştur:")
                print("1. Google Cloud Console → APIs & Services → Credentials")
                print("2. CREATE CREDENTIALS → OAuth client ID")
                print("3. Application type: Desktop app")
                print("4. JSON'u indir ve 'oauth_credentials.json' olarak kaydet")
                return None
            
            # OAuth flow (hem "installed" hem "web" formatını destekler)
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            # Local server ile OAuth flow başlat
            # Port 8081 (Ekrandaki listede var)
            print("OAuth flow baslatiliyor...")
            print("Port: 8081")
            print("OAuth client'ta http://localhost:8081 redirect URI olarak tanımlı olmalı.")
            
            # STRICT MODE: Fallback yok. Random port yok.
            # Kullanıcı isteği üzerine browser otomatik açılıyor
            # Explicitly set redirect_uri to what we expect to match Console
            expected_uri = "http://localhost:8081/"
            print(f"\n⚠️ BEKLENEN REDIRECT URI: {expected_uri}")
            print(f"Lütfen Google Cloud Console'da BU ADRESİN ekli olduğundan emin olun (sonundaki / dahil).")
            
            creds = flow.run_local_server(port=8081, prompt='consent', open_browser=True)
        
        # Token'ı kaydet
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    # Refresh token'ı göster
    if creds.refresh_token:
        print("\n✅ REFRESH TOKEN ALINDI!")
        print("\n" + "="*60)
        print("REFRESH TOKEN:")
        print("="*60)
        print(creds.refresh_token)
        print("="*60)
        print("\nBu token'ı Cloud Run'da GOOGLE_REFRESH_TOKEN environment variable olarak kullan")
        print("Client ID ve Client Secret'ı da GOOGLE_CLIENT_ID ve GOOGLE_CLIENT_SECRET olarak ekle")
        return creds.refresh_token
    else:
        print("❌ Refresh token alınamadı")
        return None

if __name__ == "__main__":
    print("=== OAUTH 2.0 REFRESH TOKEN ALMA ===\n")
    get_refresh_token()

