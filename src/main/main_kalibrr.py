import pandas as pd
from src.scraper.jobscraper_kalibrr import jobscraper_kalibrr
from src.utils.data_validator import validate_job_data
from src.utils.upload_to_s3 import upload_to_s3
import asyncio

async def run_kalibrr_pipeline(keyword:str):
    print("--- 🏁 Memulai Pipeline Kalibrr ---")
    URL = f"https://kalibrr.id/id-ID/home/w/100-internship-_-ojt/w/200-entry-level-_-junior-and-apprentice/te/{keyword}?sort=Relevance"

    raw_data =  await jobscraper_kalibrr(URL,headless=True)

    if not raw_data:
        print("❌ Gagal: Tidak ada data yang berhasil ditarik.")
        return
    
    try:
        df = pd.DataFrame(raw_data)
        df_validated = validate_job_data(df)
        print(f"✅ Validasi Sukses: {len(df_validated)} baris siap dikirim.")

        success = upload_to_s3(df_validated,platform="kalibrr")
        if success:
            print("--- 🏆 Pipeline Selesai dengan Sukses ---")
        else:
            print("--- ⚠️ Pipeline Selesai dengan Error di S3 ---")
    except Exception as e:
        print(f"❌ Pipeline Berhenti di tahap Validasi/Upload: {e}")
    
if __name__ == "__main__":
    keyword = "data-engineer-intern"
    asyncio.run(run_kalibrr_pipeline(keyword))