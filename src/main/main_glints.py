import pandas as pd
from src.scraper.jobscraper_glints import jobscraper_glints
from src.utils.data_validator import validate_job_data
from src.utils.upload_to_s3 import upload_to_s3
import asyncio

async def run_glints_pipeline(keyword:str):
    print("--- 🏁 Memulai Pipeline glints ---")
    URL = f"https://glints.com/id/opportunities/jobs/explore?keyword={keyword}&country=ID&locationName=All+Cities%2FProvinces&lowestLocationLevel=1&sortBy=LATEST&jobTypes=INTERNSHIP%2CFULL_TIME&yearsOfExperienceRanges=LESS_THAN_A_YEAR%2CFRESH_GRAD%2CNO_EXPERIENCE"

    raw_data =  await jobscraper_glints(URL,headless=True)

    if not raw_data:
        print("❌ Gagal: Tidak ada data yang berhasil ditarik.")
        return
    
    try:
        df = pd.DataFrame(raw_data)
        df_validated = validate_job_data(df)
        print(f"✅ Validasi Sukses: {len(df_validated)} baris siap dikirim.")

        success = upload_to_s3(df_validated,platform="glints")
        if success:
            print("--- 🏆 Pipeline Selesai dengan Sukses ---")
        else:
            print("--- ⚠️ Pipeline Selesai dengan Error di S3 ---")
    except Exception as e:
        print(f"❌ Pipeline Berhenti di tahap Validasi/Upload: {e}")
    
if __name__ == "__main__":
    keyword = "data+engineer+intern"
    asyncio.run(run_glints_pipeline(keyword))