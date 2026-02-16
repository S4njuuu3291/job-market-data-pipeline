from playwright.async_api import Browser,BrowserContext,Page,async_playwright
from datetime import datetime
from src.utils.scraper_utils import create_browser,create_stealth_context,human_delay,fast_human_scroll
from src.utils.data_validator import job_schema
from src.utils.keywords import ALLOWED,BLOCKED
import hashlib
import asyncio
import json
import os

async def jobscraper_jobstreet(url: str, headless: bool = True):
    async with async_playwright() as p:
        browser: Browser = await create_browser(p, headless=headless)
        print("Berhasil create browser")
        context: BrowserContext = await create_stealth_context(browser)
        print("Berhasil create stealth_context")

        page = await context.new_page()

        print(f"Navigating ke url {url}")
        # Gunakan wait_until domcontentloaded agar lebih cepat
        await page.goto(url, wait_until="domcontentloaded")
        
        # Penanganan modal login yang sering muncul di JobStreet
        await page.keyboard.press("Escape")
        await asyncio.sleep(1)

        # Strategi Scroll: Lakukan scroll perlahan 3 kali saja
        # Ini memicu lazy loading tanpa mencekik RAM 8GB
        for i in range(3):
            await fast_human_scroll(page)
            await asyncio.sleep(1)

        results = []

        # Mengincar atribut data-automation yang sangat stabil di JobStreet
        job_cards = await page.locator('article[data-automation="normalJob"]').all()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for card in job_cards:
            try:
                # 1. Job Title
                title_elem = card.locator('[data-automation="jobTitle"]').first
                job_title = (await title_elem.text_content()).strip()

                # --- INTEGRASI FILTER PUSAT ---
                job_title_lower = job_title.lower()
                if not any(word in job_title_lower for word in ALLOWED) or \
                   any(word in job_title_lower for word in BLOCKED):
                    continue

                # 2. URL (Path relatif, perlu prefix)
                relative_url = await title_elem.get_attribute('href')
                full_url = f"https://id.jobstreet.com{relative_url}"

                # 3. Company Name
                company_elem = card.locator('[data-automation="jobCompany"]').first
                company_name = (await company_elem.text_content()).strip()

                # 4. Location
                # Mengambil teks lokasi (Jakarta Selatan, dll)
                location_elem = card.locator('[data-automation="jobLocation"]').first
                location = (await location_elem.text_content()).strip()

                # 5. Job ID (Hash dari URL agar konsisten antar platform)
                job_id = hashlib.md5(full_url.encode()).hexdigest()

                results.append({
                    "job_id": job_id,
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": location,
                    "job_url": full_url,
                    "platform": "jobstreet",
                    "scraped_at": timestamp
                })
            except Exception as e:
                continue

        filename = f"jobstreet_raw_{timestamp}.json"
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_path = os.path.join(output_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"✅ Sukses! {len(results)} data JobStreet disimpan di: {file_path}")
        except Exception as e:
            print(f"❌ Gagal menyimpan JSON: {e}")

        await context.close()
        await browser.close()

        return results