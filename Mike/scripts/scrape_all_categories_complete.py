"""
Complete categorie scraper die ALLE categorieën, subcategorieën en sub-subcategorieën scrapet
door interactief door de Marktplaats dropdowns te navigeren.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Optional, Set


async def scrape_all_categories_complete() -> List[Dict]:
    """
    Scrape alle categorieën door recursief door alle dropdowns te navigeren.
    """
    categories: List[Dict] = []
    seen_paths: Set[str] = set()
    
    # URL van de gebruiker
    url = "https://www.marktplaats.nl/plaats?_gl=1*jfec9j*_gcl_au*ODM2Nzk2NDgwLjE3NjAzOTAwMTY.*_ga*OTM2MDI3NjIuMTc2MDM5MDAxNA..*_ga_YECTZ2BX2K*czE3NjQzNDE1MzQkbzckZzEkdDE3NjQzNDM3OTIkajQzJGwwJGg1ODYzODY4OTY.*_fplc*diUyRiUyQkhGY0lLOVlDN1YxTFhsd1NCbFlhNElHUUVBaEhmejF2eHF0blZLWkdPOTN3S3hGZ0ZtaTBKNmglMkJzQnlmJTJCUWVVJTJCcVclMkJnZHBzalNpcklGQkFBdXFyJTJGV0RNRFg3YU8zVEpiNm0yRW5XYkV0UTJmVWNzS3pxZHUlMkJXVmcyQSUzRCUzRA.."
    
    async with async_playwright() as p:
        # Gebruik Chrome in plaats van Chromium (gebruiker is al ingelogd in Chrome)
        # Op macOS: ~/Library/Application Support/Google/Chrome
        chrome_user_data = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        
        # Probeer eerst Chrome te gebruiken met de default user data
        try:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=chrome_user_data,  # Gebruik Chrome's user data (waar je al ingelogd bent)
                channel="chrome",  # Gebruik Chrome in plaats van Chromium
                headless=False,  # Zichtbaar zodat we kunnen zien wat er gebeurt
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
            print("✅ Chrome gebruikt (met ingelogde sessie)")
        except Exception as e:
            print(f"⚠️ Kon Chrome niet gebruiken met user_data ({e})")
            print("   Probeer Chrome zonder user_data directory...")
            try:
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=None,  # Laat Playwright een nieuwe context maken
                    channel="chrome",  # Gebruik Chrome
                    headless=False,
                    viewport={"width": 1280, "height": 900},
                    args=["--disable-blink-features=AutomationControlled"],
                )
                print("✅ Chrome gebruikt (nieuwe sessie)")
            except Exception as e2:
                print(f"⚠️ Kon Chrome niet gebruiken ({e2}), val terug op Chromium...")
                # Fallback naar Chromium met user_data directory
                user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    viewport={"width": 1280, "height": 900},
                    args=["--disable-blink-features=AutomationControlled"],
                )
                print("✅ Chromium gebruikt (met user_data directory)")
        page = await browser.new_page()
        
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(45000)
        
        print("=" * 70)
        print("🔍 Marktplaats Complete Categorie Scraper")
        print("=" * 70)
        print(f"\n📍 Navigeren naar: {url}")
        
        # Navigeer naar de pagina
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Accepteer cookies
        try:
            accept = page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower() or "akkoord" in (n or '').lower())
            if await accept.count() > 0:
                await accept.first.click()
                await page.wait_for_timeout(1000)
                print("✅ Cookies geaccepteerd")
        except:
            pass
        
        # Wacht tot de pagina volledig geladen is
        await page.wait_for_load_state("networkidle", timeout=10000)
        await page.wait_for_timeout(2000)
        
        # Zoek naar "Of selecteer zelf een categorie" en klik erop
        print("\n🔍 Zoeken naar categorie selectie...")
        try:
            select_self = page.get_by_text("Of selecteer zelf een categorie", exact=False)
            if await select_self.count() > 0:
                await select_self.first.scroll_into_view_if_needed()
                await select_self.first.click()
                await page.wait_for_timeout(2000)
                print("✅ 'Selecteer zelf categorie' geklikt")
            else:
                # Probeer alternatieve teksten
                for alt_text in ["selecteer zelf", "zelf een categorie"]:
                    elem = page.get_by_text(alt_text, exact=False)
                    if await elem.count() > 0:
                        await elem.first.scroll_into_view_if_needed()
                        await elem.first.click()
                        await page.wait_for_timeout(2000)
                        print(f"✅ '{alt_text}' geklikt")
                        break
        except Exception as e:
            print(f"⚠️ Fout bij klikken op categorie selectie: {e}")
        
        await page.wait_for_timeout(2000)
        
        # Zoek naar alle categorie dropdowns
        print("\n📋 Zoeken naar categorie dropdowns...")
        
        # Wacht op dropdowns om te laden
        try:
            await page.wait_for_selector("select", timeout=5000)
        except:
            pass
        
        # Vind alle select elementen (categorie dropdowns)
        selects = await page.locator("select").all()
        print(f"✅ Gevonden {len(selects)} categorie dropdown(s)")
        
        if len(selects) == 0:
            print("⚠️ Geen select dropdowns gevonden. Probeer alternatieve methoden...")
            # Probeer custom dropdowns
            dropdowns = await page.locator("[class*='Dropdown'], [class*='dropdown'], [role='combobox']").all()
            print(f"Gevonden {len(dropdowns)} alternatieve dropdowns")
            if len(dropdowns) > 0:
                selects = dropdowns
        
        if len(selects) == 0:
            print("❌ Geen categorie dropdowns gevonden!")
            await browser.close()
            return []
        
        # Functie om opties van een select te krijgen
        async def get_select_options(select, select_index: int) -> List[tuple]:
            """Haal alle geldige opties van een select op."""
            try:
                await select.scroll_into_view_if_needed()
                await page.wait_for_timeout(300)
                
                # Klik op de select
                await select.click()
                await page.wait_for_timeout(500)
                
                # Haal alle opties op
                options = await select.locator("option").all()
                
                valid_options = []
                for opt in options:
                    text = await opt.text_content()
                    value = await opt.get_attribute("value")
                    if (text and text.strip() and 
                        value and value != "" and 
                        text.strip().lower() not in ["kies...", "selecteer...", "choose...", "", "---", "selecteer"]):
                        valid_options.append((text.strip(), value))
                
                return valid_options
            except Exception as e:
                print(f"   ⚠️ Fout bij ophalen opties van dropdown {select_index + 1}: {e}")
                return []
        
        # Haal eerst alle opties van alle dropdowns op
        print("\n📋 Ophalen van alle opties per dropdown...")
        all_options = []
        for idx, select in enumerate(selects):
            options = await get_select_options(select, idx)
            all_options.append(options)
            print(f"   Dropdown {idx + 1}: {len(options)} opties")
        
        # Recursieve functie om alle combinaties te doorlopen
        async def scrape_combinations(select_index: int, current_path: List[str], current_ids: List[str], level: int = 1):
            """Recursief scrape alle combinaties van categorieën."""
            if select_index >= len(selects):
                return
            
            select = selects[select_index]
            options = all_options[select_index]
            
            if not options:
                return
            
            print(f"\n📂 Level {level} - Dropdown {select_index + 1}: {len(options)} opties")
            
            for opt_text, opt_value in options:
                # Maak nieuwe path en IDs
                new_path = current_path + [opt_text]
                full_path = " > ".join(new_path)
                path_key = full_path.lower()
                
                # Skip als we deze al hebben gezien
                if path_key in seen_paths:
                    continue
                
                seen_paths.add(path_key)
                
                # Maak categorie ID
                cat_id = opt_value or opt_text.lower().replace(" ", "-").replace("&", "en")
                parent_id = current_ids[-1] if current_ids else None
                
                category = {
                    "id": cat_id,
                    "name": opt_text,
                    "level": level,
                    "parentId": parent_id,
                    "path": full_path,
                    "marktplaatsId": opt_value if opt_value and opt_value.isdigit() else None,
                }
                
                categories.append(category)
                print(f"   ✓ {full_path} (Level {level})")
                
                # Selecteer deze optie
                try:
                    await select.scroll_into_view_if_needed()
                    await select.select_option(value=opt_value)
                    await page.wait_for_timeout(1500)  # Wacht tot volgende dropdown laadt/update
                    
                    # Controleer of er een volgende dropdown is
                    if select_index + 1 < len(selects):
                        # Haal opties van volgende dropdown opnieuw op (mogelijk zijn ze veranderd)
                        next_select = selects[select_index + 1]
                        next_options = await get_select_options(next_select, select_index + 1)
                        
                        if next_options:
                            # Update all_options voor volgende dropdown
                            all_options[select_index + 1] = next_options
                            
                            # Recursief scrape volgende level
                            await scrape_combinations(
                                select_index + 1,
                                new_path,
                                current_ids + [cat_id],
                                level + 1
                            )
                except Exception as e:
                    print(f"   ⚠️ Fout bij selecteren '{opt_text}': {e}")
                    continue
        
        # Start met het eerste dropdown (level 1)
        print("\n🚀 Start met scrapen van alle categorie combinaties...")
        await scrape_combinations(0, [], [], 1)
        
        # Wacht even voor inspectie
        print("\n⏳ Wachten 3 seconden voor inspectie...")
        await page.wait_for_timeout(3000)
        
        await browser.close()
    
    print(f"\n✅ Totaal {len(categories)} categorieën gescraped!")
    return categories


async def main():
    print("=" * 70)
    print("Marktplaats Complete Categorie Scraper")
    print("Scrapet ALLE categorieën, subcategorieën en sub-subcategorieën")
    print("=" * 70)
    
    categories = await scrape_all_categories_complete()
    
    if not categories:
        print("\n⚠️ Geen categorieën gevonden!")
        return
    
    # Sla op als JSON
    output_file = os.path.join(os.path.dirname(__file__), "..", "categories.json")
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

