"""
Scrape advertentie statistieken van een geplaatste Marktplaats advertentie.
Haalt op: advertentienummer, aantal views, aantal saves, en geplaatst datum.
"""
import re
from typing import Dict, Optional
from playwright.async_api import Page


async def scrape_ad_stats(page: Page, ad_url: str) -> Optional[Dict[str, any]]:
	"""
	Scrape statistieken van een Marktplaats advertentie pagina.
	
	Returns:
		Dict met: ad_id, views, saves, posted_at
		None als scraping faalt
	"""
	try:
		# Navigate to the ad page
		await page.goto(ad_url, wait_until="domcontentloaded", timeout=30000)
		await page.wait_for_timeout(2000)
		
		stats = {
			'ad_id': None,
			'views': 0,
			'saves': 0,
			'posted_at': None,
		}
		
		# Extract ad ID from URL (format: a1519860984)
		ad_id_match = re.search(r'/a(\d+)-', ad_url)
		if ad_id_match:
			stats['ad_id'] = f"a{ad_id_match.group(1)}"
		
		# Try to find "Advertentienummer: a1519860984"
		try:
			ad_number_text = page.get_by_text("Advertentienummer:", exact=False)
			if await ad_number_text.count() > 0:
				parent = ad_number_text.first.locator("..")
				text = await parent.text_content()
				if text:
					# Extract ad ID from text
					ad_id_match = re.search(r'a\d+', text)
					if ad_id_match:
						stats['ad_id'] = ad_id_match.group(0)
		except Exception:
			pass
		
		# Scrape views (format: "31x bekeken" or "32x bekeken")
		try:
			views_text = page.get_by_text(re.compile(r'\d+x bekeken', re.IGNORECASE), exact=False)
			if await views_text.count() > 0:
				text = await views_text.first.text_content()
				if text:
					views_match = re.search(r'(\d+)x\s+bekeken', text, re.IGNORECASE)
					if views_match:
						stats['views'] = int(views_match.group(1))
		except Exception:
			pass
		
		# Scrape saves (format: "0x bewaard" or "5x bewaard")
		try:
			saves_text = page.get_by_text(re.compile(r'\d+x bewaard', re.IGNORECASE), exact=False)
			if await saves_text.count() > 0:
				text = await saves_text.first.text_content()
				if text:
					saves_match = re.search(r'(\d+)x\s+bewaard', text, re.IGNORECASE)
					if saves_match:
						stats['saves'] = int(saves_match.group(1))
		except Exception:
			pass
		
		# Scrape posted date (format: "Sinds 6 nov '25" or "Sinds 6 nov 2025")
		try:
			date_text = page.get_by_text(re.compile(r'Sinds \d+', re.IGNORECASE), exact=False)
			if await date_text.count() > 0:
				text = await date_text.first.text_content()
				if text:
					# Extract date - format can vary
					# We'll store the raw text and parse it later if needed
					stats['posted_at'] = text.replace('Sinds', '').strip()
		except Exception:
			pass
		
		# Alternative: Try to find all stats in a container
		try:
			# Look for container with stats (often in a box with icons)
			stats_container = page.locator('[class*="stats"], [class*="statistics"], [data-testid*="stats"]').first
			if await stats_container.count() > 0:
				container_text = await stats_container.text_content()
				if container_text:
					# Extract views
					views_match = re.search(r'(\d+)x\s+bekeken', container_text, re.IGNORECASE)
					if views_match:
						stats['views'] = int(views_match.group(1))
					
					# Extract saves
					saves_match = re.search(r'(\d+)x\s+bewaard', container_text, re.IGNORECASE)
					if saves_match:
						stats['saves'] = int(saves_match.group(1))
					
					# Extract date
					date_match = re.search(r'Sinds\s+(.+)', container_text, re.IGNORECASE)
					if date_match:
						stats['posted_at'] = date_match.group(1).strip()
		except Exception:
			pass
		
		return stats
		
	except Exception as e:
		print(f"Error scraping ad stats: {e}")
		return None

