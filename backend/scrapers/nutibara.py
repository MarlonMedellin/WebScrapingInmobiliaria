from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class NutibaraScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "nutibara"
        self.base_url = "https://anutibara.com"

    async def scrape(self):
        try:
            # La URL sugerida por el usuario que incluye tipos residenciales
            # Arrendamientos Nutibara usa una URL tipo search con parámetros
            base_search_url = f"{self.base_url}/search/apartaestudio-apartamento-casa/arriendo/all"
            
            logger.info(f"[{self.portal_name}] Iniciando scraping masivo residencial")
            await self._scrape_url(base_search_url)
                
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 10:  # Límite de seguridad
            # Nutibara usa ?pagina=X
            current_url = f"{base_url}?pagina={page_num}&isEmpty=0"
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar a que el contenido de Nuxt cargue
            await self.page.wait_for_selector(".card-container", timeout=15000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".card-container")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    full_link = card.get('href')
                    if full_link and not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    if not full_link: continue

                    # Title / Type
                    type_tag = card.select_one(".text-type")
                    prop_type = type_tag.get_text(strip=True) if type_tag else "Inmueble"
                    
                    # Location (Barrio)
                    loc_tag = card.select_one(".neighbourhood")
                    neighborhood = loc_tag.get_text(strip=True) if loc_tag else ""
                    location = f"{neighborhood}, Medellín" if neighborhood else "Medellín"

                    # Price
                    # Buscamos el div.priceCode que contenga el símbolo $
                    price = 0
                    price_tags = card.select(".priceCode span.text")
                    for p_tag in price_tags:
                        text = p_tag.get_text(strip=True)
                        if "$" in text:
                            price = int(re.sub(r'[^\d]', '', text))
                            break
                    
                    # Image
                    image_tag = card.select_one(".image") # En Nutibara la clase suele estar en el img dentro del container
                    if not image_tag:
                        image_tag = card.select_one("img.image")
                    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None

                    # Features (Amenities)
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    amenity_items = card.select(".amenity-item")
                    for item in amenity_items:
                        img_tag = item.select_one("img")
                        span_tag = item.select_one("span")
                        if not img_tag or not span_tag: continue
                        
                        title_attr = img_tag.get('title', '').lower()
                        val_text = span_tag.get_text(strip=True).lower()
                        
                        if "área" in title_attr or "area" in title_attr:
                            match = re.search(r'([\d.,]+)', val_text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif "habitaciones" in title_attr or "alcobas" in title_attr:
                            match = re.search(r'(\d+)', val_text)
                            if match: bedrooms = int(match.group(1))
                        elif "baños" in title_attr:
                            match = re.search(r'([\d.,]+)', val_text)
                            if match: bathrooms = float(match.group(1).replace(',', '.'))

                    entry = {
                        "title": f"{prop_type} en {neighborhood}",
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
            await self.page.wait_for_timeout(1500)
