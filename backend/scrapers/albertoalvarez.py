from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re
import json

logger = logging.getLogger(__name__)

class AlbertoAlvarezScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "albertoalvarez"
        self.base_url = "https://albertoalvarez.com"

    async def scrape(self):
        try:
            # Tipos de inmueble proporcionados por el usuario
            types = ["apartamento", "apartaestudio", "casa"]
            
            for p_type in types:
                url = f"{self.base_url}/inmuebles/arrendamientos/{p_type}/medellin/"
                logger.info(f"[{self.portal_name}] Iniciando scraping para tipo: {p_type}")
                await self._scrape_url(url)
                
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 15:  # Límite de seguridad
            current_url = f"{base_url}?pag={page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar a que las tarjetas carguen
            await self.page.wait_for_selector(".property", timeout=15000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".property")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Alberto Alvarez incluye un JSON en un textarea oculto, ¡muy útil!
                    json_tag = card.select_one("textarea.field-property")
                    prop_data = {}
                    if json_tag:
                        try:
                            prop_data = json.loads(json_tag.get_text(strip=True))
                        except Exception as je:
                            logger.error(f"[{self.portal_name}] Error parseando JSON de propiedad: {je}")

                    # Extraer datos con fallback
                    code = prop_data.get("code", "")
                    property_type = prop_data.get("propertyType", "Inmueble")
                    neighborhood = prop_data.get("sectorName", "")
                    city = prop_data.get("cityName", "Medellín")
                    
                    # Link
                    link_tag = card.select_one('a[href*="/inmuebles/detalle/"]')
                    full_link = link_tag['href'] if link_tag else ""
                    if full_link and not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    if not full_link: continue

                    # Title
                    title = f"{property_type} en {neighborhood or 'Medellín'}"
                    
                    # Price
                    price = prop_data.get("rentValue", 0)
                    if not price:
                        price_tag = card.select_one(".price")
                        price_text = price_tag.get_text(strip=True) if price_tag else "0"
                        price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0

                    # Image
                    image_tag = card.select_one("img.img-fill")
                    image_url = image_tag['src'] if image_tag else None

                    # Features
                    area = prop_data.get("builtArea", 0)
                    bedrooms = prop_data.get("numberOfRooms", 0)
                    bathrooms = prop_data.get("householdFeatures", {}).get("baths", 0)

                    # Fallbacks if JSON fails to provide features
                    if not area:
                        specs = card.select(".specs li")
                        if len(specs) >= 1:
                            area_match = re.search(r'(\d+)', specs[0].get_text())
                            if area_match: area = float(area_match.group(1))

                    location = f"{neighborhood}, {city}" if neighborhood else city

                    entry = {
                        "title": title,
                        "price": price,
                        "location": location,
                        "link": full_link,
                        "image_url": image_url,
                        "source": self.portal_name,
                        "area": float(area) if area else 0,
                        "bedrooms": int(bedrooms) if bedrooms else 0,
                        "bathrooms": float(bathrooms) if bathrooms else 0
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
            await self.page.wait_for_timeout(1500)
