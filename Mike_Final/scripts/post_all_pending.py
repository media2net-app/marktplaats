"""
Script to post all pending products from the database via API.
This replaces the old CSV-based batch processing.
"""
import asyncio
import os
import sys
import requests
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
	try:
		sys.stdout.reconfigure(encoding='utf-8')
	except:
		pass

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))
from post_ads import run

async def main():
	# Find .env file - look in script directory and parent directory
	script_dir = os.path.dirname(os.path.abspath(__file__))
	parent_dir = os.path.dirname(script_dir)
	env_paths = [
		os.path.join(parent_dir, '.env'),  # .env in root (where run_marktplaats.bat is)
		os.path.join(script_dir, '.env'),   # .env in scripts folder
		os.path.join(os.getcwd(), '.env'),  # .env in current working directory
	]
	
	env_loaded = False
	loaded_from = None
	for env_path in env_paths:
		if os.path.exists(env_path):
			load_dotenv(env_path, override=True)
			env_loaded = True
			loaded_from = env_path
			print(f"[DEBUG] .env geladen van: {env_path}")
			break
	
	# If no .env found, try default location
	if not env_loaded:
		load_dotenv(override=True)
		print("[DEBUG] Geen .env bestand gevonden op verwachte locaties:")
		for env_path in env_paths:
			print(f"  - {env_path} {'✓' if os.path.exists(env_path) else '✗ (niet gevonden)'}")
		print("[DEBUG] Probeer default load_dotenv()...")
	
	# Get API URL from environment or use default
	nextauth_url = os.getenv('NEXTAUTH_URL')
	api_base_url = os.getenv('API_BASE_URL')
	base_url = nextauth_url or api_base_url or 'http://localhost:3000'
	api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
	
	# Always show debug output to help troubleshoot
	print(f"[DEBUG] NEXTAUTH_URL uit .env: {nextauth_url}")
	print(f"[DEBUG] API_BASE_URL uit .env: {api_base_url}")
	print(f"[DEBUG] base_url (gebruikt): {base_url}")
	print(f"[DEBUG] INTERNAL_API_KEY aanwezig: {'Ja' if api_key != 'internal-key-change-in-production' else 'Nee (gebruikt default)'}")
	print()
	
	# Check if still using localhost (development)
	if 'localhost' in base_url or '127.0.0.1' in base_url:
		print("=" * 70)
		print("WAARSCHUWING: Je gebruikt nog localhost!")
		print("=" * 70)
		print(f"Huidige URL: {base_url}")
		print()
		print("Dit script werkt alleen met een LIVE productie URL!")
		print()
		print("STAP 1: Open het .env bestand in deze map")
		print("STAP 2: Pas de volgende regels aan:")
		print("   NEXTAUTH_URL=https://jouw-domein.vercel.app")
		print("   API_BASE_URL=https://jouw-domein.vercel.app")
		print("   INTERNAL_API_KEY=jouw-api-key")
		print()
		print("STAP 3: Vervang 'jouw-domein.vercel.app' door je echte Vercel URL")
		print("        (bijvoorbeeld: https://marktplaats-eight.vercel.app)")
		print()
		print("STAP 4: Vervang 'jouw-api-key' door je echte INTERNAL_API_KEY")
		print("        (deze staat in je Vercel environment variables)")
		print()
		print("=" * 70)
		print("SCRIPT GESTOPT - Pas eerst je .env bestand aan!")
		print("=" * 70)
		input("\nDruk op Enter om af te sluiten...")
		sys.exit(1)
	
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

