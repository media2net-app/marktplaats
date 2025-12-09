"""
Import gescrapete categorieën naar de database via de API.
"""
import json
import os
import requests
from dotenv import load_dotenv
from typing import List, Dict


def import_categories_to_db(categories_file: str = None, api_url: str = None, api_key: str = None):
    """
    Import categorieën van een JSON bestand naar de database via de API.
    
    Args:
        categories_file: Pad naar het JSON bestand met categorieën (default: categories_scraped.json)
        api_url: Base URL van de API (default: uit .env)
        api_key: API key voor authenticatie (default: uit .env)
    """
    load_dotenv()
    
    # Default waarden
    if categories_file is None:
        categories_file = os.path.join(os.path.dirname(__file__), "..", "categories_scraped.json")
    
    if api_url is None:
        api_url = os.getenv('NEXTAUTH_URL') or os.getenv('API_BASE_URL') or 'http://localhost:3000'
    
    if api_key is None:
        api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    
    # Check of bestand bestaat
    if not os.path.exists(categories_file):
        print(f"❌ Bestand niet gevonden: {categories_file}")
        print("\n💡 Tip: Run eerst scrape_categories_from_homepage.py om categorieën te scrapen")
        return
    
    # Lees categorieën
    print(f"📖 Lezen van {categories_file}...")
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except Exception as e:
        print(f"❌ Fout bij lezen van bestand: {e}")
        return
    
    if not categories or len(categories) == 0:
        print("❌ Geen categorieën gevonden in bestand!")
        return
    
    print(f"✅ {len(categories)} categorieën geladen")
    
    # API endpoint
    api_endpoint = f"{api_url}/api/categories?api_key={api_key}"
    
    print(f"\n📤 Verzenden naar: {api_endpoint}")
    print(f"   (API key: {'*' * (len(api_key) - 4)}{api_key[-4:]})")
    
    # Verstuur naar API
    try:
        response = requests.post(
            api_endpoint,
            json={"categories": categories},
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
            },
            timeout=60,
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n" + "=" * 70)
        print("✅ Categorieën succesvol geïmporteerd!")
        print("=" * 70)
        print(f"\n📊 Resultaten:")
        print(f"   ✅ Aangemaakt: {result.get('created', 0)}")
        print(f"   🔄 Bijgewerkt: {result.get('updated', 0)}")
        print(f"   ⏭️  Overgeslagen: {result.get('skipped', 0)}")
        
        if result.get('errors') and len(result['errors']) > 0:
            print(f"\n⚠️  Fouten ({len(result['errors'])}):")
            for error in result['errors'][:10]:  # Toon eerste 10 fouten
                print(f"   - {error}")
            if len(result['errors']) > 10:
                print(f"   ... en {len(result['errors']) - 10} meer fouten")
        
        print("\n" + "=" * 70)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Fout bij verzenden naar API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status code: {e.response.status_code}")
            try:
                print(f"   Response: {e.response.text}")
            except:
                pass
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")


def main():
    import sys
    
    print("=" * 70)
    print("Marktplaats Categorie Import Tool")
    print("Importeert gescrapete categorieën naar de database")
    print("=" * 70)
    print()
    
    # Optionele command line argumenten
    categories_file = sys.argv[1] if len(sys.argv) > 1 else None
    api_url = sys.argv[2] if len(sys.argv) > 2 else None
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    
    import_categories_to_db(categories_file, api_url, api_key)


if __name__ == "__main__":
    main()














