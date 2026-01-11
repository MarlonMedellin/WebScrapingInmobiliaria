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

SEARCH_URL = "https://www.fincaraiz.com.co/venta/apartamentos/medellin"

class FincaRaizScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "fincaraiz"

    async def scrape(self):
        try:
            await self.navigate(SEARCH_URL)
            
            # Wait for content to load
            try:
                # Wait for at least one article or card
                await self.page.wait_for_selector("div.listingCard", timeout=15000)
            except Exception as e:
                logger.error("Timeout waiting for content. Dumping HTML...")
                await self.dump_html()
                return

            # Scroll down to load more items (infinite scroll handling - basic)
            for _ in range(3):
                await self.page.mouse.wheel(0, 500)
                await asyncio.sleep(1)

            # Extract Items
            cards = await self.page.locator("div.listingCard").all()
            
            logger.info(f"Found {len(cards)} listings")

            if len(cards) == 0:
                await self.dump_html()
            
            for i, card in enumerate(cards):
                try:
                    # LINK
                    link_locator = card.locator("a.lc-data").first
                    url_suffix = await link_locator.get_attribute("href")
                    if not url_suffix:
                        continue
                    full_link = f"https://www.fincaraiz.com.co{url_suffix}" if not url_suffix.startswith("http") else url_suffix
                    
                    # PRICE
                    price_text = await card.locator(".main-price").first.text_content()
                    price = float(re.sub(r'[^\d]', '', price_text)) if price_text and re.sub(r'[^\d]', '', price_text) else 0

                    # TITLE
                    title_text = await card.locator("h2.lc-title").first.text_content()
                    
                    # LOCATION
                    location_text = await card.locator("strong.lc-location").first.text_content()

                    # Process Data
                    await self.process_property({
                        "title": title_text.strip() if title_text else "No Title",
                        "price": price,
                        "location": location_text.strip() if location_text else "Medellin",
                        "link": full_link,
                        "source": self.portal_name
                    })

                except Exception as e:
                    logger.error(f"Error parsing card {i}: {e}")
                    continue
        finally:
            await self.close_browser()

def run_scraper_manual():
    db = SessionLocal()
    scraper = FincaRaizScraper(db)
    asyncio.run(scraper.scrape())
    db.close()

if __name__ == "__main__":
    run_scraper_manual()

