"""
Get the logged in Marktplaats account email/username
"""
import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def get_marktplaats_account() -> str | None:
    """Get the logged in Marktplaats account email or username"""
    load_dotenv()
    base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
    user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await browser.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(45000)
        
        try:
            # Go to Marktplaats homepage
            await page.goto(f"{base_url}/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Try to find account info in various places
            account_info = None
            
            # Method 1: Check for user menu/profile link
            try:
                profile_link = page.locator('a[href*="/u/"]').first
                if await profile_link.count() > 0:
                    href = await profile_link.get_attribute('href')
                    if href:
                        # Extract username from URL like /u/username/12345
                        parts = href.split('/u/')
                        if len(parts) > 1:
                            username = parts[1].split('/')[0]
                            account_info = username
            except:
                pass
            
            # Method 2: Check for email in user menu
            if not account_info:
                try:
                    # Look for user menu button
                    user_menu = page.locator('[data-testid="user-menu"], [aria-label*="account"], [aria-label*="profiel"]').first
                    if await user_menu.count() > 0:
                        await user_menu.click()
                        await page.wait_for_timeout(1000)
                        
                        # Look for email in dropdown
                        email_elem = page.locator('text=/@.*\\./').first
                        if await email_elem.count() > 0:
                            account_info = await email_elem.text_content()
                except:
                    pass
            
            # Method 3: Check page title or meta tags
            if not account_info:
                try:
                    title = await page.title()
                    if '@' in title:
                        # Extract email from title if present
                        import re
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', title)
                        if email_match:
                            account_info = email_match.group(0)
                except:
                    pass
            
            # Method 4: Use environment variable as fallback
            if not account_info:
                account_info = os.getenv('MARKTPLAATS_EMAIL')
            
            await browser.close()
            return account_info
            
        except Exception as e:
            print(f"Error getting Marktplaats account: {e}")
            await browser.close()
            return os.getenv('MARKTPLAATS_EMAIL')  # Fallback to env var

if __name__ == '__main__':
    result = asyncio.run(get_marktplaats_account())
    if result:
        print(f"MARKTPLAATS_ACCOUNT={result}")
    else:
        print("MARKTPLAATS_ACCOUNT=unknown")

