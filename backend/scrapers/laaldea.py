from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re

logger = logging.getLogger(__name__)

class LaAldeaScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "laaldea"
        self.base_url = "https://www.arrendamientoslaaldea.com.co"

    async def scrape(self):
        try:
            # URL proporcionada por el usuario que incluye múltiples tipos residenciales
            url = f"{self.base_url}/inmuebles/Arriendo/clases_Apartamento_Apto-Loft_Amoblados_Apartaestudio_Casa/precio_0_999999999999/"
            logger.info(f"[{self.portal_name}] Iniciando scraping masivo")
            await self._scrape_url(url)
        finally:
            await self.close_browser()

    async def _scrape_url(self, base_url):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= 10:  # Límite de seguridad
            # La Aldea usa un doble slash para la paginación según la auditoría
            current_url = f"{base_url.rstrip('/')}//{page_num}" if page_num > 1 else base_url
            logger.info(f"[{self.portal_name}] Explorando página {page_num}: {current_url}")
            
            await self.navigate(current_url)
            # Esperar a que las tarjetas carguen
            await self.page.wait_for_selector(".listing-item", timeout=15000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            cards = soup.select(".listing-item")
            if not cards:
                logger.info(f"[{self.portal_name}] No se encontraron más propiedades.")
                break
                
            logger.info(f"[{self.portal_name}] Encontrados {len(cards)} inmuebles en la página {page_num}")
            
            for card in cards:
                try:
                    # Link
                    link_tag = card.select_one(".listing-img-container")
                    if not link_tag: continue
                    full_link = link_tag['href']
                    if not full_link.startswith("http"):
                        full_link = f"{self.base_url.rstrip('/')}/{full_link.lstrip('/')}"
                    
                    # Title
                    title_tag = card.select_one(".listing-title h4 span")
                    title = title_tag.get_text(strip=True) if title_tag else "Inmueble"

                    # Price
                    price_tag = card.select_one(".listing-price span")
                    price_text = price_tag.get_text(strip=True) if price_tag else "0"
                    price = int(re.sub(r'[^\d]', '', price_text)) if re.sub(r'[^\d]', '', price_text) else 0
                    
                    # Image
                    image_tag = card.select_one(".listing-img-container img")
                    image_url = image_tag['src'] if image_tag else None
                    if image_url and image_url.startswith("//"):
                        image_url = f"https:{image_url}"

                    # Location (Barrio / Ciudad)
                    # Está después del icono fa-map-marker en .listing-title
                    loc_container = card.select_one(".listing-title")
                    location = "Medellín"
                    if loc_container:
                        # Extraemos el texto ignorando el span del título
                        loc_text = loc_container.get_text(separator="|", strip=True)
                        # El formato suele ser "Título | Itagüí, Centro | Ver Más"
                        parts = loc_text.split("|")
                        if len(parts) > 1:
                            location = parts[1].strip()

                    # Features
                    area = 0
                    bedrooms = 0
                    bathrooms = 0
                    
                    details = card.select(".listing-details li")
                    for i, li in enumerate(details):
                        text = li.get_text(strip=True).lower()
                        if i == 0: # Área
                            match = re.search(r'([\d.,]+)', text)
                            if match: area = float(match.group(1).replace(',', '.'))
                        elif i == 1: # Alcobas
                            match = re.search(r'(\d+)', text)
                            if match: 
                                bedrooms = int(match.group(1))
                            elif "una" in text:
                                bedrooms = 1
                        elif i == 2: # Baños
                            if "un" in text or "uno" in text:
                                bathrooms = 1
                            else:
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
            
            page_num += 1
            await self.page.wait_for_timeout(1000)
