import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path(r"c:\Users\niran\Downloads\mini project collage\learning\AI_College_Transport_Analyzer\screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def record_full_demo():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        print("[REC] Starting video recording of full application demo...")

        # Helper to wait for Streamlit render
        async def wait_render(extra_sec=4):
            await asyncio.sleep(1)
            try:
                await page.wait_for_selector('div[data-testid="stSkeleton"]', state="hidden", timeout=10000)
            except Exception:
                pass
            await asyncio.sleep(extra_sec)

        # 1. Home Overview
        print("[REC] Navigating to Home Overview...")
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=60000)
        await wait_render(4)

        # 2. Transport Overview
        print("[REC] Visiting Transport Overview...")
        link = page.locator("span:has-text('Transport Overview')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 3. Bus Analytics
        print("[REC] Visiting Bus Analytics...")
        link = page.locator("span:has-text('Bus Analytics')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 4. Route Analytics
        print("[REC] Visiting Route Analytics...")
        link = page.locator("span:has-text('Route Analytics')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 5. Stop Analytics
        print("[REC] Visiting Stop Analytics...")
        link = page.locator("span:has-text('Stop Analytics')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 6. Complaints Analysis
        print("[REC] Visiting Complaints Analysis...")
        link = page.locator("span:has-text('Complaints')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 7. AI Intelligence Insights
        print("[REC] Visiting AI Intelligence Insights...")
        link = page.locator("span:has-text('AI Insights')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 8. Demand Prediction (Machine Learning)
        print("[REC] Visiting Demand Prediction (ML)...")
        link = page.locator("span:has-text('Demand Prediction')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 9. Ask Transport AI Chatbot
        print("[REC] Visiting Ask Transport AI Chatbot...")
        link = page.locator("span:has-text('Ask Transport AI')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(3)
            
            # Click quick preset question button
            btn = page.locator("button:has-text('Which bus is most crowded?')").first
            if await btn.count() > 0:
                print("[REC] Asking Chatbot question: 'Which bus is most crowded?'...")
                await btn.click()
                await wait_render(4)

        # 10. Data Upload & Management
        print("[REC] Visiting Data Management & Upload...")
        link = page.locator("span:has-text('Data Upload')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(4)

        # 11. Super Admin Console & Executive Reports
        print("[REC] Visiting Super Admin Console...")
        link = page.locator("span:has-text('Super Admin Console')").first
        if await link.count() > 0:
            await link.click()
            await wait_render(5)

        # Close context to save video
        video_path = await page.video.path()
        await context.close()
        await browser.close()
        
        print(f"[REC] Video recording saved to: {video_path}")
        
        # Rename recorded video to a clean name: working_demo.webm
        target_video = OUTPUT_DIR / "working_demo.webm"
        if Path(video_path).exists():
            import shutil
            shutil.copy(video_path, target_video)
            print(f"[REC] Copied video to: {target_video}")

if __name__ == "__main__":
    asyncio.run(record_full_demo())
