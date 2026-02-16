# Job Market Data Pipeline

ETL pipeline untuk scraping job market data dari multiple platforms, validasi dengan Pandera, dan upload ke S3 dengan partitioning.

## Features

### 🕷️ Multi-Platform Scrapers
- **Kalibrr**: Scrape internship & entry-level positions dengan load more logic
- **JobStreet**: Modal handling + lazy-load scroll strategy
- **Glints**: Network idle wait + JobCard extraction

### 🔍 Data Quality
- **Keyword Filtering**: Centralized ALLOWED/BLOCKED word lists untuk filter job title
- **Schema Validation**: Pandera validation untuk data quality assurance
- **Stealth Browsing**: Human-like behavior, anti-detection techniques

### ☁️ Cloud Integration
- **S3 Upload**: Automatic parquet conversion & upload ke AWS S3
- **Partitioning**: `platform={platform}/ingestion_date={date}/{platform}_{timestamp}.parquet`
- **IaC**: Terraform untuk AWS infrastructure (IAM, S3 buckets)

## Project Structure
```
src/
├── main/           # Pipeline orchestrators per platform
├── scraper/        # Platform-specific scrapers (Playwright)
├── utils/          # Utilities (stealth browser, validation, S3, keywords)
terraform/          # AWS infrastructure as code
tests/              # Test suite (WIP)
output/             # Local output files (git-ignored)
```

## Setup

### 1. Install Dependencies
```bash
poetry install
playwright install chromium
```

### 2. Environment Variables
Create `.env` file:
```env
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=ap-southeast-1
```

### 3. Run Pipeline
```bash
# Kalibrr
poetry run python -m src.main.main_kalibrr

# JobStreet
poetry run python -m src.main.main_jobstreet

# Glints
poetry run python -m src.main.main_glints
```

## Infrastructure (Terraform)

Deploy AWS resources:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Resources created:
- IAM User untuk scraper bot
- S3 Bronze bucket dengan encryption & access blocks
- IAM policies untuk write access

## Output Format

Data disimpan dalam Parquet format dengan schema:
- `job_id`: MD5 hash dari job URL (unique)
- `job_title`: Job title
- `company_name`: Company name
- `location`: Location
- `job_url`: Full job URL
- `platform`: Source platform (kalibrr/jobstreet/glints)
- `scraped_at`: Timestamp scraping

## Tech Stack
- **Python 3.12+**: Poetry, Playwright, Pandas, Pandera, Boto3, PyArrow
- **AWS**: S3, IAM
- **IaC**: Terraform
