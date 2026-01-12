import logging
import asyncio
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from playwright.async_api import Page, async_playwright, Browser, BrowserContext
from crud import create_property, get_property_by_link, update_property_last_seen, update_property_price

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .config import SEARCH_CRITERIA, should_include_property

class BaseScraper(ABC):
    def __init__(self, db: Session):
        self.db = db
        self.portal_name = "generic" # Should be overwritten
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self._playwright = None

    async def init_browser(self, headless: bool = True):
        """Initialize Playwright browser, context, and page."""
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()

    async def close_browser(self):
        """Close browser and stop Playwright."""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """Navigate to a URL using the initialized page."""
        if not self.page:
            await self.init_browser()
        
        logger.info(f"[{self.portal_name}] Navigating to {url}")
        await self.page.goto(url, wait_until=wait_until, timeout=60000)

    @abstractmethod
    async def scrape(self):
        """Main scraping logic to be implemented by subclasses."""
        pass

    async def process_property(self, data: dict) -> str:
        """
        Standard logic to save or update a property.
        'data' dictionary must contain: title, price, location, link
        
        Returns:
            str: 'new', 'updated', 'existing', or 'skipped'
        """
        link = data["link"]
        title = data.get("title", "")
        location = data.get("location", "")
        price = data.get("price", 0)

        # Ensure source is set
        if "source" not in data:
            data["source"] = self.portal_name

        # --- PHASE 5: Pre-Save Filtering ---
        # 1. Price Check
        if price > SEARCH_CRITERIA["max_price"]:
            logger.debug(f"[{self.portal_name}] Skipped (Price > {SEARCH_CRITERIA['max_price']}): {price} - {link}")
            return "skipped"

        # 2. Location/Zone Check
        if not should_include_property(title, location):
            logger.debug(f"[{self.portal_name}] Skipped (Zone not matched): {title} | {location} - {link}")
            return "skipped"
        # -----------------------------------

        # --- DB Persist (Async-safe) ---
        # Moving synchronous DB calls to a separate thread to avoid blocking the event loop
        def persist_db():
            existing = get_property_by_link(self.db, link)
            
            if existing:
                update_property_last_seen(self.db, existing)
                # Update price if changed
                if existing.price != data["price"]:
                    update_property_price(self.db, existing, data["price"])
                    return "updated"
                else:
                    return "existing"
            else:
                create_property(self.db, data)
                return "new"

        status = await asyncio.to_thread(persist_db)
        
        if status == "updated":
            logger.info(f"[{self.portal_name}] Updated Price: {link}")
        elif status == "existing":
            logger.info(f"[{self.portal_name}] Seen (No Change): {link}")
        elif status == "new":
            logger.info(f"[{self.portal_name}] Created: {link}")
            
        return status

    def should_stop_scraping(self, consecutive_existing: int, max_consecutive: int = 10) -> bool:
        """
        Check if we should stop scraping based on consecutive existing items.
        """
        if consecutive_existing >= max_consecutive:
            logger.info(f"[{self.portal_name}] Stopping: Found {consecutive_existing} consecutive existing items.")
            return True
        return False

    async def dump_html(self, page: Page = None, prefix: str = "debug"):
        """Helper to save HTML for debugging."""
        target_page = page or self.page
        if not target_page:
            logger.error(f"[{self.portal_name}] No page to dump.")
            return

        filename = f"{prefix}_{self.portal_name}.html"
        try:
            content = await target_page.content()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved debug HTML to {filename}")
        except Exception as e:
            logger.error(f"Failed to dump HTML: {e}")


