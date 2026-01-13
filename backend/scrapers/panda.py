from bs4 import BeautifulSoup
from .base import BaseScraper
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from .config import SEARCH_CRITERIA

class PandaScraper(BaseScraper):
    """
    Scraper for Panda Inmobiliaria.
    
    GOLDEN RULES:
    1. SPA Interactions: Uses Playwright to toggle checkboxes (Comprar OFF, Arrendar ON).
    2. Type Iteration: Explicitly loop through types (Apartamento, Casa, etc.) via 'type-X' IDs.
    3. Dynamic Waiting: Wait for article[data-testid="property-card"] to ensure SPA content loads.
    4. Data Attributes: Extract details from 'data-property-*' attributes for reliability.
    """
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "panda"
        self.base_url = "https://pandainmobiliaria.com"

    async def scrape(self):
        url = f"{self.base_url}/inmuebles"
        try:
            logger.info(f"[{self.portal_name}] Navigating to {url}")
            await self.navigate(url)
            await self.page.wait_for_timeout(3000)

            # --- FILTERING ---
            logger.info(f"[{self.portal_name}] Applying filters: Arrendar ON, Comprar OFF")

            # 1. Expand "Gestión" if needed (it seems expanded by default in HTML)
            # 2. Uncheck Comprar (mode-5) - Default Checked
            try:
                # Use label click for reliability
                comprar_label = self.page.locator('label[for="mode-5"]')
                if await comprar_label.count() > 0:
                    # Check if input is checked
                    is_checked = await self.page.eval_on_selector('#mode-5', 'el => el.checked')
                    if is_checked:
                        logger.info(f"[{self.portal_name}] Unchecking 'Comprar'...")
                        await comprar_label.click()
                        await self.page.wait_for_timeout(1000)
            except Exception as e:
                logger.warning(f"[{self.portal_name}] Issue unchecking Comprar: {e}")

            # 3. Check Arrendar (mode-1) - Default Unchecked
            try:
                 arriendar_label = self.page.locator('label[for="mode-1"]')
                 is_arriendo_checked = await self.page.eval_on_selector('#mode-1', 'el => el.checked')
                 if not is_arriendo_checked:
                     logger.info(f"[{self.portal_name}] Checking 'Arrendar'...")
                     await arriendar_label.click()
                     await self.page.wait_for_timeout(2000) # Wait for list refresh
            except Exception as e:
                logger.error(f"[{self.portal_name}] Issue checking Arrendar: {e}")

            # --- TYPE ITERATION ---
            # Map types to input IDs
            target_types = {
                "Apartamento": "type-2",
                "Casa": "type-1", 
                "Apartaestudio": "type-14",
                "Local": "type-3",
                "Oficina": "type-4"
            }

            for type_name, input_id in target_types.items():
                logger.info(f"[{self.portal_name}] Filtering by type: {type_name}")
                
                # Check the specific type
                type_label = self.page.locator(f'label[for="{input_id}"]')
                try:
                    await type_label.scroll_into_view_if_needed()
                    await type_label.click()
                    await self.page.wait_for_timeout(2000) # Wait for results
                except Exception as e:
                    logger.warning(f"[{self.portal_name}] Could not select type {type_name}: {e}")
                    continue

                # Scrape Pages for this Type
                page_num = 1
                consecutive_existing_type = 0
                
                while True:
                    logger.info(f"[{self.portal_name}] Scraping {type_name} - Page {page_num}")
                    
                    # Wait for cards
                    # Sometimes there are no results, so we wait briefly
                    try:
                        await self.page.wait_for_selector('article[data-testid="property-card"]', state='visible', timeout=5000)
                    except:
                        logger.info(f"[{self.portal_name}] No properties found for {type_name} on page {page_num}")
                        break

                    cards = await self.page.locator('article[data-testid="property-card"]').all()
                    logger.info(f"[{self.portal_name}] Found {len(cards)} cards on page.")
                    
                    if not cards:
                        break

                    for i, card in enumerate(cards):
                        try:
                            # Extract data from attributes (much cleaner!)
                            type_attr = await card.get_attribute("data-property-type") or "Inmueble"
                            city_attr = await card.get_attribute("data-property-city") or ""
                            suburb_attr = await card.get_attribute("data-property-suburb") or ""
                            price_attr = await card.get_attribute("data-property-price") or "0"
                            area_attr = await card.get_attribute("data-property-area") or "0"
                            rooms_attr = await card.get_attribute("data-property-rooms") or "0"
                            
                            title = f"{type_attr} en Alquiler en {suburb_attr}, {city_attr}"
                            location = f"{suburb_attr}, {city_attr}"
                            price = float(price_attr)
                            area = float(area_attr)
                            bedrooms = int(rooms_attr)

                            link_el = card.locator('a[data-testid="property-card-link"]')
                            link_href = await link_el.get_attribute("href")
                            link = f"{self.base_url}{link_href}"
                            
                            # Image
                            # Try to get background image style
                            # Selector from dump: figure > div[style]
                            # Or just first div with background image
                            image_url = None
                            try:
                                style = await card.locator("figure > div").first.get_attribute("style")
                                if style and "url(" in style:
                                    import re
                                    match = re.search(r'url\("?(.*?)"?\)', style)
                                    if match:
                                        image_url = match.group(1)
                            except:
                                pass

                            status = await self.process_property({
                                "title": title,
                                "price": price,
                                "location": location,
                                "link": link,
                                "image_url": image_url,
                                "area": area,
                                "bedrooms": bedrooms,
                                "source": self.portal_name
                            })

                            if status == "existing":
                                consecutive_existing_type += 1
                            else:
                                consecutive_existing_type = 0
                            
                        except Exception as e:
                            logger.error(f"[{self.portal_name}] Error parsing card {i}: {e}")

                    if self.should_stop_scraping(consecutive_existing_type):
                        logger.info(f"[{self.portal_name}] Stopping {type_name} due to existing limit.")
                        break

                    # Pagination
                    # Look for Next button. Common patterns: Text "Siguiente", ">", or classes.
                    # Since I couldn't find it in grep, I'll try generic text locators.
                    try:
                        # Try finding a button/link with "Siguiente" or icon
                        # We will try a few selectors
                        next_btn = self.page.locator('li.next a, li.next button, a:has-text("Siguiente"), button:has-text("Siguiente")')
                        
                        if await next_btn.count() > 0 and await next_btn.first.is_visible():
                            # Check if disabled
                            parent_li = next_btn.locator("xpath=..") # Assuming it's inside an li
                            class_attr = await parent_li.get_attribute("class") or ""
                            if "disabled" in class_attr:
                                logger.info(f"[{self.portal_name}] Next button disabled (end of list).")
                                break
                                
                            await next_btn.first.click()
                            await self.page.wait_for_timeout(3000)
                            page_num += 1
                        else:
                            # Try just ">"
                            next_symbol = self.page.locator('a:has-text(">"), button:has-text(">")')
                            if await next_symbol.count() > 0 and await next_symbol.first.is_visible():
                                await next_symbol.first.click()
                                await self.page.wait_for_timeout(3000)
                                page_num += 1
                            else:
                                logger.info(f"[{self.portal_name}] No 'Next' button found on page {page_num}.")
                                break
                    except Exception as e:
                        logger.warning(f"[{self.portal_name}] Pagination error: {e}")
                        break
                
                # Uncheck current type to verify next
                try:
                    await type_label.scroll_into_view_if_needed()
                    await type_label.click()
                    await self.page.wait_for_timeout(1000)
                except:
                    pass

        except Exception as e:
            logger.error(f"[{self.portal_name}] Error during scrape: {e}")
            await self.dump_html(prefix="error_panda")
        finally:
            await self.close_browser()
