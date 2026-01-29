#!/usr/bin/env python3
"""Check alle producten in de database om te zien wat hun status is."""
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

base_url = os.environ.get('API_BASE_URL') or os.getenv('API_BASE_URL', 'https://marktplaats-eight.vercel.app')
api_key = os.getenv('INTERNAL_API_KEY', 'LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs=')

print("=" * 70)
print("🔍 Check Alle Producten (via webapp login)")
print("=" * 70)
print()
print("⚠️  Let op: Dit vereist dat je ingelogd bent in de webapp.")
print("   De /api/products endpoint werkt alleen met session authenticatie.")
print()
print("Ga naar de webapp en check:")
print("   1. Wat is de status van je producten? (pending/processing/completed/failed)")
print("   2. Zijn ze echt 'pending' of hebben ze een andere status?")
print()
print("Of test het script opnieuw over een paar minuten")
print("   (na Vercel deployment is voltooid)")
print()
print("=" * 70)
