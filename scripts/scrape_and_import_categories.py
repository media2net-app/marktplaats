"""
Complete workflow: Scrape categorieën van Marktplaats en importeer ze direct naar de database.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Import de scraper en importer
from scrape_categories_from_homepage import scrape_categories_from_homepage
from import_categories_to_db import import_categories_to_db


async def main():
    load_dotenv()
    
    print("=" * 70)
    print("Marktplaats Categorie Scraper & Importer")
    print("Scrapet categorieën en importeert ze direct naar de database")
    print("=" * 70)
    print()
    
    # Stap 1: Scrape categorieën
    print("📋 Stap 1: Scrapen van categorieën van Marktplaats...")
    print("-" * 70)
    categories = await scrape_categories_from_homepage()
    
    if not categories or len(categories) == 0:
        print("\n❌ Geen categorieën gescraped. Stoppen.")
        return
    
    print(f"\n✅ {len(categories)} categorieën gescraped")
    
    # Stap 2: Import naar database
    print("\n📤 Stap 2: Importeren naar database...")
    print("-" * 70)
    
    # Gebruik de gescrapete categorieën direct (niet via JSON bestand)
    import json
    import tempfile
    import requests
    
    # Maak tijdelijk JSON bestand
    temp_file = os.path.join(tempfile.gettempdir(), "marktplaats_categories_temp.json")
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)
    
    try:
        # Import via de import functie
        import_categories_to_db(temp_file)
    finally:
        # Verwijder tijdelijk bestand
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\n✅ Klaar!")


if __name__ == "__main__":
    asyncio.run(main())



















