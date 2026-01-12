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

# Mapping of config neighborhoods to Fincaraiz URL slugs
SLUGS = {
    "santa fe": "santa-fe",
    "san pablo": "san-pablo",
    "campo amor": "campo-amor",
    "santafe": "santa-fe",
    "santa fé": "santa-fe"
}

class FincaRaizScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "fincaraiz"

    async def scrape(self):
        try:
            # FIXED: Use explicit Arriendo URL to avoid mixing Venta results
            # We'll scrape the general Arriendo page for Medellin with price filter
            base_url = "https://www.fincaraiz.com.co/arriendo/apartamentos-casas-apartaestudios/medellin"
            max_price = SEARCH_CRITERIA["max_price"]
            
            # Single URL with price filter - let base.py filter by zone
            search_url = f"{base_url}?precioHasta={max_price}"
            logger.info(f"[{self.portal_name}] Scraping: {search_url}")
            
            await self._scrape_single_url(search_url)

        finally:
            await self.close_browser()

    async def _scrape_single_url(self, url):
        try:
            await self.navigate(url)
            
            # Wait for content to load
            try:
                await self.page.wait_for_selector("div.listingCard", timeout=10000)
            except Exception as e:
                logger.warning(f"[{self.portal_name}] No content found for {url}")
                return

            # Scroll to load more items
            scrolls = SEARCH_CRITERIA.get("scroll_depth", 3)
            for _ in range(scrolls):
                await self.page.mouse.wheel(0, 1000)
                await asyncio.sleep(1)

            # Extract Items
            cards = await self.page.locator("div.listingCard").all()
            
            logger.info(f"[{self.portal_name}] Found {len(cards)} listings")
            
            consecutive_existing = 0

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

                    # Process Data - base.py will filter by price and zone
                    status = await self.process_property({
                        "title": title_text.strip() if title_text else "No Title",
                        "price": price,
                        "location": location_text.strip() if location_text else "Medellín",
                        "link": full_link,
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
                    logger.error(f"Error parsing card {i}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error scraping url {url}: {e}")

def run_scraper_manual():
    db = SessionLocal()
    scraper = FincaRaizScraper(db)
    asyncio.run(scraper.scrape())
    db.close()

if __name__ == "__main__":
    run_scraper_manual()
