from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from .base import BaseScraper
import logging
import re

from .config import SEARCH_CRITERIA
logger = logging.getLogger(__name__)

class SantaFeScraper(BaseScraper):
    def __init__(self, db: Session):

        super().__init__(db)
        self.portal_name = "santafe"
        self.base_url = "https://arrendamientossantafe.com"

    async def scrape(self):
        try:
            # Starts with Arrendar
            url_arriendo = f"{self.base_url}/propiedades/?bussines_type=Arrendar"
            await self._scrape_url(url_arriendo)
        finally:
            await self.close_browser()

        
        # Could also add Venta if needed, for now complying with Phase 2 objective
    
    async def _scrape_url(self, url):
        logger.info(f"Navigating to {url}")
        await self.navigate(url)
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        cards = soup.select(".property-card")
        logger.info(f"Found {len(cards)} properties on {url}")
        
        count = 0
        consecutive_existing = 0

        for card in cards:
            try:
                # Link and ID
                link_tag = card.select_one(".inner-card a")
                if not link_tag:
                    continue
                relative_link = link_tag['href']
                full_link = f"{self.base_url.rstrip('/')}{relative_link}"
                
                # Image
                img_div = card.select_one(".img-preview")
                image_url = None
                if img_div and 'style' in img_div.attrs:
                    style = img_div['style']
                    # extract url(...)
                    import re
                    match = re.search(r'url\((.*?)\)', style)
                    if match:
                        image_url = match.group(1).strip()

                # Body details
                body = card.select_one(".property-body")
                if not body:
                    continue
                
                # Location
                sector_tag = body.select_one(".sector p")
                location = sector_tag.get_text(strip=True).replace("Ubicación:", "").strip() if sector_tag else "Unknown"
                
                # Type
                type_tag = body.select_one(".tipo-inmueble")
                property_type = type_tag.get_text(strip=True).replace("Tipo:", "").strip() if type_tag else "Unknown"
                
                # Price
                price_tag = body.select_one(".precio p")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                # Clean price
                price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                
                # Details
                area = 0
                bedrooms = 0
                bathrooms = 0 # Not explicitly seen in debug snippet, assuming standard if present
                
                detail_prop = body.select_one(".detail-prop")
                if detail_prop:
                    # Alcobas
                    # Sometimes it's a span or div with class 'alcobas' or inside an li
                    bedroom_nodes = detail_prop.select("span, div, li")
                    for node in bedroom_nodes:
                        txt = node.get_text(strip=True).lower()
                        if "alcoba" in txt or "habitacion" in txt:
                            match = re.search(r'(\d+)', txt)
                            if match:
                                bedrooms = int(match.group(1))
                                break
                    
                    # Area
                    for node in bedroom_nodes:
                        txt = node.get_text(strip=True).lower()
                        if "m2" in txt or "m²" in txt or "area" in txt:
                             match = re.search(r'([\d.,]+)', txt)
                             if match:
                                 try:
                                     # normalize '50,5' to 50.5 if needed, though usually just ints
                                     val_str = match.group(1).replace(',', '.')
                                     area = float(val_str)
                                 except:
                                     pass
                                 break

                title = f"{property_type} en {location}"
                
                entry = {
                    "title": title,
                    "price": price,
                    "location": location,
                    "link": full_link,
                    "image_url": image_url,
                    "source": self.portal_name,
                    "area": area,
                    "bedrooms": bedrooms
                }
                
                status = await self.process_property(entry)
                count += 1
                
                # Stop logic
                if status == "existing":
                    consecutive_existing += 1
                elif status == "new" or status == "updated":
                    consecutive_existing = 0
                
                if self.should_stop_scraping(consecutive_existing):
                    break
                
            except Exception as e:
                logger.error(f"Error parsing card: {e}")
                continue
                
        logger.info(f"Saved {count} properties from Santa Fe")
