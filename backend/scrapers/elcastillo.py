from .base import BaseScraper
from bs4 import BeautifulSoup
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

class ElCastilloScraper(BaseScraper):
    """
    Scraper for Arrendamientos El Castillo.
    
    GOLDEN RULES:
    1. Infinite Scroll: Uses window.scrollTo with a robust loop to load all cards.
    2. Wait Time: Must wait at least 6 seconds (6000ms) after scroll to ensure JS fetch completes.
    3. Location Fix: Appends ", Medellín" to locations (e.g., "BELEN PARQUE") to pass the 'should_include_property' filter.
    4. Field Cleaning: Ignores 'garage' field as it's not supported by the current Property model.
    """
    
    def __init__(self, db_session):
        super().__init__(db_session)
        self.portal_name = "elcastillo"
        self.base_url = "https://www.arrendamientoselcastillo.com.co"

    async def scrape(self):
        url = f"{self.base_url}/resultados?gestion=Arriendo"
        
        logger.info(f"[{self.portal_name}] Navigating to {url}")
        
        await self.navigate(url)
        await self.page.wait_for_timeout(3000) # Wait for initial load

        # Iterate until no new cards are loaded
        last_count = 0
        retries = 0
        max_retries = 10 # High retry count for stability during network lags
        
        processed_ids = set()
        
        while True:
            # GOLDEN RULE: Scroll to bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # GOLDEN RULE: Wait 6s for dynamic content
            await self.page.wait_for_timeout(6000) 
            
            # Check for new cards
            cards = await self.page.locator(".estate_itm").all()
            current_count = len(cards)
            
            logger.info(f"[{self.portal_name}] Current visible cards: {current_count}")
            
            if current_count == last_count:
                retries += 1
                logger.info(f"[{self.portal_name}] No new cards found (Retry {retries}/{max_retries})")
                if retries >= max_retries:
                    logger.info(f"[{self.portal_name}] Infinite scroll finished. Total cards: {current_count}")
                    break
            else:
                retries = 0
                last_count = current_count
                
                # Check for max pages limit (if set, e.g., for testing)
                if self.max_pages and retries == 0:
                   # treat approx 20 cards as a 'page'
                   if current_count // 20 >= self.max_pages:
                       logger.info(f"[{self.portal_name}] Reached max pages/scrolls limit ({self.max_pages}). Stopping.")
                       break

                content = await self.page.content()
                await self.process_html(content, processed_ids)

    async def process_html(self, content, processed_ids):
        soup = BeautifulSoup(content, 'html.parser')
        cards = soup.select(".estate_itm")
        
        new_cards_count = 0
        for card in cards:
            try:
                # Extract ID/Code
                code_span = card.select_one("._top span")
                code_text = code_span.get_text(strip=True) if code_span else ""
                code = re.sub(r'[^0-9]', '', code_text)
                
                if not code or code in processed_ids:
                    continue
                
                processed_ids.add(code)
                new_cards_count += 1
                
                # Link
                link_tag = card.select_one("._estate-link a")
                link = link_tag['href'] if link_tag else ""
                if not link:
                    # Fallback for onclick handling
                    onclick_tag = card.select_one("h4[onclick]")
                    if onclick_tag:
                         match = re.search(r"window.open\('([^']+)'\)", onclick_tag['onclick'])
                         if match:
                             link = match.group(1)

                if not link:
                    continue

                # Title & Location
                title_tag = card.select_one("h4")
                title = title_tag.get_text(strip=True) if title_tag else ""
                
                # GOLDEN RULE: Location Fix (Append City)
                location = "Medellín"
                if "-" in title:
                    sub_loc = title.split("-")[-1].strip()
                    location = f"{sub_loc}, Medellín"

                # Price
                price_tag = card.select_one(".price p")
                price_text = price_tag.get_text(strip=True) if price_tag else "0"
                price = int(re.sub(r'[^0-9]', '', price_text)) if re.sub(r'[^0-9]', '', price_text) else 0

                # Area
                area = 0
                area_tag = card.select_one(".size small")
                if area_tag:
                    area_text = area_tag.get_text(strip=True)
                    # "70 m²"
                    area = float(re.sub(r'[^0-9.]', '', area_text)) if re.sub(r'[^0-9.]', '', area_text) else 0

                # Bedrooms, Bathrooms, Garage
                bedrooms = 0
                bathrooms = 0
                garage = 0
                
                info_items = card.select("._info-itm")
                for item in info_items:
                    text = item.get_text(strip=True).lower()
                    if "alcobas" in text:
                        bedrooms = int(re.sub(r'[^0-9]', '', text)) if re.sub(r'[^0-9]', '', text) else 0
                    elif "baños" in text:
                        bathrooms = int(re.sub(r'[^0-9]', '', text)) if re.sub(r'[^0-9]', '', text) else 0
                    elif "parq" in text:
                        garage = int(re.sub(r'[^0-9]', '', text)) if re.sub(r'[^0-9]', '', text) else 0

                # Image
                image_tag = card.select_one("picture img")
                image_url = image_tag['src'] if image_tag else None

                description = title

                data = {
                    "title": title,
                    "price": price,
                    "location": location,
                    "link": link,
                    "image_url": image_url,
                    "area": area,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    # 'garage' excluded as it is not in the Property model
                    "source": self.portal_name,
                    "description": description
                }
                
                await self.process_property(data)
                
            except Exception as e:
                logger.error(f"[{self.portal_name}] Error parsing card {code}: {e}")
                continue
        
        if new_cards_count > 0:
            logger.info(f"[{self.portal_name}] Processed {new_cards_count} new cards this batch")
