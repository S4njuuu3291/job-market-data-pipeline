# Lazy import untuk cold start cepat
@lambda: None  # Decorator placeholder
async def jobscraper_kalibrr(url:str,headless:bool=True):
    # Import HANYA saat fungsi dipanggil (lazy loading)
    from playwright.async_api import Browser, BrowserContext, Page, async_playwright
    from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
    from datetime import datetime
    from src.utils.scraper_utils import create_browser, create_stealth_context, human_delay, fast_human_scroll
    from src.utils.keywords import ALLOWED, BLOCKED
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    import hashlib
    import json
    import os
    
    # Apply retry decorator dynamically
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(PlaywrightTimeoutError),
        reraise=True
    )
    async def _scrape():
        async with async_playwright() as p:
            browser:Browser = await create_browser(p,headless=headless)
            print("Berhasil create browser")
            context:BrowserContext = await create_stealth_context(browser)
            print("Berhasil create stealth_context")

            print("Creating new page...")
            page = await context.new_page()
            print("Page created successfully")
            
            # Block resource berat untuk mempercepat load
            print("Setting up resource blocking...")
            await page.route("**/*.{png,jpg,jpeg,svg,gif,css,woff,woff2,otf,ttf}", lambda route: route.abort())
            print("Resource blocking enabled")

            print(f"Navigating to URL: {url}")
            try:
                await page.goto(url,wait_until="domcontentloaded", timeout=60000)
                print(f"Successfully loaded page")
            except Exception as e:
                print(f"Error during page.goto: {type(e).__name__}: {str(e)}")
                raise

            results = []

            max_clicks = 1
            button_selector = "button.k-btn-primary:has-text('Load more jobs')"

            for i in range(max_clicks):
                load_more_button = page.locator(button_selector)

                if await load_more_button.is_visible():
                    print(f"Klik Load More ke-{i+1}...")
                    await load_more_button.scroll_into_view_if_needed()
                    await human_delay()

                    await load_more_button.click()

                    await human_delay(min_ms=1500,max_ms=2000)
                else:
                    print("Selesai: Tombol Load More sudah tidak ada.")
                    break
            else:
                print("Selesai: Mencapai batas maksimal klik (limit keamanan).")

            job_cards = await page.locator("div.css-1otdiuc").all()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for card in job_cards:
                try:
                    # 1. Job Title & URL (Pakai atribut itemprop="name" yang ada di tag <a>)
                    title_elem = card.locator('h2 a[itemprop="name"]').first
                    job_title = (await title_elem.text_content()).strip()

                    job_title_lower = job_title.lower()

                    is_relevant = any(word in job_title_lower for word in ALLOWED)
                    is_trash = any(word in job_title_lower for word in BLOCKED)

                    if not is_relevant or is_trash:
                        continue
                    
                    relative_url = await title_elem.get_attribute('href')
                    full_url = f"https://www.kalibrr.com{relative_url}"
                    
                    # 2. Company Name (Pakai selector class yang lebih simpel)
                    company_name = (await card.locator('a.k-text-subdued.k-font-bold').first.text_content()).strip()
                    
                    # 3. Location (Mencari icon map atau class lokasi)
                    location = (await card.locator('span.k-text-gray-500').first.text_content()).strip()
                    
                    # 4. Create Job ID (Sesuai diskusi kita: Hash dari URL)
                    job_id = hashlib.md5(full_url.encode()).hexdigest()

                    results.append({
                        "job_id": job_id,
                        "job_title": job_title,
                        "company_name": company_name,
                        "location": location,
                        "job_url": full_url,
                        "platform": "kalibrr",
                        "scraped_at": timestamp # Nanti pakai datetime.now()
                    })
                    
                except Exception as e:
                    print(f"Gagal ekstrak card: {e}")
                    continue
            
            filename = f"kalibrr_raw_{timestamp}.json"

            output_dir = "/tmp/output"
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

            return results
    
    return await _scrape() # list


if __name__ == "__main__":
    URL = "https://kalibrr.id/id-ID/home/w/100-internship-_-ojt/te/data-engineer-intern"

    # asyncio.run(jobscraper_kalibrr(URL))