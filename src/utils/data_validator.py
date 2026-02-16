import pandas as pd
import pandera as pa
from pandera.pandas import DataFrameSchema,Column,Check
import json

job_schema = DataFrameSchema(
    {
        "job_id": Column(str, unique= True),
        "job_title": Column(str),
        "company_name": Column(str),
        "location": Column(str),
        "job_url": Column(str),
        "platform": Column(str, Check.isin(["kalibrr","jobstreet","glints","dealls","karir.com"])),
        "scraped_at": Column(str)
    },
    strict=False,
    coerce=True
)

if __name__ == "__main__":
    file_path = r"output/kalibrr_raw_20260216_081739.json" 
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f) 
        print("✅ Berhasil ngeload JSON")
        
        df = pd.DataFrame(results)
        
        job_schema.validate(df)
        print("✅ Data berhasil divalidasi!")
        
    except Exception as e:
        print(f"❌ Gagal proses: {e}")