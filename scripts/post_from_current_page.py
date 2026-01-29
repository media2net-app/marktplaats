#!/usr/bin/env python3
"""
Script om producten te plaatsen vanaf de huidige browser pagina
Gebruik dit als je al ingelogd bent en op de plaats advertentie pagina staat
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marktplaats.main import MarktplaatsAutomator, read_products_from_api
from marktplaats.utils import log_step, log_success, log_error

async def main():
    """Main function - plaatst producten vanaf huidige pagina"""
    load_dotenv(override=True)
    
    base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
    user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
    media_root = os.getenv('MEDIA_ROOT', './public/media')
    
    # API configuratie - gebruik altijd localhost voor dit script
    api_base_url = os.getenv('API_BASE_URL') or 'http://localhost:3000'
    # Override als NEXTAUTH_URL is productie URL
    if os.getenv('NEXTAUTH_URL') and 'localhost' not in os.getenv('NEXTAUTH_URL'):
        api_base_url = 'http://localhost:3000'
    
    api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    api_url = f"{api_base_url}/api/products/pending?api_key={api_key}"
    
    print(f"API Base URL: {api_base_url}")
    print(f"API Key: {'✅ Set' if api_key != 'internal-key-change-in-production' else '⚠️  Using default'}")
    print("")
    
    print("=" * 70)
    print("📝 Marktplaats - Plaats Producten vanaf Huidige Pagina")
    print("=" * 70)
    print("")
    print("⚠️  Zorg dat je:")
    print("   1. Ingelogd bent op Marktplaats")
    print("   2. Op de 'Plaats advertentie' pagina staat")
    print("   3. De browser open hebt")
    print("")
    print("Het script zal nu:")
    print("   1. Pending producten ophalen van de API")
    print("   2. Browser starten (gebruikt bestaande login sessie)")
    print("   3. Direct beginnen met invullen")
    print("   4. Producten één voor één plaatsen")
    print("")
    print("Starten over 2 seconden...")
    import time
    time.sleep(2)
    print("")
    
    # Haal pending producten op
    try:
        log_step("Ophalen pending producten...")
        products = read_products_from_api(api_url)
        
        if not products:
            log_error("Geen pending producten gevonden")
            return
        
        log_success(f"{len(products)} product(en) gevonden")
        print("")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p.title} (#{p.article_number})")
        print("")
        print("Starten met plaatsen over 2 seconden...")
        import time
        time.sleep(2)
        print("")
        
    except Exception as e:
        log_error(f"Fout bij ophalen producten: {e}")
        return
    
    # Start automator
    automator = MarktplaatsAutomator(user_data_dir, media_root, base_url)
    
    try:
        # Start browser (gebruikt bestaande sessie)
        log_step("Browser starten (gebruikt bestaande sessie)...")
        await automator.start()
        
        # Navigeer naar plaats pagina (gebruikt bestaande login sessie)
        log_step("Navigeren naar plaats advertentie pagina...")
        await automator.page.goto(f"{base_url}/plaats", wait_until="domcontentloaded")
        await automator.page.wait_for_timeout(2000)
        log_success("Op plaats advertentie pagina")
        
        # Plaats producten (skip navigatie voor eerste product)
        log_step("Starten met plaatsen...")
        results = await automator.post_products(products, skip_first_navigation=True)
        
        # Toon resultaten
        print("")
        print("=" * 70)
        print("✅ RESULTATEN")
        print("=" * 70)
        completed = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        
        print(f"Totaal: {len(results)}")
        print(f"✅ Geplaatst: {completed}")
        print(f"❌ Mislukt: {failed}")
        print("")
        
        for result in results:
            if result.get('status') == 'completed':
                print(f"✅ {result.get('title')}")
                print(f"   URL: {result.get('ad_url')}")
            else:
                print(f"❌ {result.get('title')}")
                if result.get('error'):
                    print(f"   Fout: {result.get('error')}")
            print("")
        
        # Update database
        if completed > 0:
            log_step("Bijwerken database...")
            try:
                import requests
                update_url = f"{api_base_url}/api/products/batch-update"
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }
                
                updates = []
                for result in results:
                    if result.get('ad_url'):
                        updates.append({
                            'productId': result.get('id'),  # We need to match by article_number
                            'status': 'completed',
                            'ad_url': result.get('ad_url'),
                        })
                
                if updates:
                    response = requests.post(update_url, json={'updates': updates}, headers=headers)
                    if response.ok:
                        log_success(f"{len(updates)} product(en) bijgewerkt in database")
                    else:
                        log_error(f"Fout bij bijwerken: {response.status_code}")
            except Exception as e:
                log_error(f"Fout bij bijwerken database: {e}")
        
        print("=" * 70)
        log_success("Klaar!")
        print("=" * 70)
        
        # Keep browser open for a bit, then close
        log_step("Browser blijft 10 seconden open voor inspectie...")
        await automator.page.wait_for_timeout(10000)
        await automator.close()
        
    except Exception as e:
        log_error(f"Fout: {e}")
        import traceback
        traceback.print_exc()
        await automator.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        sys.exit(1)
