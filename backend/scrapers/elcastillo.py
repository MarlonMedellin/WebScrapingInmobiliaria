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

from .config import SEARCH_CRITERIA

# Note: Investigating filtering capabilities. Using generic Arriendo filter + Price if supported.
# If not supported, BaseScraper logic (Phase 5) will handle exclusion.

class ElCastilloScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "elcastillo"

    async def scrape(self):
        try:
            # Construct URL with price if possible. 
            # Trying standard param approach just in case, otherwise fallback specific
            # URL: .../resultados?gestion=Arriendo
            max_price = SEARCH_CRITERIA["max_price"]
            # Adding generic params often seen in software used by them (Simi/Wasi?)
            # Actually El Castillo looks custom or specific template.
            # We'll use the base Arriendo url and rely on Python filtering for now to be safe,
            # as adding wrong params might break results.
            url = "https://www.arrendamientoselcastillo.com.co/resultados?gestion=Arriendo"
            
            await self.navigate(url)
            
            try:
                await self.page.wait_for_selector("div.estate_itm", timeout=15000)
            except Exception as e:
                logger.error("Timeout waiting for content.")
                await self.dump_html()
                return

            # Scroll to load (simple scroll)
            scrolls = SEARCH_CRITERIA.get("scroll_depth", 10)
            for _ in range(scrolls):
                await self.page.mouse.wheel(0, 1000)
                await asyncio.sleep(1)

            cards = await self.page.locator("div.estate_itm").all()
            logger.info(f"Found {len(cards)} listings")

            count = 0
            consecutive_existing = 0

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

                    status = await self.process_property({
                        "title": title_text.strip() if title_text else "No Title",
                        "price": price,
                        "location": location_text,
                        "link": full_link,
                        "source": self.portal_name
                    })
                    count += 1
                    
                    # Stop logic
                    if status == "existing":
                        consecutive_existing += 1
                    elif status == "new" or status == "updated":
                        consecutive_existing = 0
                    
                    if self.should_stop_scraping(consecutive_existing):
                        break

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

