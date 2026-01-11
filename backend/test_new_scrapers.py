
import asyncio
import logging
import sys
from database import SessionLocal
from scrapers.factory import ScraperFactory

logging.basicConfig(level=logging.INFO)

async def test_portal(portal_name: str):
    db = SessionLocal()
    print(f"Testing {portal_name} Scraper...")
    try:
        scraper = ScraperFactory.get_scraper(portal_name, db)
        await scraper.scrape()
        print(f"Finished testing {portal_name}")
    except Exception as e:
        print(f"Error testing {portal_name}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        portal = sys.argv[1]
        asyncio.run(test_portal(portal))
    else:
        print("Please provide a portal name: fincaraiz, elcastillo, santafe, panda, integridad, protebienes, lacastellana, monserrate, aportal")
