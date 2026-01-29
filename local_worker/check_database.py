#!/usr/bin/env python3
"""Check wat er in de database staat via de webapp API (vereist login)."""
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

base_url = os.environ.get('API_BASE_URL') or os.getenv('API_BASE_URL', 'https://marktplaats-eight.vercel.app')

print("=" * 70)
print("🔍 Database Check")
print("=" * 70)
print()
print("⚠️  Let op: Deze check vereist dat je ingelogd bent in de webapp.")
print()
print("Om te zien wat er in de database staat:")
print("1. Ga naar: https://marktplaats-eight.vercel.app/dashboard")
print("2. Open de browser console (F12)")
print("3. Kijk naar de Network tab")
print("4. Check de /api/products request")
print()
print("Of check direct in de webapp:")
print("- Ga naar Dashboard")
print("- Kijk naar 'Status Overzicht'")
print("- Zie hoeveel producten er per status zijn")
print()
print("=" * 70)
print()
print("💡 Als je 2 producten ziet met status 'Wachtend' in de webapp,")
print("   maar het script vindt ze niet, dan kan het zijn dat:")
print("   1. De producten van een andere gebruiker zijn")
print("   2. De status in de database anders is dan 'pending'")
print("   3. De deployment nog niet klaar is")
print()
print("=" * 70)
