from bs4 import BeautifulSoup
from .base import BaseScraper
import logging
import re

from .config import SEARCH_CRITERIA
logger = logging.getLogger(__name__)

class CastellanaScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db)
        self.portal_name = "lacastellana"
        self.base_url = "https://lacastellana.com.co"

    async def scrape(self):
        property_types = ["apartamento", "apartaestudio"]
        
        for p_type in property_types:
            page_num = 1
            consecutive_existing = 0
            
            logger.info(f"[{self.portal_name}] Starting scraping for type: {p_type}")
            
            while page_num <= self.max_pages:
                # Golden URL Structure: /s/{type}/alquileres?page={n}
                if page_num == 1:
                    url = f"{self.base_url}/s/{p_type}/alquileres" 
                else:
                    url = f"{self.base_url}/s/{p_type}/alquileres?page={page_num}"
                
                logger.info(f"[{self.portal_name}] Scraping {p_type} page {page_num}: {url}")
                
                try:
                    await self.navigate(url)
                    
                    # Wait for grid Items
                    try:
                        await self.page.wait_for_selector(".item.shadow-sm", timeout=10000)
                    except:
                        logger.info(f"[{self.portal_name}] No properties found on page {page_num} for {p_type}. Stopping type.")
                        break

                    content = await self.page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    cards = soup.select(".item.shadow-sm")
                    if not cards:
                        logger.info(f"[{self.portal_name}] No cards found on page {page_num}. Stopping type.")
                        break
                        
                    logger.info(f"[{self.portal_name}] Found {len(cards)} properties on page {page_num}")
                    
                    type_consecutive_existing = 0
                    
                    for card in cards:
                        try:
                            # Title and Link
                            title_tag = card.select_one(".t8-title.link")
                            if not title_tag:
                                continue
                            title = title_tag.get_text(strip=True)
                            link = title_tag['href']
                            if not link.startswith("http"):
                                link = f"{self.base_url}{link}"
                                
                            # Image
                            image_tag = card.select_one(".fill.object-fit-cover img")
                            image_url = image_tag['src'] if image_tag else None
                            
                            # Price
                            price_tag = card.select_one(".areaPrecio p.t8-title")
                            price_text = price_tag.get_text(strip=True) if price_tag else "0"
                            price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                            
                            # Location
                            loc_tag = card.select_one(".ubicacion.t8-title")
                            location = loc_tag.get_text(strip=True) if loc_tag else "Medellín"
                            
                            # Details (rooms, area)
                            area = 0
                            bedrooms = 0
                            details = card.select(".info_details .col-6")
                            for det in details:
                                text = det.get_text(strip=True).lower()
                                val_tag = det.select_one("strong")
                                val_text = val_tag.get_text(strip=True) if val_tag else ""
                                
                                if "área" in text or "m2" in text or "m²" in text:
                                    try:
                                        area = float(re.sub(r'[^\d.]', '', val_text))
                                    except:
                                        pass
                                elif "alcobas" in text:
                                    try:
                                        bedrooms = int(re.sub(r'\D', '', val_text))
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

                            # Stop logic
                            if status == "existing":
                                type_consecutive_existing += 1
                            elif status == "new" or status == "updated":
                                type_consecutive_existing = 0
                            
                        except Exception as e:
                            logger.error(f"[{self.portal_name}] Error parsing card: {e}")
                            continue

                    if self.should_stop_scraping(type_consecutive_existing):
                        logger.info(f"[{self.portal_name}] Existing limit reached for {p_type}. Moving to next type.")
                        break
                        
                    page_num += 1

                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error scraping URL {url}: {e}")
                    break
        
        await self.close_browser()
