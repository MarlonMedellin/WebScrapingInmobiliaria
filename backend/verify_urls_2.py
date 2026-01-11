import asyncio
from playwright.async_api import async_playwright

URLS = [
    "http://arrendamientosintegridad.com.co/", # Try HTTP
    "https://inmobiliariaprotebienes.com/", # Retrying
    "https://lacastellana.com.co/",
    "https://www.arrendamientosmonserrate.com/"
]

async def check(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(ignore_https_errors=True) # Ignore SSL errors
        try:
            resp = await page.goto(url, timeout=20000)
            print(f"[{url}] {resp.status} - {await page.title()}")
        except Exception as e:
            print(f"[{url}] ERROR: {e}")
        await browser.close()

async def main():
    for u in URLS:
        await check(u)

asyncio.run(main())
