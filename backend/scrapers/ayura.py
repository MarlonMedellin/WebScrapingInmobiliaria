from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class AyuraScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "ayura"
        self.base_url = "https://www.arrendamientosayura.com"

    async def scrape(self):
        try:
            # Tipos definidos por el usuario: 1 Apartamento, 2 Casa, 11 Apartaestudio
            property_type_ids = ["1", "2", "11"]
            
            for type_id in property_type_ids:
                # iku5-service_type=0 es Arriendo
                base_search_url = f"{self.base_url}/buscar?iku5-service_type=0&iku5-id_type={type_id}"
                logger.info(f"[{self.portal_name}] Iniciando scraping para tipo ID: {type_id}")
                await self._scrape_type_url(base_search_url)
                
        finally:
            await self.close_browser()

    async def _scrape_type_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= self.max_pages:  # Límite dinámico (BaseScraper defaults to 20 or seed overrides)
            # catalog_iku5 es el parámetro de paginación
            current_url = f"{base_url}&catalog_iku5={page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar a que el CMS cargue los datos en los atributos cms-field-var
            try:
                await self.page.wait_for_selector("[cms-content-catalog-body]", timeout=15000)
            except Exception:
                logger.info(f"[{self.portal_name}] No se detectaron más inmuebles en la página {page_num}.")
                break
            
            # Dejar un pequeño tiempo extra para que el CMS pueble los campos
            await self.page.wait_for_timeout(2000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select("[cms-content-catalog-body]")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron tarjetas en la página.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Datos del CMS (atributos cms-field-var)
                    neighborhood_tag = card.select_one('[cms-field-var="id_neighborhood.name"]')
                    city_tag = card.select_one('[cms-field-var="city.name"]')
                    price_tag = card.select_one('[cms-field-var="price"]')
                    area_tag = card.select_one('[cms-field-var="area"]')
                    rooms_tag = card.select_one('[cms-field-var="n_rooms"]')
                    baths_tag = card.select_one('[cms-field-var="n_baths"]')
                    
                    neighborhood = neighborhood_tag.get_text(strip=True) if neighborhood_tag else ""
                    city = city_tag.get_text(strip=True) if city_tag else "Medellín"
                    location = f"{neighborhood}, {city}" if neighborhood else city

                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0

                    area = 0
                    if area_tag:
                        match = re.search(r'([\d.,]+)', area_tag.get_text(strip=True))
                        if match: area = float(match.group(1).replace(',', '.'))

                    bedrooms = 0
                    if rooms_tag:
                        match = re.search(r'(\d+)', rooms_tag.get_text(strip=True))
                        if match: bedrooms = int(match.group(1))

                    bathrooms = 0
                    if baths_tag:
                        match = re.search(r'(\d+)', baths_tag.get_text(strip=True))
                        if match: bathrooms = int(match.group(1))

                    # El enlace suele estar en un botón "Ver Detalles" o en la imagen
                    link_tag = card.select_one('a[id="i18xi6"]') or card.select_one('a:has(img)')
                    full_link = ""
                    if link_tag and link_tag.has_attr('href'):
                        full_link = link_tag['href']
                        if not full_link.startswith("http"):
                            full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    if not full_link: continue

                    # Imagen
                    image_tag = card.select_one('img.cms-object-cover') or card.select_one('img')
                    image_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else None

                    # Título dinámico basado en tipo y barrio
                    # Como no tenemos el nombre del tipo directamente en el card, usamos una inferencia simple
                    raw_title = neighborhood if neighborhood else "Inmueble"
                    
                    entry = {
                        "title": raw_title,
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
