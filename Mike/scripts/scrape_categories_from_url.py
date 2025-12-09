"""
Scrape alle categorieën van Marktplaats vanaf de plaats advertentie pagina.
Gebruikt de specifieke URL waar de gebruiker ingelogd is.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from typing import Dict, List, Set


async def scrape_categories_from_url() -> List[Dict]:
    """Scrape alle categorieën van de specifieke Marktplaats URL."""
    categories: List[Dict] = []
    seen_paths: Set[str] = set()
    
    url = "https://www.marktplaats.nl/plaats?_gl=1*118k9bk*_gcl_au*MTQyNzI5MDQ0NC4xNzU5OTAwOTIw*_ga*MTA1OTcwMzM4MS4xNzU5OTAwOTE3*_ga_YECTZ2BX2K*czE3NjQzMjQ5MzIkbzQkZzEkdDE3NjQzMjc1MTYkajU5JGwwJGg5NTUzMDk5NDQ.*_fplc*NHJuY0poWjBZZ1JzcEFjbm1pQ3g5NGY1bjBlV1NWUFViQ3RKUEZYMjBqOEhiTWEzS0piTVdRbEZyQ0JtbEhCTDQlMkYxazElMkZqJTJGdWxZWDNrVGptOE9xUlR1MnRaaFJMc00lMkYwMHVQVjklMkZvdHV2bENQVjclMkY3NmZuQTA5SVl1WXB3JTNEJTNE"
    
    async with async_playwright() as p:
        # Gebruik dezelfde persistent context als post_ads.py om ingelogd te blijven
        user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # Zichtbaar zodat we kunnen zien wat er gebeurt
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = await browser.new_page()
        
        # Verhoog timeouts voor betere stabiliteit
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(45000)
        
        # Gebruik dezelfde login logica als post_ads.py
        base_url = "https://www.marktplaats.nl"
        
        # Zorg eerst dat we ingelogd zijn (zelfde als post_ads.py)
        print("🔐 Controleren of we ingelogd zijn...")
        for attempt in range(2):
            try:
                await page.goto(f"{base_url}/", wait_until="domcontentloaded")
                break
            except Exception:
                if attempt == 1:
                    raise
                await page.wait_for_timeout(1500)
        
        # Accepteer cookies als banner verschijnt (zelfde als post_ads.py)
        try:
            accept = page.get_by_role("button", name=lambda n: "accepte" in (n or '').lower() or "akkoord" in (n or '').lower())
            if await accept.count() > 0:
                await accept.first.click()
                await page.wait_for_timeout(1000)
                print("✅ Cookies geaccepteerd")
        except Exception:
            pass
        
        print("Navigeren naar Marktplaats plaats advertentie pagina...")
        # Gebruik dezelfde URL structuur als post_ads.py
        await page.goto(f"{base_url}/plaats", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        print("\n🔍 Zoeken naar categorie dropdowns...")
        
        # Screenshot maken voor debugging
        await page.screenshot(path="debug_page.png")
        print("📸 Screenshot opgeslagen als debug_page.png")
        
        # Methode 1: Zoek naar "Of selecteer zelf een categorie" en klik erop
        print("🔍 Zoeken naar 'Of selecteer zelf een categorie'...")
        try:
            # Wacht op de pagina om volledig te laden
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            select_self_text = page.get_by_text("Of selecteer zelf een categorie", exact=False)
            if await select_self_text.count() > 0:
                await select_self_text.first.scroll_into_view_if_needed()
                await select_self_text.first.click()
                await page.wait_for_timeout(3000)
                print("✅ 'Selecteer zelf categorie' geklikt")
            else:
                # Probeer alternatieve teksten
                alt_texts = [
                    "selecteer zelf",
                    "zelf een categorie",
                    "categorie selecteren",
                ]
                clicked = False
                for alt in alt_texts:
                    elem = page.get_by_text(alt, exact=False)
                    if await elem.count() > 0:
                        await elem.first.scroll_into_view_if_needed()
                        await elem.first.click()
                        await page.wait_for_timeout(3000)
                        print(f"✅ '{alt}' geklikt")
                        clicked = True
                        break
                if not clicked:
                    print("⚠️ Kon 'selecteer zelf categorie' niet vinden")
        except Exception as e:
            print(f"⚠️ Fout bij zoeken naar categorie selectie: {e}")
        
        # Wacht tot dropdowns geladen zijn
        await page.wait_for_timeout(3000)
        
        # Methode 2: Zoek naar alle select dropdowns voor categorieën
        print("\n📋 Methode 1: Zoeken naar select dropdowns...")
        try:
            # Wacht op select elementen die mogelijk dynamisch worden geladen
            try:
                await page.wait_for_selector("select", timeout=5000)
            except:
                pass
            
            # Zoek naar alle select elementen (ook verborgen)
            selects = await page.locator("select").all()
            print(f"Gevonden {len(selects)} select elementen")
            
            # Probeer ook dropdowns die mogelijk niet als <select> zijn geïmplementeerd
            dropdowns = await page.locator(".hz-Dropdown, [class*='dropdown'], [class*='Dropdown'], [role='combobox'], select.hz-Dropdown-input").all()
            print(f"Gevonden {len(dropdowns)} dropdown elementen")
            
            # Probeer specifiek de categorie dropdowns te vinden
            category_selects = await page.locator("select[name*='category'], select[name*='Category'], select[id*='category'], select.hz-Dropdown-input").all()
            print(f"Gevonden {len(category_selects)} categorie select elementen")
            
            for idx, select in enumerate(selects):
                try:
                    # Klik op de select om opties te tonen
                    await select.scroll_into_view_if_needed()
                    await select.click()
                    await page.wait_for_timeout(500)
                    
                    # Haal alle opties op
                    options = await select.locator("option").all()
                    print(f"  Select {idx + 1}: {len(options)} opties gevonden")
                    
                    for opt_idx, opt in enumerate(options):
                        text = await opt.text_content()
                        value = await opt.get_attribute("value")
                        
                        if text and text.strip() and value and value != "":
                            # Skip placeholder opties
                            if text.strip().lower() in ["kies...", "selecteer...", "choose...", ""]:
                                continue
                            
                            path_key = f"{idx}_{text.strip()}"
                            if path_key not in seen_paths:
                                seen_paths.add(path_key)
                                categories.append({
                                    "id": value or f"cat-{idx}-{opt_idx}",
                                    "name": text.strip(),
                                    "level": idx + 1,
                                    "parentId": None,  # Wordt later bepaald
                                    "path": text.strip(),
                                })
                                print(f"    ✓ {text.strip()} (Level {idx + 1})")
                except Exception as e:
                    print(f"  ⚠️ Fout bij select {idx + 1}: {e}")
        except Exception as e:
            print(f"⚠️ Fout bij methode 1: {e}")
        
        # Methode 3: Zoek naar categorie elementen in de DOM
        print("\n📋 Methode 2: Zoeken naar categorie elementen in DOM...")
        try:
            # Zoek naar verschillende mogelijke categorie selectors
            selectors = [
                "[class*='category']",
                "[data-category]",
                "[data-testid*='category']",
                ".hz-Dropdown",
                "select[name*='category']",
            ]
            
            for selector in selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        print(f"  Gevonden {len(elements)} elementen met selector: {selector}")
                        for elem in elements[:20]:  # Limiteer tot eerste 20
                            try:
                                text = await elem.text_content()
                                if text and text.strip() and len(text.strip()) > 2:
                                    path_key = text.strip()
                                    if path_key not in seen_paths and text.strip().lower() not in ["kies...", "selecteer..."]:
                                        seen_paths.add(path_key)
                                        categories.append({
                                            "id": f"dom-{len(categories)}",
                                            "name": text.strip(),
                                            "level": 1,
                                            "parentId": None,
                                            "path": text.strip(),
                                        })
                            except:
                                continue
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Fout bij methode 2: {e}")
        
        # Methode 4: Probeer JavaScript uit te voeren om categorie data te krijgen
        print("\n📋 Methode 3: JavaScript extractie...")
        try:
            # Probeer categorie data uit de pagina te halen via JavaScript
            category_data = await page.evaluate("""
                () => {
                    const categories = [];
                    
                    // Zoek naar alle select elementen
                    document.querySelectorAll('select').forEach((select, idx) => {
                        const options = Array.from(select.options);
                        options.forEach(opt => {
                            if (opt.value && opt.text && opt.text.trim() && 
                                !opt.text.toLowerCase().includes('kies') &&
                                !opt.text.toLowerCase().includes('selecteer') &&
                                !opt.text.toLowerCase().includes('choose')) {
                                categories.push({
                                    level: idx + 1,
                                    name: opt.text.trim(),
                                    value: opt.value,
                                    selectIndex: idx
                                });
                            }
                        });
                    });
                    
                    // Zoek ook naar dropdown items in custom dropdowns
                    document.querySelectorAll('[class*="dropdown"], [class*="Dropdown"], [role="option"]').forEach((elem, idx) => {
                        const text = elem.textContent?.trim();
                        if (text && text.length > 2 && 
                            !text.toLowerCase().includes('kies') &&
                            !text.toLowerCase().includes('selecteer')) {
                            categories.push({
                                level: 1,
                                name: text,
                                value: elem.getAttribute('value') || elem.getAttribute('data-value') || text.toLowerCase().replace(/\s+/g, '-'),
                                selectIndex: -1
                            });
                        }
                    });
                    
                    // Zoek naar categorie data in window object of React state
                    if (window.__NEXT_DATA__) {
                        const nextData = window.__NEXT_DATA__;
                        // Probeer categorie data te vinden in Next.js data
                        const dataStr = JSON.stringify(nextData);
                        if (dataStr.includes('categorie') || dataStr.includes('category')) {
                            console.log('Found category data in __NEXT_DATA__');
                        }
                    }
                    
                    return categories;
                }
            """)
            
            if category_data:
                print(f"  ✅ {len(category_data)} categorieën gevonden via JavaScript")
                for cat in category_data:
                    path_key = f"js-{cat['level']}-{cat['name']}"
                    if path_key not in seen_paths:
                        seen_paths.add(path_key)
                        categories.append({
                            "id": cat.get("value") or f"js-{cat['level']}-{len(categories)}",
                            "name": cat["name"],
                            "level": cat["level"],
                            "parentId": None,
                            "path": cat["name"],
                        })
        except Exception as e:
            print(f"⚠️ Fout bij methode 3: {e}")
        
        # Wacht even zodat we kunnen zien wat er gebeurt
        print("\n⏳ Wachten 5 seconden voor inspectie...")
        await page.wait_for_timeout(5000)
        
        await browser.close()
    
    # Organiseer categorieën per level en maak hiërarchie
    print("\n🔧 Organiseren van categorieën...")
    organized = organize_categories(categories)
    
    return organized


def organize_categories(categories: List[Dict]) -> List[Dict]:
    """Organiseer categorieën in hiërarchische structuur."""
    # Groepeer per level
    by_level = {}
    for cat in categories:
        level = cat["level"]
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(cat)
    
    # Maak parent-child relaties
    organized = []
    
    # Level 1 categorieën (hoofdcategorieën)
    for cat in by_level.get(1, []):
        organized.append(cat)
    
    # Level 2 categorieën (subcategorieën)
    for cat in by_level.get(2, []):
        # Probeer parent te vinden op basis van naam of context
        # Voor nu zetten we parentId op None, kan later worden aangepast
        organized.append(cat)
    
    # Level 3 categorieën (sub-subcategorieën)
    for cat in by_level.get(3, []):
        organized.append(cat)
    
    return organized


async def main():
    print("=" * 70)
    print("Marktplaats Categorie Scraper - Van Specifieke URL")
    print("=" * 70)
    
    categories = await scrape_categories_from_url()
    
    if not categories:
        print("\n⚠️ Geen categorieën gevonden. Gebruik handmatige lijst...")
        from scrape_categories_advanced import get_manual_categories
        categories = get_manual_categories()
    
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
    
    print("\n📋 Voorbeelden (eerste 15):")
    for cat in categories[:15]:
        print(f"  - {cat['path']} (Level {cat['level']})")


if __name__ == "__main__":
    asyncio.run(main())

