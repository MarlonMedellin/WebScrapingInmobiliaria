from bs4 import BeautifulSoup
from .base import BaseScraper
import logging
import re

from .config import SEARCH_CRITERIA
logger = logging.getLogger(__name__)

class AportalScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db)
        self.portal_name = "aportal"
        self.base_url = "https://aportal.com.co"

    async def scrape(self):
        url = f"{self.base_url}/es/arrendar"
        try:
            await self.navigate(url)
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".properties")
            logger.info(f"[{self.portal_name}] Found {len(cards)} properties")
            
            consecutive_existing = 0

            for card in cards:
                try:
                    # Skip if "No Disponible"
                    status_tag = card.select_one(".status")
                    if status_tag and "No Disponible" in status_tag.get_text():
                        continue
                    
                    # Title and Link
                    title_tag = card.select_one("h4 a")
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    if not link.startswith("http"):
                        link = f"{self.base_url}{link}"
                    
                    # Image
                    image_tag = card.select_one(".image-holder img")
                    image_url = image_tag['src'] if image_tag else None
                    if image_url and not image_url.startswith("http"):
                        image_url = f"{self.base_url}{image_url}"
                    
                    # Price
                    price_tag = card.select_one("p.Precio")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Location
                    # It's in a div.row with a marker icon
                    location = "Medellín"
                    loc_row = card.select_one(".row:has(.glyphicon-map-marker)")
                    if loc_row:
                        location = loc_row.get_text(strip=True)
                    
                    # This site doesn't show area/rooms in the card list (only detail page)
                    # For now, following Phase 1/2 style of extraction from list.
                    
                    status = await self.process_property({
                        "title": title,
                        "price": price,
                        "location": location,
                        "link": link,
                        "image_url": image_url,
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
        finally:
            await self.close_browser()
