import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(r"c:\Users\niran\Downloads\mini project collage\learning\AI_College_Transport_Analyzer\screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def capture_all_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 960})
        page = await context.new_page()

        print("Navigating to Streamlit Home Page...")
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=60000)
        
        async def wait_for_streamlit_render():
            await asyncio.sleep(2)
            try:
                await page.wait_for_selector('div[data-testid="stSkeleton"]', state="hidden", timeout=12000)
            except Exception:
                pass
            await asyncio.sleep(5)

        print("Waiting for Home Page render...")
        await wait_for_streamlit_render()
        print("Capturing 01_Home_Overview.png...")
        await page.screenshot(path=str(OUTPUT_DIR / "01_Home_Overview.png"), full_page=False)

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
                print(f"Navigating to '{nav_text}'...")
                link = page.locator(f"span:has-text('{nav_text}')").first
                if await link.count() > 0:
                    await link.click()
                    await wait_for_streamlit_render()
                    await page.screenshot(path=str(OUTPUT_DIR / filename), full_page=False)
                    print(f"[OK] Successfully captured {filename}")
                else:
                    print(f"[ERR] Could not find sidebar link for: {nav_text}")
            except Exception as e:
                print(f"[ERR] Error capturing {nav_text}: {e}")

        await browser.close()
        print("All page screenshots captured with full visuals!")

if __name__ == "__main__":
    asyncio.run(capture_all_pages())
