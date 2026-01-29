#!/usr/bin/env python3
"""
Monitor script om de voortgang van categorie scraping te volgen.
"""
import json
import os
import time
import sys
from datetime import datetime

def check_status():
    """Check de huidige status van het scraping proces."""
    print("=" * 70)
    print("MARKTPLAATS CATEGORIE SCRAPER - MONITOR")
    print("=" * 70)
    print(f"Tijd: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Check of script draait
    import subprocess
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'scrape_and_import' in result.stdout or 'scrape_categories_from_homepage' in result.stdout:
        print("✅ Script draait")
    else:
        print("❌ Script draait niet meer")
    
    print()
    
    # Check bestand
    if os.path.exists('categories_scraped.json'):
        mtime = os.path.getmtime('categories_scraped.json')
        age = int(time.time() - mtime)
        
        try:
            with open('categories_scraped.json', 'r') as f:
                cats = json.load(f)
            
            print(f"✅ Bestand bestaat: {len(cats)} categorieën")
            print(f"📅 Laatste update: {datetime.fromtimestamp(mtime).strftime('%H:%M:%S')} ({age}s geleden)")
            print()
            
            # Statistieken per level
            by_level = {}
            for c in cats:
                level = c.get('level', 0)
                by_level[level] = by_level.get(level, 0) + 1
            
            print("📊 Per level:")
            for level in sorted(by_level.keys()):
                print(f"   Level {level}: {by_level[level]} categorieën")
            
            # Laatste categorieën
            print()
            print("📋 Laatste 15 gescrapete categorieën:")
            for cat in cats[-15:]:
                path = cat.get('path', cat.get('name', 'Unknown'))
                level = cat.get('level', 0)
                print(f"   [{level}] {path}")
            
            # Hoofdcategorieën met meeste subcategorieën
            print()
            print("📈 Top 10 hoofdcategorieën (meeste subcategorieën):")
            by_parent = {}
            for c in cats:
                if c.get('level') == 2:
                    parent = c.get('parentId', 'Unknown')
                    by_parent[parent] = by_parent.get(parent, 0) + 1
            
            sorted_parents = sorted(by_parent.items(), key=lambda x: x[1], reverse=True)[:10]
            for parent, count in sorted_parents:
                print(f"   {parent}: {count} subcategorieën")
                
        except Exception as e:
            print(f"⚠️ Fout bij lezen bestand: {e}")
    else:
        print("⏳ Bestand nog niet aangemaakt")
        print("   Script is nog bezig met scrapen...")
        print("   Dit kan enkele minuten duren.")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        # Continue monitoring
        try:
            while True:
                os.system('clear' if os.name != 'nt' else 'cls')
                check_status()
                print("\n🔄 Volgende update over 10 seconden... (Ctrl+C om te stoppen)")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n\nMonitor gestopt.")
    else:
        # Single check
        check_status()



















