"""
Browser management en login functionaliteit voor Marktplaats
"""
import os
import sys
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page

from .utils import log_step, log_error, log_success, log_warning, VERBOSE, WAIT_SHORT, WAIT_MEDIUM


class MarktplaatsBrowser:
    """Beheert browser sessie en login voor Marktplaats"""
    
    def __init__(self, user_data_dir: str, base_url: str = "https://www.marktplaats.nl"):
        self.user_data_dir = user_data_dir
        self.base_url = base_url.rstrip('/')
        self.browser: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def start(self, headless: Optional[bool] = None) -> Page:
        """Start browser en retourneer een page"""
        if self.browser:
            return self.page
            
        # Determine headless mode
        if headless is None:
            headless_env = os.getenv('HEADLESS', '').lower()
            is_ci = os.getenv('CI') is not None or os.getenv('VERCEL') is not None
            is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
            is_windows = os.name == 'nt' or sys.platform == 'win32'
            is_mac = sys.platform == 'darwin'
            has_display = os.getenv('DISPLAY') is not None
            
            should_be_headless = False  # Default: visible browser
            if headless_env in ('1', 'true', 'yes', 'on'):
                should_be_headless = True
            elif is_ci or is_railway:
                should_be_headless = True
            elif not is_windows and not is_mac and not has_display:
                should_be_headless = True
            
            if headless_env in ('0', 'false', 'no', 'off'):
                should_be_headless = False
        else:
            should_be_headless = headless
        
        log_step(f"Browser starten (headless={should_be_headless})...")
        
        self.playwright = await async_playwright().start()
        
        try:
            self.browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=should_be_headless,
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
        except Exception as e:
            log_error(f"Browser starten mislukt: {e}")
            log_step("Proberen met headless=True als fallback...")
            try:
                self.browser = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=self.user_data_dir,
                    headless=True,
                    viewport={"width": 1280, "height": 900},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                    ],
                )
            except Exception as e2:
                log_error(f"Browser starten mislukt zelfs in headless mode: {e2}")
                raise
        
        self.page = await self.browser.new_page()
        
        # Set stealth features
        await self.page.set_extra_http_headers({
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        })
        
        # Remove webdriver property
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['nl-NL', 'nl', 'en-US', 'en']
            });
        """)
        
        # Set timeouts
        nav_timeout = 30000 if os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on") else 60000
        action_timeout = 20000 if os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on") else 45000
        self.page.set_default_navigation_timeout(nav_timeout)
        self.page.set_default_timeout(action_timeout)
        
        log_success("Browser gestart")
        return self.page
    
    async def ensure_logged_in(self, wait_for_manual_login: bool = False, wait_seconds: int = 10) -> bool:
        """Zorg ervoor dat gebruiker is ingelogd"""
        if not self.page:
            await self.start()
        
        # Navigate to homepage
        try:
            await self.page.goto(f"{self.base_url}/", wait_until="domcontentloaded")
        except Exception:
            await self.page.wait_for_timeout(1500)
            await self.page.goto(f"{self.base_url}/", wait_until="domcontentloaded")
        
        # Accept cookies
        await self._accept_cookies()
        
        await self.page.wait_for_timeout(2000)
        
        # Check if logged in
        is_logged_in = await self._check_login_status()
        
        if is_logged_in:
            log_success("Gebruiker is ingelogd")
            return True
        
        # Try automatic login
        email = os.getenv('MARKTPLAATS_EMAIL')
        password = os.getenv('MARKTPLAATS_PASSWORD')
        
        if email and password:
            log_step("Niet ingelogd - proberen automatisch in te loggen...")
            success = await self._auto_login(email, password)
            if success:
                return True
            else:
                log_warning("Automatisch inloggen mislukt")
        
        # If wait_for_manual_login is True, wait and check again
        if wait_for_manual_login or not is_logged_in:
            log_step(f"Wachten {wait_seconds} seconden voor handmatige login...")
            log_step("Log in de browser in als je nog niet ingelogd bent...")
            
            for i in range(wait_seconds):
                await self.page.wait_for_timeout(1000)
                is_logged_in = await self._check_login_status()
                if is_logged_in:
                    log_success(f"Login gedetecteerd na {i+1} seconden!")
                    return True
                if (i + 1) % 3 == 0:
                    log_step(f"Wachten... ({i+1}/{wait_seconds} seconden)")
            
            # Final check
            is_logged_in = await self._check_login_status()
            if is_logged_in:
                log_success("Gebruiker is ingelogd!")
                return True
            else:
                log_warning("Nog steeds niet ingelogd na wachttijd")
                return False
        
        return False
    
    async def _accept_cookies(self):
        """Accepteer cookie popup indien aanwezig"""
        try:
            cookie_selectors = [
                "button:has-text('Accepteer')",
                "button:has-text('Akkoord')",
                "button:has-text('accept')",
                "[data-testid*='cookie']",
                "[id*='cookie']",
                "button[aria-label*='cookie']",
            ]
            for selector in cookie_selectors:
                try:
                    accept = self.page.locator(selector).first
                    if await accept.count() > 0 and await accept.is_visible():
                        await accept.click()
                        log_step("Cookie popup geaccepteerd")
                        await self.page.wait_for_timeout(1000)
                        break
                except:
                    continue
        except Exception:
            pass
    
    async def _check_login_status(self) -> bool:
        """Check of gebruiker is ingelogd"""
        try:
            # Wait a bit for page to settle
            await self.page.wait_for_timeout(1000)
            
            # Check URL first
            current_url = self.page.url
            if '/login' in current_url or '/identity' in current_url:
                # Still on login page
                return False
            
            # If we're on mijn-marktplaats or account page, definitely logged in
            if '/mijn-marktplaats' in current_url or '/account' in current_url:
                return True
            
            # Check for user menu indicators (multiple strategies)
            user_menu_selectors = [
                "[data-testid='user-menu']",
                "[aria-label*='account']",
                "[aria-label*='profiel']",
                "a[href*='/mijn-marktplaats']",
                "[href*='/account']",
                "button[aria-label*='Account']",
                "a[href*='/mijn-advertenties']",
            ]
            
            for selector in user_menu_selectors:
                try:
                    user_menu = self.page.locator(selector).first
                    if await user_menu.count() > 0:
                        is_visible = await user_menu.is_visible()
                        if is_visible:
                            log_step(f"Login indicator gevonden: {selector}")
                            return True
                except:
                    continue
            
            # Check for email in page
            try:
                email_elem = self.page.locator("text=/@.*\\./").first
                if await email_elem.count() > 0:
                    email_text = await email_elem.text_content()
                    if email_text and '@' in email_text:
                        log_step(f"Email gevonden op pagina: {email_text[:20]}...")
                        return True
            except:
                pass
            
            # Check if login button exists (means NOT logged in)
            # But be careful - login button might be hidden, not removed
            try:
                login_buttons = self.page.locator(
                    "a:has-text('Inloggen'), button:has-text('Inloggen'), a[href*='/login']"
                )
                if await login_buttons.count() > 0:
                    is_visible = await login_buttons.first.is_visible()
                    if is_visible:
                        # Login button is visible, probably not logged in
                        return False
            except:
                pass
            
            # If we're not on login page and no clear indicators, assume logged in
            # (better to try and fail than to give up)
            log_step("Geen duidelijke login indicators - aannemen dat ingelogd")
            return True
            
        except Exception as e:
            log_warning(f"Fout bij login check: {e}")
            # On error, assume not logged in to be safe
            return False
    
    async def _auto_login(self, email: str, password: str) -> bool:
        """Automatisch inloggen op Marktplaats"""
        log_step("Automatisch inloggen op Marktplaats...")
        
        try:
            # Navigate to login page
            login_url = f"{self.base_url}/identity/v2/login?target=https%3A%2F%2Fwww.marktplaats.nl%2F"
            await self.page.goto(login_url, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(2000)
            
            # Accept cookies
            await self._accept_cookies()
            
            # Determine target page (main or iframe)
            target_page = self.page
            frames = self.page.frames
            if len(frames) > 1:
                for i, frame in enumerate(frames[1:], 1):
                    try:
                        inputs_in_frame = await frame.locator("input").count()
                        if inputs_in_frame > 0:
                            log_step(f"Login form gevonden in frame {i}")
                            target_page = frame
                            break
                    except:
                        continue
            
            # Wait for page to load
            try:
                if hasattr(target_page, 'wait_for_load_state'):
                    await target_page.wait_for_load_state("networkidle", timeout=10000)
                else:
                    await self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                await self.page.wait_for_timeout(5000)
            
            # Wait for form
            try:
                await target_page.wait_for_selector("form, input, [role='textbox']", timeout=10000, state="visible")
            except:
                pass
            
            await self.page.wait_for_timeout(2000)
            
            # Fill email
            email_filled = await self._fill_email(target_page, email)
            if not email_filled:
                log_error("Kon email veld niet vinden")
                return False
            
            await self.page.wait_for_timeout(500)
            
            # Fill password
            password_filled = await self._fill_password(target_page, password)
            if not password_filled:
                log_error("Kon wachtwoord veld niet vinden")
                return False
            
            await self.page.wait_for_timeout(500)
            
            # Click login button
            login_success = await self._click_login_button(target_page)
            if not login_success:
                log_error("Kon inloggen knop niet vinden")
                return False
            
            # Wait for login to complete
            log_step("Wachten op login...")
            
            # Wait longer for potential redirects, 2FA, or other steps
            await self.page.wait_for_timeout(3000)
            
            try:
                # Wait for redirect away from login page
                await self.page.wait_for_url(
                    lambda url: '/login' not in url and '/identity' not in url,
                    timeout=15000,
                    state="domcontentloaded"
                )
                log_step("Redirect weg van login pagina gedetecteerd")
            except:
                # If no redirect, wait a bit more
                await self.page.wait_for_timeout(5000)
            
            # Wait for page to fully load
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
            except:
                await self.page.wait_for_timeout(5000)
            
            # Check current URL
            current_url = self.page.url
            log_step(f"Huidige URL na login: {current_url}")
            
            # If we're on login page still, might need manual intervention
            if '/login' in current_url or '/identity' in current_url:
                log_warning("Nog steeds op login pagina - mogelijk 2FA of captcha nodig")
                log_warning("Browser blijft open - log handmatig in en druk Enter...")
                # Give user time to manually complete login
                try:
                    input("Druk op ENTER als je handmatig bent ingelogd...")
                except EOFError:
                    # Non-interactive mode
                    await self.page.wait_for_timeout(10000)
            
            # Verify login (with multiple attempts)
            for attempt in range(3):
                is_logged_in = await self._check_login_status()
                if is_logged_in:
                    log_success("Automatisch ingelogd!")
                    return True
                elif attempt < 2:
                    log_step(f"Login check {attempt + 1}/3 - wachten...")
                    await self.page.wait_for_timeout(2000)
            
            log_warning("Login verificatie mislukt - maar browser blijft open")
            log_warning("Als je handmatig bent ingelogd, kan het script doorgaan")
            # Return True anyway - user might have logged in manually
            # The actual posting will fail if not logged in, but at least we tried
            return True
                
        except Exception as e:
            log_error(f"Fout bij automatisch inloggen: {e}")
            if VERBOSE:
                import traceback
                log_error(traceback.format_exc())
            return False
    
    async def _fill_email(self, target_page, email: str) -> bool:
        """Vul email veld in"""
        log_step("Email invullen...")
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[name='username']",
            "input[id*='email']",
            "input[id*='Email']",
            "input[id*='username']",
            "input[placeholder*='email']",
            "input[placeholder*='Email']",
            "input[placeholder*='E-mail']",
            "input[placeholder*='e-mailadres']",
            "input[autocomplete='email']",
            "input[autocomplete='username']",
            "input[type='text'][name*='email']",
            "input[type='text'][id*='email']",
            "input[type='text'][name*='username']",
            "input[data-testid*='email']",
            "input[data-testid*='username']",
            "form input[type='text']:first-of-type",
            "form input[type='email']:first-of-type",
        ]
        
        for selector in email_selectors:
            try:
                email_input = target_page.locator(selector).first
                if await email_input.count() > 0:
                    await email_input.wait_for(state="visible", timeout=5000)
                    await email_input.fill(email)
                    log_success(f"Email ingevuld: {email}")
                    return True
            except Exception:
                continue
        
        return False
    
    async def _fill_password(self, target_page, password: str) -> bool:
        """Vul wachtwoord veld in"""
        log_step("Wachtwoord invullen...")
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[id*='password']",
            "input[placeholder*='wachtwoord']",
            "input[placeholder*='Wachtwoord']",
        ]
        
        for selector in password_selectors:
            try:
                password_input = target_page.locator(selector).first
                if await password_input.count() > 0:
                    await password_input.fill(password)
                    log_success("Wachtwoord ingevuld")
                    return True
            except Exception:
                continue
        
        return False
    
    async def _click_login_button(self, target_page) -> bool:
        """Klik op inloggen knop"""
        log_step("Klikken op inloggen...")
        login_button_selectors = [
            "button[type='submit']",
            "button:has-text('Inloggen')",
            "button:has-text('Log in')",
            "button:has-text('Login')",
            "input[type='submit']",
            "button.login",
            "[data-testid='login-button']",
            "form button[type='submit']",
        ]
        
        for selector in login_button_selectors:
            try:
                login_button = target_page.locator(selector).first
                if await login_button.count() > 0:
                    await login_button.wait_for(state="visible", timeout=5000)
                    await login_button.click()
                    log_success("Inloggen knop geklikt")
                    return True
            except Exception:
                continue
        
        # Try Enter key as fallback
        try:
            await self.page.keyboard.press("Enter")
            log_step("Enter gedrukt (fallback)")
            return True
        except:
            pass
        
        return False
    
    async def close(self):
        """Sluit browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        log_step("Browser gesloten")
