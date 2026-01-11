import asyncio
from playwright.async_api import async_playwright
import os

PORTALS = [
    {"name": "integridad", "url": "http://arrendamientosintegridad.com.co/inmuebles/Arriendo/"},
    {"name": "santafe", "url": "https://arrendamientossantafe.com/propiedades/?bussines_type=Arrendar"},
    {"name": "panda", "url": "https://pandainmobiliaria.com/inmuebles?operacion=2"},
    {"name": "protebienes", "url": "https://www.inmobiliariaprotebienes.com.co/inmuebles/Arriendo/"},
    {"name": "lacastellana", "url": "https://lacastellana.com.co/s/alquileres"},
    {"name": "monserrate", "url": "https://www.arrendamientosmonserrate.com/inmuebles/?operacion=2"},
    {"name": "aportal", "url": "https://aportal.com.co/es/arrendar"}
]

async def analyze(portal):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(ignore_https_errors=True)
        try:
            print(f"[{portal['name']}] Navigating to {portal['url']}...")
            await page.goto(portal['url'], timeout=60000)
            await page.wait_for_timeout(5000) # Wait for JS
            
            # Dump HTML
            content = await page.content()
            filename = f"debug_{portal['name']}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[{portal['name']}] Saved {filename}")
            
        except Exception as e:
            print(f"[{portal['name']}] Error: {e}")
        await browser.close()

async def main():
    for p in PORTALS:
        await analyze(p)

if __name__ == "__main__":
    asyncio.run(main())
