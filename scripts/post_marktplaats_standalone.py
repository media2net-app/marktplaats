"""
Standalone script voor Marktplaats posting.
Dit script werkt zonder lokale bestanden - alles wordt via de API opgehaald.
"""
import asyncio
import os
import sys
import tempfile
import requests
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))
from post_ads import run

# Configuration - kan worden aangepast via environment variables of hier direct
# Voor productie gebruik: https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app
API_BASE_URL = os.getenv('API_BASE_URL', 'https://marktplaats-bp5bbsuk5-media2net-apps-projects.vercel.app')
API_KEY = os.getenv('INTERNAL_API_KEY', 'internal-key-change-in-production')

# Als de API URL verandert, pas deze regel aan:
# API_BASE_URL = 'https://jouw-nieuwe-url.vercel.app'

async def download_product_images(product_id: str, article_number: str, temp_dir: str) -> list:
    """Download product images from API to temporary directory."""
    images_url = f"{API_BASE_URL}/api/products/{product_id}/images?api_key={API_KEY}"
    
    try:
        response = requests.get(images_url, headers={'x-api-key': API_KEY}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        image_urls = data.get('images', [])
        if not image_urls:
            print(f"  Geen foto's gevonden voor product {article_number}")
            return []
        
        downloaded_paths = []
        for idx, image_url in enumerate(image_urls):
            try:
                # Download image
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                # Determine file extension from URL or content type
                ext = '.jpg'  # default
                if '.png' in image_url.lower():
                    ext = '.png'
                elif '.jpeg' in image_url.lower() or '.jpg' in image_url.lower():
                    ext = '.jpg'
                elif 'image/png' in img_response.headers.get('content-type', ''):
                    ext = '.png'
                
                # Save to temp directory
                filename = f"{article_number}_{idx+1}{ext}"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                downloaded_paths.append(filepath)
                print(f"  [OK] Foto gedownload: {filename}")
            except Exception as e:
                print(f"  [WARNING] Fout bij downloaden foto {idx+1}: {e}")
                continue
        
        return downloaded_paths
    except Exception as e:
        print(f"  [ERROR] Fout bij ophalen foto's: {e}")
        return []

async def main():
    print("=" * 70)
    print("Marktplaats Automator - Standalone Versie")
    print("=" * 70)
    print(f"API URL: {API_BASE_URL}")
    print()
    
    # Create temporary directory for images
    temp_dir = tempfile.mkdtemp(prefix='marktplaats_')
    print(f"Tijdelijke map voor foto's: {temp_dir}")
    print()
    
    try:
        # Fetch pending products
        api_url = f"{API_BASE_URL}/api/products/pending?api_key={API_KEY}"
        print(f"Ophalen pending producten...")
        
        response = requests.get(api_url, headers={'x-api-key': API_KEY}, timeout=30)
        response.raise_for_status()
        pending_products = response.json()
        
        if not pending_products or len(pending_products) == 0:
            print("[OK] Geen pending producten gevonden.")
            return
        
        print(f"[OK] Gevonden {len(pending_products)} pending product(en)")
        print()
        
        # Download images for each product and update product data
        for product in pending_products:
            product_id = product.get('id')
            article_number = product.get('article_number')
            
            if product_id and article_number:
                print(f"Downloaden foto's voor: {product.get('title', 'Onbekend')}")
                # Prefer API-provided photo_api_url (contains correct key/base)
                photo_api_url = product.get('photo_api_url') or f"{API_BASE_URL}/api/products/{product_id}/images?api_key={API_KEY}"
                
                # Extract API key from photo_api_url if it contains one, otherwise use default
                import urllib.parse
                parsed_url = urllib.parse.urlparse(photo_api_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                url_api_key = query_params.get('api_key', [None])[0]
                # Use API key from URL if available, otherwise use the default
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
                            elif '.jpeg' in image_url.lower() or '.jpg' in image_url.lower():
                                ext = '.jpg'
                            elif 'image/png' in img_response.headers.get('content-type', ''):
                                ext = '.png'
                            filename = f"{article_number}_{idx+1}{ext}"
                            filepath = os.path.join(temp_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(img_response.content)
                            downloaded_paths.append(filepath)
                            print(f"  [OK] Foto gedownload: {filename} ({len(img_response.content)} bytes)")
                        except Exception as e:
                            print(f"  [WARNING] Fout bij downloaden foto {idx+1}: {e}")
                            continue
                    
                    if downloaded_paths:
                        product['photos'] = downloaded_paths
                        print(f"  [OK] Totaal {len(downloaded_paths)} foto(s) gedownload voor {article_number}")
                    else:
                        product['photos'] = []
                        print(f"  [WARNING] Geen foto's gedownload voor {article_number}")
                except Exception as e:
                    print(f"  [ERROR] Fout bij ophalen foto's: {e}")
                    import traceback
                    print(f"  Traceback: {traceback.format_exc()}")
                    product['photos'] = []
                print()
        
        # Create a modified API response that includes the downloaded images
        # We need to pass the products with images to the run function
        # The run function expects an API URL, but we need to modify the data
        # So we'll create a temporary API-like response
        
        # Run the main posting script
        # We need to modify post_ads.py to accept products directly, or create a wrapper
        # For now, let's modify the products in the API response by creating a custom endpoint
        # Actually, we can modify the read_products_from_api to use our modified data
        
        print("Starten met plaatsen op Marktplaats...")
        print()
        
        # Temporarily modify the read_products_from_api function to use our data
        import post_ads
        original_read = post_ads.read_products_from_api
        
        def custom_read(api_url_param):
            # Return our modified products
            products_list = []
            for item in pending_products:
                photos = item.get('photos', []) or []
                delivery_methods = item.get('delivery_methods', []) or []
                category_fields = item.get('category_fields') or {}
                
                # Log photo information for debugging
                if photos:
                    print(f"[DEBUG] Product {item.get('title', 'Unknown')} heeft {len(photos)} foto(s):")
                    for i, photo_path in enumerate(photos, 1):
                        exists = os.path.exists(photo_path) if photo_path else False
                        print(f"  Foto {i}: {photo_path} (exists: {exists})")
                else:
                    print(f"[DEBUG] Product {item.get('title', 'Unknown')} heeft geen foto's")
                
                product = post_ads.Product(
                    title=item.get('title', '').strip(),
                    description=item.get('description', '').strip(),
                    price=str(item.get('price', '')).strip(),
                    category_path=item.get('category_path') or None,
                    location=item.get('location') or None,
                    photos=photos,  # Use downloaded photos
                    article_number=item.get('article_number') or None,
                    condition=item.get('condition') or 'Gebruikt',
                    delivery_methods=delivery_methods,
                    material=item.get('material') or None,  # Keep for backward compatibility
                    thickness=item.get('thickness') or None,  # Keep for backward compatibility
                    total_surface=item.get('total_surface') or None,  # Keep for backward compatibility
                    delivery_option=item.get('delivery_option') or 'Ophalen of Verzenden',
                    category_fields=category_fields if isinstance(category_fields, dict) else {},
                )
                products_list.append(product)
            
            print(f"[OK] {len(products_list)} product(en) opgehaald (met gedownloade foto's)")
            return products_list
        
        # Replace the function temporarily
        post_ads.read_products_from_api = custom_read
        
        # Set media_root to temp_dir so photos are found
        import os
        original_media_root = os.getenv('MEDIA_ROOT')
        os.environ['MEDIA_ROOT'] = temp_dir
        
        try:
            results = await run(
                csv_path=None,
                api_url=api_url,  # Will use our custom function
                product_id=None,
                login_only=False,
                keep_open=False
            )
        finally:
            # Restore original function
            post_ads.read_products_from_api = original_read
            if original_media_root:
                os.environ['MEDIA_ROOT'] = original_media_root
            elif 'MEDIA_ROOT' in os.environ:
                del os.environ['MEDIA_ROOT']
        
        # Update products via batch endpoint
        if results and len(results) > 0:
            updates = []
            for result in results:
                matching_product = None
                for product in pending_products:
                    if result.get('article_number') and product.get('articleNumber') == result.get('article_number'):
                        matching_product = product
                        break
                    elif result.get('title') and product.get('title') == result.get('title'):
                        matching_product = product
                        break
                
                if matching_product:
                    updates.append({
                        'productId': matching_product['id'],
                        'status': 'completed',
                        'ad_url': result.get('ad_url'),
                        'ad_id': result.get('ad_id'),
                        'views': result.get('views', 0),
                        'saves': result.get('saves', 0),
                        'posted_at': result.get('posted_at'),
                    })
            
            if updates:
                update_url = f"{API_BASE_URL}/api/products/batch-update"
                try:
                    update_response = requests.post(
                        update_url,
                        json={'updates': updates},
                        headers={'x-api-key': API_KEY},
                        timeout=30
                    )
                    if update_response.ok:
                        print(f"\n[OK] {len(updates)} product(en) bijgewerkt in database")
                    else:
                        print(f"\n[WARNING] Fout bij bijwerken: {update_response.status_code}")
                except Exception as e:
                    print(f"\n[WARNING] Fout bij bijwerken: {e}")
    finally:
        # Cleanup temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n[CLEANUP] Tijdelijke bestanden opgeruimd")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())

