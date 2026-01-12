import asyncio
import logging
from celery import shared_task
from database import SessionLocal
from scrapers.factory import ScraperFactory
from core.worker import celery_app
from crud import archive_stale_properties

logger = logging.getLogger(__name__)

# Async wrapper for Celery
# Playwright is async, Celery is sync by default. We need a bridge.
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@celery_app.task(name="scrape_portal")
def scrape_portal_task(portal_name: str):
    logger.info(f"Starting generic scrape task for: {portal_name}")
    db = SessionLocal()
    try:
        scraper = ScraperFactory.get_scraper(portal_name, db)
        run_async(scraper.scrape())
        logger.info(f"Finished scraping: {portal_name}")
        return f"Scraped {portal_name}"
    except Exception as e:
        logger.error(f"Error scraping {portal_name}: {e}")
        raise e
    finally:
        db.close()

@celery_app.task(name="scrape_all")
def scrape_all_task():
    logger.info("Starting scrape ALL task")
    # In a real heavy production env, this might spawn child tasks.
    # For now, sequential execution in one worker or parallel if multiple workers are up.
    # Let's verify we can access the list.
    portals = [
        "fincaraiz", "elcastillo", "santafe", "panda", 
        "integridad", "protebienes", "lacastellana", "monserrate", "aportal"
    ]

    results = {}
    
    # We can trigger them as sub-tasks or run them here. 
    # Triggering sub-tasks is better for scaling.
    for p in portals:
        scrape_portal_task.delay(p)
        
    return f"Triggered scraping for {portals}"

@celery_app.task(name="cleanup_stale_properties")
def cleanup_stale_properties_task(days: int = 3):
    logger.info(f"Starting cleanup of stale properties (older than {days} days)")
    db = SessionLocal()
    try:
        count = archive_stale_properties(db, days=days)
        logger.info(f"Archived {count} stale properties")
        return f"Archived {count} properties"
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        raise e
    finally:
        db.close()
