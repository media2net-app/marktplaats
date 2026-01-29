#!/usr/bin/env python3
"""
Railway Worker Script
Continuously checks for pending products and processes them.
Designed to run as a background service on Railway.
"""
import asyncio
import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))
from post_ads import run

def log(message: str, level: str = "inf"):
    """Log message with timestamp and level."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    # Railway uses structured logging
    print(f"[{level}] {message}", file=sys.stderr)

async def check_and_process_pending():
    """Check for pending products and process them."""
    load_dotenv(override=True)
    
    # Get configuration
    base_url = os.getenv('NEXTAUTH_URL') or os.getenv('API_BASE_URL') or 'http://localhost:3000'
    api_key = os.getenv('INTERNAL_API_KEY') or 'internal-key-change-in-production'
    check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # Default 5 minutes
    
    log("=" * 70)
    log("🚂 Railway Marktplaats Worker")
    log("=" * 70)
    log(f"API Base URL: {base_url}")
    log(f"Check Interval: {check_interval} seconds ({check_interval // 60} minutes)")
    log(f"INTERNAL_API_KEY: {'✅ Set' if api_key != 'internal-key-change-in-production' else '⚠️ Using default'}")
    log("=" * 70)
    log("")
    
    # Verify post_ads module can be imported
    try:
        log("✅ Successfully imported post_ads module")
    except Exception as e:
        log(f"❌ Failed to import post_ads module: {e}", "err")
        return
    
    # Use the CORRECT endpoint: /api/products/pending (not batch-post)
    api_url = f"{base_url}/api/products/pending"
    
    # Headers with API key
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Query parameter as backup
    api_url_with_key = f"{api_url}?api_key={api_key}"
    
    log(f"Checking pending products at: {api_url}")
    
    while True:
        try:
            # Fetch pending products
            response = requests.get(
                api_url_with_key,
                headers=headers,
                timeout=30
            )
            
            log(f"Response status: {response.status_code}")
            
            if response.status_code == 401:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', 'Unauthorized')
                hint = error_data.get('hint', '')
                log(f"Error checking status: {response.status_code} - {error_msg}", "err")
                if hint:
                    log(f"Hint: {hint}", "err")
                log("Waiting before retry...")
                await asyncio.sleep(check_interval)
                continue
            
            if response.status_code != 200:
                log(f"Error checking status: {response.status_code} - {response.text}", "err")
                await asyncio.sleep(check_interval)
                continue
            
            # Parse response
            pending_products = response.json()
            
            if not pending_products or len(pending_products) == 0:
                log("No pending products. Waiting...")
                await asyncio.sleep(check_interval)
                continue
            
            log(f"Found {len(pending_products)} pending product(s)")
            log("Starting processing...")
            
            # Process all pending products
            results = await run(
                csv_path=None,
                api_url=api_url_with_key,
                product_id=None,  # None means batch mode
                login_only=False,
                keep_open=False
            )
            
            if results and len(results) > 0:
                log(f"Successfully processed {len(results)} product(s)")
                
                # Update products via batch endpoint
                update_url = f"{base_url}/api/products/batch-update"
                updates = []
                
                for result in results:
                    # Match result to product by article_number or title
                    matching_product = None
                    for product in pending_products:
                        if (result.get('article_number') and 
                            product.get('article_number') == result.get('article_number')):
                            matching_product = product
                            break
                        elif (result.get('title') and 
                              product.get('title') == result.get('title')):
                            matching_product = product
                            break
                    
                    if matching_product:
                        updates.append({
                            'productId': matching_product.get('id'),
                            'status': 'completed' if result.get('ad_url') else 'failed',
                            'ad_url': result.get('ad_url'),
                            'ad_id': result.get('ad_id'),
                            'views': result.get('views', 0),
                            'saves': result.get('saves', 0),
                            'posted_at': result.get('posted_at'),
                        })
                
                # Send batch update
                if updates:
                    try:
                        update_response = requests.post(
                            update_url,
                            json={'updates': updates},
                            headers=headers,
                            timeout=30
                        )
                        if update_response.ok:
                            log(f"✅ Updated {len(updates)} product(s) in database")
                        else:
                            log(f"⚠️ Failed to update products: {update_response.status_code}", "warn")
                    except Exception as e:
                        log(f"⚠️ Error updating products: {e}", "warn")
            else:
                log("No results from processing", "warn")
            
            # Wait before next check
            log(f"Waiting {check_interval} seconds before next check...")
            await asyncio.sleep(check_interval)
            
        except requests.exceptions.RequestException as e:
            log(f"Network error: {e}", "err")
            await asyncio.sleep(check_interval)
        except Exception as e:
            log(f"Unexpected error: {e}", "err")
            import traceback
            log(traceback.format_exc(), "err")
            await asyncio.sleep(check_interval)

if __name__ == "__main__":
    try:
        asyncio.run(check_and_process_pending())
    except KeyboardInterrupt:
        log("Worker stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}", "err")
        sys.exit(1)
