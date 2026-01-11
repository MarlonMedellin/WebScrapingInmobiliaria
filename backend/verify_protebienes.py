import asyncio
from playwright.async_api import async_playwright

URL = "https://www.inmobiliariaprotebienes.com.co/"

async def check(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Protebienes might need a real user agent or ignore https errors
        page = await browser.new_page(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        try:
            print(f"Navigating to {url}...")
            resp = await page.goto(url, timeout=30000)
            status = resp.status if resp else "N/A"
            title = await page.title()
            print(f"✅ [{url}] Status: {status} | Title: {title.strip()}")
        except Exception as e:
            print(f"❌ [{url}] ERROR: {e}")
            # Try to dump html if reachable but logic fails? No, just connection check.
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check(URL))
