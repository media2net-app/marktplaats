#!/usr/bin/env python3
"""Test debug endpoint om alle producten in database te zien."""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env')

base_url = os.environ.get('API_BASE_URL') or os.getenv('API_BASE_URL', 'https://marktplaats-eight.vercel.app')
api_key = os.getenv('INTERNAL_API_KEY', 'LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=')

headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("🔍 Debug: Alle Producten in Database")
print("=" * 70)
print(f"API URL: {base_url}")
print()

try:
    response = requests.get(
        f"{base_url}/api/products/debug-all",
        headers=headers,
        params={'api_key': api_key},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print()
    
    if response.ok:
        data = response.json()
        
        print("📊 Overzicht:")
        print(f"   Totaal producten: {data.get('total', 0)}")
        print()
        print("📈 Per status:")
        by_status = data.get('byStatus', {})
        print(f"   Pending: {by_status.get('pending', 0)}")
        print(f"   Processing: {by_status.get('processing', 0)}")
        print(f"   Completed: {by_status.get('completed', 0)}")
        print(f"   Failed: {by_status.get('failed', 0)}")
        print()
        print(f"👥 Unieke gebruikers: {len(data.get('userIds', []))}")
        print(f"   User IDs: {data.get('userIds', [])}")
        print()
        
        pending = data.get('pendingProducts', [])
        if pending:
            print(f"✅ Pending producten ({len(pending)}):")
            for i, p in enumerate(pending, 1):
                print(f"   {i}. {p.get('title', 'Geen titel')}")
                print(f"      ID: {p.get('id')}")
                print(f"      User ID: {p.get('userId')}")
                print(f"      Artikelnummer: {p.get('articleNumber', 'N/A')}")
        else:
            print("⚠️  Geen pending producten gevonden!")
            print()
            print("Alle producten:")
            all_products = data.get('products', [])
            for i, p in enumerate(all_products[:10], 1):  # Show first 10
                print(f"   {i}. {p.get('title', 'Geen titel')} - Status: {p.get('status')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
