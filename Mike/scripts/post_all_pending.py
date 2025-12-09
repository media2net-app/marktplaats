"""
Script to post all pending products from the database via API.
This replaces the old CSV-based batch processing.
"""
import asyncio
import os
import sys
import requests
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))
from post_ads import run

async def main():
	load_dotenv(override=True)
	
	# Get API URL from environment or use default
	base_url = os.getenv('NEXTAUTH_URL') or os.getenv('API_BASE_URL') or 'http://localhost:3000'
	api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
	
	# Check if still using localhost (development)
	if 'localhost' in base_url or '127.0.0.1' in base_url:
		print("=" * 70)
		print("⚠️  WAARSCHUWING: Je gebruikt nog localhost!")
		print("=" * 70)
		print(f"   Huidige URL: {base_url}")
		print()
		print("   Voor productie:")
		print("   1. Open het .env bestand in de rootmap")
		print("   2. Pas NEXTAUTH_URL en API_BASE_URL aan naar je productie URL")
		print("   3. Bijvoorbeeld: https://jouw-domein.vercel.app")
		print()
		print("   Doorgaan met localhost...")
		print("=" * 70)
		print()
	
	# Use the pending products endpoint
	api_url = f"{base_url}/api/products/pending?api_key={api_key}"
	
	print("=" * 70)
	print("Marktplaats Batch Posting - Alle Pending Producten")
	print("=" * 70)
	print(f"API URL: {api_url}")
	print()
	
	# First, fetch pending products to get their IDs
	try:
		response = requests.get(api_url, timeout=30, headers={'x-api-key': api_key})
		response.raise_for_status()
		pending_products = response.json()
		
		if not pending_products or len(pending_products) == 0:
			print("Geen pending producten gevonden.")
			return
		
		print(f"Gevonden {len(pending_products)} pending product(en)")
		print()
	except Exception as e:
		print(f"[ERROR] Fout bij ophalen pending producten: {e}")
		if hasattr(e, 'response') and hasattr(e.response, 'text'):
			print(f"Response: {e.response.text}")
		return
	
	# Run the main script with API URL (no product_id for batch mode)
	# This will process all products from the API
	results = await run(
		csv_path=None,
		api_url=api_url,
		product_id=None,  # None means batch mode
		login_only=False,
		keep_open=False
	)
	
	# Update all products via batch endpoint
	if results and len(results) > 0:
		# Match results to products by article_number or title
		updates = []
		for result in results:
			# Find matching product
			matching_product = None
			for product in pending_products:
				# Match by article number (most reliable)
				if result.get('article_number') and product.get('articleNumber') == result.get('article_number'):
					matching_product = product
					break
				# Match by title
				elif result.get('title') and product.get('title') == result.get('title'):
					matching_product = product
					break
			
			if matching_product:
				updates.append({
					'productId': matching_product['id'],
					'status': 'completed',
					'ad_url': result.get('ad_url'),
					'ad_id': result.get('ad_id'),
					'views': result.get('views', 0),
					'saves': result.get('saves', 0),
					'posted_at': result.get('posted_at'),
				})
		
		# Update all products via batch endpoint
		if updates:
			update_url = f"{base_url}/api/products/batch-update"
			try:
				update_response = requests.post(
					update_url,
					json={'updates': updates},
					headers={'x-api-key': api_key},
					timeout=30
				)
				if update_response.ok:
					print(f"\n[SUCCESS] {len(updates)} product(en) bijgewerkt in database")
					print(f"   Status: completed")
					print(f"   Advertenties geplaatst: {len(updates)}")
				else:
					print(f"\n[WARNING] Fout bij bijwerken producten: {update_response.status_code}")
					print(f"   Response: {update_response.text}")
			except Exception as e:
				print(f"\n[WARNING] Fout bij bijwerken producten: {e}")
		else:
			print("\n[WARNING] Geen producten gevonden om bij te werken")
	else:
		print("\n[WARNING] Geen resultaten om bij te werken")

if __name__ == "__main__":
	asyncio.run(main())

