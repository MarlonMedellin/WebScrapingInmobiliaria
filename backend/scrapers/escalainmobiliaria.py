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
            
            cards = soup.select(".card.card-space")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    link_tag = card.select_one("a.inmueblelink")
                    if not link_tag: continue
                    full_link = link_tag['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}{full_link}"

                    # Title & Type (Escala suele tener el tipo en el link o breadcrumb, usamos el link text o un genérico)
                    title = "Apartamento en Arriendo"
                    title_tag = card.select_one(".cb-nombre")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    
                    # Price
                    price_tag = card.select_one("h4")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Image
                    image_tag = card.select_one(".card-img-top img")
                    image_url = image_tag['src'] if image_tag else None

                    # Features (Area, Rooms, Baths)
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    location = "Medellín"
                    
                    # Las ubicaciones están en .vi-link-ubicacion, el último suele ser el barrio
                    loc_tags = card.select(".vi-link-ubicacion")
                    if loc_tags:
                        location = ", ".join([l.get_text(strip=True) for l in loc_tags])

                    # Características suelen estar en spans dentro del card
                    # Buscamos por texto ya que las clases pueden variar
                    spans = card.select("span")
                    for s in spans:
                        text = s.get_text(strip=True).lower()
                        if "m2" in text or "m²" in text:
                            match = re.search(r'([\d.,]+)', text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif "alcoba" in text or "hab" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bedrooms = int(match.group(1))
                        elif "baño" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bathrooms = int(match.group(1))

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
