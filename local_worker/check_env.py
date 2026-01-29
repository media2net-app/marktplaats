#!/usr/bin/env python3
"""Check if .env is correctly configured."""
import os
from dotenv import load_dotenv

# Load .env
load_dotenv('.env')

# Expected values
expected_key = 'LvR3fBWmRxgqdt+ggF/sxCMEjDQYd7TtcC3sBnP+Kvs='

# Get values
api_url = os.getenv('API_BASE_URL', 'NIET GEVONDEN')
api_key = os.getenv('INTERNAL_API_KEY', 'NIET GEVONDEN')
mp_url = os.getenv('MARKTPLAATS_BASE_URL', 'NIET GEVONDEN')
user_data_dir = os.getenv('USER_DATA_DIR', 'NIET GEVONDEN')
media_root = os.getenv('MEDIA_ROOT', 'NIET GEVONDEN')

print("=" * 70)
print("🔍 .env Configuratie Check")
print("=" * 70)
print()
print(f"API_BASE_URL:        {api_url}")
if api_key != 'NIET GEVONDEN' and len(api_key) > 20:
    print(f"INTERNAL_API_KEY:    {api_key[:20]}...{api_key[-5:]}")
else:
    print(f"INTERNAL_API_KEY:    {api_key}")
print(f"MARKTPLAATS_BASE_URL: {mp_url}")
print(f"USER_DATA_DIR:       {user_data_dir}")
print(f"MEDIA_ROOT:          {media_root}")
print()
print("=" * 70)
print("✅/❌ Validatie")
print("=" * 70)

# Check API_BASE_URL
if api_url == 'http://localhost:3000' or 'marktplaats-eight.vercel.app' in api_url:
    print("✅ API_BASE_URL is correct ingesteld")
else:
    print(f"⚠️  API_BASE_URL: {api_url} (verwacht: http://localhost:3000 of productie URL)")

# Check INTERNAL_API_KEY
if api_key == expected_key:
    print("✅ INTERNAL_API_KEY komt overeen met .env.local")
elif api_key == 'NIET GEVONDEN':
    print("❌ INTERNAL_API_KEY niet gevonden in .env")
elif api_key == 'internal-key-change-in-production':
    print("⚠️  INTERNAL_API_KEY gebruikt nog de default waarde!")
    print("   Vervang met de echte key uit INTERNAL_API_KEY.txt")
else:
    print("❌ INTERNAL_API_KEY komt NIET overeen met .env.local")
    print(f"   Verwacht: {expected_key[:20]}...")
    print(f"   Gevonden: {api_key[:20] if len(api_key) > 20 else api_key}...")

# Check other values
if mp_url == 'https://www.marktplaats.nl':
    print("✅ MARKTPLAATS_BASE_URL is correct")
else:
    print(f"⚠️  MARKTPLAATS_BASE_URL: {mp_url}")

if user_data_dir != 'NIET GEVONDEN':
    print("✅ USER_DATA_DIR is ingesteld")
else:
    print("⚠️  USER_DATA_DIR niet ingesteld (gebruikt default)")

if media_root != 'NIET GEVONDEN':
    print("✅ MEDIA_ROOT is ingesteld")
else:
    print("⚠️  MEDIA_ROOT niet ingesteld (gebruikt default)")

print()
print("=" * 70)
if api_key == expected_key and api_url != 'NIET GEVONDEN':
    print("✅ Configuratie ziet er goed uit!")
else:
    print("⚠️  Controleer de bovenstaande waarschuwingen")
print("=" * 70)
