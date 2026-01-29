#!/usr/bin/env python3
"""Debug script om te zien wat er met pending producten aan de hand is."""
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

base_url = os.getenv('API_BASE_URL', 'https://marktplaats-eight.vercel.app')
api_key = os.getenv('INTERNAL_API_KEY', 'LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=')

print("=" * 70)
print("🔍 Debug: Pending Producten")
print("=" * 70)
print(f"API URL: {base_url}")
print(f"API Key: {api_key[:20]}...")
print()

# Test batch-post endpoint (geeft counts)
print("1. Test batch-post endpoint (geeft counts):")
try:
    response = requests.get(
        f"{base_url}/api/products/batch-post",
        headers={'x-api-key': api_key},
        params={'api_key': api_key},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   Pending: {data.get('pending', 0)}")
        print(f"   Processing: {data.get('processing', 0)}")
        print(f"   Completed: {data.get('completed', 0)}")
        print(f"   Failed: {data.get('failed', 0)}")
        print(f"   Total: {data.get('total', 0)}")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test pending endpoint
print("2. Test pending endpoint (geeft producten):")
try:
    response = requests.get(
        f"{base_url}/api/products/pending",
        headers={'x-api-key': api_key},
        params={'api_key': api_key},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        products = response.json()
        print(f"   Aantal producten: {len(products)}")
        if products:
            print("   Producten:")
            for i, p in enumerate(products, 1):
                print(f"      {i}. {p.get('title', 'Geen titel')} (ID: {p.get('id', 'N/A')})")
        else:
            print("   ⚠️  Geen producten gevonden!")
    else:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print()
print("=" * 70)
