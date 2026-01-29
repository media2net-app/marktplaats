#!/usr/bin/env python3
"""
Nieuwe modulaire versie van post_ads.py
Gebruikt de nieuwe marktplaats module structuur
"""
import asyncio
import argparse
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from marktplaats.main import run


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Marktplaats automator (nieuwe modulaire versie)")
    parser.add_argument("--csv", type=str, help="Path to products.csv", default=None)
    parser.add_argument("--api", type=str, help="API URL to fetch product data", default=None)
    parser.add_argument("--product-id", type=str, help="Product ID (used with --api)", default=None)
    parser.add_argument("--login", action="store_true", help="Prepare login session only")
    parser.add_argument("--keep-open", action="store_true", help="Keep browser open after run for debugging")
    args = parser.parse_args()
    return args.csv, args.api, args.product_id, args.login, args.keep_open


if __name__ == "__main__":
    csv_path, api_url, product_id, login_only, keep_open = parse_args()
    try:
        results = asyncio.run(run(csv_path, api_url, product_id, login_only, keep_open))
        if results:
            print(f"\n✅ {len(results)} product(en) verwerkt")
            completed = sum(1 for r in results if r.get('status') == 'completed')
            failed = sum(1 for r in results if r.get('status') == 'failed')
            print(f"   Geplaatst: {completed}")
            print(f"   Mislukt: {failed}")
    except KeyboardInterrupt:
        print("\n⚠️  Gestopt door gebruiker")
    except Exception as e:
        print(f"\n❌ Fout: {e}")
        sys.exit(1)
