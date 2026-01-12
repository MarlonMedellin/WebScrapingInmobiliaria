from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class PortofinoScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "portofino"
        self.base_url = "https://portofinopropiedadraiz.com"

    async def scrape(self):
        try:
            # IDs de tipos de inmuebles (tomados de la auditoría)
            # 1247: Apartamento, 1253: Apartaestudio, 1249: Casa
            property_type_ids = ["1247", "1253", "1249"]
            
            for type_id in property_type_ids:
                # Servicio=1 es Arriendo, Municipio=1 es Medellín
                url = f"{self.base_url}/resultados-de-busqueda/?Servicio=1&TipoInmueble={type_id}&Municipio=1"
                logger.info(f"[{self.portal_name}] Iniciando scraping para TipoInmueble: {type_id}")
                await self._scrape_url(url)
                
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 10:
            current_url = f"{base_url}&Pagina={page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar un poco a que cargue el contenido dinámico de Arrendasoft
            await self.page.wait_for_timeout(2000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # El selector de las tarjetas es el tag <a> que envuelve todo
            cards = soup.select('a[href*="detalle-propiedad"]')
            
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    full_link = card['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    # Title
                    title_tag = card.select_one(".body p.rojo")
                    title = title_tag.get_text(strip=True) if title_tag else "Inmueble en Arriendo"

                    # Price
                    price_tag = card.select_one(".body .contenedor2 p span.parse-float")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Image
                    image_tag = card.select_one(".image img")
                    image_url = image_tag['src'] if image_tag else None

                    # Location
                    loc_tag = card.select_one(".body .contenedor2 p") # El primer p suele ser la ubicación
                    location = loc_tag.get_text(strip=True) if loc_tag else "Medellín"

                    # Features
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    icons_span = card.select(".body .iconos span")
                    for span in icons_span:
                        text = span.get_text(strip=True).lower()
                        if "mt2" in text or "m2" in text:
                            match = re.search(r'([\d.,]+)', text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif "hab" in text or "alcoba" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bedrooms = int(match.group(1))
                        elif "baño" in text:
                            match = re.search(r'(\d+)', text)
                            if match: bathrooms = float(match.group(1))

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
            
            # Verificar si existe el botón "Siguiente" real en el DOM
            # Si no hay botón '#' o similar, o si se detecta el final del listado
            # (Arrendasoft a veces muestra las mismas tarjetas si la página no existe)
            page_num += 1
            await self.page.wait_for_timeout(1000)
