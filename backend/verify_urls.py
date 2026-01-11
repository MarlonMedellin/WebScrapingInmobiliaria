import asyncio
from playwright.async_api import async_playwright

URLS = [
    "https://arrendamientosintegridad.com.co/",
    "https://arrendamientossantafe.com/",
    "https://pandainmobiliaria.com/",
    "https://arrendamientoselcastillo.com.co/",
    "https://inmobiliariaprotebienes.com/",
    "https://lacastellana.com.co/",
    "https://www.arrendamientosmonserrate.com/",
    "https://aportal.com.co/"
]

async def version_check(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                status = response.status if response else "N/A"
                title = await page.title()
                print(f"✅ {url} | Status: {status} | Title: {title.strip()}")
            except Exception as e:
                print(f"❌ {url} | Error: {str(e)[:100]}")
            await browser.close()
    except Exception as e:
        print(f"❌ {url} | Browser Error: {e}")

async def main():
    print("Verifying URLs...")
    for url in URLS:
        await version_check(url)

if __name__ == "__main__":
    asyncio.run(main())
