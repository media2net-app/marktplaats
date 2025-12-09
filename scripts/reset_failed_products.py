"""
Script om alle failed producten te resetten naar pending status.
Dit kan handig zijn als je alle mislukte producten opnieuw wilt proberen.
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
        print("⚠️  WAARSCHUWING: Je gebruikt nog localhost!")
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
    
    # Reset all failed products
    reset_url = f"{base_url}/api/products/reset-all-failed"
    
    print("=" * 70)
    print("Reset Failed Products naar Pending")
    print("=" * 70)
    print(f"API URL: {reset_url}")
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
            print(f"   {data.get('updated', 0)} product(en) bijgewerkt naar pending")
            print()
            print("Je kunt nu run_marktplaats.bat uitvoeren om ze te plaatsen.")
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
                print("Alternatief: Gebruik de 'Reset X mislukt(e)' knop op de producten pagina.")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Kan niet verbinden met de API server.")
        print(f"   Zorg dat de Next.js server draait op {base_url}")
        print()
        print("Start de server met: cd webapp && npm run dev")
    except Exception as e:
        print(f"[ERROR] Fout: {e}")
        print()
        print("Alternatief: Gebruik de 'Reset X mislukt(e)' knop op de producten pagina.")

if __name__ == "__main__":
    main()

