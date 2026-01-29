#!/usr/bin/env python3
"""
Open Chromium browser for Marktplaats login
============================================

Dit script opent de Chromium browser met dezelfde user data directory
als het hoofdscript, zodat je kunt inloggen en de sessie behouden blijft.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Configuration
MARKTPLAATS_BASE_URL = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
USER_DATA_DIR = os.getenv('USER_DATA_DIR', os.path.join(os.path.expanduser('~'), '.marktplaats_browser'))

# Ensure directory exists
os.makedirs(USER_DATA_DIR, exist_ok=True)


async def main():
    """Open browser for login."""
    print("=" * 70)
    print("Marktplaats Browser - Inloggen")
    print("=" * 70)
    print("")
    print(f"User Data Directory: {USER_DATA_DIR}")
    print(f"Marktplaats URL: {MARKTPLAATS_BASE_URL}")
    print("")
    print("De browser wordt geopend. Log in op Marktplaats.")
    print("De browser blijft open zodat je kunt inloggen.")
    print("Sluit de browser wanneer je klaar bent.")
    print("")
    
    async with async_playwright() as p:
        try:
            # Launch browser in visible mode (not headless)
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,  # Always visible for login
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
            
            # Create a new page
            page = await browser.new_page()
            
            # Navigate to Marktplaats login page
            login_url = f"{MARKTPLAATS_BASE_URL}/my-account/sell/index.html"
            print(f"Navigeren naar: {login_url}")
            await page.goto(login_url, wait_until="domcontentloaded")
            
            print("")
            print("✅ Browser is geopend!")
            print("")
            print("Je kunt nu inloggen op Marktplaats.")
            print("De browser blijft open totdat je deze sluit.")
            print("")
            print("Druk op Ctrl+C om dit script te stoppen (browser blijft open).")
            print("")
            
            # Keep the browser open
            try:
                # Wait indefinitely (until user closes browser or presses Ctrl+C)
                while True:
                    await asyncio.sleep(1)
                    # Check if browser is still connected
                    if not browser.pages:
                        print("\nBrowser is gesloten. Script stopt.")
                        break
            except KeyboardInterrupt:
                print("\n\nScript gestopt door gebruiker.")
                print("Browser blijft open - je kunt deze handmatig sluiten.")
            
        except Exception as e:
            print(f"❌ Fout bij openen browser: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGestopt door gebruiker.")
    except Exception as e:
        print(f"Fatale fout: {e}")
        sys.exit(1)
