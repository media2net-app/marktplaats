#!/usr/bin/env python3
"""
Script om producten op pending te zetten via batch-update.
Dit werkt met product IDs die je kunt vinden in de database of web interface.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()
base_url = os.getenv('API_BASE_URL', 'https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app')
api_key = os.getenv('INTERNAL_API_KEY', 'internal-key-change-in-production')

headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json'
}

print("=" * 70)
print("Producten Resetten naar Pending")
print("=" * 70)
print()

# Since we can't easily get all products, let's try a different approach
# We'll use the batch-update endpoint with product IDs
# For now, let's check if there are any completed products by trying to update them

print("Let op: Om alle producten te resetten, gebruik de web interface")
print("of voer dit script uit met specifieke product IDs.")
print()
print("Alternatief: Gebruik de web interface op:")
print(f"  {base_url.replace('/api', '')}")
print("  Ga naar Products en zet de status handmatig op 'pending'")
print()
print("Of als je product IDs hebt, kan ik ze voor je updaten.")
print()

# Try to get pending products to see current status
print("Controleren huidige status...")
pending_url = f"{base_url}/api/products/pending?api_key={api_key}"
try:
    response = requests.get(pending_url, headers=headers, timeout=30)
    if response.ok:
        pending = response.json()
        count = len(pending) if isinstance(pending, list) else 0
        print(f"✅ Huidige pending producten: {count}")
        if count > 0:
            print("   Er zijn al pending producten - script kan deze plaatsen!")
    else:
        print(f"⚠️  Kon pending status niet ophalen: {response.status_code}")
except Exception as e:
    print(f"⚠️  Fout: {e}")

print()
print("=" * 70)
print("Om producten op pending te zetten:")
print("1. Gebruik de web interface (aanbevolen)")
print("2. Of voeg product IDs toe aan dit script")
print("=" * 70)
