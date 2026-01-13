from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .base import BaseScraper
import logging
import re
from .config import SEARCH_CRITERIA

logger = logging.getLogger(__name__)

class MonserrateScraper(BaseScraper):
    """
    Scraper for Arrendamientos Monserrate (WooCommerce).
    
    GOLDEN RULES:
    1. URL Pattern: /product-category/arrendamiento/page/{n}/
    2. Data Extraction: 
       - Grid: Extract Title, Price, Link.
       - Detail Page: Extract precise Area, Bedrooms, Bathrooms from 'table.shop_attributes'.
    3. Stop Condition: 404 page or empty .products list.
    """
    def __init__(self, db: Session):
        super().__init__(db)
        self.portal_name = "monserrate"
        self.base_url = "https://www.arrendamientosmonserrate.com"

    async def scrape(self):
        page_num = 1
        consecutive_existing = 0
        
        while page_num <= self.max_pages:
            url = f"{self.base_url}/product-category/arrendamiento/page/{page_num}/"
            logger.info(f"[{self.portal_name}] Scraping page {page_num}: {url}")
            
            try:
                await self.navigate(url)
                
                # Check 404/Empty
                content = await self.page.content()
                if "No se encontraron productos" in content:
                    logger.info(f"[{self.portal_name}] Fin de resultados en página {page_num}.")
                    break

                try:
                    await self.page.wait_for_selector(".products", timeout=10000)
                except:
                    logger.info(f"[{self.portal_name}] No .products found on page {page_num}.")
                    break
                
                soup = BeautifulSoup(content, 'html.parser')
                cards = soup.select("li.product")
                
                if not cards:
                    logger.info(f"[{self.portal_name}] No cards found on page {page_num}.")
                    break
                    
                logger.info(f"[{self.portal_name}] Found {len(cards)} properties on page {page_num}. Extracting details...")
                
                # We extract links first
                properties_to_scrape = []
                for card in cards:
                    title_tag = card.select_one("h4 a")
                    if not title_tag: continue
                    
                    price_tag = card.select_one(".price .amount")
                    price = 0
                    if price_tag:
                        price_text = price_tag.get_text(strip=True)
                        price = int(re.sub(r'[^\d]', '', price_text))
                    
                    img_tag = card.select_one("img.wp-post-image")
                    image_url = img_tag['src'] if img_tag else None
                    
                    properties_to_scrape.append({
                        "title": title_tag.get_text(strip=True),
                        "link": title_tag['href'],
                        "price": price,
                        "image_url": image_url
                    })

                for prop in properties_to_scrape:
                    try:
                        logger.info(f"[{self.portal_name}] Fetching details: {prop['link']}")
                        await self.navigate(prop['link'])
                        
                        detail_content = await self.page.content()
                        detail_soup = BeautifulSoup(detail_content, 'html.parser')
                        
                        # Metadata from table
                        meta = {"area": 0.0, "bedrooms": 0, "bathrooms": 0.0, "location": "Medellín"}
                        
                        table = detail_soup.select_one("table.shop_attributes")
                        if table:
                            for row in table.select("tr"):
                                th_tag = row.select_one("th")
                                td_tag = row.select_one("td")
                                if not th_tag or not td_tag: continue
                                
                                th = th_tag.get_text(strip=True).lower()
                                td = td_tag.get_text(strip=True)
                                
                                if "área" in th or "area" in th:
                                    num = re.search(r'(\d+)', td)
                                    if num: meta["area"] = float(num.group(1))
                                elif "alcobas" in th:
                                    num = re.search(r'(\d+)', td)
                                    if num: meta["bedrooms"] = int(num.group(1))
                                elif "baños" in th or "banos" in th:
                                    num = re.search(r'(\d+)', td)
                                    if num: meta["bathrooms"] = float(num.group(1))
                                elif "sector" in th:
                                    meta["location"] = f"{td}, Medellín"
                        
                        if meta["location"] == "Medellín":
                            meta["location"] = f"{prop['title']}, Medellín"

                        entry = {
                            "title": prop["title"],
                            "price": prop["price"],
                            "location": meta["location"],
                            "link": prop["link"],
                            "image_url": prop["image_url"],
                            "source": self.portal_name,
                            "area": meta["area"],
                            "bedrooms": meta["bedrooms"],
                            "bathrooms": meta["bathrooms"]
                        }
                        
                        status = await self.process_property(entry)
                        
                        if status == "existing":
                            consecutive_existing += 1
                        elif status in ["new", "updated"]:
                            consecutive_existing = 0
                            
                        if self.should_stop_scraping(consecutive_existing):
                            logger.info(f"[{self.portal_name}] Limit reached.")
                            return

                    except Exception as e:
                        logger.error(f"[{self.portal_name}] Error scraping detail page {prop['link']}: {e}")
                        continue
                        
                page_num += 1
                await self.page.wait_for_timeout(2000)
                
            except Exception as e:
                logger.error(f"[{self.portal_name}] Page error: {e}")
                break
