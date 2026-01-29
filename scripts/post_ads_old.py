import asyncio
import csv
import os
import sys
import time
import json
from dataclasses import dataclass
from typing import List, Optional, Dict

from dotenv import load_dotenv
from playwright.async_api import async_playwright, BrowserContext, Page

try:
	import requests
except ImportError:
	requests = None


ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}

VERBOSE = os.getenv("MP_VERBOSE", "true").lower() in ("1", "true", "yes", "on")
FAST_MODE = os.getenv("MP_FAST", "true").lower() in ("1", "true", "yes", "on")  # Fast mode reduces wait times

def log_step(message: str) -> None:
	if VERBOSE:
		print(f"[STEP] {message}")

# Wait time constants - shorter in fast mode
WAIT_SHORT = 100 if FAST_MODE else 300
WAIT_MEDIUM = 300 if FAST_MODE else 600
WAIT_LONG = 500 if FAST_MODE else 1000
WAIT_NAVIGATION = 800 if FAST_MODE else 1500


@dataclass
class Product:
	title: str
	description: str
	price: str
	category_path: Optional[str]
	location: Optional[str]
	photos: List[str]
	article_number: Optional[str] = None
	condition: Optional[str] = None
	delivery_methods: List[str] = None
	material: Optional[str] = None  # Deprecated: use category_fields instead
	thickness: Optional[str] = None  # Deprecated: use category_fields instead
	total_surface: Optional[str] = None  # Deprecated: use category_fields instead
	delivery_option: Optional[str] = None
	category_fields: Optional[Dict] = None  # Category-specific fields from database


def read_products_from_api(api_url: str) -> List[Product]:
	"""Read product data from API endpoint. Can return single product or list of products."""
	if not requests:
		raise ImportError("requests library is required for API mode. Install with: pip install requests")
	
	# Extract API key from URL or environment
	api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
	
	# Prepare headers with API key
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
				condition=item.get('condition') or None,
				delivery_methods=delivery_methods,
				material=item.get('material') or None,  # Keep for backward compatibility
				thickness=item.get('thickness') or None,  # Keep for backward compatibility
				total_surface=item.get('total_surface') or None,  # Keep for backward compatibility
				delivery_option=item.get('delivery_option') or None,
				category_fields=category_fields if isinstance(category_fields, dict) else {},
			)
			products.append(product)
		
		print(f"[OK] {len(products)} product(en) opgehaald van API")
		return products
	except Exception as e:
		print(f"Error fetching products from API: {e}")
		raise


def read_products(csv_path: Optional[str] = None) -> List[Product]:
	"""Read products from CSV file."""
	if not csv_path:
		raise ValueError("CSV path is required")
	
	products: List[Product] = []
	with open(csv_path, newline='', encoding='utf-8') as f:
		reader = csv.DictReader(f)
		for row in reader:
			photos = [p.strip() for p in (row.get('photos') or '').split(';') if p.strip()]
			article_number = (row.get('article_number') or '').strip() or None
			delivery_methods = [m.strip() for m in (row.get('delivery_methods') or '').split(',') if m.strip()]
			products.append(Product(
				title=(row.get('title') or '').strip(),
				description=(row.get('description') or '').strip(),
				price=str(row.get('price', '')).strip(),
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
			))
	return products


def find_photos_for_article(media_root: str, article_number: str) -> List[str]:
	folder = os.path.join(media_root, str(article_number))
	if not os.path.isdir(folder):
		return []
	files: List[str] = []
	for name in sorted(os.listdir(folder)):
		path = os.path.join(folder, name)
		if not os.path.isfile(path):
			continue
		ext = os.path.splitext(name)[1].lower()
		if ext in ALLOWED_IMAGE_EXTS:
			files.append(os.path.abspath(path))
	return files


async def auto_login(page: Page, base_url: str, email: str, password: str) -> bool:
	"""
	Automatically log in to Marktplaats with credentials.
	Returns True if login successful, False otherwise.
	"""
	log_step("Automatisch inloggen op Marktplaats...")
	
	try:
		# Navigate to login page (use the correct identity v2 login URL)
		login_url = f"{base_url}/identity/v2/login?target=https%3A%2F%2Fwww.marktplaats.nl%2F"
		await page.goto(login_url, wait_until="domcontentloaded")
		await page.wait_for_timeout(2000)
		
		# Check current URL (might have redirected)
		current_url = page.url
		log_step(f"Debug: Huidige URL: {current_url}")
		
		# Accept cookies if needed (try multiple selectors)
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
					accept = page.locator(selector).first
					if await accept.count() > 0 and await accept.is_visible():
						await accept.click()
						log_step("✅ Cookie popup geaccepteerd")
						await page.wait_for_timeout(2000)
						break
				except:
					continue
		except Exception:
			pass
		
		# Determine which page/frame to use for login
		target_page = page  # Default to main page
		
		# Check for iframes (identity v2 might use iframe)
		frames = page.frames
		log_step(f"Debug: Gevonden {len(frames)} frame(s) op de pagina")
		if len(frames) > 1:
			# Try to find login form in iframes
			for i, frame in enumerate(frames[1:], 1):  # Skip main frame
				try:
					inputs_in_frame = await frame.locator("input").count()
					if inputs_in_frame > 0:
						log_step(f"Debug: Frame {i} heeft {inputs_in_frame} input velden - gebruik dit frame")
						target_page = frame
						break
				except:
					continue
		
		# Wait for the identity v2 login page to fully load
		# Wait for network to be idle (all resources loaded)
		try:
			if hasattr(target_page, 'wait_for_load_state'):
				await target_page.wait_for_load_state("networkidle", timeout=10000)
			else:
				await page.wait_for_load_state("networkidle", timeout=10000)
		except:
			await page.wait_for_timeout(5000)
		
		# Wait for any form or input to appear (identity v2 loads dynamically)
		try:
			await target_page.wait_for_selector("form, input, [role='textbox']", timeout=10000, state="visible")
		except:
			pass
		
		# Additional wait for dynamic content
		await page.wait_for_timeout(2000)
		
		# Find and fill email field
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
		
		email_filled = False
		for selector in email_selectors:
			try:
				email_input = target_page.locator(selector).first
				if await email_input.count() > 0:
					await email_input.wait_for(state="visible", timeout=5000)
					await email_input.fill(email)
					email_filled = True
					log_step(f"✅ Email ingevuld: {email}")
					break
			except Exception as e:
				if VERBOSE:
					log_step(f"Selector {selector} niet gevonden: {e}")
				continue
		
		if not email_filled:
			log_step("⚠️  Kon email veld niet vinden")
			# Debug: log all input fields found on the page
			try:
				all_inputs = await target_page.locator("input").all()
				log_step(f"Debug: Gevonden {len(all_inputs)} input velden op de pagina")
				for i, inp in enumerate(all_inputs[:5]):  # Log first 5 inputs
					try:
						input_type = await inp.get_attribute("type") or "text"
						input_name = await inp.get_attribute("name") or ""
						input_id = await inp.get_attribute("id") or ""
						log_step(f"  Input {i+1}: type={input_type}, name={input_name}, id={input_id}")
					except:
						pass
			except Exception as e:
				if VERBOSE:
					log_step(f"Debug error: {e}")
			
			# Try to take a screenshot for debugging
			try:
				await page.screenshot(path="login_page_debug.png")
				log_step("Screenshot opgeslagen als login_page_debug.png")
			except:
				pass
			return False
		
		await page.wait_for_timeout(500)
		
		# Find and fill password field
		log_step("Wachtwoord invullen...")
		password_selectors = [
			"input[type='password']",
			"input[name='password']",
			"input[id*='password']",
			"input[placeholder*='wachtwoord']",
			"input[placeholder*='Wachtwoord']",
		]
		
		password_filled = False
		for selector in password_selectors:
			try:
				password_input = target_page.locator(selector).first
				if await password_input.count() > 0:
					await password_input.fill(password)
					password_filled = True
					log_step("✅ Wachtwoord ingevuld")
					break
			except Exception:
				continue
		
		if not password_filled:
			log_step("⚠️  Kon wachtwoord veld niet vinden")
			return False
		
		await page.wait_for_timeout(500)
		
		# Find and click login button (use target_page if we found a frame)
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
		
		login_clicked = False
		for selector in login_button_selectors:
			try:
				login_button = target_page.locator(selector).first
				if await login_button.count() > 0:
					await login_button.wait_for(state="visible", timeout=5000)
					await login_button.click()
					login_clicked = True
					log_step("✅ Inloggen knop geklikt")
					break
			except Exception:
				continue
		
		if not login_clicked:
			# Try pressing Enter as fallback
			try:
				await page.keyboard.press("Enter")
				login_clicked = True
				log_step("✅ Enter gedrukt (fallback)")
			except Exception:
				pass
		
		if not login_clicked:
			log_step("⚠️  Kon inloggen knop niet vinden")
			return False
		
		# Wait for navigation/login to complete
		log_step("Wachten op login...")
		
		# Wait for URL to change (redirect after login) or page to load
		try:
			# Wait for navigation - login usually redirects
			await page.wait_for_url("**/mijn-marktplaats**", timeout=10000, state="domcontentloaded")
			log_step("✅ Redirect naar mijn-marktplaats gedetecteerd")
		except:
			try:
				# Alternative: wait for URL to not be login page anymore
				await page.wait_for_function(
					"window.location.href.indexOf('/login') === -1 && window.location.href.indexOf('/identity') === -1",
					timeout=10000
				)
				log_step("✅ Redirect weg van login pagina gedetecteerd")
			except:
				# Fallback: just wait
				await page.wait_for_timeout(5000)
		
		# Wait a bit more for page to fully load
		try:
			await page.wait_for_load_state("networkidle", timeout=5000)
		except:
			await page.wait_for_timeout(3000)
		
		# Check if login was successful
		is_logged_in = await check_login_status_internal(page)
		
		if is_logged_in:
			log_step("✅ Automatisch ingelogd!")
			return True
		else:
			log_step("⚠️  Login lijkt niet gelukt - controleer handmatig")
			return False
		
	except Exception as e:
		log_step(f"❌ Fout bij automatisch inloggen: {e}")
		import traceback
		log_step(traceback.format_exc())
		return False


async def check_login_status_internal(page: Page) -> bool:
	"""Internal helper to check login status."""
	try:
		# Strategy 0: Check URL - if not on login page, might be logged in
		current_url = page.url
		if '/login' not in current_url and '/identity' not in current_url:
			# Not on login page, could be logged in
			# Continue to check other indicators
			pass
		elif '/login' in current_url or '/identity' in current_url:
			# Still on login page, probably not logged in
			return False
	except Exception:
		pass
	
	try:
		# Strategy 1: Look for user menu or account indicators
		user_menu = page.locator("[data-testid='user-menu'], [aria-label*='account'], [aria-label*='profiel'], a[href*='/mijn-marktplaats'], [href*='/account'], button[aria-label*='Account']").first
		if await user_menu.count() > 0:
			is_visible = await user_menu.is_visible()
			if is_visible:
				return True
	except Exception:
		pass
	
	# Strategy 2: Look for email/username in page
	try:
		email_elem = page.locator("text=/@.*\\./").first
		if await email_elem.count() > 0:
			return True
	except Exception:
		pass
	
	# Strategy 3: Check if we're on mijn-marktplaats or account page
	try:
		current_url = page.url
		if '/mijn-marktplaats' in current_url or '/account' in current_url:
			return True
	except Exception:
		pass
	
	# Strategy 4: Check if login button exists (means NOT logged in)
	try:
		login_buttons = page.locator("a:has-text('Inloggen'), button:has-text('Inloggen'), a[href*='/login']")
		if await login_buttons.count() > 0 and await login_buttons.first.is_visible():
			return False
	except Exception:
		pass
	
	return False


async def ensure_logged_in(page: Page, base_url: str) -> bool:
	"""
	Ensure user is logged in to Marktplaats.
	Returns True if logged in, False otherwise.
	If credentials are available in environment, attempts automatic login.
	"""
	for attempt in range(2):
		try:
			await page.goto(f"{base_url}/", wait_until="domcontentloaded")
			break
		except Exception:
			if attempt == 1:
				raise
			await page.wait_for_timeout(1500)
	
	# Accept cookies if banner appears
	try:
		accept = page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower() or "akkoord" in (n or '').lower())
		if await accept.count() > 0:
			await accept.first.click()
			await page.wait_for_timeout(1000)
	except Exception:
		pass
	
	# Wait a bit for page to fully load
	await page.wait_for_timeout(2000)
	
	# Check if logged in
	is_logged_in = await check_login_status_internal(page)
	
	if is_logged_in:
		try:
			user_menu = page.locator("[data-testid='user-menu'], [aria-label*='account'], [aria-label*='profiel'], a[href*='/mijn-marktplaats']").first
			if await user_menu.count() > 0 and await user_menu.is_visible():
				user_text = await user_menu.text_content()
				log_step(f"✅ Gebruiker ingelogd: {user_text}")
			else:
				email_elem = page.locator("text=/@.*\\./").first
				if await email_elem.count() > 0:
					email = await email_elem.text_content()
					log_step(f"✅ Gebruiker ingelogd: {email}")
		except Exception:
			log_step("✅ Gebruiker ingelogd")
		return True
	
	# Not logged in - try automatic login if credentials available
	marktplaats_email = os.getenv('MARKTPLAATS_EMAIL')
	marktplaats_password = os.getenv('MARKTPLAATS_PASSWORD')
	
	if marktplaats_email and marktplaats_password:
		log_step("Niet ingelogd - proberen automatisch in te loggen...")
		login_success = await auto_login(page, base_url, marktplaats_email, marktplaats_password)
		if login_success:
			return True
		else:
			log_step("⚠️  Automatisch inloggen mislukt - handmatige login nodig")
			return False
	else:
		log_step("⚠️  Niet ingelogd en geen login credentials gevonden in .env")
		return False


async def click_place_ad(page: Page, base_url: str) -> None:
	await page.goto(f"{base_url}/plaats", wait_until="domcontentloaded")
	if page.url.rstrip('/') not in (f"{base_url}/plaats", f"{base_url}/plaats/"):
		link = page.get_by_role("link", name="Plaats advertentie")
		if await link.count() > 0:
			await link.first.click()
			await page.wait_for_load_state('domcontentloaded')


async def auto_suggest_category(page: Page, title: str) -> None:
	try:
		title_input = page.get_by_label("Titel", exact=False)
		if await title_input.count() == 0:
			title_input = page.get_by_placeholder("Titel", exact=False)
		await title_input.first.fill(title)
	except Exception:
		pass
	try:
		find_button = page.get_by_role("button", name="Vind categorie")
		if await find_button.count() == 0:
			find_button = page.locator("[data-testid='findCategory']")
		if await find_button.count() > 0:
			await find_button.first.click()
			await page.wait_for_timeout(WAIT_SHORT)
	except Exception:
		pass
	try:
		first_radio = page.locator("input[type='radio']").first
		if await first_radio.count() > 0:
			await first_radio.check()
			await page.wait_for_timeout(WAIT_SHORT)
	except Exception:
		pass
	try:
		next_button = page.get_by_role("button", name="Verder")
		if await next_button.count() > 0:
			await next_button.first.click()
			await page.wait_for_load_state("domcontentloaded")
	except Exception:
		pass


async def choose_category(page: Page, category_path: Optional[str]) -> None:
	if not category_path:
		return
	log_step(f"Categorie kiezen: {category_path}")
	parts = [p.strip() for p in category_path.split('>') if p.strip()]
	
	if not parts:
		log_step("Waarschuwing: Lege categorie path")
		return
	
	# Wait for category selection page to load
	await page.wait_for_timeout(WAIT_MEDIUM)
	
	# First, check if we're on the suggestions page (with radio buttons)
	# If so, try to find the exact category in suggestions first
	found_in_suggestions = False  # Initialize before try block to avoid UnboundLocalError
	try:
		radio_buttons = page.locator("input[type='radio']")
		radio_count = await radio_buttons.count()
		if radio_count > 0:
			log_step(f"  Gevonden {radio_count} categorie suggesties, zoeken naar exacte match...")
			found_in_suggestions = False
			
			# Try to find exact match in radio button labels
			# Marktplaats uses a specific structure: radio button with label containing category name
			for i in range(radio_count):
				try:
					radio = radio_buttons.nth(i)
					
					# Strategy 1: Find label using for/id relationship
					radio_id = await radio.get_attribute("id")
					label_text = None
					
					if radio_id:
						label = page.locator(f"label[for='{radio_id}']")
						if await label.count() > 0:
							label_text = await label.first.text_content()
					
					# Strategy 2: Find label as sibling or parent
					if not label_text:
						# Try to find label element near the radio
						parent = radio.locator("xpath=..")
						label = parent.locator("label")
						if await label.count() > 0:
							label_text = await label.first.text_content()
						else:
							# Try next sibling
							label = radio.locator("xpath=following-sibling::label[1]")
							if await label.count() > 0:
								label_text = await label.first.text_content()
							else:
								# Try previous sibling
								label = radio.locator("xpath=preceding-sibling::label[1]")
								if await label.count() > 0:
									label_text = await label.first.text_content()
					
					# Strategy 3: Get text from parent container
					if not label_text:
						parent = radio.locator("xpath=..")
						parent_text = await parent.text_content()
						if parent_text:
							# Extract just the category name (might have extra text)
							label_text = parent_text.strip()
					
					if label_text:
						label_text = label_text.strip()
						# Clean up label text (remove extra info like "(Laatst gekozen categorie)")
						label_text_clean = label_text.split("(")[0].strip()
						
						# Check if this matches our first category part (more flexible matching)
						first_part_clean = parts[0].strip()
						
						# Try exact match first
						if first_part_clean.lower() == label_text_clean.lower():
							log_step(f"  [OK] Exacte match gevonden in suggesties: '{label_text_clean}', selecteren...")
							await radio.check()
							await page.wait_for_timeout(500)
							found_in_suggestions = True
							if len(parts) == 1:
								return
							# Continue with next parts
							break
						# Try partial match
						elif first_part_clean.lower() in label_text_clean.lower() or label_text_clean.lower() in first_part_clean.lower():
							log_step(f"  [OK] Gedeeltelijke match gevonden in suggesties: '{label_text_clean}', selecteren...")
							await radio.check()
							await page.wait_for_timeout(500)
							found_in_suggestions = True
							
							# If this was the only part, we're done
							if len(parts) == 1:
								return
							
							# If there are more parts, click "Verder" and continue
							try:
								next_btn = page.get_by_role("button", name="Verder")
								if await next_btn.count() == 0:
									next_btn = page.locator("button:has-text('Verder')")
								if await next_btn.count() > 0:
									log_step("  Klikken op 'Verder' om door te gaan...")
									await next_btn.first.click()
									await page.wait_for_load_state("domcontentloaded")
									await page.wait_for_timeout(WAIT_MEDIUM)
								else:
									log_step("  [WARNING] Kon 'Verder' knop niet vinden")
							except Exception as e:
								log_step(f"  [WARNING] Fout bij klikken op 'Verder': {e}")
							
							# Mark that we need to skip first part in loop
							# We'll handle this by starting the loop from index 1
							break
				except Exception as e:
					log_step(f"  [DEBUG] Fout bij checken radio {i}: {e}")
					continue
			
			if found_in_suggestions:
				# We found the first part in suggestions
				# If there are more parts, we need to continue navigating
				if len(parts) > 1:
					log_step(f"  Doorgaan met resterende categorie delen: {' > '.join(parts[1:])}")
					# Continue with remaining parts in the loop below
				else:
					# Single part category, we're done
					return
			
			if not found_in_suggestions:
				# Category not in suggestions, click "Of selecteer zelf een categorie"
				log_step("  Categorie niet in suggesties, openen categorie selectie...")
				try:
					select_self = page.get_by_text("Of selecteer zelf een categorie", exact=False)
					if await select_self.count() == 0:
						select_self = page.get_by_text("selecteer zelf", exact=False)
					if await select_self.count() > 0:
						await select_self.first.click()
						await page.wait_for_timeout(WAIT_MEDIUM)
					else:
						log_step("  [WARNING] Kon 'selecteer zelf categorie' niet vinden")
				except Exception as e:
					log_step(f"  [WARNING] Fout bij openen categorie selectie: {e}")
	except Exception as e:
		log_step(f"  [INFO] Geen suggesties gevonden, direct zoeken in categorieboom: {e}")
	
	# Now navigate through the category tree
	# If we found the first part in suggestions, start from index 1 (skip first)
	start_idx = 1 if found_in_suggestions else 0
	for idx, part in enumerate(parts[start_idx:], start=start_idx + 1):
		log_step(f"  Stap {idx}/{len(parts)}: Zoeken naar '{part}'")
		locator = None
		found = False
		
		# Wait a bit for page to load and dropdown to open
		await page.wait_for_timeout(WAIT_MEDIUM)
		
		# Check if there's a dropdown/select element open
		# Marktplaats might use a dropdown menu structure
		try:
			# Strategy 0: Check for dropdown/select elements first
			# Look for open dropdowns (aria-expanded=true) or visible dropdown menus
			select_elements = page.locator("select, [role='combobox'], [role='listbox'], [aria-expanded='true'], .dropdown, [class*='dropdown'], [class*='select'], [class*='menu'], [class*='list']")
			select_count = await select_elements.count()
			if select_count > 0:
				log_step(f"  Gevonden {select_count} dropdown/select element(en), zoeken daarin...")
				for i in range(min(select_count, 10)):  # Check first 10 dropdowns
					try:
						select_elem = select_elements.nth(i)
						# Check if element is visible
						is_visible = await select_elem.is_visible()
						if not is_visible:
							continue
						
						# Try to find option with matching text - check multiple selectors
						options = select_elem.locator("option, [role='option'], li, a, div, span")
						opt_count = await options.count()
						
						if opt_count > 0:
							log_step(f"    Dropdown {i+1}: {opt_count} opties gevonden")
							for j in range(min(opt_count, 100)):
								try:
									opt = options.nth(j)
									# Check visibility
									opt_visible = await opt.is_visible()
									if not opt_visible:
										continue
									
									opt_text = await opt.text_content()
									if opt_text:
										opt_text_clean = opt_text.strip().split("(")[0].strip().split("\n")[0].strip()
										# Check for exact or partial match
										if part.lower() == opt_text_clean.lower() or part.lower() in opt_text_clean.lower() or opt_text_clean.lower() in part.lower():
											log_step(f"  [OK] Gevonden in dropdown: '{opt_text_clean}'")
											await opt.scroll_into_view_if_needed()
											await page.wait_for_timeout(WAIT_SHORT)
											await opt.click()
											await page.wait_for_timeout(WAIT_MEDIUM)
											found = True
											break
								except:
									continue
						if found:
							break
					except Exception as e:
						log_step(f"  [DEBUG] Dropdown {i+1} check fout: {e}")
						continue
		except Exception as e:
			log_step(f"  [DEBUG] Dropdown check fout: {e}")
		
		# If not found in dropdown, try other strategies
		if not found:
			# Try multiple strategies to find the category element
			try:
				locator = None
				
				# Strategy 1: Look for links with exact or partial text
				try:
					locator = page.get_by_role("link", name=part, exact=False)
					if await locator.count() > 0:
						found = True
				except:
					pass
				
				# Strategy 2: Look for buttons (if strategy 1 didn't work)
				if not locator or await locator.count() == 0:
					try:
						locator = page.get_by_role("button", name=part, exact=False)
						if await locator.count() > 0:
							found = True
					except:
						pass
				
				# Strategy 3: Look for clickable elements with text (including divs, spans that might be clickable)
				if not locator or await locator.count() == 0:
					try:
						# Try more element types that might be clickable
						locator = page.locator(f"a:has-text('{part}'), button:has-text('{part}'), div:has-text('{part}'), span:has-text('{part}'), li:has-text('{part}')").first
						if await locator.count() > 0:
							# Check if it's actually visible and clickable
							is_visible = await locator.first.is_visible()
							if is_visible:
								found = True
					except:
						pass
				
				# Strategy 4: Look for any element containing the text (case insensitive)
				if not locator or await locator.count() == 0:
					try:
						escaped_part = part.replace("'", "\\'").replace('"', '\\"')
						locator = page.locator(f"text=/^{escaped_part}$/i, text=/{escaped_part}/i").first
						if await locator.count() > 0:
							found = True
					except:
						pass
				
				# Strategy 5: Look in all clickable elements (links, buttons, divs, spans)
				if not locator or await locator.count() == 0:
					try:
						# Try more element types
						all_clickable = page.locator("a[href], button, div[onclick], span[onclick], li[onclick], [role='button'], [role='link'], [tabindex='0']")
						count = await all_clickable.count()
						log_step(f"  Zoeken in {count} klikbare elementen...")
						for i in range(min(count, 150)):  # Increase limit
							try:
								elem = all_clickable.nth(i)
								# Check if visible
								is_visible = await elem.is_visible()
								if not is_visible:
									continue
								
								text = await elem.text_content()
								if text:
									text_clean = text.strip().split("(")[0].strip().split("\n")[0].strip()  # Remove extra info and newlines
									# Check for exact or partial match
									if part.lower() == text_clean.lower() or part.lower() in text_clean.lower() or text_clean.lower() in part.lower():
										locator = elem
										found = True
										log_step(f"  [OK] Gevonden via strategy 5: '{text_clean}'")
										break
							except:
								continue
					except Exception as e:
						log_step(f"  [DEBUG] Strategy 5 fout: {e}")
				
				if locator and await locator.count() > 0:
					log_step(f"  [OK] '{part}' gevonden, klikken...")
					await locator.first.scroll_into_view_if_needed()
					await page.wait_for_timeout(WAIT_SHORT)
					
					# Click the element
					try:
						await locator.first.click()
					except:
						# If normal click fails, try force click
						await locator.first.click(force=True)
					
					# Wait for page to update after clicking (use domcontentloaded instead of networkidle for speed)
					await page.wait_for_timeout(WAIT_MEDIUM)
					
					# Wait for navigation or content change (faster than networkidle)
					try:
						await page.wait_for_load_state("domcontentloaded", timeout=2000)
					except:
						pass
					
					found = True
				else:
					log_step(f"  [ERROR] Kon '{part}' niet vinden op pagina")
					# Only take screenshot in verbose mode or if debug is enabled
					if VERBOSE and os.getenv("MP_DEBUG_SCREENSHOTS", "false").lower() == "true":
						try:
							await page.screenshot(path=f"debug_category_{idx}_{part[:10]}.png")
							log_step(f"  [DEBUG] Screenshot opgeslagen: debug_category_{idx}_{part[:10]}.png")
						except:
							pass
			except Exception as e:
				log_step(f"  [ERROR] Fout bij klikken op '{part}': {e}")
		
		if not found:
			log_step(f"  [WARNING] Kon '{part}' niet vinden")
			if idx < len(parts):
				log_step(f"  [WARNING] Probeer volgende stap...")
				# Try to continue anyway, but log warning
			else:
				log_step(f"  [ERROR] Kon laatste categorie deel niet vinden - categorie selectie mislukt")
				return


async def fill_basic_fields(page: Page, product: Product) -> None:
	log_step(f"Titel invullen: {product.title}")
	# Title
	try:
		title_input = page.get_by_label("Titel", exact=False)
		if await title_input.count() == 0:
			title_input = page.get_by_placeholder("Titel", exact=False)
		value = await title_input.first.input_value()
		if not value:
			await title_input.first.fill(product.title)
	except Exception:
		pass
	log_step("Omschrijving invullen")
	# Description: rich text editor
	try:
		rte = page.locator("[data-testid='text-editor-input_nl-NL']").first
		if await rte.count() > 0:
			await rte.fill(product.description)
		else:
			desc_input = page.get_by_label("Beschrijving", exact=False)
			if await desc_input.count() == 0:
				desc_input = page.get_by_placeholder("Beschrijving", exact=False)
			await desc_input.first.fill(product.description)
	except Exception:
		pass
	log_step(f"Prijs invullen: {product.price}")
	# Price (string input like 0,00). Convert dot to comma for Dutch format.
	try:
		# Convert price format: replace dot with comma (10.50 -> 10,50)
		price_str = str(product.price or "").strip()
		# Replace dot with comma if it's a decimal separator
		if '.' in price_str and ',' not in price_str:
			price_str = price_str.replace('.', ',')
		# Remove any spaces
		price_str = price_str.replace(' ', '')
		
		price_input = page.locator("#price\\.value, input#price\\.value")
		if await price_input.count() == 0:
			price_input = page.get_by_label("Prijs", exact=False)
		if await price_input.count() == 0:
			price_input = page.locator("input[name='price.value']")
		if await price_input.count() == 0:
			price_input = page.locator("input[type='text'][name*='price'], input[type='number'][name*='price']")
		if await price_input.count() > 0:
			await price_input.first.fill(price_str)
			log_step(f"✅ Prijs ingevuld: {price_str}")
		else:
			log_step("⚠️  Kon prijs veld niet vinden")
	except Exception as e:
		log_step(f"⚠️  Fout bij invullen prijs: {e}")
		pass
	if product.condition:
		log_step(f"Staat kiezen: {product.condition}")
	# Condition (select)
	if product.condition:
		try:
			select = page.locator("select[name='singleSelectAttribute[condition]']")
			if await select.count() > 0:
				await select.select_option(label=product.condition)
		except Exception:
			pass
	if product.material:
		log_step(f"Materiaal kiezen: {product.material}")
	# Material (select)
	if product.material:
		try:
			select = page.locator("select[name='singleSelectAttribute[material]']")
			if await select.count() > 0:
				await select.select_option(label=product.material)
		except Exception:
			pass
	if product.thickness:
		log_step(f"Dikte kiezen: {product.thickness}")
	# Thickness (select)
	if product.thickness:
		try:
			select = page.locator("select[name='singleSelectAttribute[thickness]']")
			if await select.count() > 0:
				await select.select_option(label=product.thickness)
		except Exception:
			pass
	if product.total_surface:
		log_step(f"Oppervlakte kiezen: {product.total_surface}")
	# Total surface (select)
	if product.total_surface:
		try:
			select = page.locator("select[name='singleSelectAttribute[totalSurface]']")
			if await select.count() > 0:
				await select.select_option(label=product.total_surface)
		except Exception:
			pass
	if product.delivery_option:
		log_step(f"Levering kiezen: {product.delivery_option}")
	# Delivery radio combined option
	if product.delivery_option:
		try:
			radio = page.locator("input[name='deliveryMethod'][type='Radio']")
			if await radio.count() == 0:
				radio = page.get_by_label(product.delivery_option, exact=False)
			if await radio.count() > 0:
				await radio.first.check()
		except Exception:
			pass
	if product.location:
		log_step(f"Locatie invullen: {product.location}")
	# Location (optional)
	if product.location:
		try:
			loc_input = page.get_by_label("Plaatsnaam", exact=False)
			if await loc_input.count() == 0:
				loc_input = page.get_by_placeholder("Plaatsnaam", exact=False)
			await loc_input.first.fill(product.location)
		except Exception:
			pass
	
	# Fill category-specific fields
	if product.category_fields:
		await fill_category_fields(page, product.category_fields)


async def fill_category_fields(page: Page, category_fields: Dict) -> None:
	"""Fill category-specific fields on Marktplaats form."""
	if not category_fields or not isinstance(category_fields, dict):
		return
	
	log_step("Categorie-specifieke velden invullen...")
	
	for field_name, field_value in category_fields.items():
		if not field_value or field_value == '':
			continue
		
		try:
			# Handle different field types based on field name patterns
			# Marktplaats uses patterns like:
			# - SINGLESELECTATTRIBUTE[MATERIAL]
			# - SINGLESELECTATTRIBUTE[THICKNESS]
			# - MULTISELECTATTRIBUTE[TYPE]
			# - PACKAGESIZE
			# - DELIVERYMETHOD
			# - etc.
			
			field_name_upper = field_name.upper()
			
			# Try select fields first (most common)
			# Pattern: select[name='singleSelectAttribute[material]'] or select[name='SINGLESELECTATTRIBUTE[MATERIAL]']
			# Extract the attribute name from field_name (e.g., "SINGLESELECTATTRIBUTE[MATERIAL]" -> "MATERIAL")
			attr_name = field_name_upper
			if '[' in field_name_upper and ']' in field_name_upper:
				# Extract content between brackets
				start = field_name_upper.find('[') + 1
				end = field_name_upper.find(']')
				if start > 0 and end > start:
					attr_name = field_name_upper[start:end]
			
			select_locators = [
				f"select[name='{field_name}']",
				f"select[name='{field_name.lower()}']",
				f"select[name='{field_name_upper}']",
				f"select[name='singleSelectAttribute[{attr_name.lower()}]']",
				f"select[name='SINGLESELECTATTRIBUTE[{attr_name}]']",
				f"select[name='singleSelectAttribute[{attr_name}]']",
				f"select[name='SINGLESELECTATTRIBUTE[{attr_name.lower()}]']",
			]
			
			filled = False
			for selector in select_locators:
				try:
					select = page.locator(selector)
					if await select.count() > 0:
						# Try to select by label/value
						value_str = str(field_value).strip()
						try:
							await select.select_option(label=value_str)
							log_step(f"  [OK] {field_name}: {value_str}")
							filled = True
							break
						except:
							try:
								await select.select_option(value=value_str)
								log_step(f"  [OK] {field_name}: {value_str}")
								filled = True
								break
							except:
								pass
				except:
					continue
			
			# If not filled as select, try radio buttons
			if not filled:
				radio_locators = [
					f"input[type='radio'][name='{field_name}']",
					f"input[type='radio'][name='{field_name.lower()}']",
					f"input[type='radio'][name='{field_name_upper}']",
				]
				
				for selector in radio_locators:
					try:
						radios = page.locator(selector)
						count = await radios.count()
						if count > 0:
							value_str = str(field_value).strip()
							# Try to find radio by value or label
							for i in range(count):
								radio = radios.nth(i)
								radio_value = await radio.get_attribute("value")
								if radio_value and value_str.lower() in radio_value.lower():
									await radio.check()
									log_step(f"  [OK] {field_name}: {value_str} (radio)")
									filled = True
									break
								# Try by label
								try:
									label = radio.locator("xpath=following-sibling::label | xpath=preceding-sibling::label | xpath=../label")
									if await label.count() > 0:
										label_text = await label.first.text_content()
										if label_text and value_str.lower() in label_text.lower():
											await radio.check()
											log_step(f"  [OK] {field_name}: {value_str} (radio)")
											filled = True
											break
								except:
									pass
							if filled:
								break
					except:
						continue
			
			# If not filled, try text input
			if not filled:
				text_locators = [
					f"input[name='{field_name}']",
					f"input[name='{field_name.lower()}']",
					f"textarea[name='{field_name}']",
				]
				
				for selector in text_locators:
					try:
						input_elem = page.locator(selector)
						if await input_elem.count() > 0:
							value_str = str(field_value).strip()
							await input_elem.first.fill(value_str)
							log_step(f"  [OK] {field_name}: {value_str} (text)")
							filled = True
							break
					except:
						continue
			
			# If still not filled, try by label
			if not filled:
				try:
					value_str = str(field_value).strip()
					# Try to find input by label text
					label = page.get_by_label(field_name, exact=False)
					if await label.count() == 0:
						# Try to find by partial label match
						all_labels = page.locator("label")
						count = await all_labels.count()
						for i in range(min(count, 50)):
							try:
								label_elem = all_labels.nth(i)
								label_text = await label_elem.text_content()
								if label_text and field_name.upper() in label_text.upper():
									# Found matching label, get associated input
									label_for = await label_elem.get_attribute("for")
									if label_for:
										input_elem = page.locator(f"#{label_for}")
										if await input_elem.count() > 0:
											await input_elem.first.fill(value_str)
											log_step(f"  [OK] {field_name}: {value_str} (by label)")
											filled = True
											break
							except:
								continue
					else:
						# Found label, get associated input
						label_for = await label.first.get_attribute("for")
						if label_for:
							input_elem = page.locator(f"#{label_for}")
							if await input_elem.count() > 0:
								await input_elem.first.fill(value_str)
								log_step(f"  [OK] {field_name}: {value_str} (by label)")
								filled = True
				except:
					pass
			
			if not filled:
				log_step(f"  [WARNING] Kon veld '{field_name}' niet invullen (waarde: {field_value})")
		
		except Exception as e:
			log_step(f"  [ERROR] Fout bij invullen veld '{field_name}': {e}")
			continue


async def upload_photos(page: Page, product: Product, media_root: str) -> None:
	# Get photos from product, convert to absolute paths
	photos: List[str] = []
	
	log_step(f"Foto's ophalen voor product (media_root: {media_root})")
	
	if product.photos:
		log_step(f"  Product heeft {len(product.photos)} foto path(s) in product.photos")
		for i, p in enumerate(product.photos, 1):
			if not p:
				log_step(f"  Foto {i}: (leeg)")
				continue
			
			# Try as absolute path first
			if os.path.isabs(p):
				if os.path.exists(p):
					photos.append(p)
					log_step(f"  Foto {i}: {p} (gevonden als absolute path)")
				else:
					log_step(f"  Foto {i}: {p} (niet gevonden als absolute path)")
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
					else:
						log_step(f"  Foto {i}: {p} (niet gevonden)")
	
	# If no photos from product.photos, try to find by article number
	if not photos and product.article_number:
		log_step(f"  Geen foto's in product.photos, zoeken op artikelnummer: {product.article_number}")
		found_photos = find_photos_for_article(media_root, product.article_number)
		if found_photos:
			photos = [os.path.abspath(p) for p in found_photos]
			log_step(f"  {len(photos)} foto(s) gevonden op artikelnummer")
	
	# Filter to only existing files and normalize paths
	existing_photos = []
	for p in photos:
		normalized = os.path.normpath(os.path.abspath(p))
		if os.path.exists(normalized):
			existing_photos.append(normalized)
		else:
			log_step(f"  [WARNING] Foto bestaat niet: {normalized}")
	
	if not existing_photos:
		log_step("Geen foto's gevonden voor product; overslaan upload")
		if product.photos:
			log_step(f"  Foto paths in product: {product.photos}")
		if product.article_number:
			log_step(f"  Artikelnummer: {product.article_number}")
		log_step(f"  Media root: {media_root}")
		return
	
	log_step(f"Foto's uploaden: {len(existing_photos)} bestand(en)")
	for i, photo_path in enumerate(existing_photos, 1):
		log_step(f"  Foto {i}: {os.path.basename(photo_path)}")
	
	try:
		# Wait a bit for page to be ready
		await page.wait_for_timeout(WAIT_MEDIUM)
		
		# Multiple strategies for input selection
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
				if count > 0:
					# For hidden inputs, we can still use them even if not visible
					# Check if it exists and is enabled
					is_enabled = await locator.first.is_enabled()
					if is_enabled:
						file_input = locator.first
						found_selector = sel
						log_step(f"  File input gevonden met selector: {sel}")
						break
			except Exception as e:
				log_step(f"  Selector '{sel}' fout: {e}")
				continue
		
		if not file_input:
			log_step("  [ERROR] Kon file input niet vinden op pagina")
			# Only take screenshot if debug is enabled
			if os.getenv("MP_DEBUG_SCREENSHOTS", "false").lower() == "true":
				try:
					await page.screenshot(path="debug_no_file_input.png")
					log_step("  Screenshot opgeslagen: debug_no_file_input.png")
				except:
					pass
			return
		
		# Upload files
		log_step(f"  Uploaden van {len(existing_photos)} foto's...")
		await file_input.set_input_files(existing_photos)
		
		# Wait for upload to complete (shorter wait in fast mode)
		upload_wait = 1000 if FAST_MODE else 2000
		await page.wait_for_timeout(upload_wait)
		
		# Check if upload was successful by looking for preview images or success indicators
		try:
			# Wait for image previews to appear (common pattern on Marktplaats)
			preview_images = page.locator("img[src*='blob'], img[src*='data:'], .image-preview, [class*='preview'], [class*='upload']")
			await preview_images.first.wait_for(state="visible", timeout=3000 if FAST_MODE else 5000)
			log_step(f"  [OK] Foto's succesvol geüpload (previews gevonden)")
		except:
			# If no preview found, assume it worked (some pages don't show previews immediately)
			log_step(f"  [OK] Foto's geüpload (wachten op bevestiging...)")
			await page.wait_for_timeout(WAIT_SHORT)
		
	except Exception as e:
		log_step(f"  [ERROR] Fout bij uploaden foto's: {e}")
		import traceback
		log_step(f"  Traceback: {traceback.format_exc()}")
		# Always take screenshot on errors (helpful for debugging)
		try:
			await page.screenshot(path="debug_photo_upload_error.png")
			log_step("  Screenshot opgeslagen: debug_photo_upload_error.png")
		except:
			pass


async def select_free_bundle(page: Page) -> None:
	try:
		free = page.locator("#feature-FREE, [id='feature-FREE']")
		if await free.count() > 0:
			# Click the 'Kiezen' within the free bundle block if needed
			choose = free.locator("text=Kiezen").first
			if await choose.count() > 0:
				await choose.click()
			else:
				await free.click()
		await page.wait_for_timeout(WAIT_SHORT)
	except Exception:
		pass


async def get_posted_ad_url(page: Page, product_title: Optional[str] = None) -> Optional[str]:
	"""Extract the URL of the posted ad from the current page or from 'Mijn advertenties'."""
	try:
		# Wait a bit for redirect or page load (shorter in fast mode)
		await page.wait_for_timeout(2000 if FAST_MODE else 4000)
		
		# Check current URL - if it's an ad page, return it
		current_url = page.url
		log_step(f"Current URL na plaatsen: {current_url}")
		
		# Filter out help/terms pages
		if '/help/' in current_url or '/voorwaarden' in current_url or '/privacy' in current_url:
			log_step(f"Waarschuwing: Op help/voorwaarden pagina, niet op ad pagina")
		elif '/v/' in current_url or '/a' in current_url:
			log_step(f"Ad URL gevonden in current URL: {current_url}")
			return current_url
		
		# Try to find "Bekijk je advertentie" link first (most reliable)
		view_ad_texts = [
			"Bekijk je advertentie",
			"Bekijk advertentie",
			"Naar je advertentie",
			"Je advertentie bekijken"
		]
		for text in view_ad_texts:
			try:
				view_ad_link = page.get_by_text(text, exact=False)
				if await view_ad_link.count() > 0:
					# Try to find href in parent or self
					parent = view_ad_link.first.locator("..")
					href = await parent.get_attribute('href')
					if not href:
						# Try as link itself
						href = await view_ad_link.first.get_attribute('href')
					if href and ('/v/' in href or '/a' in href):
						if href.startswith('http'):
							log_step(f"Ad URL gevonden via '{text}': {href}")
							return href
						else:
							base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
							full_url = f"{base_url}{href}"
							log_step(f"Ad URL gevonden via '{text}': {full_url}")
							return full_url
			except Exception:
				continue
		
		# Try to find ad links (but exclude help/terms links)
		ad_link = page.locator("a[href*='/v/'], a[href*='/a']").first
		if await ad_link.count() > 0:
			href = await ad_link.get_attribute('href')
			if href and '/help/' not in href and '/voorwaarden' not in href and '/privacy' not in href:
				if href.startswith('http'):
					log_step(f"Ad URL gevonden via link: {href}")
					return href
				else:
					base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
					full_url = f"{base_url}{href}"
					log_step(f"Ad URL gevonden via link: {full_url}")
					return full_url
		
		# Try to find success message and extract URL from it
		success_messages = [
			"Je advertentie is geplaatst",
			"Advertentie geplaatst",
			"Succesvol geplaatst"
		]
		for msg in success_messages:
			try:
				success_elem = page.get_by_text(msg, exact=False)
				if await success_elem.count() > 0:
					# Look for nearby links
					parent = success_elem.first.locator("..")
					link = parent.locator("a[href*='/v/'], a[href*='/a']").first
					if await link.count() > 0:
						href = await link.get_attribute('href')
						if href and '/help/' not in href:
							if href.startswith('http'):
								return href
							else:
								base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
								return f"{base_url}{href}"
			except Exception:
				continue
		
		# If not found on current page, try "Mijn advertenties" page
		log_step("Ad URL niet gevonden op huidige pagina, proberen 'Mijn advertenties'...")
		base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
		
		# Wait a bit longer for ad to appear in "Mijn advertenties"
		await page.wait_for_timeout(5000)
		
		# Navigate to "Mijn advertenties" - use the confirmed URL
		my_ads_urls = [
			f"{base_url}/my-account/sell/index.html",  # Confirmed correct URL
			f"{base_url}/mijn-marktplaats/mijn-advertenties",
			f"{base_url}/mijn-marktplaats",
		]
		
		# Try to find "Mijn advertenties" link first as backup
		my_ads_link_selectors = [
			"a:has-text('Mijn advertenties')",
			"a:has-text('mijn advertenties')",
			"a[href*='my-account/sell']",
			"a[href*='mijn-advertenties']",
			"a[href*='advertenties']",
		]
		
		for selector in my_ads_link_selectors:
			try:
				link = page.locator(selector).first
				if await link.count() > 0:
					href = await link.get_attribute('href')
					if href:
						if href.startswith('http'):
							my_ads_urls.insert(0, href)  # Add to front of list
						else:
							url = f"{base_url}{href}" if href.startswith('/') else f"{base_url}/{href}"
							my_ads_urls.insert(0, url)
						log_step(f"Gevonden 'Mijn advertenties' link: {my_ads_urls[0]}")
						break
			except Exception:
				continue
		
		for my_ads_url in my_ads_urls:
			try:
				log_step(f"Navigeren naar: {my_ads_url}")
				await page.goto(my_ads_url, wait_until="domcontentloaded", timeout=30000)
				await page.wait_for_timeout(5000)  # Wait longer for page to load
				
				# Check if we're logged in - if not, can't access "Mijn advertenties"
				current_url_after = page.url
				if 'login' in current_url_after.lower() or 'inloggen' in current_url_after.lower():
					log_step("⚠️  Niet ingelogd - kan 'Mijn advertenties' niet openen")
					continue
				
				# Look for the most recent ad (first ad in the list)
				# Try multiple selectors for ad listings - be more specific
				# On /my-account/sell/index.html, ads are typically in a list or table
				ad_selectors = [
					'table a[href*="/v/"]',  # Table rows with ad links
					'table a[href*="/a"]',
					'tbody a[href*="/v/"]',  # Table body
					'tbody a[href*="/a"]',
					'tr a[href*="/v/"]',  # Table rows
					'tr a[href*="/a"]',
					'li a[href*="/v/"]',  # List items
					'li a[href*="/a"]',
					'article[data-testid="ad"] a[href*="/v/"]',
					'article[data-testid="ad"] a[href*="/a"]',
					'[data-testid="ad-card"] a[href*="/v/"]',
					'[data-testid="ad-card"] a[href*="/a"]',
					'.mp-Listing a[href*="/v/"]',
					'.mp-Listing a[href*="/a"]',
					'article a[href*="/v/"]',
					'article a[href*="/a"]',
					'a[href*="/v/"]',  # Any link with /v/
					'a[href*="/a"]',   # Any link with /a
				]
				
				for selector in ad_selectors:
					try:
						ad_links = page.locator(selector)
						count = await ad_links.count()
						log_step(f"  Selector '{selector}': {count} links gevonden")
						
						if count > 0:
							# Get the first (most recent) ad
							first_ad = ad_links.first
							# Check if visible
							is_visible = await first_ad.is_visible()
							if not is_visible:
								continue
								
							href = await first_ad.get_attribute('href')
							
							if href:
								# Filter out non-ad links
								if '/v/' in href or '/a' in href:
									if '/help/' not in href and '/voorwaarden' not in href and '/privacy' not in href:
										if href.startswith('http'):
											log_step(f"✅ Ad URL gevonden in Mijn advertenties: {href}")
											return href
										else:
											full_url = f"{base_url}{href}" if not href.startswith('/') else f"{base_url}{href}"
											log_step(f"✅ Ad URL gevonden in Mijn advertenties: {full_url}")
											return full_url
					except Exception as e:
						log_step(f"  Selector '{selector}' fout: {e}")
						continue
				
				# Alternative: try to find ad by title if provided
				if product_title:
					log_step(f"Zoeken naar ad met titel: {product_title}")
					try:
						# Look for text containing the title
						title_elements = page.get_by_text(product_title, exact=False)
						count = await title_elements.count()
						log_step(f"  Gevonden {count} element(en) met titel '{product_title}'")
						
						for i in range(min(count, 10)):
							try:
								title_elem = title_elements.nth(i)
								# Try to find parent or ancestor link
								parent_link = title_elem.locator("xpath=ancestor::a[contains(@href, '/v/') or contains(@href, '/a')]")
								if await parent_link.count() > 0:
									href = await parent_link.first.get_attribute('href')
									if href and '/help/' not in href:
										if href.startswith('http'):
											log_step(f"✅ Ad URL gevonden via titel: {href}")
											return href
										else:
											full_url = f"{base_url}{href}" if not href.startswith('/') else f"{base_url}{href}"
											log_step(f"✅ Ad URL gevonden via titel: {full_url}")
											return full_url
								
								# Try sibling link
								sibling_link = title_elem.locator("xpath=following-sibling::a[1] | preceding-sibling::a[1]")
								if await sibling_link.count() > 0:
									href = await sibling_link.first.get_attribute('href')
									if href and ('/v/' in href or '/a' in href) and '/help/' not in href:
										if href.startswith('http'):
											log_step(f"✅ Ad URL gevonden via titel (sibling): {href}")
											return href
										else:
											full_url = f"{base_url}{href}" if not href.startswith('/') else f"{base_url}{href}"
											log_step(f"✅ Ad URL gevonden via titel (sibling): {full_url}")
											return full_url
							except Exception as e:
								log_step(f"  Fout bij element {i}: {e}")
								continue
					except Exception as e:
						log_step(f"Zoeken op titel fout: {e}")
				
				# Last resort: get all links and find the first ad link
				log_step("Laatste poging: alle links scannen...")
				try:
					all_links = page.locator("a[href*='/v/'], a[href*='/a']")
					link_count = await all_links.count()
					log_step(f"  Totaal {link_count} ad links gevonden op pagina")
					
					for i in range(min(link_count, 20)):
						try:
							link = all_links.nth(i)
							href = await link.get_attribute('href')
							
							if href:
								# Clean up href
								href = href.strip()
								
								# Filter out non-ad links - must be marktplaats.nl ad URLs
								# Exclude: logout, login, help, privacy, auth, etc.
								excluded_patterns = [
									'/logout', '/login', '/help/', '/voorwaarden', '/privacy',
									'/auth/', 'auth.marktplaats.nl', '/identity/', '/account/',
									'/mijn-marktplaats', '/my-account', '/sell/index.html'
								]
								
								# Check if it's excluded
								is_excluded = any(pattern in href.lower() for pattern in excluded_patterns)
								
								# Must be a marktplaats.nl ad URL (contains /v/ or /a/ and is from marktplaats.nl)
								is_ad_url = (
									('/v/' in href or '/a' in href) and
									('marktplaats.nl' in href or href.startswith('/v/') or href.startswith('/a')) and
									not is_excluded
								)
								
								if is_ad_url:
									# Remove query parameters that might interfere
									if '?' in href:
										href = href.split('?')[0]
									
									# Check if it's visible and looks like an ad
									try:
										is_visible = await link.is_visible()
									except:
										is_visible = True  # Assume visible if check fails
									
									# Get text to verify it's an ad link
									try:
										text = await link.text_content()
										text = text.strip() if text else ""
									except:
										text = ""
									
									# Accept if visible or has text (or if we can't determine)
									if is_visible or text:
										if href.startswith('http'):
											log_step(f"✅ Ad URL gevonden (laatste poging, link {i+1}): {href}")
											return href
										else:
											# Make sure href starts with /
											if not href.startswith('/'):
												href = f"/{href}"
											full_url = f"{base_url}{href}"
											log_step(f"✅ Ad URL gevonden (laatste poging, link {i+1}): {full_url}")
											return full_url
						except Exception as e:
							log_step(f"  Fout bij link {i+1}: {e}")
							continue
				except Exception as e:
					log_step(f"Laatste poging fout: {e}")
				
			except Exception as e:
				log_step(f"Fout bij navigeren naar {my_ads_url}: {e}")
				continue
		
		log_step(f"Waarschuwing: Kon geen ad URL vinden op pagina of in Mijn advertenties")
		return None
	except Exception as e:
		print(f"Error getting ad URL: {e}")
		import traceback
		traceback.print_exc()
		return None


async def publish_ad(page: Page, product_title: Optional[str] = None) -> Optional[str]:
	"""Publish ad and verify it was actually posted."""
	log_step("Zoeken naar 'Plaats advertentie' knop...")
	
	# Store current URL before clicking
	url_before = page.url
	log_step(f"URL voor plaatsen: {url_before}")
	
	# Try specific id first
	button_clicked = False
	try:
		btn = page.locator("#syi-place-ad-button")
		if await btn.count() > 0:
			log_step("Knop #syi-place-ad-button gevonden")
			await btn.first.scroll_into_view_if_needed()
			# wait until enabled
			try:
				await btn.first.wait_for(state="visible", timeout=3000 if FAST_MODE else 5000)
			except Exception:
				pass
			try:
				# Check if button is disabled
				is_disabled = await btn.first.get_attribute('disabled')
				if is_disabled:
					log_step("⚠️  Knop is uitgeschakeld (disabled)")
				else:
					log_step("Klikken op knop...")
					await btn.first.click(force=True)
					button_clicked = True
					await page.wait_for_timeout(2000)  # Wait for navigation/response
					await page.wait_for_load_state('domcontentloaded')
			except Exception as e:
				log_step(f"Fout bij klikken: {e}, proberen JavaScript click...")
				try:
					await btn.first.evaluate("(b)=>b.click()")
					button_clicked = True
					await page.wait_for_timeout(2000)
					await page.wait_for_load_state('domcontentloaded')
				except Exception as e2:
					log_step(f"JavaScript click ook gefaald: {e2}")
	except Exception as e:
		log_step(f"Fout bij zoeken naar #syi-place-ad-button: {e}")
	
	# If button not clicked yet, try generic buttons
	if not button_clicked:
		candidates = [
			("button", "Plaats"),
			("button", "Publiceer"),
			("button", "Doorgaan"),
			("link", "Plaats"),
		]
		for role, text in candidates:
			try:
				locator = page.get_by_role(role, name=text) if hasattr(page, 'get_by_role') else page.get_by_text(text)
				if await locator.count() > 0:
					log_step(f"Knop gevonden: {role} met tekst '{text}'")
					await locator.first.scroll_into_view_if_needed()
					await locator.first.click(force=True)
					button_clicked = True
					await page.wait_for_timeout(2000)
					await page.wait_for_load_state('domcontentloaded')
					break
			except Exception as e:
				log_step(f"Fout bij {role} '{text}': {e}")
				continue
	
	# If still not clicked, try variants
	if not button_clicked:
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
				loc = page.locator(sel)
				if await loc.count() > 0:
					log_step(f"Knop gevonden met selector: {sel}")
					await loc.first.scroll_into_view_if_needed()
					await loc.first.click(force=True)
					button_clicked = True
					await page.wait_for_timeout(2000)
					await page.wait_for_load_state('domcontentloaded')
					break
			except Exception as e:
				log_step(f"Fout bij selector '{sel}': {e}")
				continue
	
	# Last resort: form submit
	if not button_clicked:
		try:
			form = page.locator("form").last
			if await form.count() > 0:
				log_step("Form submit proberen...")
				await form.evaluate("(f)=>f.submit()")
				button_clicked = True
				await page.wait_for_timeout(2000)
				await page.wait_for_load_state('domcontentloaded')
		except Exception as e:
			log_step(f"Form submit gefaald: {e}")
	
	if not button_clicked:
		log_step("❌ Geen knop gevonden om advertentie te plaatsen")
		return None
	
	# Wait longer for page to process
	log_step("Wachten op verwerking...")
	await page.wait_for_timeout(5000)  # Wait longer for ad to be processed
	
	# Check URL after clicking
	url_after = page.url
	log_step(f"URL na plaatsen: {url_after}")
	
	# Check for error messages
	error_selectors = [
		"text=Er is een fout opgetreden",
		"text=Er ging iets mis",
		"text=Probeer het opnieuw",
		"[class*='error']",
		"[class*='Error']",
	]
	for selector in error_selectors:
		try:
			error_elem = page.locator(selector).first
			if await error_elem.count() > 0:
				error_text = await error_elem.text_content()
				log_step(f"⚠️  Foutmelding gevonden: {error_text}")
				return None
		except:
			continue
	
	# Check for success messages
	success_selectors = [
		"text=Je advertentie is geplaatst",
		"text=Advertentie geplaatst",
		"text=Succesvol geplaatst",
		"text=Bekijk je advertentie",
	]
	has_success_message = False
	for selector in success_selectors:
		try:
			success_elem = page.locator(selector).first
			if await success_elem.count() > 0:
				log_step(f"✅ Succesbericht gevonden: {selector}")
				has_success_message = True
				break
		except:
			continue
	
	# Try to get ad URL
	ad_url = await get_posted_ad_url(page, product_title)
	
	# Verify: if we got a URL, make sure it's actually an ad page
	if ad_url:
		log_step(f"Ad URL gevonden: {ad_url}")
		# Verify by checking if URL changed to an ad page
		if '/v/' in url_after or '/a' in url_after:
			log_step("✅ URL is veranderd naar ad pagina - advertentie lijkt geplaatst")
			return ad_url
		elif has_success_message:
			log_step("✅ Succesbericht gevonden - advertentie lijkt geplaatst")
			return ad_url
		else:
			# Double-check by navigating to the URL
			log_step("Verifiëren ad URL door erheen te navigeren...")
			try:
				await page.goto(ad_url, wait_until="domcontentloaded", timeout=10000)
				await page.wait_for_timeout(2000)
				current_url = page.url
				if '/v/' in current_url or '/a' in current_url:
					log_step(f"✅ Ad URL geverifieerd: {current_url}")
					return current_url
				else:
					log_step(f"⚠️  Ad URL lijkt niet geldig (redirect naar: {current_url})")
					return None
			except Exception as e:
				log_step(f"⚠️  Kon ad URL niet verifiëren: {e}")
				# Still return it if we have it, but log warning
				return ad_url
	else:
		log_step("⚠️  Geen ad URL gevonden na plaatsen")
		return None


async def run(csv_path: Optional[str], api_url: Optional[str], product_id: Optional[str], login_only: bool, keep_open: bool=False) -> Optional[List[Dict]]:
	load_dotenv(override=True)
	base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
	user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
	media_root = os.getenv('MEDIA_ROOT', './public/media')
	action_delay_ms = int(os.getenv('ACTION_DELAY_MS', '200'))

	os.makedirs(user_data_dir, exist_ok=True)

	# Determine if we should run headless
	# Default: NOT headless on Windows/Mac (user needs to see browser for login)
	# Run headless if: explicitly set, in CI/serverless environment, or no DISPLAY (Linux)
	headless_env = os.getenv('HEADLESS', '').lower()
	has_display = os.getenv('DISPLAY') is not None
	is_ci = os.getenv('CI') is not None or os.getenv('VERCEL') is not None
	is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
	is_windows = os.name == 'nt' or sys.platform == 'win32'
	is_mac = sys.platform == 'darwin'
	
	# Default to visible browser on Windows/Mac (better for login)
	# Only run headless on Linux servers or if explicitly requested
	should_be_headless = False  # Default: visible browser
	
	# Override to headless if:
	# - Explicitly set to true
	# - Running on CI/Railway
	# - On Linux without DISPLAY
	if headless_env in ('1', 'true', 'yes', 'on'):
		should_be_headless = True
	elif is_ci or is_railway:
		should_be_headless = True
	elif not is_windows and not is_mac and not has_display:
		should_be_headless = True
	
	# Allow explicit override to false
	if headless_env in ('0', 'false', 'no', 'off'):
		should_be_headless = False
	
	if VERBOSE:
		print(f"[DEBUG] Headless mode: {should_be_headless} (HEADLESS={headless_env}, OS={sys.platform}, CI={is_ci}, RAILWAY={is_railway})")

	async with async_playwright() as p:
		try:
			browser = await p.chromium.launch_persistent_context(
				user_data_dir=user_data_dir,
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
			print(f"[ERROR] Failed to launch browser: {e}")
			print(f"[ERROR] Trying with headless=True as fallback...")
			try:
				browser = await p.chromium.launch_persistent_context(
					user_data_dir=user_data_dir,
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
				print("[OK] Browser launched in headless mode (fallback)")
			except Exception as e2:
				print(f"[ERROR] Failed to launch browser even in headless mode: {e2}")
				raise
		page = await browser.new_page()
		
		# Add stealth features to avoid detection
		# Set realistic user agent (latest Chrome on macOS)
		await page.set_extra_http_headers({
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
		
		# Remove webdriver property to avoid detection
		await page.add_init_script("""
			Object.defineProperty(navigator, 'webdriver', {
				get: () => undefined
			});
			// Override plugins
			Object.defineProperty(navigator, 'plugins', {
				get: () => [1, 2, 3, 4, 5]
			});
			// Override languages
			Object.defineProperty(navigator, 'languages', {
				get: () => ['nl-NL', 'nl', 'en-US', 'en']
			});
		""")
		
		# Set default timeouts (shorter in fast mode)
		nav_timeout = 30000 if FAST_MODE else 60000
		action_timeout = 20000 if FAST_MODE else 45000
		page.set_default_navigation_timeout(nav_timeout)
		page.set_default_timeout(action_timeout)

		# Check login status
		is_logged_in = await ensure_logged_in(page, base_url)
		
		if login_only:
			if is_logged_in:
				print("✅ Login session prepared. You can close the browser.")
			else:
				print("⚠️  Not logged in. Please log in manually in the browser.")
				print("   The browser will stay open. Press Enter when you're logged in...")
				input()
			await browser.close()
			return
		
		# If not logged in, try automatic login or help user log in
		if not is_logged_in:
			# Check if credentials are available for automatic login
			marktplaats_email = os.getenv('MARKTPLAATS_EMAIL')
			marktplaats_password = os.getenv('MARKTPLAATS_PASSWORD')
			
			if marktplaats_email and marktplaats_password:
				# Automatic login was already attempted in ensure_logged_in
				# If we're here, it failed, so try once more
				print("")
				print("Automatisch inloggen mislukt. Controleren of handmatige login nodig is...")
				print("")
				# Re-check login status (maybe user logged in manually while we were trying)
				await page.wait_for_timeout(2000)
				is_logged_in = await ensure_logged_in(page, base_url)
			
			if not is_logged_in:
				# No credentials or automatic login failed - ask user to log in manually
				print("")
				print("=" * 70)
				print("⚠️  INLOGGEN NODIG")
				print("=" * 70)
				print("")
				print("Het script heeft gedetecteerd dat je niet ingelogd bent op Marktplaats.")
				print("")
				
				if not (marktplaats_email and marktplaats_password):
					print("Geen login credentials gevonden in .env bestand.")
					print("Voeg toe aan .env:")
					print("  MARKTPLAATS_EMAIL=je-email@voorbeeld.nl")
					print("  MARKTPLAATS_PASSWORD=je-wachtwoord")
					print("")
				
				print("STAPPEN:")
				print("1. Log in op Marktplaats in de browser die is geopend")
				print("2. Wacht tot je bent ingelogd (je ziet je profiel/account)")
				print("3. Druk op ENTER in dit venster om door te gaan")
				print("")
				print("De browser blijft open totdat je op ENTER drukt...")
				print("")
				
				# Navigate to login page (use the correct identity v2 login URL)
				try:
					login_url = f"{base_url}/identity/v2/login?target=https%3A%2F%2Fwww.marktplaats.nl%2F"
					await page.goto(login_url, wait_until="domcontentloaded")
				except:
					await page.goto(f"{base_url}/", wait_until="domcontentloaded")
				
				# Wait for user to press Enter (only if interactive)
				try:
					input("Druk op ENTER als je bent ingelogd...")
				except EOFError:
					# Non-interactive mode (like when run via tool)
					print("⚠️  Non-interactive mode - kan niet wachten op input")
					print("   Script gaat door, maar login kan nodig zijn")
				
				# Check login status again
				await page.wait_for_timeout(2000)
				is_logged_in = await ensure_logged_in(page, base_url)
				if not is_logged_in:
					print("⚠️  Login nog niet gedetecteerd. Het script gaat door, maar dit kan problemen veroorzaken.")
					print("   Als producten niet worden geplaatst, controleer of je echt bent ingelogd.")
				else:
					print("✅ Login succesvol gedetecteerd!")
				print("")

		# Read products from API or CSV
		if api_url:
			print(f"Fetching product from API: {api_url}")
			products = read_products_from_api(api_url)
		elif csv_path:
			products = read_products(csv_path)
		else:
			raise SystemExit("Either --csv or --api is required when not using --login")
		# Import scrape function
		sys.path.insert(0, os.path.dirname(__file__))
		from scrape_ad_stats import scrape_ad_stats
		
		all_results = []
		for index, product in enumerate(products, start=1):
			try:
				print(f"Posting {index}/{len(products)}: {product.title}")
				await click_place_ad(page, base_url)
				
				# Use category_path if available, otherwise use auto-suggest
				if product.category_path:
					log_step(f"Gebruik categorie uit product: {product.category_path}")
					# Fill title first (needed for category selection on some pages)
					try:
						title_input = page.get_by_label("Titel", exact=False)
						if await title_input.count() == 0:
							title_input = page.get_by_placeholder("Titel", exact=False)
						if await title_input.count() > 0:
							value = await title_input.first.input_value()
							if not value:
								await title_input.first.fill(product.title)
								await page.wait_for_timeout(WAIT_SHORT)
					except Exception:
						pass
					
					# Navigate to category selection
					try:
						find_button = page.get_by_role("button", name="Vind categorie")
						if await find_button.count() == 0:
							find_button = page.locator("[data-testid='findCategory']")
						if await find_button.count() > 0:
							await find_button.first.click()
							await page.wait_for_timeout(WAIT_MEDIUM)
					except Exception as e:
						log_step(f"Waarschuwing: Kon 'Vind categorie' niet vinden: {e}")
					
					# Now choose the specific category
					await choose_category(page, product.category_path)
					
					# Click "Verder" if needed
					try:
						next_button = page.get_by_role("button", name="Verder")
						if await next_button.count() > 0:
							await next_button.first.click()
							await page.wait_for_load_state("domcontentloaded")
							await page.wait_for_timeout(WAIT_SHORT)
					except Exception:
						pass
				else:
					log_step("Geen categorie opgegeven, gebruik auto-suggest")
					await auto_suggest_category(page, product.title)
				
				await fill_basic_fields(page, product)
				await upload_photos(page, product, media_root)
				await select_free_bundle(page)
				ad_url = await publish_ad(page, product.title)
				
				# Scrape stats if ad was posted successfully
				ad_stats = None
				if ad_url:
					print(f"Ad posted at: {ad_url}")
					print("Scraping ad statistics...")
					
					# Try to scrape from individual ad page first
					ad_stats = await scrape_ad_stats(page, ad_url)
					
					# If that fails or doesn't get all data, try user page
					if not ad_stats or not ad_stats.get('ad_id'):
						try:
							from scrape_user_ads import get_user_url_from_ad, scrape_user_ads
							user_url = await get_user_url_from_ad(page, ad_url)
							if user_url:
								print(f"Found user page: {user_url}")
								print("Scraping all ads from user page...")
								user_ads = await scrape_user_ads(page, user_url)
								
								# Find matching ad by article number or title
								for user_ad in user_ads:
									if user_ad.get('ad_id') and product.article_number:
										# Try to match by checking if article number might be in title or URL
										if product.article_number in (user_ad.get('title', '') or ''):
											ad_stats = user_ad
											break
									elif user_ad.get('ad_url') == ad_url:
										ad_stats = user_ad
										break
						except Exception as e:
							print(f"Fout bij scrapen user page: {e}")
					
					if ad_stats:
						print(f"Stats scraped: Ad ID={ad_stats.get('ad_id')}, Views={ad_stats.get('views')}, Saves={ad_stats.get('saves')}")
				
				await page.wait_for_timeout(action_delay_ms)
				print(f"[OK] Succesvol verwerkt: {product.title}")
				
				# Store result for API mode
				product_result = {
					'ad_url': ad_url,
					'ad_id': ad_stats.get('ad_id') if ad_stats else None,
					'views': ad_stats.get('views', 0) if ad_stats else 0,
					'saves': ad_stats.get('saves', 0) if ad_stats else 0,
					'posted_at': ad_stats.get('posted_at') if ad_stats else None,
					'article_number': product.article_number,
					'title': product.title,
					'status': 'completed' if ad_url else 'failed',
				}
				
				# For single product mode (has product_id), return immediately
				if product_id:
					import json
					print(f"RESULT_JSON:{json.dumps(product_result)}")
					all_results.append(product_result)
					break
				
				# For batch mode, collect results
				all_results.append(product_result)
			except Exception as e:
				print(f"[ERROR] Fout bij plaatsen product {index}/{len(products)} ({product.title}): {e}")
				import traceback
				traceback.print_exc()
				# Store failed result
				failed_result = {
					'ad_url': None,
					'ad_id': None,
					'views': 0,
					'saves': 0,
					'posted_at': None,
					'article_number': product.article_number,
					'title': product.title,
					'status': 'failed',
					'error': str(e),
				}
				if product_id:
					import json
					print(f"RESULT_JSON:{json.dumps(failed_result)}")
					all_results.append(failed_result)
					break
				else:
					all_results.append(failed_result)
				# Continue with next product in batch mode
				continue

		print("Done.")
		if keep_open:
			print("Keep-open enabled. Browser will stay open for inspection.")
			await page.wait_for_timeout(3600000)
		else:
			await browser.close()
		
		return all_results


def parse_args() -> tuple[Optional[str], Optional[str], Optional[str], bool, bool]:
	import argparse
	parser = argparse.ArgumentParser(description="Marktplaats automator")
	parser.add_argument("--csv", type=str, help="Path to products.csv", default=None)
	parser.add_argument("--api", type=str, help="API URL to fetch product data", default=None)
	parser.add_argument("--product-id", type=str, help="Product ID (used with --api)", default=None)
	parser.add_argument("--login", action="store_true", help="Prepare login session only")
	parser.add_argument("--keep-open", action="store_true", help="Keep browser open after run for debugging")
	args = parser.parse_args()
	return args.csv, args.api, args.product_id, args.login, args.keep_open


if __name__ == "__main__":
	csv_path, api_url, product_id, login_only, keep_open = parse_args()
	asyncio.run(run(csv_path, api_url, product_id, login_only, keep_open))
