"""
Script om Marktplaats categorieën te scrapen en op te slaan.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Optional


async def scrape_categories() -> List[Dict]:
    """Scrape alle categorieën van Marktplaats."""
    categories = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Ga naar de plaats advertentie pagina
        await page.goto("https://www.marktplaats.nl/plaats", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Klik op "Of selecteer zelf een categorie"
        try:
            select_self = page.get_by_text("Of selecteer zelf een categorie", exact=False)
            if await select_self.count() > 0:
                await select_self.first.click()
                await page.wait_for_timeout(500)
        except Exception as e:
            print(f"Could not find 'select zelf categorie': {e}")
        
        # Zoek naar de categorie dropdowns
        # Meestal zijn dit select elementen of klikbare elementen
        try:
            # Probeer verschillende selectors voor categorie dropdowns
            category_selectors = [
                "select[name*='category']",
                "select[class*='category']",
                ".category-select",
                "[data-testid*='category']",
            ]
            
            # Probeer de eerste dropdown te vinden
            first_dropdown = None
            for selector in category_selectors:
                elements = await page.locator(selector).all()
                if elements:
                    first_dropdown = elements[0]
                    break
            
            if first_dropdown:
                # Klik op de dropdown om opties te tonen
                await first_dropdown.click()
                await page.wait_for_timeout(500)
                
                # Haal opties op
                options = await first_dropdown.locator("option").all()
                for option in options:
                    text = await option.text_content()
                    value = await option.get_attribute("value")
                    if text and text.strip() and value:
                        categories.append({
                            "id": value,
                            "name": text.strip(),
                            "level": 1,
                            "parentId": None,
                            "path": text.strip(),
                        })
        except Exception as e:
            print(f"Error scraping categories: {e}")
        
        # Alternatieve methode: probeer de categorie structuur te vinden via de DOM
        try:
            # Zoek naar alle mogelijke categorie links/buttons
            category_links = await page.locator("a[href*='category'], button[data-category]").all()
            for link in category_links[:50]:  # Limiteer tot eerste 50
                text = await link.text_content()
                href = await link.get_attribute("href")
                if text and text.strip():
                    categories.append({
                        "id": href or text.strip().lower().replace(" ", "-"),
                        "name": text.strip(),
                        "level": 1,
                        "parentId": None,
                        "path": text.strip(),
                    })
        except Exception as e:
            print(f"Error with alternative method: {e}")
        
        await browser.close()
    
    return categories


async def scrape_categories_manual() -> List[Dict]:
    """
    Handmatige methode: gebruik bekende Marktplaats categorie structuur.
    Deze kunnen we uitbreiden door de pagina te inspecteren.
    """
    # Basis categorieën gebaseerd op Marktplaats structuur
    categories = [
        # Level 1 - Hoofdcategorieën
        {"id": "auto", "name": "Auto's", "level": 1, "parentId": None, "path": "Auto's"},
        {"id": "huis-inrichting", "name": "Huis en Inrichting", "level": 1, "parentId": None, "path": "Huis en Inrichting"},
        {"id": "elektronica", "name": "Elektronica", "level": 1, "parentId": None, "path": "Elektronica"},
        {"id": "kleding", "name": "Kleding, Schoenen & Accessoires", "level": 1, "parentId": None, "path": "Kleding, Schoenen & Accessoires"},
        {"id": "sport", "name": "Sport & Outdoor", "level": 1, "parentId": None, "path": "Sport & Outdoor"},
        {"id": "hobby", "name": "Hobby & Vrije tijd", "level": 1, "parentId": None, "path": "Hobby & Vrije tijd"},
        {"id": "antiek", "name": "Antiek en Kunst", "level": 1, "parentId": None, "path": "Antiek en Kunst"},
        {"id": "doe-het-zelf", "name": "Doe-het-zelf en Verbouw", "level": 1, "parentId": None, "path": "Doe-het-zelf en Verbouw"},
        
        # Level 2 - Subcategorieën voor "Huis en Inrichting"
        {"id": "banken", "name": "Banken", "level": 2, "parentId": "huis-inrichting", "path": "Huis en Inrichting > Banken"},
        {"id": "tafels", "name": "Tafels", "level": 2, "parentId": "huis-inrichting", "path": "Huis en Inrichting > Tafels"},
        {"id": "stoelen", "name": "Stoelen", "level": 2, "parentId": "huis-inrichting", "path": "Huis en Inrichting > Stoelen"},
        
        # Level 2 - Subcategorieën voor "Doe-het-zelf en Verbouw"
        {"id": "isolatie", "name": "Isolatie en Afdichting", "level": 2, "parentId": "doe-het-zelf", "path": "Doe-het-zelf en Verbouw > Isolatie en Afdichting"},
        {"id": "platen-panelen", "name": "Platen en Panelen", "level": 2, "parentId": "doe-het-zelf", "path": "Doe-het-zelf en Verbouw > Platen en Panelen"},
        
        # Level 3 - Sub-subcategorieën voor "Isolatie en Afdichting"
        {"id": "isolatie-materiaal", "name": "Isolatiemateriaal", "level": 3, "parentId": "isolatie", "path": "Doe-het-zelf en Verbouw > Isolatie en Afdichting > Isolatiemateriaal"},
        
        # Level 2 - Subcategorieën voor "Antiek en Kunst"
        {"id": "antiek-eetgerei", "name": "Eetgerei", "level": 2, "parentId": "antiek", "path": "Antiek en Kunst > Eetgerei"},
        
        # Level 3 - Sub-subcategorieën voor "Eetgerei"
        {"id": "bestek", "name": "Bestek", "level": 3, "parentId": "antiek-eetgerei", "path": "Antiek en Kunst > Eetgerei > Bestek"},
    ]
    
    return categories


async def main():
    print("Scraping Marktplaats categorieën...")
    
    # Probeer eerst automatisch te scrapen
    try:
        categories = await scrape_categories()
        if not categories:
            print("Automatisch scrapen leverde geen resultaten op, gebruik handmatige lijst...")
            categories = await scrape_categories_manual()
    except Exception as e:
        print(f"Fout bij automatisch scrapen: {e}")
        print("Gebruik handmatige lijst...")
        categories = await scrape_categories_manual()
    
    # Sla op als JSON
    output_file = os.path.join(os.path.dirname(__file__), "..", "categories.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {len(categories)} categorieën opgeslagen in {output_file}")
    print("\nVoorbeelden:")
    for cat in categories[:5]:
        print(f"  - {cat['path']} (Level {cat['level']})")


if __name__ == "__main__":
    asyncio.run(main())

