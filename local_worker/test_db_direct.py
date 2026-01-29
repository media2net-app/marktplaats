#!/usr/bin/env python3
"""Test de database direct via verschillende API endpoints."""
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
print("🔍 Direct Database Test")
print("=" * 70)
print(f"API URL: {base_url}")
print()

# Test 1: Batch-post endpoint (geeft counts)
print("1. Test /api/products/batch-post (counts):")
try:
    response = requests.get(
        f"{base_url}/api/products/batch-post",
        headers=headers,
        params={'api_key': api_key},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   📊 Counts:")
        print(f"      Pending: {data.get('pending', 0)}")
        print(f"      Processing: {data.get('processing', 0)}")
        print(f"      Completed: {data.get('completed', 0)}")
        print(f"      Failed: {data.get('failed', 0)}")
        print(f"      Total: {data.get('total', 0)}")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print()

# Test 2: Pending endpoint (geeft producten)
print("2. Test /api/products/pending (producten):")
try:
    response = requests.get(
        f"{base_url}/api/products/pending",
        headers=headers,
        params={'api_key': api_key},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.ok:
        products = response.json()
        print(f"   📦 Aantal producten: {len(products)}")
        if products:
            print(f"   ✅ Producten gevonden:")
            for i, p in enumerate(products, 1):
                print(f"      {i}. {p.get('title', 'Geen titel')}")
                print(f"         ID: {p.get('id', 'N/A')}")
                print(f"         Artikelnummer: {p.get('article_number', 'N/A')}")
                print(f"         Status: pending (in response)")
        else:
            print(f"   ⚠️  Geen producten in response!")
            print(f"   Response body: {response.text[:500]}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print()

# Test 3: Check response headers en debugging info
print("3. Debug info:")
print(f"   API Key gebruikt: {api_key[:20]}...{api_key[-5:]}")
print(f"   Key lengte: {len(api_key)}")
print()

print("=" * 70)
print("💡 Als pending count > 0 maar geen producten:")
print("   - Deployment is mogelijk nog niet klaar")
print("   - Wacht 1-2 minuten en test opnieuw")
print("   - Check Vercel dashboard voor deployment status")
print("=" * 70)
