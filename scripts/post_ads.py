import asyncio
import csv
import os
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
	material: Optional[str] = None
	thickness: Optional[str] = None
	total_surface: Optional[str] = None
	delivery_option: Optional[str] = None


def read_products_from_api(api_url: str) -> List[Product]:
	"""Read product data from API endpoint. Can return single product or list of products."""
	if not requests:
		raise ImportError("requests library is required for API mode. Install with: pip install requests")
	
	try:
		response = requests.get(api_url, timeout=30)
		response.raise_for_status()
		data = response.json()
		
		# Check if it's a list or single object
		products_data = data if isinstance(data, list) else [data]
		
		products = []
		for item in products_data:
			photos = item.get('photos', []) or []
			delivery_methods = item.get('delivery_methods', []) or []
			
			product = Product(
				title=item.get('title', '').strip(),
				description=item.get('description', '').strip(),
				price=str(item.get('price', '')).strip(),
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
			)
			products.append(product)
		
		print(f"✅ {len(products)} product(en) opgehaald van API")
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


async def ensure_logged_in(page: Page, base_url: str) -> None:
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
	except Exception:
		pass


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
			await page.wait_for_timeout(400)
	except Exception:
		pass
	try:
		first_radio = page.locator("input[type='radio']").first
		if await first_radio.count() > 0:
			await first_radio.check()
			await page.wait_for_timeout(200)
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
	parts = [p.strip() for p in category_path.split('>') if p.strip()]
	for part in parts:
		locator = page.get_by_role("link", name=part)
		if await locator.count() == 0:
			locator = page.get_by_role("button", name=part)
		if await locator.count() == 0:
			locator = page.get_by_text(part, exact=False)
		await locator.first.click()
		await page.wait_for_timeout(300)


async def fill_basic_fields(page: Page, product: Product) -> None:
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
	# Price (string input like 0,00). We fill a plain integer; site formats it.
	try:
		price_input = page.locator("#price\\.value, input#price\\.value")
		if await price_input.count() == 0:
			price_input = page.get_by_label("Prijs", exact=False)
		if await price_input.count() == 0:
			price_input = page.locator("input[name='price.value']")
		await price_input.first.fill(str(product.price or ""))
	except Exception:
		pass
	# Condition (select)
	if product.condition:
		try:
			select = page.locator("select[name='singleSelectAttribute[condition]']")
			if await select.count() > 0:
				await select.select_option(label=product.condition)
		except Exception:
			pass
	# Material (select)
	if product.material:
		try:
			select = page.locator("select[name='singleSelectAttribute[material]']")
			if await select.count() > 0:
				await select.select_option(label=product.material)
		except Exception:
			pass
	# Thickness (select)
	if product.thickness:
		try:
			select = page.locator("select[name='singleSelectAttribute[thickness]']")
			if await select.count() > 0:
				await select.select_option(label=product.thickness)
		except Exception:
			pass
	# Total surface (select)
	if product.total_surface:
		try:
			select = page.locator("select[name='singleSelectAttribute[totalSurface]']")
			if await select.count() > 0:
				await select.select_option(label=product.total_surface)
		except Exception:
			pass
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
	# Location (optional)
	if product.location:
		try:
			loc_input = page.get_by_label("Plaatsnaam", exact=False)
			if await loc_input.count() == 0:
				loc_input = page.get_by_placeholder("Plaatsnaam", exact=False)
			await loc_input.first.fill(product.location)
		except Exception:
			pass


async def upload_photos(page: Page, product: Product, media_root: str) -> None:
	photos: List[str] = [os.path.abspath(p) for p in product.photos]
	if not photos and product.article_number:
		photos = find_photos_for_article(media_root, product.article_number)
	if not photos:
		print("No photos found for product; skipping upload")
		return
	try:
		# Multiple strategies for input selection
		selectors = [
			"input[type='file'][multiple]",
			"input[type='file'][accept*='.jpg']",
			"input[type='file'][id^='html5_']",
			"input[type='file']",
		]
		file_input = None
		for sel in selectors:
			locator = page.locator(sel)
			if await locator.count() > 0:
				file_input = locator.first
				break
		if not file_input:
			print("Could not locate file input on the page")
			return
		print(f"Uploading {len(photos)} photos: {photos}")
		await file_input.set_input_files(photos)
		await page.wait_for_timeout(1500)
	except Exception as e:
		print(f"Photo upload error: {e}")
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
			await page.wait_for_timeout(300)
	except Exception:
		pass


async def get_posted_ad_url(page: Page) -> Optional[str]:
	"""Extract the URL of the posted ad from the current page."""
	try:
		# Wait a bit for redirect or page load
		await page.wait_for_timeout(3000)
		
		# Check current URL - if it's an ad page, return it
		current_url = page.url
		if '/v/' in current_url or '/a' in current_url:
			return current_url
		
		# Try to find a link to the ad
		ad_link = page.locator("a[href*='/v/'], a[href*='/a']").first
		if await ad_link.count() > 0:
			href = await ad_link.get_attribute('href')
			if href:
				if href.startswith('http'):
					return href
				else:
					base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
					return f"{base_url}{href}"
		
		# Try to find "Bekijk je advertentie" link
		view_ad_link = page.get_by_text("Bekijk je advertentie", exact=False)
		if await view_ad_link.count() > 0:
			parent = view_ad_link.first.locator("..")
			href = await parent.get_attribute('href')
			if href:
				if href.startswith('http'):
					return href
				else:
					base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl')
					return f"{base_url}{href}"
		
		return None
	except Exception as e:
		print(f"Error getting ad URL: {e}")
		return None


async def publish_ad(page: Page) -> Optional[str]:
	# Try specific id first
	try:
		btn = page.locator("#syi-place-ad-button")
		if await btn.count() > 0:
			await btn.first.scroll_into_view_if_needed()
			# wait until enabled
			try:
				await btn.first.wait_for(state="visible", timeout=5000)
			except Exception:
				pass
			try:
				await btn.first.click(force=True)
				await page.wait_for_load_state('load')
				return await get_posted_ad_url(page)
			except Exception:
				try:
					await btn.first.evaluate("(b)=>b.click()")
					await page.wait_for_load_state('load')
					return await get_posted_ad_url(page)
				except Exception:
					pass
	except Exception:
		pass
	# Generic buttons
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
				await locator.first.scroll_into_view_if_needed()
				await locator.first.click(force=True)
				await page.wait_for_load_state('load')
				return await get_posted_ad_url(page)
		except Exception:
			continue
	# Variants of 'Plaats je advertentie'
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
				await loc.first.scroll_into_view_if_needed()
				await loc.first.click(force=True)
				await page.wait_for_load_state('load')
				return await get_posted_ad_url(page)
		except Exception:
			continue
	# Form submit fallback and Enter
	try:
		form = page.locator("form").last
		if await form.count() > 0:
			await form.evaluate("(f)=>f.submit()")
			await page.wait_for_load_state('load')
			return await get_posted_ad_url(page)
	except Exception:
		pass
	try:
		await page.keyboard.press("Enter")
		await page.wait_for_timeout(700)
		return await get_posted_ad_url(page)
	except Exception:
		pass
	return None


async def run(csv_path: Optional[str], api_url: Optional[str], product_id: Optional[str], login_only: bool, keep_open: bool=False) -> Optional[List[Dict]]:
	load_dotenv(override=True)
	base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
	user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
	media_root = os.getenv('MEDIA_ROOT', './public/media')
	action_delay_ms = int(os.getenv('ACTION_DELAY_MS', '200'))

	os.makedirs(user_data_dir, exist_ok=True)

	async with async_playwright() as p:
		browser = await p.chromium.launch_persistent_context(
			user_data_dir=user_data_dir,
			headless=False,
			viewport={"width": 1280, "height": 900},
			args=["--disable-blink-features=AutomationControlled"],
		)
		page = await browser.new_page()
		# Increase default timeouts for flaky loads
		page.set_default_navigation_timeout(60000)
		page.set_default_timeout(45000)

		await ensure_logged_in(page, base_url)
		if login_only:
			print("Login session prepared. You can close the browser.")
			await browser.close()
			return

		# Read products from API or CSV
		if api_url:
			print(f"Fetching product from API: {api_url}")
			products = read_products_from_api(api_url)
		elif csv_path:
			products = read_products(csv_path)
		else:
			raise SystemExit("Either --csv or --api is required when not using --login")
		# Import scrape function
		import sys
		sys.path.insert(0, os.path.dirname(__file__))
		from scrape_ad_stats import scrape_ad_stats
		
		all_results = []
		for index, product in enumerate(products, start=1):
			print(f"Posting {index}/{len(products)}: {product.title}")
			await click_place_ad(page, base_url)
			await auto_suggest_category(page, product.title)
			await fill_basic_fields(page, product)
			await upload_photos(page, product, media_root)
			await select_free_bundle(page)
			ad_url = await publish_ad(page)
			
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
			print(f"✔ Succesvol verwerkt: {product.title}")
			
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
