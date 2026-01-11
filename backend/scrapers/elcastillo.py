import asyncio
import logging
import re

from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from .base import BaseScraper
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.arrendamientoselcastillo.com.co/resultados?gestion=Arriendo"

class ElCastilloScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "elcastillo"

    async def scrape(self):
        try:
            await self.navigate(SEARCH_URL)
            
            try:
                await self.page.wait_for_selector("div.estate_itm", timeout=15000)
            except Exception as e:
                logger.error("Timeout waiting for content.")
                await self.dump_html()
                return

            # Scroll to load (simple scroll)
            for _ in range(3):
                await self.page.mouse.wheel(0, 1000)
                await asyncio.sleep(1)

            cards = await self.page.locator("div.estate_itm").all()
            logger.info(f"Found {len(cards)} listings")

            count = 0
            for i, card in enumerate(cards):
                try:
                    # Link
                    link_locator = card.locator("div.estate_itm--media > a").first
                    full_link = await link_locator.get_attribute("href")
                    if not full_link:
                        continue
                    
                    # Title
                    title_locator = card.locator("div.estate_itm--info h4").first
                    title_text = await title_locator.text_content()
                    
                    # Price
                    price_locator = card.locator("div.price p").first
                    price_text = await price_locator.text_content()
                    price = float(re.sub(r'[^\d]', '', price_text)) if price_text and re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Location
                    location_text = "Medellin"
                    if title_text and "-" in title_text:
                        parts = title_text.split("-")
                        if len(parts) > 1:
                            location_text = parts[-1].strip()

                    await self.process_property({
                        "title": title_text.strip() if title_text else "No Title",
                        "price": price,
                        "location": location_text,
                        "link": full_link,
                        "source": self.portal_name
                    })
                    count += 1
                except Exception as e:
                    logger.error(f"Error parsing card {i}: {e}")
                    continue
            
            logger.info(f"Successfully processed {count} properties")
        finally:
            await self.close_browser()

if __name__ == "__main__":
    db = SessionLocal()
    scraper = ElCastilloScraper(db)
    asyncio.run(scraper.scrape())
    db.close()

