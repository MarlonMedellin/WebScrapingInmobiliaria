import asyncio
import logging
import argparse
from sqlalchemy.orm import Session
from database import SessionLocal
from scrapers.albertoalvarez import AlbertoAlvarezScraper
from scrapers.ayura import AyuraScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LocalSeeder")

SCRAPERS = {
    "albertoalvarez": AlbertoAlvarezScraper,
    "ayura": AyuraScraper
}

async def seed_portal(portal_name: str, max_pages: int, headless: bool):
    logger.info(f"Starting Seeding for {portal_name} with max_pages={max_pages}")
    
    db: Session = SessionLocal()
    scraper_class = SCRAPERS.get(portal_name)
    
    if not scraper_class:
        logger.error(f"Scraper not found for {portal_name}")
        return

    scraper = scraper_class(db)
    
    # --- ACTIVATE SEED MODE ---
    scraper.seed_mode = True
    scraper.max_pages = max_pages
    # --------------------------

    try:
        await scraper.init_browser(headless=headless)
        await scraper.scrape()
        logger.info(f"Seeding completed for {portal_name}")
    except Exception as e:
        logger.error(f"Critical error in seeder: {e}")
    finally:
        await scraper.close_browser()
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Deep Scrape Seeder")
    parser.add_argument("--portal", required=True, help="Portal key (e.g., albertoalvarez)")
    parser.add_argument("--max-pages", type=int, default=1000, help="Max pages to scrape")
    parser.add_argument("--visible", action="store_true", help="Show browser window (not headless)")
    
    args = parser.parse_args()
    
    asyncio.run(seed_portal(args.portal, args.max_pages, not args.visible))
