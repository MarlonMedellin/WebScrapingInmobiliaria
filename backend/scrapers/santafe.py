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

    async def scrape(self):
        try:
            # URL proporcionada por el usuario con filtros masivos
            url = f"{self.base_url}/propiedades/?bussines_type=Arrendar&desde=0&hasta=50000000&min_price=0&max_price=50000000&alcobas=&banios=&garaje=&min_area=&max_area="
            logger.info(f"[{self.portal_name}] Iniciando scraping masivo")
            await self._scrape_url(url)
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 15:  # Límite de seguridad
            current_url = f"{base_url}&page={page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar a que las tarjetas carguen
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

                    # Title / Type
                    type_tag = card.select_one(".tipo-inmueble")
                    prop_type = type_tag.get_text(strip=True).replace("Tipo:", "").strip() if type_tag else "Inmueble"
                    title = f"{prop_type} en {location}"

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

                    # Los baños no suelen estar en el listado de Santa Fe, pero lo dejamos por si acaso
                    # o se podría extraer del detalle si fuera crítico.

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
