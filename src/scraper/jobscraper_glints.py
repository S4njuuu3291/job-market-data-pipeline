from playwright.async_api import Browser,BrowserContext,Page,async_playwright
from datetime import datetime
from src.utils.scraper_utils import create_browser,create_stealth_context,human_delay,fast_human_scroll
from src.utils.data_validator import job_schema
from src.utils.keywords import ALLOWED,BLOCKED
import hashlib
import json
import os

async def jobscraper_glints(url:str,headless:bool=True):
    async with async_playwright() as p:
        browser:Browser = await create_browser(p,headless=headless)
        print("Berhasil create browser")
        context:BrowserContext = await create_stealth_context(browser)
        print("Berhasil create stealth_context")

        page = await context.new_page()

        print(f"Navigating ke url {url}")

        await page.goto(url, wait_until="networkidle")
        await fast_human_scroll(page)

        results = []

        job_cards = await page.locator('div[class*="JobCardsc__JobCardWrapper"]').all()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    
        for card in job_cards:
            try:
                # 1. Job Title
                title_elem = card.locator('h2 a[class*="JobCardTitle"]').first
                job_title = (await title_elem.text_content()).strip()

                # --- INTEGRASI FILTER PUSAT ---
                job_title_lower = job_title.lower()
                if not any(word in job_title_lower for word in ALLOWED) or \
                any(word in job_title_lower for word in BLOCKED):
                    continue

                # 2. URL (Glints pake path relatif)
                relative_url = await title_elem.get_attribute('href')
                full_url = f"https://glints.com{relative_url}"

                # 3. Company Name
                company_elem = card.locator('a[class*="CompanyLink"]').first
                company_name = (await company_elem.text_content()).strip()

                # 4. Location
                location = (await card.locator('div[class*="CardJobLocation__LocationWrapper"]').first.text_content()).strip()

                # 5. Job ID (Hash dari URL)
                job_id = hashlib.md5(full_url.encode()).hexdigest()

                results.append({
                    "job_id": job_id,
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "job_url": full_url,
                    "platform": "glints",
                    "scraped_at": datetime.now().strftime("%Y%m%d_%H%M%S")
                })
            except Exception as e:
                continue

        filename = f"kalibrr_raw_{timestamp}.json"

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"✅ Sukses! {len(results)} data disimpan di: {file_path}")
        except Exception as e:
            print(f"❌ Gagal menyimpan JSON: {e}")

        await context.close()
        await browser.close()

        return results # list