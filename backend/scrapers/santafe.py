from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class SantaFeScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "santafe"
        self.base_url = "https://arrendamientossantafe.com"
        self.last_page_links = set()


    async def scrape(self):
        try:
            # GOLDEN URL PARAMETERS (Verified 2026-01-13)
            # 1. 'page' param must be FIRST.
            # 2. Must use double ampersand '&&' separator.
            # 3. 'bussines_type=Arrendar' is sufficient, no extra filters needed.
            base_url = f"{self.base_url}/propiedades/?page=1&&bussines_type=Arrendar"
            logger.info(f"[{self.portal_name}] Iniciando scraping (URL Patrón: ?page=X&&...)")
            await self._scrape_url(base_url)
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while self.should_continue(page_num, consecutive_existing):
            # Construction Pattern: ?page={num}&&bussines_type=Arrendar
            current_url = f"{self.base_url}/propiedades/?page={page_num}&&bussines_type=Arrendar"

            
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            # --- LOOP DETECTION ---
            current_links = set()
            # ----------------------
            
            await self.navigate(current_url)
            # Add delay to allow rendering and simulated human behavior
            import random
            await self.page.wait_for_timeout(random.randint(3000, 5000))
            
            await self.page.wait_for_selector(".inner-card", timeout=15000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".inner-card")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    link_tag = card.select_one('a[href^="/propiedad/"]')
                    if not link_tag: continue
                    full_link = link_tag['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    # Track link for loop detection
                    current_links.add(full_link)

                    # Image
                    image_url = None
                    img_preview = card.select_one(".img-preview")
                    if img_preview and 'style' in img_preview.attrs:
                        style = img_preview['style']
                        match = re.search(r'url\((.*?)\)', style)
                        if match:
                            image_url = match.group(1).strip().strip('"').strip("'")

                    # Location (Sector)
                    loc_tag = card.select_one(".sector p")
                    location = loc_tag.get_text(strip=True).replace("Ubicación:", "").strip() if loc_tag else "Medellín"
                    if "medellín" not in location.lower() and "medellin" not in location.lower():
                        location = f"{location}, Medellín"

                    # Title / Type
                    type_tag = card.select_one(".tipo-inmueble")
                    property_type_raw = type_tag.get_text(strip=True).replace("Tipo:", "").strip() if type_tag else "Inmueble"
                    title = f"{property_type_raw} en {location}"

                    # Price
                    price_tag = card.select_one(".precio p")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Features
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    area_tag = card.select_one(".area")
                    if area_tag:
                        text = area_tag.get_text(strip=True).lower()
                        match = re.search(r'([\d.,]+)', text)
                        if match: area = float(match.group(1).replace(',', '.'))

                    alcobas_tag = card.select_one(".alcobas")
                    if alcobas_tag:
                        text = alcobas_tag.get_text(strip=True)
                        match = re.search(r'(\d+)', text)
                        if match: bedrooms = int(match.group(1))

                    entry = {
                        "title": title,
                        "price": price,
                        "location": location,
                        "link": full_link,
                        "image_url": image_url,
                        "source": self.portal_name,
                        "area": area,
                        "bedrooms": bedrooms,
                        "bathrooms": bathrooms
                    }
                    
                    status = await self.process_property(entry)
                    
                    if status == "existing":
                        consecutive_existing += 1
                    elif status in ["new", "updated"]:
                        consecutive_existing = 0
                    
                    if self.should_stop_scraping(consecutive_existing):
                        logger.info(f"[{self.portal_name}] Límite de inmuebles existentes alcanzado.")
                        return 

                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error procesando card: {e}")
                    continue
            
            # --- Check for Infinite Loop (Page N == Page N-1) ---
            if page_num > 1 and current_links == self.last_page_links:
                logger.warning(f"[{self.portal_name}] 🛑 LOOP DETECTED: Page {page_num} is identical to Page {page_num-1}. Server is ignoring 'page' param.")
                break
            
            self.last_page_links = current_links
            # ----------------------------------------------------

            page_num += 1
            await self.page.wait_for_timeout(1000)

    def should_continue(self, page_num, consecutive_existing):
        if self.seed_mode:
            return page_num <= self.max_pages
        return not self.should_stop_scraping(consecutive_existing)
