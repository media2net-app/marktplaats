"""
Geavanceerd script om alle Marktplaats categorieën te scrapen.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Set


async def scrape_all_categories() -> List[Dict]:
    """Scrape alle categorieën van Marktplaats door de categorie selectie pagina te bezoeken."""
    categories: List[Dict] = []
    seen_paths: Set[str] = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False om te zien wat er gebeurt
        page = await browser.new_page()
        
        print("Navigeren naar Marktplaats plaats advertentie pagina...")
        await page.goto("https://www.marktplaats.nl/plaats", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Accepteer cookies als nodig
        try:
            accept_button = page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower() or "akkoord" in (n or '').lower())
            if await accept_button.count() > 0:
                await accept_button.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass
        
        # Klik op "Of selecteer zelf een categorie"
        print("Zoeken naar categorie selectie...")
        try:
            # Probeer verschillende manieren om de categorie selectie te vinden
            selectors = [
                "text=Of selecteer zelf een categorie",
                "text=selecteer zelf",
                "[data-testid*='category']",
                ".category-select",
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.click()
                        await page.wait_for_timeout(2000)
                        clicked = True
                        print(f"✅ Categorie selectie gevonden via: {selector}")
                        break
                except:
                    continue
            
            if not clicked:
                print("⚠️ Kon categorie selectie niet vinden, probeer handmatig navigeren...")
                # Probeer direct naar categorie pagina te gaan
                await page.goto("https://www.marktplaats.nl/plaats/categorie", wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"⚠️ Fout bij openen categorie selectie: {e}")
        
        # Wacht even zodat de pagina geladen is
        await page.wait_for_timeout(2000)
        
        # Methode 1: Zoek naar alle select dropdowns
        print("Methode 1: Zoeken naar select dropdowns...")
        try:
            selects = await page.locator("select").all()
            print(f"Gevonden {len(selects)} select elementen")
            
            for idx, select in enumerate(selects):
                try:
                    # Klik op de select om opties te tonen
                    await select.click()
                    await page.wait_for_timeout(500)
                    
                    options = await select.locator("option").all()
                    for opt in options:
                        text = await opt.text_content()
                        value = await opt.get_attribute("value")
                        if text and text.strip() and value and value != "":
                            path_key = text.strip()
                            if path_key not in seen_paths and text.strip() not in ["Kies...", "Selecteer..."]:
                                seen_paths.add(path_key)
                                categories.append({
                                    "id": value or text.strip().lower().replace(" ", "-"),
                                    "name": text.strip(),
                                    "level": idx + 1,
                                    "parentId": None,  # Wordt later bepaald
                                    "path": text.strip(),
                                })
                                print(f"  - {text.strip()} (Level {idx + 1})")
                except Exception as e:
                    print(f"  ⚠️ Fout bij select {idx}: {e}")
        except Exception as e:
            print(f"⚠️ Fout bij methode 1: {e}")
        
        # Methode 2: Zoek naar categorie links/buttons in de DOM
        print("\nMethode 2: Zoeken naar categorie links...")
        try:
            # Zoek naar alle mogelijke categorie elementen
            category_elements = await page.locator("a[href*='categorie'], button[data-category], [class*='category'], [data-testid*='category']").all()
            print(f"Gevonden {len(category_elements)} mogelijke categorie elementen")
            
            for elem in category_elements[:100]:  # Limiteer tot eerste 100
                try:
                    text = await elem.text_content()
                    href = await elem.get_attribute("href")
                    data_id = await elem.get_attribute("data-id") or await elem.get_attribute("id")
                    
                    if text and text.strip() and len(text.strip()) > 2:
                        path_key = text.strip()
                        if path_key not in seen_paths:
                            seen_paths.add(path_key)
                            categories.append({
                                "id": data_id or href or text.strip().lower().replace(" ", "-"),
                                "name": text.strip(),
                                "level": 1,  # Default, wordt later bepaald
                                "parentId": None,
                                "path": text.strip(),
                            })
                            print(f"  - {text.strip()}")
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Fout bij methode 2: {e}")
        
        # Methode 3: Probeer de categorie API/JSON data te vinden
        print("\nMethode 3: Zoeken naar JSON data in de pagina...")
        try:
            # Zoek naar script tags met JSON data
            scripts = await page.locator("script[type='application/json'], script").all()
            for script in scripts:
                try:
                    content = await script.text_content()
                    if content and ("categorie" in content.lower() or "category" in content.lower()):
                        # Probeer JSON te parsen
                        if "{" in content and "}" in content:
                            # Extract JSON object
                            start = content.find("{")
                            end = content.rfind("}") + 1
                            if start >= 0 and end > start:
                                json_str = content[start:end]
                                try:
                                    data = json.loads(json_str)
                                    # Recursief zoeken naar categorie data
                                    def find_categories(obj, path=""):
                                        if isinstance(obj, dict):
                                            for key, value in obj.items():
                                                if "categorie" in key.lower() or "category" in key.lower():
                                                    if isinstance(value, (list, dict)):
                                                        print(f"  📦 Gevonden categorie data in: {path}.{key}")
                                                find_categories(value, f"{path}.{key}")
                                        elif isinstance(obj, list):
                                            for idx, item in enumerate(obj):
                                                find_categories(item, f"{path}[{idx}]")
                                    find_categories(data)
                                except:
                                    pass
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Fout bij methode 3: {e}")
        
        # Methode 4: Probeer network requests te onderscheppen
        print("\nMethode 4: Monitoring network requests...")
        category_data_found = False
        
        async def handle_response(response):
            nonlocal category_data_found
            try:
                url = response.url
                if "categorie" in url.lower() or "category" in url.lower():
                    print(f"  📡 Categorie API gevonden: {url}")
                    try:
                        data = await response.json()
                        print(f"  ✅ JSON data ontvangen van {url}")
                        # Verwerk de data
                        def extract_categories(obj, level=1, parent_id=None, parent_path=""):
                            if isinstance(obj, list):
                                for item in obj:
                                    extract_categories(item, level, parent_id, parent_path)
                            elif isinstance(obj, dict):
                                name = obj.get("name") or obj.get("title") or obj.get("label")
                                cat_id = obj.get("id") or obj.get("value") or obj.get("categoryId")
                                children = obj.get("children") or obj.get("subcategories") or []
                                
                                if name and cat_id:
                                    full_path = f"{parent_path} > {name}" if parent_path else name
                                    path_key = full_path
                                    if path_key not in seen_paths:
                                        seen_paths.add(path_key)
                                        categories.append({
                                            "id": str(cat_id),
                                            "name": name,
                                            "level": level,
                                            "parentId": str(parent_id) if parent_id else None,
                                            "path": full_path,
                                        })
                                        print(f"    - {full_path} (Level {level})")
                                
                                if children:
                                    extract_categories(children, level + 1, cat_id, full_path if name else parent_path)
                        
                        extract_categories(data)
                        category_data_found = True
                    except:
                        pass
            except:
                pass
        
        page.on("response", handle_response)
        
        # Refresh de pagina om requests te triggeren
        await page.reload(wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Als we nog geen categorieën hebben, gebruik de handmatige lijst
        if len(categories) == 0:
            print("\n⚠️ Geen categorieën gevonden via scraping, gebruik uitgebreide handmatige lijst...")
            categories = get_manual_categories()
        
        await browser.close()
    
    return categories


def get_manual_categories() -> List[Dict]:
    """Uitgebreide handmatige lijst van Marktplaats categorieën."""
    categories = []
    
    # Level 1 - Hoofdcategorieën (volledige lijst van Marktplaats)
    main_categories = [
        {"id": "auto", "name": "Auto's", "path": "Auto's"},
        {"id": "huis-inrichting", "name": "Huis en Inrichting", "path": "Huis en Inrichting"},
        {"id": "elektronica", "name": "Elektronica", "path": "Elektronica"},
        {"id": "kleding", "name": "Kleding, Schoenen & Accessoires", "path": "Kleding, Schoenen & Accessoires"},
        {"id": "sport", "name": "Sport & Outdoor", "path": "Sport & Outdoor"},
        {"id": "hobby", "name": "Hobby & Vrije tijd", "path": "Hobby & Vrije tijd"},
        {"id": "antiek", "name": "Antiek en Kunst", "path": "Antiek en Kunst"},
        {"id": "doe-het-zelf", "name": "Doe-het-zelf en Verbouw", "path": "Doe-het-zelf en Verbouw"},
        {"id": "tuin", "name": "Tuin & Terras", "path": "Tuin & Terras"},
        {"id": "dieren", "name": "Dieren en Toebehoren", "path": "Dieren en Toebehoren"},
        {"id": "kinderen", "name": "Baby's en Kinderen", "path": "Baby's en Kinderen"},
        {"id": "muziek", "name": "Muziek en Instrumenten", "path": "Muziek en Instrumenten"},
        {"id": "boeken", "name": "Boeken, Tijdschriften & Media", "path": "Boeken, Tijdschriften & Media"},
        {"id": "computers", "name": "Computers en Software", "path": "Computers en Software"},
        {"id": "telefoons", "name": "Telefoons en Toebehoren", "path": "Telefoons en Toebehoren"},
        {"id": "foto-video", "name": "Foto, Video & Optiek", "path": "Foto, Video & Optiek"},
        {"id": "games", "name": "Games en Spelcomputers", "path": "Games en Spelcomputers"},
        {"id": "sieraden", "name": "Sieraden & Tassen", "path": "Sieraden & Tassen"},
        {"id": "verzamelen", "name": "Verzamelen", "path": "Verzamelen"},
        {"id": "zakelijk", "name": "Zakelijk", "path": "Zakelijk"},
        {"id": "diensten", "name": "Diensten en Vakmensen", "path": "Diensten en Vakmensen"},
        {"id": "auto-onderdelen", "name": "Auto-onderdelen en Accessoires", "path": "Auto-onderdelen en Accessoires"},
        {"id": "motoren", "name": "Motoren", "path": "Motoren"},
        {"id": "caravans", "name": "Caravans en Kampeermateriaal", "path": "Caravans en Kampeermateriaal"},
    ]
    
    for cat in main_categories:
        categories.append({
            "id": cat["id"],
            "name": cat["name"],
            "level": 1,
            "parentId": None,
            "path": cat["path"],
        })
    
    # Level 2 - Subcategorieën voor "Huis en Inrichting"
    huis_sub = [
        {"id": "banken", "name": "Banken", "parent": "huis-inrichting"},
        {"id": "tafels", "name": "Tafels", "parent": "huis-inrichting"},
        {"id": "stoelen", "name": "Stoelen", "parent": "huis-inrichting"},
        {"id": "kasten", "name": "Kasten", "parent": "huis-inrichting"},
        {"id": "bedden", "name": "Bedden", "parent": "huis-inrichting"},
        {"id": "meubels-overig", "name": "Meubels Overig", "parent": "huis-inrichting"},
        {"id": "verlichting", "name": "Verlichting", "parent": "huis-inrichting"},
        {"id": "wonen-accessoires", "name": "Wonen & Accessoires", "parent": "huis-inrichting"},
        {"id": "keuken", "name": "Keuken", "parent": "huis-inrichting"},
        {"id": "badkamer", "name": "Badkamer", "parent": "huis-inrichting"},
        {"id": "gordijnen", "name": "Gordijnen en Raamdecoratie", "parent": "huis-inrichting"},
        {"id": "vloerkleden", "name": "Vloerkleden", "parent": "huis-inrichting"},
        {"id": "kussens", "name": "Kussens en Kussenovertrekken", "parent": "huis-inrichting"},
        {"id": "spiegels", "name": "Spiegels", "parent": "huis-inrichting"},
        {"id": "klokken", "name": "Klokken", "parent": "huis-inrichting"},
    ]
    
    for sub in huis_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Huis en Inrichting > {sub['name']}",
        })
    
    # Level 2 - Subcategorieën voor "Doe-het-zelf en Verbouw"
    diy_sub = [
        {"id": "isolatie", "name": "Isolatie en Afdichting", "parent": "doe-het-zelf"},
        {"id": "platen-panelen", "name": "Platen en Panelen", "parent": "doe-het-zelf"},
        {"id": "bouwmaterialen", "name": "Bouwmaterialen", "parent": "doe-het-zelf"},
        {"id": "gereedschap", "name": "Gereedschap", "parent": "doe-het-zelf"},
        {"id": "verf", "name": "Verf en Behang", "parent": "doe-het-zelf"},
        {"id": "sanitair", "name": "Sanitair", "parent": "doe-het-zelf"},
        {"id": "elektra", "name": "Elektra", "parent": "doe-het-zelf"},
        {"id": "vloeren", "name": "Vloeren", "parent": "doe-het-zelf"},
        {"id": "ramen-deuren", "name": "Ramen en Deuren", "parent": "doe-het-zelf"},
        {"id": "tegels", "name": "Tegels", "parent": "doe-het-zelf"},
        {"id": "hout", "name": "Hout", "parent": "doe-het-zelf"},
        {"id": "metaal", "name": "Metaal", "parent": "doe-het-zelf"},
        {"id": "beton", "name": "Beton en Cement", "parent": "doe-het-zelf"},
        {"id": "dakbedekking", "name": "Dakbedekking", "parent": "doe-het-zelf"},
    ]
    
    for sub in diy_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Doe-het-zelf en Verbouw > {sub['name']}",
        })
    
    # Level 3 - Sub-subcategorieën voor "Isolatie en Afdichting"
    isolatie_sub = [
        {"id": "isolatie-materiaal", "name": "Isolatiemateriaal", "parent": "isolatie"},
        {"id": "dakisolatie", "name": "Dakisolatie", "parent": "isolatie"},
        {"id": "muurisolatie", "name": "Muurisolatie", "parent": "isolatie"},
        {"id": "vloerisolatie", "name": "Vloerisolatie", "parent": "isolatie"},
        {"id": "afdichtingsmaterialen", "name": "Afdichtingsmaterialen", "parent": "isolatie"},
        {"id": "isolatieplaten", "name": "Isolatieplaten", "parent": "isolatie"},
        {"id": "glaswol", "name": "Glaswol", "parent": "isolatie"},
        {"id": "steenvool", "name": "Steenwol", "parent": "isolatie"},
        {"id": "hardschuim", "name": "Hardschuim (PIR)", "parent": "isolatie"},
        {"id": "piepschuim", "name": "Piepschuim (EPS)", "parent": "isolatie"},
    ]
    
    # Level 2 - Subcategorieën voor "Elektronica"
    elektronica_sub = [
        {"id": "tv", "name": "TV's", "parent": "elektronica"},
        {"id": "audio", "name": "Audio", "parent": "elektronica"},
        {"id": "huishoudelijk", "name": "Huishoudelijke Apparaten", "parent": "elektronica"},
        {"id": "klimaat", "name": "Klimaatbeheersing", "parent": "elektronica"},
    ]
    
    # Level 2 - Subcategorieën voor "Sport & Outdoor"
    sport_sub = [
        {"id": "fietsen", "name": "Fietsen", "parent": "sport"},
        {"id": "fitness", "name": "Fitness", "parent": "sport"},
        {"id": "wintersport", "name": "Wintersport", "parent": "sport"},
        {"id": "watersport", "name": "Watersport", "parent": "sport"},
        {"id": "voetbal", "name": "Voetbal", "parent": "sport"},
        {"id": "tennis", "name": "Tennis", "parent": "sport"},
    ]
    
    # Level 2 - Subcategorieën voor "Tuin & Terras"
    tuin_sub = [
        {"id": "tuinmeubelen", "name": "Tuinmeubelen", "parent": "tuin"},
        {"id": "tuingereedschap", "name": "Tuingereedschap", "parent": "tuin"},
        {"id": "planten", "name": "Planten", "parent": "tuin"},
        {"id": "tuinverlichting", "name": "Tuinverlichting", "parent": "tuin"},
    ]
    
    for sub in isolatie_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 3,
            "parentId": sub["parent"],
            "path": f"Doe-het-zelf en Verbouw > Isolatie en Afdichting > {sub['name']}",
        })
    
    # Level 2 - Subcategorieën voor "Antiek en Kunst"
    antiek_sub = [
        {"id": "antiek-eetgerei", "name": "Eetgerei", "parent": "antiek"},
        {"id": "antiek-meubels", "name": "Meubels", "parent": "antiek"},
        {"id": "kunst", "name": "Kunst", "parent": "antiek"},
        {"id": "antiek-overig", "name": "Antiek Overig", "parent": "antiek"},
    ]
    
    for sub in antiek_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Antiek en Kunst > {sub['name']}",
        })
    
    # Level 3 - Sub-subcategorieën voor "Eetgerei"
    eetgerei_sub = [
        {"id": "bestek", "name": "Bestek", "parent": "antiek-eetgerei"},
        {"id": "servies", "name": "Servies", "parent": "antiek-eetgerei"},
        {"id": "glaswerk", "name": "Glaswerk", "parent": "antiek-eetgerei"},
    ]
    
    for sub in eetgerei_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 3,
            "parentId": sub["parent"],
            "path": f"Antiek en Kunst > Eetgerei > {sub['name']}",
        })
    
    # Voeg alle nieuwe subcategorieën toe
    for sub in elektronica_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Elektronica > {sub['name']}",
        })
    
    for sub in sport_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Sport & Outdoor > {sub['name']}",
        })
    
    for sub in tuin_sub:
        categories.append({
            "id": sub["id"],
            "name": sub["name"],
            "level": 2,
            "parentId": sub["parent"],
            "path": f"Tuin & Terras > {sub['name']}",
        })
    
    return categories


async def main():
    print("=" * 60)
    print("Marktplaats Categorie Scraper - Geavanceerde Versie")
    print("=" * 60)
    
    categories = await scrape_all_categories()
    
    # Sla op als JSON
    output_file = os.path.join(os.path.dirname(__file__), "..", "categories.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ {len(categories)} categorieën opgeslagen in {output_file}")
    print("=" * 60)
    
    # Toon statistieken
    by_level = {}
    for cat in categories:
        level = cat["level"]
        by_level[level] = by_level.get(level, 0) + 1
    
    print("\n📊 Statistieken:")
    for level in sorted(by_level.keys()):
        print(f"  Level {level}: {by_level[level]} categorieën")
    
    print("\n📋 Voorbeelden:")
    for cat in categories[:10]:
        print(f"  - {cat['path']} (Level {cat['level']})")


if __name__ == "__main__":
    asyncio.run(main())

