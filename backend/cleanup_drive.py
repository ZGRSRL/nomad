#!/usr/bin/env python3
"""
Service Account'un Drive'ındaki dosyaları temizler
"""
import os
import sys
from drive_service import get_drive_service

def list_and_delete_files(service, max_files=100):
    """Drive'daki tüm dosyaları listeler ve siler"""
    try:
        # Tüm dosyaları listele
        results = service.files().list(
            pageSize=max_files,
            fields="files(id, name, size, createdTime)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print("✅ Drive boş, silinecek dosya yok")
            return
        
        print(f"📋 {len(items)} dosya bulundu:")
        total_size = 0
        
        for item in items:
            file_id = item['id']
            file_name = item.get('name', 'Unknown')
            file_size = item.get('size', '0')
            created = item.get('createdTime', 'Unknown')
            
            if file_size:
                total_size += int(file_size)
            
            print(f"  - {file_name} ({file_size} bytes, {created})")
        
        print(f"\n📊 Toplam: {len(items)} dosya, ~{total_size / 1024 / 1024:.2f} MB")
        
        # Kullanıcıya sor
        response = input("\n❓ Tüm dosyaları silmek istiyor musun? (evet/hayır): ")
        
        if response.lower() in ['evet', 'yes', 'y', 'e']:
            deleted = 0
            for item in items:
                try:
                    service.files().delete(fileId=item['id']).execute()
                    deleted += 1
                    print(f"  ✅ Silindi: {item.get('name', 'Unknown')}")
                except Exception as e:
                    print(f"  ❌ Silinemedi: {item.get('name', 'Unknown')} - {e}")
            
            print(f"\n✅ {deleted}/{len(items)} dosya silindi")
        else:
            print("❌ İşlem iptal edildi")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== SERVICE ACCOUNT DRIVE TEMİZLİĞİ ===\n")
    
    service = get_drive_service()
    if not service:
        print("❌ Drive service alınamadı!")
        sys.exit(1)
    
    list_and_delete_files(service)


