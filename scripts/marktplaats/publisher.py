"""
Publisher module voor Marktplaats advertenties
Plaatst advertenties en haalt de URL op
"""
import os
from typing import Optional
from playwright.async_api import Page

from .utils import (
    log_step, log_error, log_success, log_warning,
    WAIT_SHORT, WAIT_MEDIUM, VERBOSE
)


class Publisher:
    """Publiceert Marktplaats advertenties"""
    
    def __init__(self, page: Page, base_url: str = "https://www.marktplaats.nl"):
        self.page = page
        self.base_url = base_url.rstrip('/')
    
    async def publish_ad(self, product_title: Optional[str] = None, photo_uploader=None, product=None, media_root: str = None) -> Optional[str]:
        """Publiceer advertentie en retourneer URL"""
        # If photos weren't uploaded yet and we're still on form page, try to upload them now
        if photo_uploader and product and media_root:
            current_url = self.page.url
            if '/plaats/' in current_url:
                log_step("Controleren of foto's al zijn geüpload...")
                # Check if photos are already visible
                existing_images = self.page.locator("img[src*='blob'], img[src*='data:'], [class*='image']")
                image_count = await existing_images.count()
                if image_count == 0:
                    log_step("Geen foto's gevonden op formulier - proberen te uploaden...")
                    await photo_uploader.upload_photos(product, media_root)
                    await self.page.wait_for_timeout(5000)
        
        # First check if we're on the ad plan selection page
        if await self._is_on_plan_selection_page():
            log_step("Op advertentieplan selectie pagina - selecteren gratis plan en doorgaan...")
            plan_clicked = await self._select_free_plan_and_continue()
            if plan_clicked:
                # After clicking on plan page, wait for navigation to result page
                log_step("Wachten op navigatie na klikken op plan pagina...")
                try:
                    await self.page.wait_for_url(
                        lambda url: '/plaats/' not in url,
                        timeout=20000,
                        state="domcontentloaded"
                    )
                    log_step("Navigatie gedetecteerd na plan pagina")
                except:
                    log_step("Geen directe navigatie, wachten...")
                    await self.page.wait_for_timeout(5000)
                
                # Check if we're now on a success page or ad page
                current_url = self.page.url
                if '/v/' in current_url or '/a' in current_url:
                    log_success("Direct naar ad pagina genavigeerd!")
                    return current_url
                
                # Try to get ad URL from current page
                ad_url = await self._get_posted_ad_url(product_title)
                if ad_url:
                    return ad_url
                
                # If we're still on form page, continue with normal flow
                if '/plaats/' in current_url:
                    log_step("Nog steeds op formulier pagina, proberen normale plaats knop...")
                else:
                    # We're on some other page, try to find ad URL
                    return await self._get_posted_ad_url(product_title)
            else:
                log_warning("Kon gratis plan niet selecteren, proberen direct plaatsen...")
        
        log_step("Zoeken naar 'Plaats advertentie' knop...")
        
        url_before = self.page.url
        log_step(f"URL voor plaatsen: {url_before}")
        
        # Only try to click publish button if we're still on form page
        if '/plaats/' in url_before:
            button_clicked = await self._click_publish_button()
            
            if not button_clicked:
                log_error("Geen knop gevonden om advertentie te plaatsen")
                return None
        else:
            log_step("Niet op formulier pagina, proberen ad URL te vinden...")
            ad_url = await self._get_posted_ad_url(product_title)
            if ad_url:
                return ad_url
            return None
        
        # Wait for processing - wait longer and check for navigation
        log_step("Wachten op verwerking...")
        
        # Wait for navigation away from form page
        try:
            await self.page.wait_for_url(
                lambda url: '/plaats/' not in url,
                timeout=15000,
                state="domcontentloaded"
            )
            log_step("Navigatie gedetecteerd - formulier verlaten")
        except:
            log_step("Geen navigatie gedetecteerd na 15 seconden")
            await self.page.wait_for_timeout(3000)
        
        url_after = self.page.url
        log_step(f"URL na plaatsen: {url_after}")
        
        # Check for errors
        if await self._check_for_errors():
            log_error("Foutmelding gedetecteerd - advertentie niet geplaatst")
            return None
        
        # Get ad URL
        ad_url = await self._get_posted_ad_url(product_title)
        
        if ad_url:
            log_success(f"Advertentie geplaatst: {ad_url}")
            return ad_url
        else:
            log_warning("Geen ad URL gevonden na plaatsen")
            return None
    
    async def _click_publish_button(self) -> bool:
        """Klik op de plaats advertentie knop"""
        # Try specific ID first
        try:
            btn = self.page.locator("#syi-place-ad-button")
            if await btn.count() > 0:
                log_step("Knop #syi-place-ad-button gevonden")
                await btn.first.scroll_into_view_if_needed()
                
                try:
                    await btn.first.wait_for(state="visible", timeout=3000 if os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on") else 5000)
                except:
                    pass
                
                try:
                    is_disabled = await btn.first.get_attribute('disabled')
                    if is_disabled:
                        log_warning("Knop is uitgeschakeld (disabled)")
                    else:
                        log_step("Klikken op knop...")
                        await btn.first.click(force=True)
                        await self.page.wait_for_timeout(2000)
                        await self.page.wait_for_load_state('domcontentloaded')
                        return True
                except Exception as e:
                    log_step(f"Fout bij klikken: {e}, proberen JavaScript click...")
                    try:
                        await btn.first.evaluate("(b)=>b.click()")
                        await self.page.wait_for_timeout(2000)
                        await self.page.wait_for_load_state('domcontentloaded')
                        return True
                    except Exception as e2:
                        log_warning(f"JavaScript click ook gefaald: {e2}")
        except Exception as e:
            log_warning(f"Fout bij zoeken naar #syi-place-ad-button: {e}")
        
        # Try generic buttons (prioritize "Plaats je advertentie")
        candidates = [
            ("button", "Plaats je advertentie"),
            ("button", "Plaats"),
            ("button", "Publiceer"),
            ("button", "Doorgaan"),
            ("link", "Plaats je advertentie"),
            ("link", "Plaats"),
        ]
        
        for role, text in candidates:
            try:
                locator = self.page.get_by_role(role, name=text)
                if await locator.count() > 0:
                    log_step(f"Knop gevonden: {role} met tekst '{text}'")
                    await locator.first.scroll_into_view_if_needed()
                    await locator.first.click(force=True)
                    await self.page.wait_for_timeout(2000)
                    await self.page.wait_for_load_state('domcontentloaded')
                    return True
            except Exception:
                continue
        
        # Try variants
        variants = [
            "text=Plaats je advertentie",
            "span:has-text('Plaats je advertentie')",
            "button:has-text('Plaats je advertentie')",
            "[aria-label='Plaats je advertentie']",
            "[data-testid='placeAd'], [data-role='placeAd']",
            "[type='submit']",
        ]
        
        for sel in variants:
            try:
                loc = self.page.locator(sel)
                if await loc.count() > 0:
                    log_step(f"Knop gevonden met selector: {sel}")
                    await loc.first.scroll_into_view_if_needed()
                    await loc.first.click(force=True)
                    await self.page.wait_for_timeout(2000)
                    await self.page.wait_for_load_state('domcontentloaded')
                    return True
            except Exception:
                continue
        
        # Last resort: form submit
        try:
            form = self.page.locator("form").last
            if await form.count() > 0:
                log_step("Form submit proberen...")
                await form.evaluate("(f)=>f.submit()")
                await self.page.wait_for_timeout(2000)
                await self.page.wait_for_load_state('domcontentloaded')
                return True
        except Exception:
            pass
        
        return False
    
    async def _is_on_plan_selection_page(self) -> bool:
        """Check of we op de advertentieplan selectie pagina zijn"""
        try:
            # Check for key indicators of plan selection page
            indicators = [
                "text=Hoe wil je adverteren",
                "text=Kies een advertentievorm",
                "text=Gratis",
                "text=Plus",
                "text=Premium",
                "[id*='feature-FREE']",
                "[id*='feature-PLUS']",
                "[id*='feature-PREMIUM']",
            ]
            
            for indicator in indicators:
                try:
                    elem = self.page.locator(indicator).first
                    if await elem.count() > 0:
                        is_visible = await elem.is_visible()
                        if is_visible:
                            log_step(f"Advertentieplan pagina gedetecteerd via: {indicator}")
                            return True
                except:
                    continue
            
            # Check URL
            current_url = self.page.url
            if '/bundle' in current_url or '/plan' in current_url or '/advertentievorm' in current_url:
                log_step("Advertentieplan pagina gedetecteerd via URL")
                return True
            
            return False
        except:
            return False
    
    async def _select_free_plan_and_continue(self) -> bool:
        """Selecteer gratis plan en klik op 'Plaats je advertentie'"""
        try:
            # Wait a bit for page to load
            await self.page.wait_for_timeout(WAIT_MEDIUM)
            
            # Check if "Gratis" is already selected (should be by default)
            free_plan_indicators = [
                "text=Gratis",
                "[id*='feature-FREE']",
                "button:has-text('Gekozen')",
                "button:has-text('Gratis')",
            ]
            
            free_selected = False
            for indicator in free_plan_indicators:
                try:
                    elem = self.page.locator(indicator).first
                    if await elem.count() > 0:
                        # Check if there's a "Gekozen" button (means already selected)
                        gekozen_btn = self.page.locator("button:has-text('Gekozen')").first
                        if await gekozen_btn.count() > 0:
                            log_step("Gratis plan is al geselecteerd")
                            free_selected = True
                            break
                except:
                    continue
            
            # If not selected, try to select it
            if not free_selected:
                log_step("Gratis plan selecteren...")
                try:
                    # Try to find and click the "Gratis" option
                    free_options = [
                        "button:has-text('Gratis'):not(:has-text('Gekozen'))",
                        "[id*='feature-FREE'] button",
                        "button:has-text('Kiezen')",
                    ]
                    
                    for option in free_options:
                        try:
                            btn = self.page.locator(option).first
                            if await btn.count() > 0:
                                is_visible = await btn.is_visible()
                                if is_visible:
                                    await btn.scroll_into_view_if_needed()
                                    await btn.click()
                                    await self.page.wait_for_timeout(WAIT_SHORT)
                                    log_success("Gratis plan geselecteerd")
                                    free_selected = True
                                    break
                        except:
                            continue
                except Exception as e:
                    log_warning(f"Fout bij selecteren gratis plan: {e}")
            
            # Now click "Plaats je advertentie" button
            log_step("Zoeken naar 'Plaats je advertentie' knop op plan pagina...")
            
            place_buttons = [
                "button:has-text('Plaats je advertentie')",
                "button:has-text('Plaats advertentie')",
                "a:has-text('Plaats je advertentie')",
                "[data-testid*='place']",
                "[aria-label*='Plaats']",
            ]
            
            for btn_selector in place_buttons:
                try:
                    btn = self.page.locator(btn_selector).first
                    if await btn.count() > 0:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            log_step(f"Knop gevonden: {btn_selector}")
                            await btn.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(WAIT_SHORT)
                            await btn.click()
                            await self.page.wait_for_timeout(WAIT_MEDIUM)
                            await self.page.wait_for_load_state('domcontentloaded')
                            log_success("Geklikt op 'Plaats je advertentie' op plan pagina")
                            return True
                except:
                    continue
            
            log_warning("Kon 'Plaats je advertentie' knop niet vinden op plan pagina")
            return False
            
        except Exception as e:
            log_warning(f"Fout bij selecteren gratis plan en doorgaan: {e}")
            return False
    
    async def _check_for_errors(self) -> bool:
        """Check voor foutmeldingen"""
        await self.page.wait_for_timeout(2000)  # Wait for errors to appear
        
        error_selectors = [
            "text=Er is een fout opgetreden",
            "text=Er ging iets mis",
            "text=Probeer het opnieuw",
            "text=Verplicht veld",
            "text=Dit veld is verplicht",
            "[class*='error']",
            "[class*='Error']",
            "[role='alert']",
            ".error-message",
            "[data-testid*='error']",
        ]
        
        for selector in error_selectors:
            try:
                error_elem = self.page.locator(selector).first
                if await error_elem.count() > 0:
                    is_visible = await error_elem.is_visible()
                    if is_visible:
                        error_text = await error_elem.text_content()
                        if error_text and error_text.strip():
                            log_warning(f"Foutmelding gevonden ({selector}): {error_text}")
                            return True
            except:
                continue
        
        # Check if we're still on the form page (might indicate an error)
        current_url = self.page.url
        if '/plaats/' in current_url:
            # Still on form page - might be an error
            # But don't treat this as error if we just clicked
            log_step("Nog steeds op formulier pagina - controleren of er verplichte velden ontbreken...")
            
            # Check for required field indicators
            required_fields = self.page.locator("[required], [aria-required='true']")
            required_count = await required_fields.count()
            if required_count > 0:
                log_step(f"Gevonden {required_count} verplichte velden op pagina")
            
            # Check if publish button is still visible (might mean form wasn't submitted)
            publish_btn = self.page.locator("#syi-place-ad-button, button:has-text('Plaats')")
            if await publish_btn.count() > 0:
                is_visible = await publish_btn.first.is_visible()
                if is_visible:
                    log_warning("Plaats knop is nog steeds zichtbaar - mogelijk niet doorgestuurd")
                    # Don't return True here - might just need more time
        
        return False
    
    async def _get_posted_ad_url(self, product_title: Optional[str] = None) -> Optional[str]:
        """Haal URL op van geplaatste advertentie"""
        # Wait a bit
        fast_mode = os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on")
        await self.page.wait_for_timeout(2000 if fast_mode else 4000)
        
        current_url = self.page.url
        log_step(f"Current URL na plaatsen: {current_url}")
        
        # Check if current URL is an ad page
        if '/help/' in current_url or '/voorwaarden' in current_url or '/privacy' in current_url:
            log_warning("Op help/voorwaarden pagina, niet op ad pagina")
        elif '/v/' in current_url or '/a' in current_url:
            log_success(f"Ad URL gevonden in current URL: {current_url}")
            return current_url
        
        # Try to find "Bekijk je advertentie" link
        view_ad_texts = [
            "Bekijk je advertentie",
            "Bekijk advertentie",
            "Naar je advertentie",
            "Je advertentie bekijken"
        ]
        
        for text in view_ad_texts:
            try:
                view_ad_link = self.page.get_by_text(text, exact=False)
                if await view_ad_link.count() > 0:
                    parent = view_ad_link.first.locator("..")
                    href = await parent.get_attribute('href')
                    if not href:
                        href = await view_ad_link.first.get_attribute('href')
                    
                    if href and ('/v/' in href or '/a' in href):
                        if href.startswith('http'):
                            log_success(f"Ad URL gevonden via '{text}': {href}")
                            return href
                        else:
                            full_url = f"{self.base_url}{href}"
                            log_success(f"Ad URL gevonden via '{text}': {full_url}")
                            return full_url
            except Exception:
                continue
        
        # Try to find ad links
        ad_link = self.page.locator("a[href*='/v/'], a[href*='/a']").first
        if await ad_link.count() > 0:
            href = await ad_link.get_attribute('href')
            if href and '/help/' not in href and '/voorwaarden' not in href and '/privacy' not in href:
                if href.startswith('http'):
                    log_success(f"Ad URL gevonden via link: {href}")
                    return href
                else:
                    full_url = f"{self.base_url}{href}"
                    log_success(f"Ad URL gevonden via link: {full_url}")
                    return full_url
        
        # Try "Mijn advertenties" page as last resort
        log_step("Ad URL niet gevonden op huidige pagina, proberen 'Mijn advertenties'...")
        await self.page.wait_for_timeout(5000)
        
        my_ads_urls = [
            f"{self.base_url}/my-account/sell/index.html",
            f"{self.base_url}/mijn-marktplaats/mijn-advertenties",
            f"{self.base_url}/mijn-marktplaats",
        ]
        
        for my_ads_url in my_ads_urls:
            try:
                log_step(f"Navigeren naar: {my_ads_url}")
                await self.page.goto(my_ads_url, wait_until="domcontentloaded", timeout=30000)
                await self.page.wait_for_timeout(5000)
                
                current_url_after = self.page.url
                if 'login' in current_url_after.lower() or 'inloggen' in current_url_after.lower():
                    log_warning("Niet ingelogd - kan 'Mijn advertenties' niet openen")
                    continue
                
                # Look for first ad link
                ad_selectors = [
                    'table a[href*="/v/"]',
                    'table a[href*="/a"]',
                    'tbody a[href*="/v/"]',
                    'tbody a[href*="/a"]',
                    'tr a[href*="/v/"]',
                    'tr a[href*="/a"]',
                    'li a[href*="/v/"]',
                    'li a[href*="/a"]',
                    'article[data-testid="ad"] a[href*="/v/"]',
                    'article[data-testid="ad"] a[href*="/a"]',
                    'a[href*="/v/"]',
                    'a[href*="/a"]',
                ]
                
                for selector in ad_selectors:
                    try:
                        ad_links = self.page.locator(selector)
                        count = await ad_links.count()
                        
                        if count > 0:
                            first_ad = ad_links.first
                            is_visible = await first_ad.is_visible()
                            if not is_visible:
                                continue
                            
                            href = await first_ad.get_attribute('href')
                            
                            if href and ('/v/' in href or '/a' in href):
                                if '/help/' not in href and '/voorwaarden' not in href:
                                    if href.startswith('http'):
                                        log_success(f"Ad URL gevonden in Mijn advertenties: {href}")
                                        return href
                                    else:
                                        full_url = f"{self.base_url}{href}" if not href.startswith('/') else f"{self.base_url}{href}"
                                        log_success(f"Ad URL gevonden in Mijn advertenties: {full_url}")
                                        return full_url
                    except Exception:
                        continue
            except Exception as e:
                log_warning(f"Fout bij navigeren naar {my_ads_url}: {e}")
                continue
        
        log_warning("Kon geen ad URL vinden")
        return None
