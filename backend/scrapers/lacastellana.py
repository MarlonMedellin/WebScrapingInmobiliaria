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
        url = f"{self.base_url}/s/alquileres"
        try:
            await self.navigate(url)
            # Wait a bit for JS to load the grid
            await self.page.wait_for_selector(".item.shadow-sm", timeout=15000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".item.shadow-sm")
            logger.info(f"[{self.portal_name}] Found {len(cards)} properties")
            
            consecutive_existing = 0

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
                        consecutive_existing += 1
                    elif status == "new" or status == "updated":
                        consecutive_existing = 0
                    
                    if self.should_stop_scraping(consecutive_existing):
                        break

                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.error(f"[{self.portal_name}] Error during scrape: {e}")
            await self.dump_html() # Save HTML if it fails
        finally:
            await self.close_browser()
