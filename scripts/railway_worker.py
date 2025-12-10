"""
Railway Worker - Continuously monitors and posts pending products
This script runs on Railway and periodically checks for pending products
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
API_BASE_URL = os.getenv('API_BASE_URL') or os.getenv('NEXTAUTH_URL') or 'http://localhost:3000'
INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY')

if not INTERNAL_API_KEY:
    print("ERROR: INTERNAL_API_KEY not set in environment variables")
    sys.exit(1)

def check_pending_products():
    """Check how many pending products there are"""
    try:
        url = f"{API_BASE_URL}/api/products/batch-post"
        response = requests.get(
            url,
            headers={'x-api-key': INTERNAL_API_KEY},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('pending', 0)
        else:
            print(f"Error checking status: {response.status_code}")
            return 0
    except Exception as e:
        print(f"Error checking pending products: {e}")
        return 0

def post_pending_products():
    """Post all pending products via batch endpoint"""
    try:
        url = f"{API_BASE_URL}/api/products/batch-post"
        print(f"Calling batch post endpoint: {url}")
        
        response = requests.post(
            url,
            headers={'x-api-key': INTERNAL_API_KEY},
            timeout=600  # 10 minutes timeout for batch posting
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch posting result: {data.get('message', 'Success')}")
            print(f"   Processed: {data.get('processed', 0)}")
            print(f"   Results: {len(data.get('results', []))}")
            print(f"   Errors: {len(data.get('errors', []))}")
            
            if data.get('errors'):
                print("\n⚠️ Errors:")
                for error in data.get('errors', [])[:5]:  # Show first 5 errors
                    print(f"   - {error.get('title', 'Unknown')}: {error.get('error', 'Unknown error')}")
            
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"❌ Error posting products: {response.status_code}")
            print(f"   {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Exception during batch posting: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main worker loop"""
    print("=" * 70)
    print("🚂 Railway Marktplaats Worker")
    print("=" * 70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds ({CHECK_INTERVAL // 60} minutes)")
    print(f"INTERNAL_API_KEY: {'✅ Set' if INTERNAL_API_KEY else '❌ Not set'}")
    print("=" * 70)
    print()
    
    if not INTERNAL_API_KEY:
        print("❌ ERROR: INTERNAL_API_KEY not set!")
        print("   Please set it in Railway environment variables")
        sys.exit(1)
    
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            # Check for pending products
            pending_count = check_pending_products()
            
            if pending_count > 0:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Found {pending_count} pending product(s)")
                print("Starting batch post...")
                
                success = post_pending_products()
                
                if success:
                    consecutive_errors = 0
                    print(f"✅ Batch posting completed. Waiting {CHECK_INTERVAL} seconds before next check...")
                else:
                    consecutive_errors += 1
                    print(f"❌ Batch posting failed ({consecutive_errors}/{max_consecutive_errors})")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        print(f"\n⚠️ Too many consecutive errors ({max_consecutive_errors}). Waiting longer before retry...")
                        time.sleep(CHECK_INTERVAL * 2)  # Wait 2x longer
                        consecutive_errors = 0
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No pending products. Waiting {CHECK_INTERVAL} seconds...")
                consecutive_errors = 0  # Reset error count if no pending products
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
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
                time.sleep(CHECK_INTERVAL * 2)
                consecutive_errors = 0
            else:
                time.sleep(60)  # Wait 1 minute before retry on error

if __name__ == '__main__':
    main()

