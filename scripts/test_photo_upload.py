"""
Test script om foto upload te testen in Chromium browser.
Dit opent een echte browser en test de foto upload functionaliteit.
"""
import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_photo_upload():
    """Test foto upload op Marktplaats."""
    print("=" * 70)
    print("Foto Upload Test - Marktplaats")
    print("=" * 70)
    print()
    
    # Use an existing image or ask user to provide one
    test_image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
    if not os.path.exists(test_image_path):
        # Try to find any image in the media directory
        media_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "media")
        if os.path.exists(media_dir):
            # Look for any image file
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_image_path = os.path.join(root, file)
                        print(f"[INFO] Test image gevonden: {test_image_path}")
                        break
                if test_image_path and os.path.exists(test_image_path):
                    break
        
        if not os.path.exists(test_image_path):
            print(f"[WARNING] Geen test image gevonden!")
            print(f"  Maak een test image aan op: {test_image_path}")
            print(f"  Of plaats een image in: {media_dir}")
            print()
            print("  Je kunt ook een bestaand product gebruiken met foto's.")
            print("  Het script zal proberen een bestaande foto te vinden...")
            print()
    
    print(f"Test image: {test_image_path}")
    print(f"Image exists: {os.path.exists(test_image_path)}")
    print()
    
    # Get user data directory
    user_data_dir = os.path.join(os.path.expanduser("~"), ".marktplaats_browser")
    os.makedirs(user_data_dir, exist_ok=True)
    
    async with async_playwright() as p:
        print("Verbinden met Chrome browser...")
        # Try to connect to existing Chrome instance with remote debugging
        browser = None
        try:
            # Try to connect to existing Chrome with remote debugging
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("[OK] Verbonden met bestaande Chrome sessie (remote debugging)")
            pages = browser.pages
            if pages:
                page = pages[0]
                print(f"[OK] Gebruik bestaande tab: {await page.title()}")
            else:
                page = await browser.new_page()
        except Exception as e:
            print(f"[INFO] Kon niet verbinden met remote debugging: {e}")
            print("  Start Chrome met: chrome.exe --remote-debugging-port=9222")
            print("  OF gebruik launch_persistent_context met je Chrome profiel...")
            print()
            
            # Use a separate user data directory for testing to avoid conflicts
            test_user_data = os.path.join(os.path.expanduser("~"), ".marktplaats_chrome_test")
            os.makedirs(test_user_data, exist_ok=True)
            print(f"Gebruik test Chrome user data: {test_user_data}")
            try:
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=test_user_data,
                    headless=False,
                    viewport={"width": 1280, "height": 900},
                    args=["--disable-blink-features=AutomationControlled"],
                    channel="chrome",  # Use Chrome instead of Chromium
                )
                # Get the first page or create a new one
                pages = browser.pages
                if pages:
                    page = pages[0]
                else:
                    page = await browser.new_page()
                print("[OK] Chrome gestart met test profiel")
            except Exception as e2:
                print(f"[ERROR] Kon Chrome niet starten: {e2}")
                import traceback
                print(traceback.format_exc())
                print()
                print("  OPLOSSING:")
                print("  1. Sluit alle Chrome vensters")
                print("  2. Start Chrome met: start_chrome_for_test.bat")
                print("  3. Of start handmatig:")
                print("     chrome.exe --remote-debugging-port=9222")
                print("  4. Draai dan dit script opnieuw")
                return
        
        if not browser:
            print("[ERROR] Kon browser niet starten of verbinden")
            return
        
        if 'page' not in locals():
            page = await browser.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(45000)
        
        print("Navigeren naar Marktplaats plaats pagina...")
        await page.goto("https://www.marktplaats.nl/plaats", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Check current URL
        current_url = page.url
        print(f"Huidige URL: {current_url}")
        
        # If we're on login page, wait for user to login manually
        if "login" in current_url.lower() or "identity" in current_url.lower():
            print()
            print("[INFO] Je bent op de login pagina.")
            print("  Als je al ingelogd bent in Chrome, klik dan op 'Plaats advertentie' in de header.")
            print("  Of log in en ga naar de advertentie plaats pagina.")
            print("  Het script wacht tot je op de advertentie plaats pagina bent...")
            print()
            
            # Wait for navigation to plaats page
            try:
                await page.wait_for_url("**/plaats**", timeout=120000)  # Wait up to 2 minutes
                print("[OK] Op advertentie plaats pagina!")
            except:
                print("[WARNING] Nog niet op plaats pagina, maar verder gaan...")
                current_url = page.url
                print(f"  Huidige URL: {current_url}")
        
        # Wait for page to be ready
        await page.wait_for_load_state("networkidle", timeout=10000)
        await page.wait_for_timeout(2000)
        
        print("Zoeken naar file input element...")
        await page.wait_for_timeout(1000)
        
        # Try multiple selectors for file input
        # Marktplaats uses specific IDs and classes for file upload
        selectors = [
            "#imageUploader-hiddenInput",  # Specific Marktplaats ID
            "input[id='imageUploader-hiddenInput']",  # Alternative selector
            "input.ImageUploaderInput-module-filePicker",  # Class selector
            "input[type='file'][multiple][accept*='image']",  # Multiple with image accept
            "input[type='file'][multiple]",  # Multiple file input
            "input[type='file'][accept*='image']",  # Image accept
            "input[type='file'][accept*='.jpg']",  # JPG accept
            "input[type='file'][accept*='.jpeg']",  # JPEG accept
            "input[type='file'][accept*='.png']",  # PNG accept
            "input[type='file'][accept*='.heic']",  # HEIC accept
            "input[type='file'][id^='html5_']",  # HTML5 uploader pattern
            "input[type='file']",  # Fallback: any file input
        ]
        
        file_input = None
        found_selector = None
        
        for sel in selectors:
            try:
                locator = page.locator(sel)
                count = await locator.count()
                print(f"  Selector '{sel}': {count} element(en) gevonden")
                if count > 0:
                    # For hidden inputs, check if enabled (they can be hidden but still usable)
                    is_enabled = await locator.first.is_enabled()
                    is_visible = await locator.first.is_visible()
                    print(f"    Zichtbaar: {is_visible}, Enabled: {is_enabled}")
                    if is_enabled:  # Hidden inputs can still be used
                        file_input = locator.first
                        found_selector = sel
                        print(f"  [OK] File input gevonden met selector: {sel}")
                        break
            except Exception as e:
                print(f"    Fout: {e}")
                continue
        
        if not file_input:
            print()
            print("[ERROR] Kon file input niet vinden!")
            print("Screenshot maken voor debugging...")
            await page.screenshot(path="debug_no_file_input.png", full_page=True)
            print("Screenshot opgeslagen: debug_no_file_input.png")
            print()
            print("Wachten 10 seconden zodat je de pagina kunt bekijken...")
            await page.wait_for_timeout(10000)
            await browser.close()
            return
        
        print()
        print(f"File input gevonden! Proberen foto te uploaden: {test_image_path}")
        
        try:
            # Upload the test image
            await file_input.set_input_files(test_image_path)
            print("[OK] Foto geüpload!")
            
            # Wait a bit
            await page.wait_for_timeout(2000)
            
            # Check for preview images or success indicators
            try:
                preview_images = page.locator("img[src*='blob'], img[src*='data:'], .image-preview, [class*='preview'], [class*='upload']")
                count = await preview_images.count()
                print(f"Preview images gevonden: {count}")
                if count > 0:
                    print("[OK] Foto preview gevonden - upload succesvol!")
                else:
                    print("[INFO] Geen preview gevonden, maar upload mogelijk wel gelukt")
            except:
                print("[INFO] Kon preview niet controleren")
            
            print()
            print("Wachten 10 seconden zodat je het resultaat kunt bekijken...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"[ERROR] Fout bij uploaden: {e}")
            import traceback
            print(traceback.format_exc())
            await page.screenshot(path="debug_upload_error.png", full_page=True)
            print("Screenshot opgeslagen: debug_upload_error.png")
            await page.wait_for_timeout(5000)
        
        print()
        print("Browser sluiten...")
        await browser.close()
        print("[OK] Test voltooid!")

if __name__ == "__main__":
    try:
        asyncio.run(test_photo_upload())
    except KeyboardInterrupt:
        print("\nTest geannuleerd door gebruiker")
    except Exception as e:
        print(f"\n[ERROR] Fout: {e}")
        import traceback
        traceback.print_exc()

