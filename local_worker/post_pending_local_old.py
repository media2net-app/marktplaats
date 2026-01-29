#!/usr/bin/env python3
"""
Lokaal script om pending producten naar Marktplaats te plaatsen.
Dit script draait op je Mac en gebruikt de lokale API of productie API.

Gebruik:
    python post_pending_local.py
    
Of met custom API URL:
    API_BASE_URL=https://marktplaats-eight.vercel.app python post_pending_local.py
"""
import asyncio
import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add parent scripts directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(parent_dir, 'scripts')
sys.path.insert(0, scripts_dir)

from post_ads import run

def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

async def main():
    """Main function to process pending products."""
    # Save environment variables before loading .env (they take priority)
    env_api_url = os.environ.get('API_BASE_URL')
    env_api_key = os.environ.get('INTERNAL_API_KEY')
    
    # Load environment variables from .env files
    # First try .env in local_worker, then parent directory
    env_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(parent_dir, '.env.local'),
        os.path.join(parent_dir, '.env'),
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            log(f"Loaded environment from: {env_path}")
            break
    else:
        # Load from current environment
        load_dotenv(override=True)
        log("Using environment variables from system")
    
    # Restore environment variables (they take priority over .env file)
    if env_api_url:
        os.environ['API_BASE_URL'] = env_api_url
    if env_api_key:
        os.environ['INTERNAL_API_KEY'] = env_api_key
    
    # Get configuration (environment variable takes priority)
    base_url = os.environ.get('API_BASE_URL') or os.getenv('API_BASE_URL') or os.getenv('NEXTAUTH_URL') or 'http://localhost:3000'
    api_key = os.environ.get('INTERNAL_API_KEY') or os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    
    # Marktplaats configuration
    marktplaats_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
    user_data_dir = os.getenv('USER_DATA_DIR', os.path.join(os.path.expanduser('~'), '.marktplaats_browser'))
    media_root = os.getenv('MEDIA_ROOT', os.path.join(parent_dir, 'public', 'media'))
    
    # Ensure directories exist
    os.makedirs(user_data_dir, exist_ok=True)
    os.makedirs(media_root, exist_ok=True)
    
    log("=" * 70)
    log("🖥️  Lokaal Marktplaats Worker")
    log("=" * 70)
    log(f"API Base URL: {base_url}")
    log(f"Marktplaats URL: {marktplaats_url}")
    log(f"User Data Dir: {user_data_dir}")
    log(f"Media Root: {media_root}")
    log(f"INTERNAL_API_KEY: {'✅ Set' if api_key != 'internal-key-change-in-production' else '⚠️  Using default'}")
    log("=" * 70)
    log("")
    
    # Use the pending products endpoint
    api_url = f"{base_url}/api/products/pending"
    
    # Headers with API key
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Query parameter as backup
    api_url_with_key = f"{api_url}?api_key={api_key}"
    
    log(f"Ophalen pending producten van: {api_url}")
    log("")
    
    try:
        # Fetch pending products
        response = requests.get(
            api_url_with_key,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 401:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', 'Unauthorized')
            hint = error_data.get('hint', '')
            log(f"❌ Authenticatie fout: {error_msg}", "ERROR")
            if hint:
                log(f"   Hint: {hint}", "ERROR")
            log("")
            log("Controleer:")
            log("   1. Of INTERNAL_API_KEY overeenkomt met de API key in je .env")
            log("   2. Of de API_BASE_URL correct is ingesteld")
            log("   3. Of de API server draait (localhost:3000 of productie URL)")
            return
        
        if response.status_code != 200:
            log(f"❌ Fout bij ophalen producten: {response.status_code}", "ERROR")
            log(f"   Response: {response.text[:200]}", "ERROR")
            return
        
        # Parse response
        response_data = response.json()
        
        # Check if response is array (products) or object (with debug info)
        if isinstance(response_data, dict) and 'products' in response_data:
            # Response contains debug info
            pending_products = response_data.get('products', [])
            debug_info = response_data.get('debug', {})
            
            if len(pending_products) == 0:
                log("⚠️  Geen pending producten gevonden, maar debug info beschikbaar:", "WARNING")
                log("")
                log(f"   Totaal producten in database: {debug_info.get('totalInDb', 'N/A')}")
                log(f"   Unieke statussen: {debug_info.get('uniqueStatuses', [])}")
                log(f"   Aantal gebruikers: {debug_info.get('uniqueUserIds', 'N/A')}")
                log("")
                if debug_info.get('sampleProducts'):
                    log("   Voorbeeld producten:")
                    for p in debug_info.get('sampleProducts', [])[:5]:
                        log(f"      - {p.get('title', 'N/A')} (status: {p.get('status', 'N/A')})")
                log("")
                log("💡 Mogelijke oorzaken:")
                log("   1. Producten hebben een andere status dan 'pending'")
                log("   2. Producten zijn van een andere gebruiker")
                log("   3. Database is leeg")
                return
        else:
            # Response is array of products
            pending_products = response_data if isinstance(response_data, list) else []
        
        if not pending_products or len(pending_products) == 0:
            log("✅ Geen pending producten gevonden. Alles is up-to-date!")
            return
        
        log(f"✅ Gevonden {len(pending_products)} pending product(en)")
        log("")
        
        # Show products
        for i, product in enumerate(pending_products, 1):
            log(f"   {i}. {product.get('title', 'Geen titel')} (#{product.get('article_number', 'N/A')})")
        log("")
        
        log("Starten met plaatsen op Marktplaats...")
        log("")
        
        # Process all pending products
        results = await run(
            csv_path=None,
            api_url=api_url_with_key,
            product_id=None,  # None means batch mode
            login_only=False,
            keep_open=False
        )
        
        if not results or len(results) == 0:
            log("⚠️  Geen resultaten van plaatsing", "WARNING")
            return
        
        log("")
        log(f"✅ {len(results)} product(en) verwerkt")
        log("")
        
        # Update products via batch endpoint
        update_url = f"{base_url}/api/products/batch-update"
        updates = []
        
        for result in results:
            # Match result to product by article_number or title
            matching_product = None
            for product in pending_products:
                # Match by article number (most reliable)
                if (result.get('article_number') and 
                    product.get('article_number') == result.get('article_number')):
                    matching_product = product
                    break
                # Match by title
                elif (result.get('title') and 
                      product.get('title') == result.get('title')):
                    matching_product = product
                    break
            
            if matching_product:
                status = 'completed' if result.get('ad_url') else 'failed'
                updates.append({
                    'productId': matching_product.get('id'),
                    'status': status,
                    'ad_url': result.get('ad_url'),
                    'ad_id': result.get('ad_id'),
                    'views': result.get('views', 0),
                    'saves': result.get('saves', 0),
                    'posted_at': result.get('posted_at'),
                })
                
                # Log result
                if result.get('ad_url'):
                    log(f"✅ {result.get('title', 'Product')}: Geplaatst")
                    log(f"   URL: {result.get('ad_url')}")
                else:
                    log(f"❌ {result.get('title', 'Product')}: Mislukt")
                    if result.get('error'):
                        log(f"   Fout: {result.get('error')}")
        
        # Send batch update
        if updates:
            log("")
            log(f"Bijwerken van {len(updates)} product(en) in database...")
            try:
                update_response = requests.post(
                    update_url,
                    json={'updates': updates},
                    headers=headers,
                    timeout=30
                )
                if update_response.ok:
                    completed = sum(1 for u in updates if u.get('status') == 'completed')
                    failed = sum(1 for u in updates if u.get('status') == 'failed')
                    log("")
                    log(f"✅ {len(updates)} product(en) bijgewerkt in database")
                    log(f"   Geplaatst: {completed}")
                    log(f"   Mislukt: {failed}")
                else:
                    log(f"⚠️  Fout bij bijwerken producten: {update_response.status_code}", "WARNING")
                    log(f"   Response: {update_response.text[:200]}", "WARNING")
            except Exception as e:
                log(f"⚠️  Fout bij bijwerken producten: {e}", "WARNING")
        else:
            log("⚠️  Geen producten gevonden om bij te werken", "WARNING")
        
        log("")
        log("=" * 70)
        log("✅ Klaar!")
        log("=" * 70)
        
    except requests.exceptions.RequestException as e:
        log(f"❌ Netwerk fout: {e}", "ERROR")
        log("")
        log("Controleer:")
        log("   1. Of de API server draait")
        log("   2. Of de API_BASE_URL correct is")
        log("   3. Of je internet verbinding werkt")
    except Exception as e:
        log(f"❌ Onverwachte fout: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("")
        log("⚠️  Gestopt door gebruiker", "WARNING")
    except Exception as e:
        log(f"❌ Fatale fout: {e}", "ERROR")
        sys.exit(1)
