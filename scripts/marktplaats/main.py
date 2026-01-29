"""
Main orchestrator voor Marktplaats automatisering
Coördineert alle modules om advertenties te plaatsen
"""
import os
import sys
import csv
from typing import List, Optional, Dict
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    requests = None

from .browser import MarktplaatsBrowser
from .form_filler import FormFiller
from .photo_upload import PhotoUploader
from .publisher import Publisher
from .utils import (
    log_step, log_error, log_success, log_warning,
    Product, normalize_price, find_photos_for_article
)


class MarktplaatsAutomator:
    """Hoofdklasse voor Marktplaats automatisering"""
    
    def __init__(self, user_data_dir: str, media_root: str, base_url: str = "https://www.marktplaats.nl"):
        self.user_data_dir = user_data_dir
        self.media_root = media_root
        self.base_url = base_url.rstrip('/')
        self.browser: Optional[MarktplaatsBrowser] = None
        self.page = None
    
    async def start(self, headless: Optional[bool] = None, wait_for_manual_login: bool = False, wait_seconds: int = 10):
        """Start browser en login"""
        self.browser = MarktplaatsBrowser(self.user_data_dir, self.base_url)
        self.page = await self.browser.start(headless=headless)
        await self.browser.ensure_logged_in(wait_for_manual_login=wait_for_manual_login, wait_seconds=wait_seconds)
        return self.page
    
    async def post_product(self, product: Product, skip_navigation: bool = False) -> Dict:
        """Plaats één product op Marktplaats"""
        if not self.page:
            await self.start()
        
        try:
            log_step(f"Plaatsen product: {product.title}")
            
            # Initialize modules
            form_filler = FormFiller(self.page, self.base_url)
            photo_uploader = PhotoUploader(self.page)
            publisher = Publisher(self.page, self.base_url)
            
            # Step 1: Navigate to place ad page (skip if already there)
            await form_filler.navigate_to_place_ad(skip_if_already_there=skip_navigation)
            
            # Step 2: Select category
            await form_filler.select_category(product)
            
            # Step 3: Fill all fields
            await form_filler.fill_all_fields(product)
            
            # Step 4: Upload photos (BEFORE bundle selection, so photos are attached to form)
            # Upload photos while still on the form page
            await photo_uploader.upload_photos(product, self.media_root)
            
            # Wait for photos to be fully processed before continuing
            log_step("Wachten op verwerking van foto's...")
            await self.page.wait_for_timeout(5000)
            
            # Step 5: Select free bundle (after photos uploaded)
            await form_filler.select_free_bundle()
            
            # Step 6: Publish ad (pass photo_uploader in case photos need to be uploaded on plan page)
            ad_url = await publisher.publish_ad(product.title, photo_uploader=photo_uploader, product=product, media_root=self.media_root)
            
            if ad_url:
                log_success(f"Product geplaatst: {ad_url}")
                return {
                    'status': 'completed',
                    'ad_url': ad_url,
                    'title': product.title,
                    'article_number': product.article_number,
                }
            else:
                log_error("Product niet geplaatst")
                return {
                    'status': 'failed',
                    'ad_url': None,
                    'title': product.title,
                    'article_number': product.article_number,
                    'error': 'Kon advertentie niet plaatsen',
                }
        
        except Exception as e:
            log_error(f"Fout bij plaatsen product: {e}")
            if os.getenv("MP_VERBOSE", "true").lower() in ("1", "true", "yes", "on"):
                import traceback
                log_error(traceback.format_exc())
            
            return {
                'status': 'failed',
                'ad_url': None,
                'title': product.title,
                'article_number': product.article_number,
                'error': str(e),
            }
    
    async def post_products(self, products: List[Product], skip_first_navigation: bool = False) -> List[Dict]:
        """Plaats meerdere producten"""
        results = []
        
        for index, product in enumerate(products, start=1):
            log_step(f"Product {index}/{len(products)}: {product.title}")
            # Skip navigation only for first product (we're already on the page)
            skip_nav = skip_first_navigation and index == 1
            result = await self.post_product(product, skip_navigation=skip_nav)
            results.append(result)
            
            # After first product, we need to navigate to place ad page again
            if index < len(products):
                # Navigate to place ad page for next product
                form_filler = FormFiller(self.page, self.base_url)
                await form_filler.navigate_to_place_ad(skip_if_already_there=False)
            
            # Small delay between products
            action_delay_ms = int(os.getenv('ACTION_DELAY_MS', '200'))
            await self.page.wait_for_timeout(action_delay_ms)
        
        return results
    
    async def close(self):
        """Sluit browser"""
        if self.browser:
            await self.browser.close()


def read_products_from_api(api_url: str) -> List[Product]:
    """Lees producten van API endpoint"""
    if not requests:
        raise ImportError("requests library is required for API mode. Install with: pip install requests")
    
    api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check if it's a list or single object
        products_data = data if isinstance(data, list) else [data]
        
        products = []
        for item in products_data:
            photos = item.get('photos', []) or []
            delivery_methods = item.get('delivery_methods', []) or []
            category_fields = item.get('category_fields') or {}
            
            price_str = normalize_price(str(item.get('price', '')).strip())
            
            product = Product(
                title=item.get('title', '').strip(),
                description=item.get('description', '').strip(),
                price=price_str,
                category_path=item.get('category_path') or None,
                location=item.get('location') or None,
                photos=photos,
                article_number=item.get('article_number') or None,
                condition=item.get('condition') or None,
                delivery_methods=delivery_methods,
                material=item.get('material') or None,
                thickness=item.get('thickness') or None,
                total_surface=item.get('total_surface') or None,
                delivery_option=item.get('delivery_option') or None,
                category_fields=category_fields if isinstance(category_fields, dict) else {},
            )
            products.append(product)
        
        log_success(f"{len(products)} product(en) opgehaald van API")
        return products
    except Exception as e:
        log_error(f"Error fetching products from API: {e}")
        raise


def read_products_from_csv(csv_path: str) -> List[Product]:
    """Lees producten van CSV bestand"""
    products: List[Product] = []
    
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            photos = [p.strip() for p in (row.get('photos') or '').split(';') if p.strip()]
            article_number = (row.get('article_number') or '').strip() or None
            delivery_methods = [m.strip() for m in (row.get('delivery_methods') or '').split(',') if m.strip()]
            
            product = Product(
                title=(row.get('title') or '').strip(),
                description=(row.get('description') or '').strip(),
                price=normalize_price(str(row.get('price', '')).strip()),
                category_path=(row.get('category_path') or '').strip() or None,
                location=(row.get('location') or '').strip() or None,
                photos=photos,
                article_number=article_number,
                condition=(row.get('condition') or '').strip() or None,
                delivery_methods=delivery_methods,
                material=(row.get('material') or '').strip() or None,
                thickness=(row.get('thickness') or '').strip() or None,
                total_surface=(row.get('total_surface') or '').strip() or None,
                delivery_option=(row.get('delivery_option') or '').strip() or None,
            )
            products.append(product)
    
    return products


async def run(
    csv_path: Optional[str] = None,
    api_url: Optional[str] = None,
    product_id: Optional[str] = None,
    login_only: bool = False,
    keep_open: bool = False,
    wait_for_manual_login: bool = False,
    wait_seconds: int = 10
) -> Optional[List[Dict]]:
    """
    Hoofdfunctie om producten te plaatsen
    
    Args:
        csv_path: Pad naar CSV bestand met producten
        api_url: URL naar API endpoint voor producten
        product_id: Specifiek product ID (gebruikt met api_url)
        login_only: Alleen inloggen, geen producten plaatsen
        keep_open: Browser open houden na uitvoering
        wait_for_manual_login: Wacht op handmatige login
        wait_seconds: Aantal seconden om te wachten op handmatige login
    """
    load_dotenv(override=True)
    
    base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
    user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
    media_root = os.getenv('MEDIA_ROOT', './public/media')
    
    os.makedirs(user_data_dir, exist_ok=True)
    
    automator = MarktplaatsAutomator(user_data_dir, media_root, base_url)
    
    try:
        # Start browser
        await automator.start(wait_for_manual_login=wait_for_manual_login, wait_seconds=wait_seconds)
        
        if login_only:
            log_success("Login session prepared. You can close the browser.")
            if not keep_open:
                await automator.close()
            return None
        
        # Read products
        if api_url:
            log_step(f"Ophalen producten van API: {api_url}")
            products = read_products_from_api(api_url)
        elif csv_path:
            log_step(f"Lezen producten van CSV: {csv_path}")
            products = read_products_from_csv(csv_path)
        else:
            raise ValueError("Either --csv or --api is required when not using --login")
        
        if not products:
            log_warning("Geen producten gevonden")
            return []
        
        # Post products
        results = await automator.post_products(products)
        
        log_success(f"Klaar! {len(results)} product(en) verwerkt")
        
        if keep_open:
            log_step("Browser blijft open voor inspectie...")
            await automator.page.wait_for_timeout(3600000)  # 1 hour
        else:
            await automator.close()
        
        return results
    
    except Exception as e:
        log_error(f"Fout: {e}")
        if os.getenv("MP_VERBOSE", "true").lower() in ("1", "true", "yes", "on"):
            import traceback
            log_error(traceback.format_exc())
        
        if automator:
            await automator.close()
        
        raise
