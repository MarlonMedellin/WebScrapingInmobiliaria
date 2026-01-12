from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class SuViviendaScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "suvivienda"
        self.base_url = "https://www.suvivienda.com.co"

    async def scrape(self):
        try:
            # Tipos de inmuebles a rastrear
            property_types = ["apartamento", "casa", "apartaestudios", "loft", "estudio"]
            
            for p_type in property_types:
                # La URL usa el nombre del tipo en la ruta
                # Normalizamos un poco para la URL (suvivienda usa Capitalizado generalmente pero el router suele ser flexible)
                url_type = p_type.capitalize()
                url = f"{self.base_url}/inmuebles/Arriendo/{url_type}/Medellín/"
                logger.info(f"[{self.portal_name}] Iniciando scraping para tipo: {p_type}")
                await self._scrape_url(url)
                
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 10:  # Límite de seguridad
            current_url = f"{base_url.rstrip('/')}/{page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".property_item")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades en esta sección.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link & Title
                    link_tag = card.select_one(".property_head h3 a")
                    if not link_tag: continue
                    
                    full_link = link_tag['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}{full_link}"
                    
                    title = link_tag.get_text(strip=True)

                    # Price
                    price_tag = card.select_one(".favroute2 p")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Image
                    image_tag = card.select_one(".image img")
                    image_url = image_tag['src'] if image_tag else None

                    # Location
                    loc_tag = card.select_one(".proerty_text h4")
                    location = loc_tag.get_text(strip=True) if loc_tag else "Medellín"

                    # Features
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    meta_spans = card.select(".property_meta span")
                    for span in meta_spans:
                        text = span.get_text(strip=True).lower()
                        if "m2" in text or "m²" in text:
                            match = re.search(r'([\d.,]+)', text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif "alcoba" in text or "hab" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bedrooms = int(match.group(1))
                        elif "baño" in text:
                            match = re.search(r'([\d.,]+)', text)
                            if match: bathrooms = float(match.group(1).replace(',', '.'))

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
            
            page_num += 1
            await self.page.wait_for_timeout(1000)
