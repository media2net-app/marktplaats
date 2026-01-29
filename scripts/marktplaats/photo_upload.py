"""
Photo upload module voor Marktplaats advertenties
"""
import os
from typing import List
from playwright.async_api import Page

from .utils import (
    log_step, log_error, log_success, log_warning,
    WAIT_SHORT, WAIT_MEDIUM, VERBOSE, Product, find_photos_for_article
)


class PhotoUploader:
    """Upload foto's voor een Marktplaats advertentie"""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def upload_photos(self, product: Product, media_root: str):
        """Upload foto's voor een product"""
        # Get photos
        photos = await self._get_photos(product, media_root)
        
        if not photos:
            log_step("Geen foto's gevonden voor product; overslaan upload")
            return
        
        log_step(f"Foto's uploaden: {len(photos)} bestand(en)")
        for i, photo_path in enumerate(photos, 1):
            log_step(f"  Foto {i}: {os.path.basename(photo_path)}")
        
        # Wait a bit for page to fully load
        await self.page.wait_for_timeout(WAIT_MEDIUM)
        
        # Find file input
        file_input = await self._find_file_input()
        if not file_input:
            log_warning("Kon file input niet vinden op pagina - proberen alternatieve methoden...")
            
            # Try to scroll to find upload area
            try:
                upload_area = self.page.locator("[class*='upload'], [class*='photo'], [class*='image'], [data-testid*='upload']")
                if await upload_area.count() > 0:
                    await upload_area.first.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(WAIT_SHORT)
                    file_input = await self._find_file_input()
            except:
                pass
            
            if not file_input:
                log_error("Kon file input niet vinden op pagina")
                if os.getenv("MP_DEBUG_SCREENSHOTS", "false").lower() == "true":
                    try:
                        await self.page.screenshot(path="debug_no_file_input.png")
                        log_step("Screenshot opgeslagen: debug_no_file_input.png")
                    except:
                        pass
                return
        
        # Upload files
        try:
            log_step(f"Uploaden van {len(photos)} foto's...")
            
            # Scroll file input into view if possible
            try:
                await file_input.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(500)
            except:
                pass
            
            # Set files
            await file_input.set_input_files(photos)
            log_step("Bestanden toegevoegd aan file input")
            
            # Wait for upload - longer wait for multiple files
            # Marktplaats needs time to process and upload images
            upload_wait = 3000 + (len(photos) * 2000)  # 3 seconds base + 2 seconds per photo
            log_step(f"Wachten {upload_wait/1000:.1f} seconden op upload verwerking...")
            await self.page.wait_for_timeout(upload_wait)
            
            # Wait for network to be idle (uploads complete)
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
                log_step("Netwerk idle - uploads voltooid")
            except:
                log_step("Wachten op netwerk idle timeout, doorgaan...")
                await self.page.wait_for_timeout(2000)
            
            # Check for preview images or upload indicators
            try:
                # Wait for any image previews
                preview_selectors = [
                    "img[src*='blob']",
                    "img[src*='data:']",
                    "img[src*='base64']",
                    ".image-preview",
                    "[class*='preview']",
                    "[class*='upload']",
                    "[class*='photo']",
                    "[class*='image']",
                    "[data-testid*='image']",
                    "[data-testid*='photo']",
                ]
                
                preview_found = False
                for selector in preview_selectors:
                    try:
                        preview_images = self.page.locator(selector)
                        count = await preview_images.count()
                        if count > 0:
                            # Check if at least one is visible
                            for i in range(min(count, 5)):
                                try:
                                    is_visible = await preview_images.nth(i).is_visible()
                                    if is_visible:
                                        preview_found = True
                                        log_success(f"Foto preview gevonden ({selector})")
                                        break
                                except:
                                    continue
                            if preview_found:
                                break
                    except:
                        continue
                
                if not preview_found:
                    # Check for upload progress indicators or error messages
                    progress_selectors = [
                        "[class*='progress']",
                        "[class*='uploading']",
                        "[aria-label*='upload']",
                        "[class*='error']",
                        "[class*='failed']",
                    ]
                    for selector in progress_selectors:
                        try:
                            progress = self.page.locator(selector)
                            if await progress.count() > 0:
                                is_visible = await progress.first.is_visible()
                                if is_visible:
                                    text = await progress.first.text_content()
                                    if 'error' in text.lower() or 'failed' in text.lower():
                                        log_warning(f"Upload fout indicator gevonden: {text}")
                                    else:
                                        log_step("Upload indicator gevonden - wachten op voltooiing...")
                                        await self.page.wait_for_timeout(5000)
                                    break
                        except:
                            continue
                    
                    # Final check: look for any images on the page
                    all_images = self.page.locator("img")
                    image_count = await all_images.count()
                    if image_count > 0:
                        log_step(f"Gevonden {image_count} afbeelding(en) op pagina")
                        # Check if any are upload previews
                        for i in range(min(image_count, 10)):
                            try:
                                img = all_images.nth(i)
                                src = await img.get_attribute('src')
                                if src and ('blob' in src or 'data:' in src or 'upload' in src.lower()):
                                    log_success("Upload preview afbeelding gevonden!")
                                    preview_found = True
                                    break
                            except:
                                continue
                    
                    if not preview_found:
                        log_warning("Geen foto preview gevonden - mogelijk niet geüpload")
                        log_step("Extra wachttijd voor upload verwerking...")
                        await self.page.wait_for_timeout(5000)
                    else:
                        log_success("Foto's succesvol geüpload en geverifieerd")
                        
                        # Extra verificatie: wacht tot foto's echt zijn opgeslagen
                        # Check for image count or upload completion indicators
                        log_step("Wachten op definitieve opslag van foto's...")
                        
                        # Wait for upload to complete - check multiple times
                        for attempt in range(3):
                            await self.page.wait_for_timeout(2000)
                            
                            # Verify images are still there (not removed)
                            final_check = self.page.locator("img[src*='blob'], img[src*='data:'], [class*='image'], [class*='photo']")
                            final_count = await final_check.count()
                            
                            if final_count > 0:
                                # Check if at least one is visible
                                visible_count = 0
                                for i in range(min(final_count, 10)):
                                    try:
                                        img = final_check.nth(i)
                                        if await img.is_visible():
                                            visible_count += 1
                                    except:
                                        continue
                                
                                if visible_count > 0:
                                    log_success(f"Foto's bevestigd: {visible_count} afbeelding(en) zichtbaar na {attempt + 1} poging(en)")
                                    break
                                elif attempt == 2:
                                    log_warning(f"Foto's gevonden maar niet zichtbaar na {attempt + 1} pogingen")
                            elif attempt == 2:
                                log_warning("Geen foto's gevonden na wachttijd - mogelijk upload fout")
                        
                        # Final wait to ensure upload is complete
                        await self.page.wait_for_timeout(2000)
            except Exception as e:
                log_warning(f"Fout bij checken preview: {e}")
                log_success("Foto's geüpload (verificatie overgeslagen)")
                await self.page.wait_for_timeout(WAIT_SHORT)
        except Exception as e:
            log_error(f"Fout bij uploaden foto's: {e}")
            if VERBOSE:
                import traceback
                log_error(traceback.format_exc())
            
            # Take screenshot on error
            try:
                await self.page.screenshot(path="debug_photo_upload_error.png")
                log_step("Screenshot opgeslagen: debug_photo_upload_error.png")
            except:
                pass
    
    async def _get_photos(self, product: Product, media_root: str) -> List[str]:
        """Haal foto's op voor een product"""
        photos: List[str] = []
        
        log_step(f"Foto's ophalen voor product (media_root: {media_root})")
        
        # Get photos from product.photos
        if product.photos:
            log_step(f"Product heeft {len(product.photos)} foto path(s) in product.photos")
            for i, p in enumerate(product.photos, 1):
                if not p:
                    continue
                
                # Try as absolute path
                if os.path.isabs(p):
                    if os.path.exists(p):
                        photos.append(p)
                        log_step(f"  Foto {i}: {p} (gevonden als absolute path)")
                else:
                    # Try relative to current directory
                    abs_path = os.path.abspath(p)
                    if os.path.exists(abs_path):
                        photos.append(abs_path)
                        log_step(f"  Foto {i}: {abs_path} (gevonden als relative path)")
                    else:
                        # Try relative to media_root
                        abs_path = os.path.abspath(os.path.join(media_root, p))
                        if os.path.exists(abs_path):
                            photos.append(abs_path)
                            log_step(f"  Foto {i}: {abs_path} (gevonden in media_root)")
        
        # If no photos, try to find by article number
        if not photos and product.article_number:
            log_step(f"Geen foto's in product.photos, zoeken op artikelnummer: {product.article_number}")
            log_step(f"Media root: {os.path.abspath(media_root)}")
            
            # Check if media_root exists
            if not os.path.isdir(media_root):
                log_warning(f"Media root directory bestaat niet: {media_root}")
            else:
                log_step(f"Media root directory bestaat: {media_root}")
            
            found_photos = find_photos_for_article(media_root, product.article_number)
            if found_photos:
                photos = [os.path.abspath(p) for p in found_photos]
                log_success(f"{len(photos)} foto(s) gevonden op artikelnummer")
                for i, photo in enumerate(photos, 1):
                    log_step(f"  Foto {i}: {os.path.basename(photo)}")
            else:
                log_warning(f"Geen foto's gevonden voor artikelnummer: {product.article_number}")
                # List available folders for debugging
                if os.path.isdir(media_root):
                    try:
                        folders = [d for d in os.listdir(media_root) if os.path.isdir(os.path.join(media_root, d))]
                        if folders:
                            log_step(f"Beschikbare folders in media root: {', '.join(folders[:10])}")
                    except:
                        pass
        
        # Filter to only existing files and normalize paths
        existing_photos = []
        for p in photos:
            normalized = os.path.normpath(os.path.abspath(p))
            if os.path.exists(normalized):
                existing_photos.append(normalized)
            else:
                log_warning(f"Foto bestaat niet: {normalized}")
        
        return existing_photos
    
    async def _find_file_input(self):
        """Zoek file input element op de pagina"""
        selectors = [
            "#imageUploader-hiddenInput",  # Specific Marktplaats ID
            "input[id='imageUploader-hiddenInput']",
            "input.ImageUploaderInput-module-filePicker",
            "input[type='file'][multiple][accept*='image']",
            "input[type='file'][multiple]",
            "input[type='file'][accept*='image']",
            "input[type='file'][accept*='.jpg']",
            "input[type='file'][accept*='.jpeg']",
            "input[type='file'][accept*='.png']",
            "input[type='file'][accept*='.heic']",
            "input[type='file'][id^='html5_']",
            "input[type='file']",  # Fallback
        ]
        
        for sel in selectors:
            try:
                locator = self.page.locator(sel)
                count = await locator.count()
                if count > 0:
                    # Check all matching inputs
                    for i in range(count):
                        input_elem = locator.nth(i)
                        try:
                            is_visible = await input_elem.is_visible()
                            is_enabled = await input_elem.is_enabled()
                            
                            # Sometimes file inputs are hidden but still usable
                            if is_enabled or not is_visible:
                                log_step(f"File input gevonden met selector: {sel} (index {i})")
                                return input_elem
                        except:
                            continue
            except Exception as e:
                if VERBOSE:
                    log_step(f"Selector '{sel}' fout: {e}")
                continue
        
        # Last resort: try to find by clicking upload button/area
        try:
            upload_buttons = [
                "button:has-text('Foto')",
                "button:has-text('Upload')",
                "[aria-label*='foto']",
                "[aria-label*='upload']",
                "[data-testid*='upload']",
            ]
            
            for btn_sel in upload_buttons:
                try:
                    btn = self.page.locator(btn_sel).first
                    if await btn.count() > 0:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            # Click button to reveal file input
                            await btn.click()
                            await self.page.wait_for_timeout(WAIT_SHORT)
                            # Try finding file input again
                            for sel in selectors[:5]:  # Try first few selectors
                                locator = self.page.locator(sel)
                                if await locator.count() > 0:
                                    log_step(f"File input gevonden na klikken upload button: {sel}")
                                    return locator.first
                except:
                    continue
        except:
            pass
        
        return None
