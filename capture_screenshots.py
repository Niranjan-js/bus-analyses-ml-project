import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(r"c:\Users\niran\Downloads\mini project collage\learning\AI_College_Transport_Analyzer\screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def capture_all_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("Navigating to Streamlit App...")
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # 1. Home / Overview Page
        print("Capturing 01_Home_Overview.png...")
        await page.screenshot(path=str(OUTPUT_DIR / "01_Home_Overview.png"), full_page=False)

        # Helper to click sidebar nav items
        pages_to_capture = [
            ("Transport Overview", "02_Transport_Overview.png"),
            ("Bus Analytics", "03_Bus_Analytics.png"),
            ("Route Analytics", "04_Route_Analytics.png"),
            ("Stop Analytics", "05_Stop_Analytics.png"),
            ("Complaints", "06_Complaints_Analysis.png"),
            ("AI Insights", "07_AI_Insights.png"),
            ("Demand Prediction", "08_Demand_Prediction.png"),
            ("Ask Transport AI", "09_Ask_Transport_AI.png"),
            ("Super Admin Console", "10_Super_Admin_Console.png"),
        ]

        for nav_text, filename in pages_to_capture:
            try:
                print(f"Navigating to {nav_text}...")
                # Click sidebar nav item
                link = page.locator(f"span:has-text('{nav_text}')").first
                if await link.count() > 0:
                    await link.click()
                    await asyncio.sleep(3.5)
                    await page.screenshot(path=str(OUTPUT_DIR / filename), full_page=False)
                    print(f"Captured {filename}")
                else:
                    print(f"Could not find nav item: {nav_text}")
            except Exception as e:
                print(f"Error capturing {nav_text}: {e}")

        await browser.close()
        print("All screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_all_pages())
