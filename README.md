# Job Market Data Pipeline

ETL pipeline for job market data using Python for scraping/validation and Terraform for AWS infrastructure.

## Structure
- src/scraper/: scraping modules (Playwright)
- src/utils/: helpers (stealth browser, validation, S3 upload)
- terraform/: AWS infrastructure (IAM, S3)
- tests/: test suite (WIP)

## Setup (Poetry)
- Install deps: `poetry install`
- Run scraper: `python -m src.scraper.jobscraper_kalibrr`

## Output
- Scraped raw JSON is saved under `output/` (ignored by git)

## Notes
- `src/utils/upload_to_s3.py` is a stub and will be implemented next.
