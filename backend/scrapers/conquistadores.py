from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class ConquistadoresScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "conquistadores"
        self.base_url = "https://conquistainmobiliaria.com"

    async def scrape(self):
        try:
            # URLs proporcionadas por el usuario (corrigiendo typos menores)
            urls = {
                "apartaestudio": "https://conquistainmobiliaria.com/s/apartaestudio/arrendar?id_property_type=14&business_type%5B0%5D=for_rent",
                "apartamento": "https://conquistainmobiliaria.com/s/apartamento/arrendar?id_property_type=2&business_type%5B0%5D=for_rent",
                "casa": "https://conquistainmobiliaria.com/s/casa/arrendar?id_property_type=1&business_type%5B0%5D=for_rent"
            }
            
            for p_type, base_url in urls.items():
                logger.info(f"[{self.portal_name}] Iniciando scraping para: {p_type}")
                await self._scrape_category(base_url)
                
        finally:
            await self.close_browser()

    async def _scrape_category(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 10:  # Límite de seguridad de 10 páginas
            url = f"{base_url}&page={page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {url}")
            
            await self.navigate(url)
            # Esperar a que las tarjetas de Wasi carguen
            try:
                await self.page.wait_for_selector(".item", timeout=10000)
            except:
                logger.info(f"[{self.portal_name}] No se encontraron items en la página {page_num}")
                break
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".item")
            if not cards:
                break
                
            for card in cards:
                try:
                    # Título y Link
                    title_tag = card.select_one("h2 a.t8-title.link")
                    if not title_tag: continue
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    if not link.startswith("http"):
                        link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"

                    # Precio
                    price_tag = card.select_one(".areaPrecio p.t8-title")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0

                    # Ubicación (Barrio, Ciudad)
                    loc_tag = card.select_one(".ubicacion.t8-title")
                    location = loc_tag.get_text(strip=True) if loc_tag else ""

                    # Imagen
                    img_tag = card.select_one("figure a img")
                    image_url = img_tag.get('src') or img_tag.get('data-src')

                    # Detalles técnicos
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    details_rows = card.select(".info_details .col-6")
                    for detail in details_rows:
                        text = detail.get_text().lower()
                        val_tag = detail.select_one("strong")
                        val = val_tag.get_text(strip=True) if val_tag else "0"
                        
                        if "habitaciones" in text:
                            bedrooms = int(val) if val.isdigit() else 0
                        elif "baño" in text:
                            bathrooms = float(val) if val.replace('.', '').isdigit() else 0
                        elif "área m2" in text or "area m2" in text:
                            area = float(val) if val.replace('.', '').isdigit() else 0

                    entry = {
                        "title": title,
                        "price": price,
                        "location": location,
                        "link": link,
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
                        logger.info(f"[{self.portal_name}] Límite de existentes alcanzado.")
                        return 

                except Exception as e:
                    logger.error(f"[{self.portal_name}] Error en card: {e}")
                    continue
            
            # Verificar si hay botón de "Next"
            next_btn = soup.select_one('.page-link[aria-label="Next"]')
            if not next_btn:
                break
                
            page_num += 1
            await self.page.wait_for_timeout(1000)
