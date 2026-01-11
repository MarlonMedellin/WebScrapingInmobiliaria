from bs4 import BeautifulSoup
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class MonserrateScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db)
        self.portal_name = "monserrate"
        self.base_url = "https://www.arrendamientosmonserrate.com"

    async def scrape(self):
        # operacion=2 is Arriendo
        url = f"{self.base_url}/inmuebles/?operacion=2"
        try:
            await self.navigate(url)
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # WooCommerce product list
            cards = soup.select("li.product")
            logger.info(f"[{self.portal_name}] Found {len(cards)} properties")
            
            for card in cards:
                try:
                    # Title and Link
                    title_tag = card.select_one("h4 a")
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    
                    # Image
                    image_tag = card.select_one(".image_frame img")
                    image_url = image_tag['src'] if image_tag else None
                    
                    # Price
                    price_tag = card.select_one(".price .amount")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Meta from classes
                    classes = card.get('class', [])
                    area = 0
                    bedrooms = 0
                    location = "Medellín"
                    
                    for cls in classes:
                        if cls.startswith("pa_area-"):
                            area_match = re.search(r'pa_area-(\d+)', cls)
                            if area_match:
                                area = float(area_match.group(1))
                        elif cls.startswith("pa_alcobas-"):
                            beds_match = re.search(r'pa_alcobas-(\d+)', cls)
                            if beds_match:
                                bedrooms = int(beds_match.group(1))
                        elif cls.startswith("pa_sector-"):
                            location = cls.replace("pa_sector-", "").replace("-", " ").title()

                    await self.process_property({
                        "title": title,
                        "price": price,
                        "location": location,
                        "link": link,
                        "image_url": image_url,
                        "area": area,
                        "bedrooms": bedrooms,
                        "source": self.portal_name
                    })
                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.error(f"[{self.portal_name}] Error during scrape: {e}")
        finally:
            await self.close_browser()
