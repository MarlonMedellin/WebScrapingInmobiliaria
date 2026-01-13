import asyncio
import logging
import argparse
from sqlalchemy.orm import Session
from database import SessionLocal
from scrapers.albertoalvarez import AlbertoAlvarezScraper
from scrapers.ayura import AyuraScraper
from scrapers.santafe import SantaFeScraper
from scrapers.protebienes import ProtebienesScraper
from scrapers.integridad import IntegridadScraper
from scrapers.lacastellana import CastellanaScraper
from scrapers.panda import PandaScraper
from scrapers.elcastillo import ElCastilloScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LocalSeeder")

SCRAPERS = {
    "albertoalvarez": AlbertoAlvarezScraper,
    "ayura": AyuraScraper,
    "santafe": SantaFeScraper,
    "protebienes": ProtebienesScraper,
    "integridad": IntegridadScraper,
    "lacastellana": CastellanaScraper,
    "elcastillo": ElCastilloScraper,
    "panda": PandaScraper
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

import requests
import sys

def verify_ip():
    FORBIDDEN_IP = "191.109.114.36"
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=10)
        current_ip = response.json().get("ip")
        logger.info(f"Current IP Scan: {current_ip}")
        
        if current_ip == FORBIDDEN_IP:
            logger.error(f"🛑 SEGURIDAD ACTIVADA: Estás usando tu IP real ({current_ip}).")
            logger.error("Por favor ACTIVA LA VPN antes de continuar.")
            sys.exit(1)
        else:
            logger.info("✅ IP Segura detectada (VPN o distinta a la local). Procediendo.")
            
    except Exception as e:
        logger.warning(f"No se pudo verificar la IP ({e}). Procediendo con precaución...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Deep Scrape Seeder")
    parser.add_argument("--portal", required=True, help="Portal key (e.g., albertoalvarez)")
    parser.add_argument("--max-pages", type=int, default=1000, help="Max pages to scrape")
    parser.add_argument("--visible", action="store_true", help="Show browser window (not headless)")
    
    args = parser.parse_args()
    
    # Verify IP before doing anything else
    verify_ip()
    
    asyncio.run(seed_portal(args.portal, args.max_pages, not args.visible))
