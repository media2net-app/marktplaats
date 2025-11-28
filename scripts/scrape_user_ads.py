"""
Scrape alle advertenties en statistieken van een Marktplaats gebruiker pagina.
Bijvoorbeeld: https://www.marktplaats.nl/u/chiel/23777446/
"""
import re
from typing import Dict, List, Optional
from playwright.async_api import Page


async def scrape_user_ads(page: Page, user_url: str) -> List[Dict[str, any]]:
	"""
	Scrape alle advertenties van een Marktplaats gebruiker pagina.
	
	Returns:
		List van dicts met: ad_id, title, price, views, saves, posted_at, ad_url
	"""
	try:
		# Navigate to the user page
		await page.goto(user_url, wait_until="domcontentloaded", timeout=30000)
		await page.wait_for_timeout(3000)
		
		ads = []
		
		# Find all ad listings on the page
		# Marktplaats uses various selectors for ad listings
		ad_selectors = [
			'article[data-testid="ad"]',
			'[data-testid="ad-card"]',
			'.mp-Listing',
			'a[href*="/v/"]',
			'a[href*="/a"]',
		]
		
		ad_elements = []
		for selector in ad_selectors:
			elements = await page.locator(selector).all()
			if elements:
				ad_elements = elements
				break
		
		# If no specific ad elements found, try to find all links to ads
		if not ad_elements:
			ad_links = await page.locator('a[href*="/v/"], a[href*="/a"]').all()
			ad_elements = ad_links
		
		print(f"Gevonden {len(ad_elements)} advertentie elementen")
		
		for idx, element in enumerate(ad_elements[:50]):  # Limit to first 50
			try:
				ad_data = {
					'ad_id': None,
					'title': '',
					'price': '',
					'views': 0,
					'saves': 0,
					'posted_at': None,
					'ad_url': None,
				}
				
				# Get ad URL
				href = await element.get_attribute('href')
				if href:
					if href.startswith('http'):
						ad_data['ad_url'] = href
					else:
						base_url = "https://www.marktplaats.nl"
						ad_data['ad_url'] = f"{base_url}{href}"
					
					# Extract ad ID from URL
					ad_id_match = re.search(r'/a(\d+)-', ad_data['ad_url'])
					if ad_id_match:
						ad_data['ad_id'] = f"a{ad_id_match.group(1)}"
				
				# Get title
				title_elem = element.locator('h2, h3, [class*="title"], [class*="Title"]').first
				if await title_elem.count() > 0:
					title_text = await title_elem.text_content()
					if title_text:
						ad_data['title'] = title_text.strip()
				
				# Get price
				price_elem = element.locator('[class*="price"], [class*="Price"], [data-testid*="price"]').first
				if await price_elem.count() > 0:
					price_text = await price_elem.text_content()
					if price_text:
						# Extract price (format: € 99,00 or €99,00)
						price_match = re.search(r'€\s*([\d.,]+)', price_text)
						if price_match:
							ad_data['price'] = price_match.group(1).replace(',', '.')
				
				# Try to get stats from the element
				element_text = await element.text_content()
				if element_text:
					# Extract views - try multiple patterns
					views_match = re.search(r'(\d+)\s*x\s*bekeken', element_text, re.IGNORECASE)
					if not views_match:
						views_match = re.search(r'(\d+)\s*bekeken', element_text, re.IGNORECASE)
					if views_match:
						ad_data['views'] = int(views_match.group(1))
					
					# Extract saves - try multiple patterns
					saves_match = re.search(r'(\d+)\s*x\s*bewaard', element_text, re.IGNORECASE)
					if not saves_match:
						saves_match = re.search(r'(\d+)\s*bewaard', element_text, re.IGNORECASE)
					if saves_match:
						ad_data['saves'] = int(saves_match.group(1))
					
					# Extract date
					date_match = re.search(r'(Vandaag|Gisteren|Een week|Sinds \d+)', element_text, re.IGNORECASE)
					if date_match:
						ad_data['posted_at'] = date_match.group(1)
				
				# If we have an ad URL, try to scrape stats from the individual ad page
				if ad_data['ad_url'] and (ad_data['views'] == 0 or ad_data['saves'] == 0):
					try:
						from scrape_ad_stats import scrape_ad_stats
						ad_stats = await scrape_ad_stats(page, ad_data['ad_url'])
						if ad_stats:
							if ad_stats.get('views'):
								ad_data['views'] = ad_stats.get('views', 0)
							if ad_stats.get('saves'):
								ad_data['saves'] = ad_stats.get('saves', 0)
							if ad_stats.get('ad_id') and not ad_data['ad_id']:
								ad_data['ad_id'] = ad_stats.get('ad_id')
							if ad_stats.get('posted_at') and not ad_data['posted_at']:
								ad_data['posted_at'] = ad_stats.get('posted_at')
					except Exception as e:
						print(f"Fout bij scrapen individuele ad stats: {e}")
				
				# Only add if we have at least an ad_id or title
				if ad_data['ad_id'] or ad_data['title']:
					ads.append(ad_data)
					
			except Exception as e:
				print(f"Fout bij verwerken advertentie {idx + 1}: {e}")
				continue
		
		# Alternative: Try to extract from page content using JavaScript
		if len(ads) == 0:
			print("Proberen JavaScript extractie...")
			try:
				ads_data = await page.evaluate("""
					() => {
						const ads = [];
						
						// Find all ad links
						document.querySelectorAll('a[href*="/v/"], a[href*="/a"]').forEach((link, idx) => {
							if (idx > 50) return; // Limit
							
							const href = link.getAttribute('href');
							const fullUrl = href.startsWith('http') ? href : 'https://www.marktplaats.nl' + href;
							
							// Extract ad ID
							const adIdMatch = fullUrl.match(/\\/a(\\d+)-/);
							const adId = adIdMatch ? 'a' + adIdMatch[1] : null;
							
							// Find title in parent or nearby elements
							const parent = link.closest('article, div, li') || link.parentElement;
							const titleElem = parent.querySelector('h2, h3, [class*="title"]');
							const title = titleElem ? titleElem.textContent.trim() : '';
							
							// Find price
							const priceElem = parent.querySelector('[class*="price"], [class*="Price"]');
							const priceText = priceElem ? priceElem.textContent : '';
							const priceMatch = priceText.match(/€\\s*([\\d.,]+)/);
							const price = priceMatch ? priceMatch[1].replace(',', '.') : '';
							
							// Get all text from parent
							const allText = parent.textContent || '';
							
							// Extract views - try multiple patterns
							let viewsMatch = allText.match(/(\\d+)\\s*x\\s*bekeken/i);
							if (!viewsMatch) {
								viewsMatch = allText.match(/(\\d+)\\s*bekeken/i);
							}
							const views = viewsMatch ? parseInt(viewsMatch[1]) : 0;
							
							// Extract saves - try multiple patterns
							let savesMatch = allText.match(/(\\d+)\\s*x\\s*bewaard/i);
							if (!savesMatch) {
								savesMatch = allText.match(/(\\d+)\\s*bewaard/i);
							}
							const saves = savesMatch ? parseInt(savesMatch[1]) : 0;
							
							// Extract date
							const dateMatch = allText.match(/(Vandaag|Gisteren|Een week|Sinds \\d+)/i);
							const postedAt = dateMatch ? dateMatch[1] : null;
							
							if (adId || title) {
								ads.push({
									ad_id: adId,
									title: title,
									price: price,
									views: views,
									saves: saves,
									posted_at: postedAt,
									ad_url: fullUrl
								});
							}
						});
						
						return ads;
					}
				""")
				
				if ads_data and len(ads_data) > 0:
					ads = ads_data
					print(f"✅ {len(ads)} advertenties gevonden via JavaScript")
			except Exception as e:
				print(f"Fout bij JavaScript extractie: {e}")
		
		return ads
		
	except Exception as e:
		print(f"Error scraping user ads: {e}")
		return []


async def get_user_url_from_ad(page: Page, ad_url: str) -> Optional[str]:
	"""
	Extract user profile URL from an ad page.
	"""
	try:
		await page.goto(ad_url, wait_until="domcontentloaded", timeout=30000)
		await page.wait_for_timeout(2000)
		
		# Look for user profile link
		user_link = page.locator('a[href*="/u/"]').first
		if await user_link.count() > 0:
			href = await user_link.get_attribute('href')
			if href:
				if href.startswith('http'):
					return href
				else:
					return f"https://www.marktplaats.nl{href}"
		
		# Alternative: look for seller info
		seller_link = page.get_by_text("Van deze adverteerder", exact=False).locator("..").locator("a").first
		if await seller_link.count() > 0:
			href = await seller_link.get_attribute('href')
			if href:
				if href.startswith('http'):
					return href
				else:
					return f"https://www.marktplaats.nl{href}"
		
		return None
	except Exception as e:
		print(f"Error getting user URL: {e}")
		return None


async def ensure_logged_in(page: Page, base_url: str) -> None:
	"""Ensure user is logged in to Marktplaats."""
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


async def main():
	"""CLI entry point for scraping user ads."""
	import asyncio
	import sys
	import json
	import argparse
	from playwright.async_api import async_playwright
	import os
	from dotenv import load_dotenv
	
	load_dotenv()
	
	parser = argparse.ArgumentParser(description="Scrape Marktplaats user ads")
	parser.add_argument("--url", type=str, required=True, help="User profile URL")
	args = parser.parse_args()
	
	user_data_dir = os.getenv('USER_DATA_DIR', './user_data')
	os.makedirs(user_data_dir, exist_ok=True)
	
	async with async_playwright() as p:
		browser = await p.chromium.launch_persistent_context(
			user_data_dir=user_data_dir,
			headless=False,
			viewport={"width": 1280, "height": 900},
			args=["--disable-blink-features=AutomationControlled"],
		)
		page = await browser.new_page()
		page.set_default_navigation_timeout(60000)
		page.set_default_timeout(45000)
		
		# Ensure logged in
		base_url = os.getenv('MARKTPLAATS_BASE_URL', 'https://www.marktplaats.nl').rstrip('/')
		await ensure_logged_in(page, base_url)
		
		print(f"Scraping user page: {args.url}")
		ads = await scrape_user_ads(page, args.url)
		
		# Output as JSON for API to parse
		print(f"USER_ADS_JSON:{json.dumps(ads)}")
		
		await browser.close()
	
	return ads


if __name__ == "__main__":
	import asyncio
	asyncio.run(main())

