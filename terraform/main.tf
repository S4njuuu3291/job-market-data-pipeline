# =========================================================
#                   IAM USER RESOURCE
# =========================================================

resource "aws_iam_user" "jobscraper_bot" {
  name = "jobscraper_bot-crawler-bot"

  tags = {
    Project   = "Job-Scraper"
    ManagedBy = "Terraform-Executor"
  }
}

resource "aws_iam_access_key" "jobscraper_bot" {
  user = aws_iam_user.jobscraper_bot.name
}

# =========================================================
#                    BUCKET RESOURCE
# =========================================================

# BRONZE

resource "aws_s3_bucket" "bronze" {
  bucket = "jobscraper-bronze-data-8424560"

  tags = {
    Layer   = "Bronze"
    Project = "Job-Scraper"
    Owner   = "Sanju"
  }
}

resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket = aws_s3_bucket.bronze.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# =========================================================
#                         POLICY
# =========================================================

resource "aws_iam_policy" "scraper_s3_write_policy" {
  name        = "jobscraper_s3_write_policy"
  description = "Write access for scraper to Bronze S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowListBucket"
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [
          aws_s3_bucket.bronze.arn
        ]
      },
      {
        Sid    = "AllowObjectReadWrite"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = [
          "${aws_s3_bucket.bronze.arn}/*"
        ]
      }
    ]
  })
}

# =========================================================
#                    POLICY ATTACHMENT
# =========================================================

resource "aws_iam_user_policy_attachment" "jobscraper_bot_s3_write" {
  user       = aws_iam_user.jobscraper_bot.name
  policy_arn = aws_iam_policy.scraper_s3_write_policy.arn
}