"""
Script om ALLE producten te resetten naar pending status.
Dit kan handig zijn als je alle producten opnieuw wilt plaatsen.
"""
import requests
import os
import sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Get API URL from environment or use default
    base_url = os.getenv('NEXTAUTH_URL') or os.getenv('API_BASE_URL') or 'http://localhost:3000'
    api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    
    # Check if still using localhost (development)
    if 'localhost' in base_url or '127.0.0.1' in base_url:
        print("=" * 70)
        print("[WARNING] Je gebruikt nog localhost!")
        print("=" * 70)
        print(f"   Huidige URL: {base_url}")
        print()
        print("   Voor productie:")
        print("   1. Open het .env bestand in de rootmap")
        print("   2. Pas NEXTAUTH_URL en API_BASE_URL aan naar je productie URL")
        print("   3. Bijvoorbeeld: https://jouw-domein.vercel.app")
        print()
        print("   Doorgaan met localhost...")
        print("=" * 70)
        print()
    
    # Reset all products
    reset_url = f"{base_url}/api/products/reset-all"
    
    print("=" * 70)
    print("Reset ALLE Producten naar Pending")
    print("=" * 70)
    print(f"API URL: {reset_url}")
    print()
    print("[WAARSCHUWING] Dit reset ALLE producten naar pending status!")
    print("   - Status wordt 'pending'")
    print("   - Marktplaats URL wordt verwijderd")
    print("   - Views en saves worden gereset")
    print()
    
    # Ask for confirmation
    confirm = input("Weet je zeker dat je ALLE producten wilt resetten? (ja/n): ")
    if confirm.lower() not in ['ja', 'j', 'yes', 'y']:
        print("Geannuleerd.")
        return
    
    print()
    print("Resetten...")
    print()
    
    try:
        # Try with API key in header
        response = requests.post(
            reset_url,
            headers={'x-api-key': api_key, 'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.ok:
            data = response.json()
            print(f"[SUCCESS] {data.get('message', 'Producten gereset')}")
            print(f"   {data.get('updated', 0)} van {data.get('total', 0)} product(en) bijgewerkt naar pending")
            print()
            print("Je kunt nu run_marktplaats_standalone.bat uitvoeren om ze te plaatsen.")
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"[ERROR] Fout: {response.status_code}")
            print(f"   Response: {response.text}")
            print()
            if response.status_code == 401:
                print("Authenticatie fout. Controleer:")
                print("   1. Of de Next.js server draait op", base_url)
                print("   2. Of INTERNAL_API_KEY correct is ingesteld")
                print()
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Kan niet verbinden met de API server.")
        print(f"   Zorg dat de Next.js server draait op {base_url}")
        print()
        print("Start de server met: npm run dev")
    except Exception as e:
        print(f"[ERROR] Fout: {e}")

if __name__ == "__main__":
    main()

