"""
Form filler module voor Marktplaats advertentie formulier
Vult stap-voor-stap het formulier in
"""
import os
from typing import Optional
from playwright.async_api import Page

from .utils import (
    log_step, log_error, log_success, log_warning,
    WAIT_SHORT, WAIT_MEDIUM, WAIT_LONG, VERBOSE, Product, normalize_price
)


class FormFiller:
    """Vult Marktplaats advertentie formulier in"""
    
    def __init__(self, page: Page, base_url: str = "https://www.marktplaats.nl"):
        self.page = page
        self.base_url = base_url.rstrip('/')
    
    async def navigate_to_place_ad(self, skip_if_already_there: bool = True):
        """Navigeer naar de plaats advertentie pagina"""
        # Check if we're already on the place ad page
        current_url = self.page.url
        if skip_if_already_there and ('/plaats' in current_url or 'advertentie plaatsen' in await self.page.title()):
            log_step("Al op plaats advertentie pagina - overslaan navigatie")
            await self.page.wait_for_timeout(WAIT_SHORT)
            return
        
        log_step("Navigeren naar plaats advertentie pagina...")
        await self.page.goto(f"{self.base_url}/plaats", wait_until="domcontentloaded")
        
        # Check if we're on the right page
        if self.page.url.rstrip('/') not in (f"{self.base_url}/plaats", f"{self.base_url}/plaats/"):
            # Try clicking "Plaats advertentie" link
            link = self.page.get_by_role("link", name="Plaats advertentie")
            if await link.count() > 0:
                await link.first.click()
                await self.page.wait_for_load_state('domcontentloaded')
        
        log_success("Op plaats advertentie pagina")
    
    async def select_category(self, product: Product):
        """Selecteer categorie voor het product"""
        if not product.category_path:
            log_step("Geen categorie opgegeven, gebruik auto-suggest")
            await self._auto_suggest_category(product.title)
            return
        
        log_step(f"Categorie kiezen: {product.category_path}")
        
        # Fill title first (needed for category selection on some pages)
        await self._fill_title(product.title)
        
        # Click "Vind categorie" button
        try:
            find_button = self.page.get_by_role("button", name="Vind categorie")
            if await find_button.count() == 0:
                find_button = self.page.locator("[data-testid='findCategory']")
            if await find_button.count() > 0:
                await find_button.first.click()
                await self.page.wait_for_timeout(WAIT_MEDIUM)
        except Exception as e:
            log_warning(f"Kon 'Vind categorie' niet vinden: {e}")
        
        # Choose the specific category
        await self._choose_category_path(product.category_path)
        
        # Click "Verder" if needed
        try:
            next_button = self.page.get_by_role("button", name="Verder")
            if await next_button.count() > 0:
                await next_button.first.click()
                await self.page.wait_for_load_state("domcontentloaded")
                await self.page.wait_for_timeout(WAIT_SHORT)
        except Exception:
            pass
    
    async def _auto_suggest_category(self, title: str):
        """Gebruik auto-suggest voor categorie"""
        try:
            title_input = self.page.get_by_label("Titel", exact=False)
            if await title_input.count() == 0:
                title_input = self.page.get_by_placeholder("Titel", exact=False)
            await title_input.first.fill(title)
        except Exception:
            pass
        
        try:
            find_button = self.page.get_by_role("button", name="Vind categorie")
            if await find_button.count() == 0:
                find_button = self.page.locator("[data-testid='findCategory']")
            if await find_button.count() > 0:
                await find_button.first.click()
                await self.page.wait_for_timeout(WAIT_SHORT)
        except Exception:
            pass
        
        try:
            first_radio = self.page.locator("input[type='radio']").first
            if await first_radio.count() > 0:
                await first_radio.check()
                await self.page.wait_for_timeout(WAIT_SHORT)
        except Exception:
            pass
        
        try:
            next_button = self.page.get_by_role("button", name="Verder")
            if await next_button.count() > 0:
                await next_button.first.click()
                await self.page.wait_for_load_state("domcontentloaded")
        except Exception:
            pass
    
    async def _choose_category_path(self, category_path: str):
        """Kies categorie via pad (bijv. "Huis en Inrichting > Banken")"""
        parts = [p.strip() for p in category_path.split('>') if p.strip()]
        
        if not parts:
            log_warning("Lege categorie path")
            return
        
        await self.page.wait_for_timeout(WAIT_MEDIUM)
        
        # Check for suggestions first
        found_in_suggestions = False
        try:
            radio_buttons = self.page.locator("input[type='radio']")
            radio_count = await radio_buttons.count()
            
            if radio_count > 0:
                log_step(f"Gevonden {radio_count} categorie suggesties, zoeken naar match...")
                
                for i in range(radio_count):
                    try:
                        radio = radio_buttons.nth(i)
                        label_text = await self._get_radio_label_text(radio)
                        
                        if label_text:
                            label_text_clean = label_text.split("(")[0].strip()
                            first_part_clean = parts[0].strip()
                            
                            # Exact or partial match
                            if (first_part_clean.lower() == label_text_clean.lower() or
                                first_part_clean.lower() in label_text_clean.lower() or
                                label_text_clean.lower() in first_part_clean.lower()):
                                
                                log_success(f"Match gevonden in suggesties: '{label_text_clean}'")
                                await radio.check()
                                await self.page.wait_for_timeout(500)
                                found_in_suggestions = True
                                
                                if len(parts) == 1:
                                    return
                                
                                # Click "Verder" to continue
                                try:
                                    next_btn = self.page.get_by_role("button", name="Verder")
                                    if await next_btn.count() == 0:
                                        next_btn = self.page.locator("button:has-text('Verder')")
                                    if await next_btn.count() > 0:
                                        await next_btn.first.click()
                                        await self.page.wait_for_load_state("domcontentloaded")
                                        await self.page.wait_for_timeout(WAIT_MEDIUM)
                                except Exception as e:
                                    log_warning(f"Fout bij klikken op 'Verder': {e}")
                                
                                break
                    except Exception:
                        continue
                
                if not found_in_suggestions:
                    # Click "Of selecteer zelf een categorie"
                    try:
                        select_self = self.page.get_by_text("Of selecteer zelf een categorie", exact=False)
                        if await select_self.count() == 0:
                            select_self = self.page.get_by_text("selecteer zelf", exact=False)
                        if await select_self.count() > 0:
                            await select_self.first.click()
                            await self.page.wait_for_timeout(WAIT_MEDIUM)
                    except Exception as e:
                        log_warning(f"Fout bij openen categorie selectie: {e}")
        except Exception as e:
            log_step(f"Geen suggesties gevonden: {e}")
        
        # Navigate through category tree
        start_idx = 1 if found_in_suggestions else 0
        for idx, part in enumerate(parts[start_idx:], start=start_idx + 1):
            log_step(f"Stap {idx}/{len(parts)}: Zoeken naar '{part}'")
            
            found = await self._find_and_click_category(part)
            
            if not found:
                log_warning(f"Kon '{part}' niet vinden")
                if idx < len(parts):
                    log_warning("Probeer volgende stap...")
                else:
                    log_error("Kon laatste categorie deel niet vinden")
                    return
    
    async def _get_radio_label_text(self, radio) -> Optional[str]:
        """Haal label tekst op voor een radio button"""
        try:
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label = self.page.locator(f"label[for='{radio_id}']")
                if await label.count() > 0:
                    return await label.first.text_content()
        except:
            pass
        
        try:
            parent = radio.locator("xpath=..")
            label = parent.locator("label")
            if await label.count() > 0:
                return await label.first.text_content()
        except:
            pass
        
        try:
            parent = radio.locator("xpath=..")
            parent_text = await parent.text_content()
            if parent_text:
                return parent_text.strip()
        except:
            pass
        
        return None
    
    async def _find_and_click_category(self, part: str) -> bool:
        """Zoek en klik op een categorie deel"""
        await self.page.wait_for_timeout(WAIT_MEDIUM)
        
        # Try dropdown/select elements first
        found = await self._try_dropdown_selection(part)
        if found:
            return True
        
        # Try multiple strategies
        strategies = [
            lambda: self.page.get_by_role("link", name=part, exact=False),
            lambda: self.page.get_by_role("button", name=part, exact=False),
            lambda: self.page.locator(f"a:has-text('{part}'), button:has-text('{part}'), div:has-text('{part}'), span:has-text('{part}'), li:has-text('{part}')").first,
        ]
        
        for strategy in strategies:
            try:
                locator = strategy()
                if await locator.count() > 0:
                    is_visible = await locator.first.is_visible()
                    if is_visible:
                        log_success(f"'{part}' gevonden, klikken...")
                        await locator.first.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(WAIT_SHORT)
                        
                        try:
                            await locator.first.click()
                        except:
                            await locator.first.click(force=True)
                        
                        await self.page.wait_for_timeout(WAIT_MEDIUM)
                        try:
                            await self.page.wait_for_load_state("domcontentloaded", timeout=2000)
                        except:
                            pass
                        
                        return True
            except Exception:
                continue
        
        # Last resort: search all clickable elements
        try:
            all_clickable = self.page.locator(
                "a[href], button, div[onclick], span[onclick], li[onclick], "
                "[role='button'], [role='link'], [tabindex='0']"
            )
            count = await all_clickable.count()
            
            for i in range(min(count, 150)):
                try:
                    elem = all_clickable.nth(i)
                    if not await elem.is_visible():
                        continue
                    
                    text = await elem.text_content()
                    if text:
                        text_clean = text.strip().split("(")[0].strip().split("\n")[0].strip()
                        if (part.lower() == text_clean.lower() or
                            part.lower() in text_clean.lower() or
                            text_clean.lower() in part.lower()):
                            
                            log_success(f"'{part}' gevonden via zoeken, klikken...")
                            await elem.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(WAIT_SHORT)
                            await elem.click()
                            await self.page.wait_for_timeout(WAIT_MEDIUM)
                            return True
                except:
                    continue
        except Exception as e:
            log_warning(f"Zoeken in klikbare elementen fout: {e}")
        
        return False
    
    async def _try_dropdown_selection(self, part: str) -> bool:
        """Probeer categorie te vinden in dropdown/select elementen"""
        try:
            select_elements = self.page.locator(
                "select, [role='combobox'], [role='listbox'], [aria-expanded='true'], "
                ".dropdown, [class*='dropdown'], [class*='select'], [class*='menu'], [class*='list']"
            )
            select_count = await select_elements.count()
            
            if select_count > 0:
                for i in range(min(select_count, 10)):
                    try:
                        select_elem = select_elements.nth(i)
                        if not await select_elem.is_visible():
                            continue
                        
                        options = select_elem.locator("option, [role='option'], li, a, div, span")
                        opt_count = await options.count()
                        
                        if opt_count > 0:
                            for j in range(min(opt_count, 100)):
                                try:
                                    opt = options.nth(j)
                                    if not await opt.is_visible():
                                        continue
                                    
                                    opt_text = await opt.text_content()
                                    if opt_text:
                                        opt_text_clean = opt_text.strip().split("(")[0].strip().split("\n")[0].strip()
                                        if (part.lower() == opt_text_clean.lower() or
                                            part.lower() in opt_text_clean.lower() or
                                            opt_text_clean.lower() in part.lower()):
                                            
                                            log_success(f"Gevonden in dropdown: '{opt_text_clean}'")
                                            await opt.scroll_into_view_if_needed()
                                            await self.page.wait_for_timeout(WAIT_SHORT)
                                            await opt.click()
                                            await self.page.wait_for_timeout(WAIT_MEDIUM)
                                            return True
                                except:
                                    continue
                    except:
                        continue
        except:
            pass
        
        return False
    
    async def fill_all_fields(self, product: Product):
        """Vul alle velden van het formulier in"""
        log_step("Formulier velden invullen...")
        
        await self._fill_title(product.title)
        await self._fill_description(product.description)
        await self._fill_price(product.price)
        
        if product.condition:
            await self._fill_condition(product.condition)
        
        if product.location:
            await self._fill_location(product.location)
        
        if product.delivery_option:
            await self._fill_delivery_option(product.delivery_option)
        
        # Legacy fields (deprecated, use category_fields instead)
        if product.material:
            await self._fill_material(product.material)
        if product.thickness:
            await self._fill_thickness(product.thickness)
        if product.total_surface:
            await self._fill_total_surface(product.total_surface)
        
        # Category-specific fields
        if product.category_fields:
            await self._fill_category_fields(product.category_fields)
        
        # Check for and fill manufacturer fields if they appear on the page
        # These are often required but may not be in category_fields
        await self._fill_manufacturer_fields_if_present()
    
    async def _fill_title(self, title: str):
        """Vul titel in"""
        log_step(f"Titel invullen: {title}")
        try:
            title_input = self.page.get_by_label("Titel", exact=False)
            if await title_input.count() == 0:
                title_input = self.page.get_by_placeholder("Titel", exact=False)
            value = await title_input.first.input_value()
            if not value:
                await title_input.first.fill(title)
        except Exception:
            pass
    
    async def _fill_description(self, description: str):
        """Vul beschrijving in"""
        log_step("Omschrijving invullen")
        try:
            rte = self.page.locator("[data-testid='text-editor-input_nl-NL']").first
            if await rte.count() > 0:
                await rte.fill(description)
            else:
                desc_input = self.page.get_by_label("Beschrijving", exact=False)
                if await desc_input.count() == 0:
                    desc_input = self.page.get_by_placeholder("Beschrijving", exact=False)
                await desc_input.first.fill(description)
        except Exception:
            pass
    
    async def _fill_price(self, price: str):
        """Vul prijs in"""
        price_str = normalize_price(price)
        log_step(f"Prijs invullen: {price_str}")
        
        try:
            price_input = self.page.locator("#price\\.value, input#price\\.value")
            if await price_input.count() == 0:
                price_input = self.page.get_by_label("Prijs", exact=False)
            if await price_input.count() == 0:
                price_input = self.page.locator("input[name='price.value']")
            if await price_input.count() == 0:
                price_input = self.page.locator("input[type='text'][name*='price'], input[type='number'][name*='price']")
            
            if await price_input.count() > 0:
                await price_input.first.fill(price_str)
                log_success(f"Prijs ingevuld: {price_str}")
            else:
                log_warning("Kon prijs veld niet vinden")
        except Exception as e:
            log_warning(f"Fout bij invullen prijs: {e}")
    
    async def _fill_condition(self, condition: str):
        """Vul staat/conditie in"""
        log_step(f"Staat kiezen: {condition}")
        try:
            select = self.page.locator("select[name='singleSelectAttribute[condition]']")
            if await select.count() > 0:
                await select.select_option(label=condition)
        except Exception:
            pass
    
    async def _fill_location(self, location: str):
        """Vul locatie in"""
        log_step(f"Locatie invullen: {location}")
        try:
            loc_input = self.page.get_by_label("Plaatsnaam", exact=False)
            if await loc_input.count() == 0:
                loc_input = self.page.get_by_placeholder("Plaatsnaam", exact=False)
            await loc_input.first.fill(location)
        except Exception:
            pass
    
    async def _fill_delivery_option(self, delivery_option: str):
        """Vul levering optie in"""
        log_step(f"Levering kiezen: {delivery_option}")
        try:
            radio = self.page.locator("input[name='deliveryMethod'][type='Radio']")
            if await radio.count() == 0:
                radio = self.page.get_by_label(delivery_option, exact=False)
            if await radio.count() > 0:
                await radio.first.check()
        except Exception:
            pass
    
    async def _fill_material(self, material: str):
        """Vul materiaal in (legacy)"""
        log_step(f"Materiaal kiezen: {material}")
        try:
            select = self.page.locator("select[name='singleSelectAttribute[material]']")
            if await select.count() > 0:
                await select.select_option(label=material)
        except Exception:
            pass
    
    async def _fill_thickness(self, thickness: str):
        """Vul dikte in (legacy)"""
        log_step(f"Dikte kiezen: {thickness}")
        try:
            select = self.page.locator("select[name='singleSelectAttribute[thickness]']")
            if await select.count() > 0:
                await select.select_option(label=thickness)
        except Exception:
            pass
    
    async def _fill_total_surface(self, total_surface: str):
        """Vul oppervlakte in (legacy)"""
        log_step(f"Oppervlakte kiezen: {total_surface}")
        try:
            select = self.page.locator("select[name='singleSelectAttribute[totalSurface]']")
            if await select.count() > 0:
                await select.select_option(label=total_surface)
        except Exception:
            pass
    
    async def _fill_category_fields(self, category_fields: dict):
        """Vul categorie-specifieke velden in"""
        if not category_fields or not isinstance(category_fields, dict):
            return
        
        log_step("Categorie-specifieke velden invullen...")
        
        for field_name, field_value in category_fields.items():
            if not field_value or field_value == '':
                continue
            
            try:
                filled = await self._fill_category_field(field_name, field_value)
                if not filled:
                    log_warning(f"Kon veld '{field_name}' niet invullen (waarde: {field_value})")
            except Exception as e:
                log_warning(f"Fout bij invullen veld '{field_name}': {e}")
    
    async def _fill_category_field(self, field_name: str, field_value: any) -> bool:
        """Vul een categorie-specifiek veld in"""
        field_name_upper = field_name.upper()
        attr_name = field_name_upper
        
        # Extract attribute name from brackets
        if '[' in field_name_upper and ']' in field_name_upper:
            start = field_name_upper.find('[') + 1
            end = field_name_upper.find(']')
            if start > 0 and end > start:
                attr_name = field_name_upper[start:end]
        
        value_str = str(field_value).strip()
        
        # Try select fields
        select_locators = [
            f"select[name='{field_name}']",
            f"select[name='{field_name.lower()}']",
            f"select[name='{field_name_upper}']",
            f"select[name='singleSelectAttribute[{attr_name.lower()}]']",
            f"select[name='SINGLESELECTATTRIBUTE[{attr_name}]']",
            f"select[name='singleSelectAttribute[{attr_name}]']",
        ]
        
        for selector in select_locators:
            try:
                select = self.page.locator(selector)
                if await select.count() > 0:
                    try:
                        await select.select_option(label=value_str)
                        log_success(f"{field_name}: {value_str}")
                        return True
                    except:
                        try:
                            await select.select_option(value=value_str)
                            log_success(f"{field_name}: {value_str}")
                            return True
                        except:
                            pass
            except:
                continue
        
        # Try radio buttons
        radio_locators = [
            f"input[type='radio'][name='{field_name}']",
            f"input[type='radio'][name='{field_name.lower()}']",
            f"input[type='radio'][name='{field_name_upper}']",
        ]
        
        for selector in radio_locators:
            try:
                radios = self.page.locator(selector)
                count = await radios.count()
                if count > 0:
                    for i in range(count):
                        radio = radios.nth(i)
                        radio_value = await radio.get_attribute("value")
                        if radio_value and value_str.lower() in radio_value.lower():
                            await radio.check()
                            log_success(f"{field_name}: {value_str} (radio)")
                            return True
            except:
                continue
        
        # Try text input
        text_locators = [
            f"input[name='{field_name}']",
            f"input[name='{field_name.lower()}']",
            f"textarea[name='{field_name}']",
        ]
        
        for selector in text_locators:
            try:
                input_elem = self.page.locator(selector)
                if await input_elem.count() > 0:
                    await input_elem.first.fill(value_str)
                    log_success(f"{field_name}: {value_str} (text)")
                    return True
            except:
                continue
        
        # Try label-based input (for fields like "Handelsnaam fabrikant")
        # Look for label containing field name, then find associated input
        try:
            field_name_lower = field_name.lower()
            # Common manufacturer field patterns
            if 'fabrikant' in field_name_lower or 'manufacturer' in field_name_lower:
                # Try to find by label text
                label_patterns = [
                    f"label:has-text('{field_name}')",
                    f"label:has-text('Handelsnaam')",
                    f"label:has-text('Postadres')",
                    f"label:has-text('E-mailadres')",
                ]
                
                for pattern in label_patterns:
                    try:
                        label = self.page.locator(pattern).first
                        if await label.count() > 0:
                            # Get the 'for' attribute to find associated input
                            label_for = await label.get_attribute('for')
                            if label_for:
                                input_elem = self.page.locator(f"#{label_for}, input[id='{label_for}'], textarea[id='{label_for}']")
                                if await input_elem.count() > 0:
                                    await input_elem.first.fill(value_str)
                                    log_success(f"{field_name}: {value_str} (via label)")
                                    return True
                            
                            # Try to find input next to or inside label
                            input_near_label = label.locator("input, textarea").first
                            if await input_near_label.count() > 0:
                                await input_near_label.fill(value_str)
                                log_success(f"{field_name}: {value_str} (via label input)")
                                return True
                    except:
                        continue
        except:
            pass
        
        return False
    
    async def _fill_manufacturer_fields_if_present(self):
        """Vul fabrikantvelden in als ze op de pagina staan (demo waarden)"""
        try:
            await self.page.wait_for_timeout(WAIT_SHORT)
            
            # Look for manufacturer field labels
            manufacturer_fields = {
                'Handelsnaam fabrikant': 'Demo Fabrikant B.V.',
                'Postadres fabrikant': 'Demo Straat 123, 1234 AB Amsterdam, Nederland',
                'E-mailadres fabrikant': 'demo@fabrikant.nl',
            }
            
            for field_label, demo_value in manufacturer_fields.items():
                try:
                    # Try to find label
                    label = self.page.locator(f"label:has-text('{field_label}')").first
                    if await label.count() > 0:
                        is_visible = await label.is_visible()
                        if is_visible:
                            # Get associated input
                            label_for = await label.get_attribute('for')
                            if label_for:
                                input_elem = self.page.locator(f"#{label_for}, input[id='{label_for}'], textarea[id='{label_for}']")
                            else:
                                # Try to find input near label
                                input_elem = label.locator("..").locator("input, textarea").first
                            
                            if await input_elem.count() > 0:
                                current_value = await input_elem.first.input_value()
                                if not current_value or current_value.strip() == '':
                                    await input_elem.first.fill(demo_value)
                                    log_success(f"{field_label}: {demo_value}")
                except Exception as e:
                    # Field not found or error - continue
                    continue
        except Exception as e:
            # Silently fail - manufacturer fields may not be present
            pass
    
    async def select_free_bundle(self):
        """Selecteer gratis bundle optie"""
        try:
            free = self.page.locator("#feature-FREE, [id='feature-FREE']")
            if await free.count() > 0:
                choose = free.locator("text=Kiezen").first
                if await choose.count() > 0:
                    await choose.click()
                else:
                    await free.click()
            await self.page.wait_for_timeout(WAIT_SHORT)
        except Exception:
            pass
