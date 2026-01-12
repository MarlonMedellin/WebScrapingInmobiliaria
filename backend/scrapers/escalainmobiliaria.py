from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class EscalaInmobiliariaScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "escalainmobiliaria"
        self.base_url = "https://escalainmobiliaria.com.co"

    async def scrape(self):
        try:
            # URL específica para Apartamentos en Arriendo en Medellín
            url = f"{self.base_url}/inmuebles/g/arriendo/t/apartamentos/c/medellin/"
            await self._scrape_url(url)
        finally:
            await self.close_browser()

    async def _scrape_url(self, url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 5:  # Límite de seguridad de 5 páginas
            current_url = f"{url}?pagina={page_num}" if page_num > 1 else url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".vi-cont-card")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    link_tag = card.select_one("a.vi-link-card")
                    if not link_tag: continue
                    full_link = link_tag['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}{full_link}"

                    # Title & Type
                    title_tag = card.select_one(".vi-title-card")
                    title = title_tag.get_text(strip=True) if title_tag else "Apartamento en Arriendo"
                    
                    # Price
                    price_tag = card.select_one(".vi-price-card")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Image
                    image_tag = card.select_one(".vi-img-card img")
                    image_url = image_tag['src'] if image_tag else None

                    # Features (Area, Rooms, Baths)
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    location = "Medellín"
                    
                    features = card.select(".vi-inf-card span")
                    for feat in features:
                        text = feat.get_text(strip=True).lower()
                        if "m2" in text or "m²" in text:
                            match = re.search(r'([\d.,]+)', text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif "alcoba" in text or "hab" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bedrooms = int(match.group(1))
                        elif "baño" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bathrooms = int(match.group(1))

                    # Ubicación específica (generalmente en una etiqueta p o div)
                    loc_tag = card.select_one(".vi-loc-card")
                    if loc_tag:
                        location = loc_tag.get_text(strip=True)

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
                        return # Stop everything if limit reached

                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error procesando card: {e}")
                    continue
            
            page_num += 1
            await self.page.wait_for_timeout(1000) # Respeto entre páginas
