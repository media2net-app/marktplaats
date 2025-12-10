"""
Railway Worker - Continuously monitors and posts pending products
This script runs on Railway and periodically checks for pending products
Uses Playwright directly to post to Marktplaats (not via API)
"""
import asyncio
import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # Check every 5 minutes (300 seconds)
API_BASE_URL = (os.getenv('API_BASE_URL') or os.getenv('NEXTAUTH_URL') or 'http://localhost:3000').rstrip('/')
INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')

# Add scripts directory to path for importing post_ads
sys.path.insert(0, os.path.dirname(__file__))

if not INTERNAL_API_KEY:
    print("=" * 70)
    print("❌ ERROR: INTERNAL_API_KEY not set in environment variables")
    print("=" * 70)
    print("Please set INTERNAL_API_KEY in Railway environment variables")
    print("This should match the INTERNAL_API_KEY in your Vercel app")
    print("=" * 70)
    sys.exit(1)

def check_pending_products():
    """Check how many pending products there are"""
    try:
        url = f"{API_BASE_URL}/api/products/batch-post"
        print(f"Checking pending products at: {url}", flush=True)
        response = requests.get(
            url,
            headers={'x-api-key': INTERNAL_API_KEY},
            timeout=30
        )
        print(f"Response status: {response.status_code}", flush=True)
        if response.status_code == 200:
            data = response.json()
            pending_count = data.get('pending', 0)
            print(f"API returned: pending={pending_count}, processing={data.get('processing', 0)}, completed={data.get('completed', 0)}, failed={data.get('failed', 0)}", flush=True)
            return pending_count
        else:
            error_text = response.text[:500] if response.text else "No error message"
            print(f"Error checking status: {response.status_code} - {error_text}", flush=True)
            return 0
    except Exception as e:
        print(f"Error checking pending products: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 0

async def post_pending_products_async():
    """Post all pending products using Playwright directly"""
    try:
        # Import post_ads module
        from post_ads import run as post_ads_run
        
        # Get pending products from API (without API key in URL - use header only)
        api_url = f"{API_BASE_URL}/api/products/pending"
        print(f"Fetching pending products from: {api_url}", flush=True)
        print(f"Using API key: {INTERNAL_API_KEY[:10]}... (length: {len(INTERNAL_API_KEY)})", flush=True)
        
        response = requests.get(
            api_url,
            headers={'x-api-key': INTERNAL_API_KEY},
            timeout=30
        )
        
        if response.status_code != 200:
            error_text = response.text[:500] if response.text else "No error message"
            print(f"❌ Error fetching pending products: {response.status_code} - {error_text}", flush=True)
            return False
        
        pending_products = response.json()
        if not pending_products or len(pending_products) == 0:
            print("No pending products found", flush=True)
            return True
        
        print(f"Found {len(pending_products)} pending product(s)", flush=True)
        
        # Call post_ads.py directly with API URL (without API key in URL)
        # post_ads.py will use INTERNAL_API_KEY from environment variable
        # This will use Playwright/Chromium to post to Marktplaats
        results = await post_ads_run(
            csv_path=None,
            api_url=api_url,  # URL without API key - post_ads.py will use env var
            product_id=None,  # None means batch mode
            login_only=False,
            keep_open=False
        )
        
        if results and len(results) > 0:
            # Update products via batch-update endpoint
            updates = []
            for result in results:
                # Find matching product
                matching_product = None
                for product in pending_products:
                    if result.get('article_number') and product.get('articleNumber') == result.get('article_number'):
                        matching_product = product
                        break
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
                update_url = f"{API_BASE_URL}/api/products/batch-update"
                try:
                    update_response = requests.post(
                        update_url,
                        json={'updates': updates},
                        headers={'x-api-key': INTERNAL_API_KEY},
                        timeout=30
                    )
                    if update_response.ok:
                        print(f"✅ {len(updates)} product(s) updated in database")
                    else:
                        print(f"⚠️ Error updating products: {update_response.status_code}")
                except Exception as e:
                    print(f"⚠️ Error updating products: {e}")
            
            print(f"✅ Batch posting completed: {len(results)} product(s) processed")
            return True
        else:
            print("⚠️ No results from posting")
            return False
            
    except Exception as e:
        print(f"❌ Exception during batch posting: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main_async():
    """Main worker loop (async)"""
    # Force flush to ensure logs are visible immediately
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    
    print("=" * 70, flush=True)
    print("🚂 Railway Marktplaats Worker", flush=True)
    print("=" * 70, flush=True)
    print(f"API Base URL: {API_BASE_URL}", flush=True)
    print(f"Check Interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL // 60} minutes)", flush=True)
    print(f"INTERNAL_API_KEY: {'✅ Set' if INTERNAL_API_KEY else '❌ Not set'}", flush=True)
    print("=" * 70, flush=True)
    print("", flush=True)
    
    if not INTERNAL_API_KEY:
        print("❌ ERROR: INTERNAL_API_KEY not set!", flush=True)
        print("   Please set it in Railway environment variables", flush=True)
        sys.exit(1)
    
    # Test import of post_ads
    try:
        from post_ads import run as post_ads_run
        print("✅ Successfully imported post_ads module", flush=True)
    except Exception as e:
        print(f"❌ ERROR: Failed to import post_ads: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            # Check for pending products
            pending_count = check_pending_products()
            
            if pending_count > 0:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {pending_count} pending product(s)", flush=True)
                print("Starting batch post with Playwright/Chromium...", flush=True)
                
                success = await post_pending_products_async()
                
                if success:
                    consecutive_errors = 0
                    print(f"✅ Batch posting completed. Waiting {CHECK_INTERVAL} seconds before next check...")
                else:
                    consecutive_errors += 1
                    print(f"❌ Batch posting failed ({consecutive_errors}/{max_consecutive_errors})")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"\n⚠️ Too many consecutive errors ({max_consecutive_errors}). Waiting longer before retry...")
                        await asyncio.sleep(CHECK_INTERVAL * 2)  # Wait 2x longer
                        consecutive_errors = 0
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No pending products. Waiting {CHECK_INTERVAL} seconds...", flush=True)
                consecutive_errors = 0  # Reset error count if no pending products
            
            # Wait before next check
            await asyncio.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Worker stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in worker loop: {e}")
            import traceback
            traceback.print_exc()
            consecutive_errors += 1
            
            if consecutive_errors >= max_consecutive_errors:
                print(f"⚠️ Too many errors. Waiting {CHECK_INTERVAL * 2} seconds before retry...")
                await asyncio.sleep(CHECK_INTERVAL * 2)
                consecutive_errors = 0
            else:
                await asyncio.sleep(60)  # Wait 1 minute before retry on error

def main():
    """Main entry point"""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()

