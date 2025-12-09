"""
Scrape alle categorieën en subcategorieën van de Marktplaats hoofdpagina.
Klikt op elke categorie in de sidebar om subcategorieën te krijgen.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Set
import re


async def scrape_categories_from_homepage() -> List[Dict]:
    """
    Scrape alle categorieën van de Marktplaats hoofdpagina.
    Navigeert door de categorie sidebar en klikt op elke categorie om subcategorieën te krijgen.
    """
    categories: List[Dict] = []
    seen_paths: Set[str] = set()
    
    url = "https://www.marktplaats.nl/"
    
    async with async_playwright() as p:
        # Voor categorieën scrapen hoeven we niet ingelogd te zijn
        # Start gewoon een nieuwe browser sessie
        try:
            browser = await p.chromium.launch(
                channel="chrome",
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            print("✅ Chrome gebruikt (nieuwe sessie, niet ingelogd)")
        except Exception as e:
            print(f"⚠️ Kon Chrome niet gebruiken ({e}), val terug op Chromium...")
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            print("✅ Chromium gebruikt (nieuwe sessie)")
        
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(45000)
        
        print("=" * 70)
        print("🔍 Marktplaats Categorie Scraper - Van Hoofdpagina")
        print("=" * 70)
        print(f"\n📍 Navigeren naar: {url}")
        
        # Navigeer naar de hoofdpagina
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Accepteer cookies
        try:
            accept_buttons = [
                page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower() or "akkoord" in (n or '').lower()),
                page.locator("button:has-text('Accepteren')"),
                page.locator("button:has-text('Akkoord')"),
            ]
            for accept in accept_buttons:
                if await accept.count() > 0:
                    await accept.first.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Cookies geaccepteerd")
                    break
        except:
            pass
        
        # Wacht tot de pagina volledig geladen is
        await page.wait_for_load_state("networkidle", timeout=10000)
        await page.wait_for_timeout(2000)
        
        print("\n🔍 Zoeken naar categorie sidebar...")
        
        # Wacht op de categorie sidebar om te laden
        await page.wait_for_timeout(2000)
        
        # Zoek naar de categorie lijst in de sidebar
        # Marktplaats heeft meestal een lijst met categorieën in een nav of ul element
        main_categories = []
        
        # Methode 1: Zoek naar alle links die naar categorieën verwijzen
        try:
            # Zoek naar links met categorie namen (meestal in een nav of lijst)
            all_links = await page.locator("a").all()
            print(f"   Gevonden {len(all_links)} links op de pagina")
            
            category_names = [
                "Antiek en Kunst", "Audio, Tv en Foto", "Auto's", "Auto-onderdelen", "Auto diversen",
                "Boeken", "Caravans en Kamperen", "Cd's en Dvd's", "Computers en Software",
                "Contacten en Berichten", "Diensten en Vakmensen", "Dieren en Toebehoren",
                "Doe-het-zelf en Verbouw", "Fietsen en Brommers", "Hobby en Vrije tijd",
                "Huis en Inrichting", "Huizen en Kamers", "Kinderen en Baby's",
                "Kleding | Dames", "Kleding | Heren", "Motoren", "Muziek en Instrumenten",
                "Postzegels en Munten", "Sieraden, Tassen en Uiterlijk", "Spelcomputers en Games",
                "Sport en Fitness", "Telecommunicatie", "Tickets en Kaartjes", "Tuin en Terras",
                "Vacatures", "Vakantie", "Verzamelen", "Watersport en Boten",
                "Witgoed en Apparatuur", "Zakelijke goederen", "Diversen"
            ]
            
            for link in all_links:
                try:
                    text = await link.text_content()
                    href = await link.get_attribute("href")
                    
                    if text and text.strip() and href:
                        # Check of dit een bekende categorie naam is
                        for cat_name in category_names:
                            if cat_name.lower() in text.strip().lower() or text.strip().lower() in cat_name.lower():
                                # Check of we deze al hebben
                                if not any(c['name'] == cat_name for c in main_categories):
                                    # Maak volledige URL
                                    if href.startswith("/"):
                                        full_href = f"https://www.marktplaats.nl{href}"
                                    elif href.startswith("http"):
                                        full_href = href
                                    else:
                                        full_href = f"https://www.marktplaats.nl/{href}"
                                    
                                    main_categories.append({
                                        "name": cat_name,
                                        "href": full_href,
                                        "element": link
                                    })
                                    break
                except:
                    continue
            
            if main_categories:
                print(f"✅ Gevonden {len(main_categories)} hoofdcategorieën via link matching")
        except Exception as e:
            print(f"⚠️ Fout bij link matching: {e}")
        
        # Methode 2: Als we nog geen categorieën hebben, probeer directe tekst matching
        if not main_categories:
            print("⚠️ Geen categorieën via links gevonden, probeer directe tekst matching...")
            try:
                for cat_name in category_names:
                    try:
                        # Zoek naar element met deze tekst
                        element = page.get_by_text(cat_name, exact=False).first
                        if await element.count() > 0:
                            # Probeer href te krijgen (als het een link is)
                            try:
                                href = await element.get_attribute("href")
                                if not href:
                                    # Als het geen link is, maak een URL op basis van de naam
                                    href = f"https://www.marktplaats.nl/c/{cat_name.lower().replace(' ', '-').replace('|', '-').replace('&', 'en')}"
                            except:
                                href = f"https://www.marktplaats.nl/c/{cat_name.lower().replace(' ', '-').replace('|', '-').replace('&', 'en')}"
                            
                            main_categories.append({
                                "name": cat_name,
                                "href": href,
                                "element": element
                            })
                    except:
                        continue
                
                if main_categories:
                    print(f"✅ Gevonden {len(main_categories)} hoofdcategorieën via tekst matching")
            except Exception as e:
                print(f"⚠️ Fout bij tekst matching: {e}")
        
        if not main_categories:
            print("❌ Geen hoofdcategorieën gevonden!")
            # Probeer screenshot te maken voor debugging
            await page.screenshot(path="debug_homepage.png")
            print("📸 Screenshot opgeslagen als debug_homepage.png")
            await context.close()
            await browser.close()
            return []
        
        print(f"\n✅ Gevonden {len(main_categories)} hoofdcategorieën")
        print("\n📋 Hoofdcategorieën:")
        for cat in main_categories[:10]:  # Toon eerste 10
            print(f"   - {cat['name']}")
        if len(main_categories) > 10:
            print(f"   ... en {len(main_categories) - 10} meer")
        
        # Functie om subcategorieën te scrapen van een categorie pagina
        async def scrape_subcategories(category_name: str, category_href: str, level: int = 1, parent_id: str = None, parent_path: str = "") -> List[Dict]:
            """Scrape subcategorieën van een categorie pagina."""
            subcategories = []
            
            try:
                # Navigeer naar de categorie pagina
                full_url = category_href if category_href.startswith("http") else f"https://www.marktplaats.nl{category_href}"
                print(f"\n   📍 Navigeren naar: {category_name} ({full_url})")
                
                try:
                    await page.goto(full_url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(3000)
                except Exception as nav_error:
                    print(f"   ⚠️ Navigatie timeout, probeer networkidle...")
                    try:
                        await page.goto(full_url, wait_until="networkidle", timeout=60000)
                        await page.wait_for_timeout(2000)
                    except:
                        print(f"   ⚠️ Kan niet navigeren naar {category_name}, skip...")
                        return []
                
                # Accepteer cookies opnieuw indien nodig
                try:
                    accept = page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower())
                    if await accept.count() > 0:
                        await accept.first.click()
                        await page.wait_for_timeout(500)
                except:
                    pass
                
                try:
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except:
                    # Als networkidle te lang duurt, wacht gewoon even
                    pass
                await page.wait_for_timeout(2000)
                
                # Zoek naar subcategorie links
                subcategory_links = []
                subcategory_selectors = [
                    "a[href*='/c/']",
                    "[class*='category'] a",
                    "[class*='subcategory'] a",
                    "nav a",
                ]
                
                for selector in subcategory_selectors:
                    try:
                        links = await page.locator(selector).all()
                        for link in links:
                            try:
                                text = await link.text_content()
                                href = await link.get_attribute("href")
                                if text and text.strip() and href and ("/c/" in href or "/categorie/" in href):
                                    # Skip de hoofdcategorie zelf
                                    if text.strip().lower() != category_name.lower():
                                        subcategory_links.append({
                                            "name": text.strip(),
                                            "href": href
                                        })
                            except:
                                continue
                        if subcategory_links:
                            break
                    except:
                        continue
                
                # Maak categorie object voor de hoofdcategorie (als level 1)
                if level == 1:
                    cat_id = category_name.lower().replace(" ", "-").replace("|", "-").replace("'", "").replace(",", "").replace("&", "en")
                    cat_id = re.sub(r'[^a-z0-9-]', '', cat_id)
                    path = category_name
                    
                    if path.lower() not in seen_paths:
                        seen_paths.add(path.lower())
                        category_obj = {
                            "id": cat_id,
                            "name": category_name,
                            "level": 1,
                            "parentId": None,
                            "path": path,
                            "marktplaatsId": None,
                        }
                        subcategories.append(category_obj)
                        print(f"   ✓ {path} (Level 1)")
                
                # Verwerk subcategorieën (level 2)
                parent_cat_id = category_name.lower().replace(" ", "-").replace("|", "-").replace("'", "").replace(",", "").replace("&", "en")
                parent_cat_id = re.sub(r'[^a-z0-9-]', '', parent_cat_id)
                current_path = parent_path if parent_path else category_name
                
                for subcat in subcategory_links[:50]:  # Limiteer tot 50 subcategorieën per categorie
                    subcat_name = subcat["name"]
                    subcat_path = f"{current_path} > {subcat_name}"
                    
                    if subcat_path.lower() not in seen_paths:
                        seen_paths.add(subcat_path.lower())
                        # Clean subcat name for ID
                        clean_subcat = subcat_name.lower().replace(' ', '-').replace('|', '-').replace("'", '').replace(',', '').replace('&', 'en')
                        subcat_id = f"{parent_cat_id}-{clean_subcat}"
                        subcat_id = re.sub(r'[^a-z0-9-]', '', subcat_id)
                        
                        category_obj = {
                            "id": subcat_id,
                            "name": subcat_name,
                            "level": 2,
                            "parentId": parent_cat_id,
                            "path": subcat_path,
                            "marktplaatsId": None,
                        }
                        subcategories.append(category_obj)
                        print(f"      ✓ {subcat_path} (Level 2)")
                
            except Exception as e:
                print(f"   ⚠️ Fout bij scrapen van {category_name}: {e}")
            
            return subcategories
        
        # Scrape alle hoofdcategorieën en hun subcategorieën
        print("\n🚀 Start met scrapen van alle categorieën...")
        
        # Sla tussentijds op (elke 5 categorieën)
        for idx, main_cat in enumerate(main_categories, 1):
            print(f"\n[{idx}/{len(main_categories)}] Verwerken: {main_cat['name']}")
            subcats = await scrape_subcategories(main_cat['name'], main_cat['href'], level=1)
            categories.extend(subcats)
            
            # Tussentijds opslaan elke 5 categorieën
            if idx % 5 == 0:
                output_file = os.path.join(os.path.dirname(__file__), "..", "categories_scraped.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(categories, f, indent=2, ensure_ascii=False)
                print(f"   💾 Tussentijds opgeslagen: {len(categories)} categorieën")
            
            # Kleine pauze tussen categorieën
            await page.wait_for_timeout(1000)
        
        # Wacht even voor inspectie
        print("\n⏳ Wachten 2 seconden...")
        await page.wait_for_timeout(2000)
        
        await context.close()
        await browser.close()
    
    print(f"\n✅ Totaal {len(categories)} categorieën gescraped!")
    return categories


async def main():
    print("=" * 70)
    print("Marktplaats Categorie Scraper - Van Hoofdpagina")
    print("Scrapet alle categorieën en subcategorieën van de hoofdpagina")
    print("=" * 70)
    
    categories = await scrape_categories_from_homepage()
    
    if not categories:
        print("\n⚠️ Geen categorieën gevonden!")
        return
    
    # Sla op als JSON
    output_file = os.path.join(os.path.dirname(__file__), "..", "categories_scraped.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"✅ {len(categories)} categorieën opgeslagen in {output_file}")
    print("=" * 70)
    
    # Toon statistieken
    by_level = {}
    for cat in categories:
        level = cat["level"]
        by_level[level] = by_level.get(level, 0) + 1
    
    print("\n📊 Statistieken:")
    for level in sorted(by_level.keys()):
        print(f"  Level {level}: {by_level[level]} categorieën")
    
    # Toon voorbeelden
    print("\n📋 Voorbeelden per level:")
    for level in sorted(by_level.keys()):
        level_cats = [c for c in categories if c["level"] == level]
        print(f"\n  Level {level} (eerste 5):")
        for cat in level_cats[:5]:
            print(f"    - {cat['path']}")


if __name__ == "__main__":
    asyncio.run(main())

