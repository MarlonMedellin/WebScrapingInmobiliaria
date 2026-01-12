from bs4 import BeautifulSoup
from .base import BaseScraper
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from .config import SEARCH_CRITERIA

class PandaScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "panda"
        self.base_url = "https://pandainmobiliaria.com"

    async def scrape(self):
        try:
            # Operacion 2 normally means Arriendo
            # We assume filtering by price in URL is risky without doc, relying on Phase 5
            url = f"{self.base_url}/inmuebles?operacion=2" 
            await self._scrape_url(url)
        finally:
            await self.close_browser()

    
    async def _scrape_url(self, url):
        logger.info(f"Navigating to {url}")
        await self.navigate(url)
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Select by data-testid="property-card"
        cards = soup.select('article[data-testid="property-card"]')
        logger.info(f"Found {len(cards)} properties on Panda")
        
        count = 0
        consecutive_existing = 0

        for card in cards:
            try:
                # Extract data attributes
                attrs = card.attrs
                
                title = f"{attrs.get('data-property-type', 'Inmueble')} en {attrs.get('data-property-suburb', '')}, {attrs.get('data-property-city', '')}"
                price_raw = attrs.get('data-property-price', '0')
                price = float(price_raw) if price_raw else 0
                
                location = f"{attrs.get('data-property-suburb', '')}, {attrs.get('data-property-city', '')}".strip(', ')
                
                # Link
                link_tag = card.select_one('a[data-testid="property-card-link"]')
                full_link = ""
                if link_tag and link_tag.has_attr('href'):
                    full_link = f"{self.base_url}{link_tag['href']}"
                
                # Image
                # In debug html: style="background-image: url("...")" in the first div inside figure
                image_url = None
                img_div = card.select_one('figure div[style*="background-image"]')
                if img_div:
                    style = img_div['style']
                    import re
                    match = re.search(r'url\("?(.*?)"?\)', style)
                    if match:
                        image_url = match.group(1).strip()
                
                # Details
                area = float(attrs.get('data-property-area', 0))
                bedrooms = int(attrs.get('data-property-rooms', 0))
                bathrooms = int(attrs.get('data-property-bathrooms', 0))
                
                # Description logic if needed (not in card usually)
                
                entry = {
                    "title": title,
                    "price": price,
                    "location": location,
                    "link": full_link,
                    "image_url": image_url,
                    "source": self.portal_name,
                    "area": area,
                    "bedrooms": bedrooms,
                    # "bathrooms": bathrooms # Model might not have this yet, check Property model
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
                logger.error(f"Error parsing Panda card: {e}")
                continue
                
        logger.info(f"Saved {count} properties from Panda")
