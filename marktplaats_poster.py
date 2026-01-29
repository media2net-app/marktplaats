#!/usr/bin/env python3
"""
Marktplaats Product Poster - Hoofdscript
=========================================

Dit is het hoofdscript om producten automatisch op Marktplaats te plaatsen.

Gebruik:
    python marktplaats_poster.py

Het script:
1. Haalt pending producten op van de API
2. Downloadt foto's
3. Opent browser en controleert login
4. Plaatst producten automatisch
5. Update database met resultaten
"""

import asyncio
import os
import sys
import tempfile
import requests
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.insert(0, scripts_dir)

from post_ads import run, Product

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app')
API_KEY = os.getenv('INTERNAL_API_KEY', 'internal-key-change-in-production')
MARKTPLAATS_BASE_URL = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
USER_DATA_DIR = os.getenv('USER_DATA_DIR', os.path.join(os.path.expanduser('~'), '.marktplaats_browser'))
MEDIA_ROOT = os.getenv('MEDIA_ROOT', os.path.join(os.path.dirname(__file__), 'public', 'media'))

# Ensure directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)


def log(message: str, level: str = "INFO"):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    prefix = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "STEP": "🔹"
    }.get(level, "•")
    print(f"[{timestamp}] {prefix} {message}")


def download_product_images(product_id: str, article_number: str, temp_dir: str) -> list:
    """Download product images from API to temporary directory."""
    images_url = f"{API_BASE_URL}/api/products/{product_id}/images?api_key={API_KEY}"
    
    try:
        response = requests.get(images_url, headers={'x-api-key': API_KEY}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        image_urls = data.get('images', [])
        if not image_urls:
            log(f"Geen foto's gevonden voor product {article_number}", "WARNING")
            return []
        
        downloaded_paths = []
        for idx, image_url in enumerate(image_urls):
            try:
                # Download image
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                # Determine file extension
                ext = '.jpg'  # default
                content_type = img_response.headers.get('content-type', '').lower()
                if 'png' in content_type or '.png' in image_url.lower():
                    ext = '.png'
                elif 'jpeg' in content_type or '.jpeg' in image_url.lower() or '.jpg' in image_url.lower():
                    ext = '.jpg'
                
                # Save to temp directory
                filename = f"{article_number}_{idx+1}{ext}"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded_paths.append(filepath)
                log(f"Foto gedownload: {filename} ({len(img_response.content)} bytes)", "OK")
            except Exception as e:
                log(f"Fout bij downloaden foto {idx+1}: {e}", "WARNING")
                continue
        
        return downloaded_paths
    except Exception as e:
        log(f"Fout bij ophalen foto's: {e}", "ERROR")
        return []


async def check_login_status(page) -> bool:
    """Check if user is logged in to Marktplaats."""
    try:
        # Navigate to homepage
        await page.goto(f"{MARKTPLAATS_BASE_URL}/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Accept cookies if needed
        try:
            accept_buttons = page.locator("button:has-text('Accepteer'), button:has-text('Akkoord'), button:has-text('accepteer')")
            if await accept_buttons.count() > 0:
                await accept_buttons.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Check for login indicators
        # Look for user menu, account links, or profile indicators
        login_indicators = [
            "[data-testid='user-menu']",
            "[aria-label*='account']",
            "[aria-label*='profiel']",
            "a[href*='/mijn-marktplaats']",
            ".user-menu",
            "[class*='account']"
        ]
        
        for selector in login_indicators:
            try:
                element = page.locator(selector).first
                if await element.count() > 0 and await element.is_visible():
                    return True
            except:
                continue
        
        # Check for login button (means NOT logged in)
        login_buttons = page.locator("a:has-text('Inloggen'), button:has-text('Inloggen'), a[href*='/login']")
        if await login_buttons.count() > 0:
            return False
        
        # If we can't determine, assume not logged in for safety
        return False
    except Exception as e:
        log(f"Fout bij checken login status: {e}", "ERROR")
        return False


async def wait_for_manual_login(page):
    """Wait for user to manually log in."""
    log("=" * 70, "STEP")
    log("INLOGGEN NODIG", "WARNING")
    log("=" * 70, "STEP")
    log("")
    log("Het script heeft gedetecteerd dat je niet ingelogd bent op Marktplaats.", "INFO")
    log("", "INFO")
    log("STAPPEN:", "STEP")
    log("1. Log in op Marktplaats in de browser die is geopend", "STEP")
    log("2. Wacht tot je bent ingelogd (je ziet je profiel/account)", "STEP")
    log("3. Druk op ENTER in dit venster om door te gaan", "STEP")
    log("", "INFO")
    log("De browser blijft open totdat je op ENTER drukt...", "INFO")
    log("", "INFO")
    
    # Navigate to login page
    try:
        await page.goto(f"{MARKTPLAATS_BASE_URL}/login", wait_until="domcontentloaded")
    except:
        await page.goto(f"{MARKTPLAATS_BASE_URL}/", wait_until="domcontentloaded")
    
    # Wait for user to press Enter
    input("Druk op ENTER als je bent ingelogd...")
    
    # Check login status again
    is_logged_in = await check_login_status(page)
    if is_logged_in:
        log("Login succesvol gedetecteerd!", "OK")
        return True
    else:
        log("Login nog niet gedetecteerd. Probeer opnieuw.", "WARNING")
        return False


async def main():
    """Main function."""
    log("=" * 70, "STEP")
    log("Marktplaats Product Poster", "STEP")
    log("=" * 70, "STEP")
    log("", "INFO")
    log(f"API URL: {API_BASE_URL}", "INFO")
    log(f"Marktplaats URL: {MARKTPLAATS_BASE_URL}", "INFO")
    log(f"User Data Dir: {USER_DATA_DIR}", "INFO")
    log("", "INFO")
    
    # Create temporary directory for images
    temp_dir = tempfile.mkdtemp(prefix='marktplaats_')
    log(f"Tijdelijke map voor foto's: {temp_dir}", "INFO")
    log("", "INFO")
    
    try:
        # Fetch pending products
        api_url = f"{API_BASE_URL}/api/products/pending?api_key={API_KEY}"
        log("Ophalen pending producten van API...", "STEP")
        
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 401:
            log("Authenticatie fout! Controleer je INTERNAL_API_KEY.", "ERROR")
            log("", "INFO")
            log("Zorg dat je een .env bestand hebt met:", "INFO")
            log("  INTERNAL_API_KEY=je-api-key", "INFO")
            log("  API_BASE_URL=je-api-url", "INFO")
            return
        
        if response.status_code != 200:
            log(f"Fout bij ophalen producten: {response.status_code}", "ERROR")
            log(f"Response: {response.text[:200]}", "ERROR")
            return
        
        pending_products = response.json()
        
        if not pending_products or len(pending_products) == 0:
            log("Geen pending producten gevonden. Alles is up-to-date!", "OK")
            return
        
        log(f"Gevonden {len(pending_products)} pending product(en)", "OK")
        log("", "INFO")
        
        # Show products
        for i, product in enumerate(pending_products, 1):
            log(f"  {i}. {product.get('title', 'Geen titel')} (#{product.get('article_number', 'N/A')})", "INFO")
        log("", "INFO")
        
        # Download images for each product
        log("Downloaden foto's...", "STEP")
        for product in pending_products:
            product_id = product.get('id')
            article_number = product.get('article_number')
            
            if product_id and article_number:
                log(f"Downloaden foto's voor: {product.get('title', 'Onbekend')}", "STEP")
                
                # Try to get photo API URL from product
                photo_api_url = product.get('photo_api_url') or f"{API_BASE_URL}/api/products/{product_id}/images?api_key={API_KEY}"
                
                # Extract API key from URL if present
                import urllib.parse
                parsed_url = urllib.parse.urlparse(photo_api_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                url_api_key = query_params.get('api_key', [None])[0]
                request_api_key = url_api_key or API_KEY
                
                # Fetch images
                try:
                    response = requests.get(photo_api_url, headers={'x-api-key': request_api_key}, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    image_urls = data.get('images', [])
                    
                    downloaded_paths = []
                    for idx, image_url in enumerate(image_urls):
                        try:
                            img_response = requests.get(image_url, timeout=30)
                            img_response.raise_for_status()
                            
                            ext = '.jpg'
                            if '.png' in image_url.lower():
                                ext = '.png'
                            elif '.jpeg' in image_url.lower():
                                ext = '.jpeg'
                            
                            filename = f"{article_number}_{idx+1}{ext}"
                            filepath = os.path.join(temp_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            
                            downloaded_paths.append(filepath)
                            log(f"  Foto {idx+1} gedownload: {filename}", "OK")
                        except Exception as e:
                            log(f"  Fout bij downloaden foto {idx+1}: {e}", "WARNING")
                            continue
                    
                    if downloaded_paths:
                        product['photos'] = downloaded_paths
                        log(f"  Totaal {len(downloaded_paths)} foto(s) gedownload", "OK")
                    else:
                        product['photos'] = []
                        log(f"  Geen foto's gedownload", "WARNING")
                except Exception as e:
                    log(f"  Fout bij ophalen foto's: {e}", "ERROR")
                    product['photos'] = []
                log("", "INFO")
        
        # Prepare products for posting
        log("Voorbereiden producten voor plaatsing...", "STEP")
        
        # Temporarily modify post_ads to use our products
        import post_ads
        original_read = post_ads.read_products_from_api
        
        def custom_read(api_url_param):
            products_list = []
            for item in pending_products:
                photos = item.get('photos', []) or []
                delivery_methods = item.get('delivery_methods', []) or []
                category_fields = item.get('category_fields') or {}
                
                # Convert price format: replace dot with comma for Dutch format
                price_str = str(item.get('price', '')).strip()
                # If price is a number with dot (like 10.50), convert to comma (10,50)
                if '.' in price_str and ',' not in price_str:
                    # Check if it's a decimal number (not just a dot in text)
                    try:
                        float(price_str)  # Check if it's a valid number
                        price_str = price_str.replace('.', ',')
                    except ValueError:
                        pass  # Not a number, leave as is
                # Remove spaces
                price_str = price_str.replace(' ', '')
                
                product = Product(
                    title=item.get('title', '').strip(),
                    description=item.get('description', '').strip(),
                    price=price_str,
                    category_path=item.get('category_path') or None,
                    location=item.get('location') or None,
                    photos=photos,
                    article_number=item.get('article_number') or None,
                    condition=item.get('condition') or 'Gebruikt',
                    delivery_methods=delivery_methods,
                    material=item.get('material') or None,
                    thickness=item.get('thickness') or None,
                    total_surface=item.get('total_surface') or None,
                    delivery_option=item.get('delivery_option') or 'Ophalen of Verzenden',
                    category_fields=category_fields if isinstance(category_fields, dict) else {},
                )
                products_list.append(product)
            
            log(f"{len(products_list)} product(en) voorbereid", "OK")
            return products_list
        
        # Replace function temporarily
        post_ads.read_products_from_api = custom_read
        
        # Set media_root to temp_dir
        original_media_root = os.getenv('MEDIA_ROOT')
        os.environ['MEDIA_ROOT'] = temp_dir
        
        # Check login before starting
        log("", "INFO")
        log("Controleren login status...", "STEP")
        
        # We'll check login in the run function, but first let's set up the browser
        # The run function will handle browser launch and login check
        
        try:
            log("Starten browser en controleren login...", "STEP")
            log("", "INFO")
            
            # Run with login check
            # We'll modify the run to check login first
            results = await run(
                csv_path=None,
                api_url=api_url,
                product_id=None,
                login_only=False,
                keep_open=False
            )
            
            if not results:
                log("Geen resultaten van plaatsing", "WARNING")
                return
            
            log("", "INFO")
            log(f"{len(results)} product(en) verwerkt", "OK")
            log("", "INFO")
            
            # Update products via batch endpoint
            update_url = f"{API_BASE_URL}/api/products/batch-update"
            updates = []
            
            for result in results:
                # Match result to product
                matching_product = None
                for product in pending_products:
                    if (result.get('article_number') and 
                        product.get('article_number') == result.get('article_number')):
                        matching_product = product
                        break
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
                        log(f"✅ {result.get('title', 'Product')}: Geplaatst", "OK")
                        log(f"   URL: {result.get('ad_url')}", "INFO")
                    else:
                        log(f"❌ {result.get('title', 'Product')}: Mislukt", "ERROR")
                        if result.get('error'):
                            log(f"   Fout: {result.get('error')}", "ERROR")
            
            # Send batch update
            if updates:
                log("", "INFO")
                log(f"Bijwerken van {len(updates)} product(en) in database...", "STEP")
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
                        log("", "INFO")
                        log(f"✅ {len(updates)} product(en) bijgewerkt in database", "OK")
                        log(f"   Geplaatst: {completed}", "INFO")
                        log(f"   Mislukt: {failed}", "INFO")
                    else:
                        log(f"⚠️  Fout bij bijwerken: {update_response.status_code}", "WARNING")
                except Exception as e:
                    log(f"⚠️  Fout bij bijwerken: {e}", "WARNING")
        finally:
            # Restore original function
            post_ads.read_products_from_api = original_read
            if original_media_root:
                os.environ['MEDIA_ROOT'] = original_media_root
            elif 'MEDIA_ROOT' in os.environ:
                del os.environ['MEDIA_ROOT']
    except requests.exceptions.RequestException as e:
        log(f"Netwerk fout: {e}", "ERROR")
        log("", "INFO")
        log("Controleer:", "INFO")
        log("  1. Of de API server draait", "INFO")
        log("  2. Of de API_BASE_URL correct is", "INFO")
        log("  3. Of je internet verbinding werkt", "INFO")
    except Exception as e:
        log(f"Onverwachte fout: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
    finally:
        # Cleanup temporary directory
        try:
            shutil.rmtree(temp_dir)
            log("", "INFO")
            log("Tijdelijke bestanden opgeruimd", "OK")
        except:
            pass
        
        log("", "INFO")
        log("=" * 70, "STEP")
        log("Klaar!", "OK")
        log("=" * 70, "STEP")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("", "INFO")
        log("Gestopt door gebruiker", "WARNING")
    except Exception as e:
        log(f"Fatale fout: {e}", "ERROR")
        sys.exit(1)
