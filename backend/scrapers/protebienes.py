from bs4 import BeautifulSoup
from .base import BaseScraper
import logging
import re

from .config import SEARCH_CRITERIA
logger = logging.getLogger(__name__)

class ProtebienesScraper(BaseScraper):
    """
    Scraper for Protebienes.
    
    GOLDEN RULES:
    1. Golden URL: /inmuebles/Arriendo/{page_num} (Simple integer pagination).
    2. Card Detection: Selector '.property_item' determines valid content.
    3. Pagination Stop: Breaks loop if card selector returns empty list.
    4. Image Fix: Handles relative (//) and root-relative URLs for images.
    """
    def __init__(self, db):
        super().__init__(db)
        self.portal_name = "protebienes"
        self.base_url = "https://www.inmobiliariaprotebienes.com"

    async def scrape(self):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= self.max_pages:
            # GOLDEN URL PARAMETERS (Verified 2026-01-13)
            # Pattern: /inmuebles/Arriendo/{page_num}
            url = f"{self.base_url}/inmuebles/Arriendo/{page_num}"
            logger.info(f"[{self.portal_name}] Scraping page {page_num}: {url}")
            
            try:
                await self.navigate(url)
                
                # Check if page exists (redirects or empty content)
                # Protebienes usually redirects to page 1 or shows empty list if out of bounds
                # We'll rely on card count
                
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                cards = soup.select(".property_item")
                if not cards:
                    logger.info(f"[{self.portal_name}] No properties found on page {page_num}. Stopping.")
                    break
                    
                logger.info(f"[{self.portal_name}] Found {len(cards)} properties on page {page_num}")
                
                 # --- LOOP DETECTION ---
                # Simple check: if we see the same first property title/link as previous page?
                # For now rely on consecutive_existing and card count.
                # ----------------------

                for card in cards:
                    try:
                        # Title and Link
                        title_tag = card.select_one(".property_head h3 a")
                        if not title_tag:
                            continue
                        title = title_tag.get_text(strip=True)
                        link = title_tag['href']
                        if not link.startswith("http"):
                            link = f"{self.base_url}{link}"
                        
                        # Image
                        image_tag = card.select_one(".image img")
                        image_url = image_tag['src'] if image_tag else None
                        if image_url and image_url.startswith("//"):
                            image_url = f"https:{image_url}"
                        elif image_url and not image_url.startswith("http"):
                            image_url = f"{self.base_url}{image_url}"
                        
                        # Price
                        price_tag = card.select_one(".favroute2 p")
                        price_text = price_tag.get_text(strip=True) if price_tag else "0"
                        price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                        
                        # Location
                        loc_tag = card.select_one(".proerty_text h4")
                        location = loc_tag.get_text(strip=True) if loc_tag else "Medellín"
                        
                        # Meta (m2, rooms)
                        area = 0
                        bedrooms = 0
                        meta_spans = card.select(".property_meta span")
                        for span in meta_spans:
                            text = span.get_text(strip=True).lower()
                            if "m2" in text or "m²" in text:
                                num_match = re.search(r'([\d.]+)', text)
                                if num_match:
                                    area = float(num_match.group(1))
                            elif "alcoba" in text or "bed" in text or "hab" in text:
                                num_match = re.search(r'(\d+)', text)
                                if num_match:
                                    bedrooms = int(num_match.group(1))

                        status = await self.process_property({
                            "title": title,
                            "price": price,
                            "location": location,
                            "link": link,
                            "image_url": image_url,
                            "area": area,
                            "bedrooms": bedrooms,
                            "source": self.portal_name
                        })

                        # Stop logic
                        if status == "existing":
                            consecutive_existing += 1
                        elif status == "new" or status == "updated":
                            consecutive_existing = 0
                        
                    except Exception as e:
                        logger.error(f"[{self.portal_name}] Error parsing card: {e}")
                        continue

                if self.should_stop_scraping(consecutive_existing):
                    logger.info(f"[{self.portal_name}] Limit reached. Stopping.")
                    break

            except Exception as e:
                logger.error(f"[{self.portal_name}] Error parsing card/page: {e}")
                
            page_num += 1
        
        await self.close_browser()
