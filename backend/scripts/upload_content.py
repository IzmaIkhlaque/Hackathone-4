"""
Upload all local chapter markdown files and quiz JSON files to AWS S3.

Usage (from backend/ directory):
    python scripts/upload_content.py

Reads credentials from backend/.env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_BUCKET_NAME).
"""

import os
import sys
from pathlib import Path

# Allow running from backend/ or backend/scripts/
ROOT = Path(__file__).parent.parent  # backend/

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass  # python-dotenv not installed; rely on env vars

import boto3
from botocore.exceptions import ClientError

# ── Config ────────────────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID    = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION           = os.environ.get("AWS_REGION", "ap-south-1")
AWS_BUCKET_NAME      = os.environ.get("AWS_BUCKET_NAME", "course-companion-fte-app")

CONTENT_DIR = ROOT / "content"
CHAPTERS_DIR = CONTENT_DIR / "chapters"
QUIZZES_DIR  = CONTENT_DIR / "quizzes"

# ── Helpers ────────────────────────────────────────────────────────────────────
def make_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
        # No endpoint_url for real AWS S3
    )


def ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
        print(f"  Bucket '{bucket}' exists.")
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            print(f"  Creating bucket '{bucket}'...")
            client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
        else:
            raise


def upload_file(client, local_path: Path, s3_key: str, content_type: str) -> None:
    size_kb = local_path.stat().st_size // 1024
    print(f"  Uploading {local_path.name} -> {s3_key}  ({size_kb} KB)", end=" ... ")
    with open(local_path, "rb") as fh:
        client.put_object(
            Bucket=AWS_BUCKET_NAME,
            Key=s3_key,
            Body=fh.read(),
            ContentType=content_type,
        )
    print("OK")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Course Companion FTE — AWS S3 Content Uploader")
    print("=" * 60)
    print(f"Bucket  : {AWS_BUCKET_NAME}")
    print(f"Region  : {AWS_REGION}")
    print()

    client = make_client()
    ensure_bucket(client, AWS_BUCKET_NAME)
    print()

    # ── Upload chapters ───────────────────────────────────────────────────────
    chapter_files = sorted(CHAPTERS_DIR.glob("chapter-*.md"))
    if not chapter_files:
        print(f"WARNING: No chapter files found in {CHAPTERS_DIR}")
    else:
        print(f"Uploading {len(chapter_files)} chapter(s):")
        for chapter_path in chapter_files:
            s3_key = f"chapters/{chapter_path.name}"
            upload_file(client, chapter_path, s3_key, "text/markdown; charset=utf-8")

    print()

    # ── Upload quizzes ────────────────────────────────────────────────────────
    quiz_files = sorted(QUIZZES_DIR.glob("quiz-*.json"))
    if not quiz_files:
        print(f"WARNING: No quiz files found in {QUIZZES_DIR}")
    else:
        print(f"Uploading {len(quiz_files)} quiz file(s):")
        for quiz_path in quiz_files:
            s3_key = f"quizzes/{quiz_path.name}"
            upload_file(client, quiz_path, s3_key, "application/json")

    print()
    print("=" * 60)
    print("Upload complete.")
    print()
    print("Verifying uploaded objects:")
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=AWS_BUCKET_NAME):
        for obj in page.get("Contents", []):
            size_kb = obj["Size"] // 1024
            print(f"  {obj['Key']}  ({size_kb} KB)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyError as exc:
        print(f"\nERROR: Missing environment variable: {exc}")
        print("Make sure backend/.env has AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_BUCKET_NAME")
        sys.exit(1)
    except ClientError as exc:
        print(f"\nAWS S3 ERROR: {exc}")
        sys.exit(1)






















# """
# Upload all local chapter markdown files and quiz JSON files to Cloudflare R2.

# Usage (from backend/ directory):
#     pip install boto3 python-dotenv
#     python scripts/upload_content.py

# Reads credentials from backend/.env  (or environment variables).

# R2 folder structure after upload:
#     course-companion-bucket/
#     ├── chapters/
#     │   ├── chapter-01.md  (free)
#     │   ├── chapter-02.md  (free)
#     │   ├── chapter-03.md  (free)
#     │   ├── chapter-04.md  (premium)
#     │   ├── chapter-05.md  (premium)
#     │   └── chapter-06.md  (pro)
#     └── quizzes/
#         ├── quiz-01.json
#         ├── quiz-02.json
#         └── quiz-03.json
# """
# import os
# import sys
# from pathlib import Path

# # Allow running from backend/ or backend/scripts/
# ROOT = Path(__file__).parent.parent  # backend/

# # Load .env
# try:
#     from dotenv import load_dotenv
#     load_dotenv(ROOT / ".env")
# except ImportError:
#     pass  # python-dotenv not installed; rely on env vars

# import boto3
# from botocore.exceptions import ClientError

# # ── Config ────────────────────────────────────────────────────────────────────
# R2_ACCOUNT_ID       = os.environ["R2_ACCOUNT_ID"]
# R2_ACCESS_KEY_ID    = os.environ["R2_ACCESS_KEY_ID"]
# R2_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]
# R2_BUCKET_NAME      = os.environ.get("R2_BUCKET_NAME", "course-companion-bucket")

# ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# CONTENT_DIR = ROOT / "content"
# CHAPTERS_DIR = CONTENT_DIR / "chapters"
# QUIZZES_DIR  = CONTENT_DIR / "quizzes"

# # ── Helpers ───────────────────────────────────────────────────────────────────
# def make_client():
#     return boto3.client(
#         "s3",
#         endpoint_url=ENDPOINT_URL,
#         aws_access_key_id=R2_ACCESS_KEY_ID,
#         aws_secret_access_key=R2_SECRET_ACCESS_KEY,
#         region_name="auto",
#     )


# def ensure_bucket(client, bucket: str) -> None:
#     try:
#         client.head_bucket(Bucket=bucket)
#         print(f"  Bucket '{bucket}' exists.")
#     except ClientError as exc:
#         code = exc.response["Error"]["Code"]
#         if code in ("404", "NoSuchBucket"):
#             print(f"  Creating bucket '{bucket}'...")
#             client.create_bucket(Bucket=bucket)
#         else:
#             raise


# def upload_file(client, local_path: Path, r2_key: str, content_type: str) -> None:
#     size_kb = local_path.stat().st_size // 1024
#     print(f"  Uploading {local_path.name} -> {r2_key}  ({size_kb} KB)", end=" ... ")
#     with open(local_path, "rb") as fh:
#         client.put_object(
#             Bucket=R2_BUCKET_NAME,
#             Key=r2_key,
#             Body=fh.read(),
#             ContentType=content_type,
#         )
#     print("OK")


# # ── Main ──────────────────────────────────────────────────────────────────────
# def main():
#     print("=" * 60)
#     print("Course Companion FTE — R2 Content Uploader")
#     print("=" * 60)
#     print(f"Bucket  : {R2_BUCKET_NAME}")
#     print(f"Endpoint: {ENDPOINT_URL}")
#     print()

#     client = make_client()
#     ensure_bucket(client, R2_BUCKET_NAME)
#     print()

#     # ── Upload chapters ───────────────────────────────────────────────────────
#     chapter_files = sorted(CHAPTERS_DIR.glob("chapter-*.md"))
#     if not chapter_files:
#         print(f"WARNING: No chapter files found in {CHAPTERS_DIR}")
#     else:
#         print(f"Uploading {len(chapter_files)} chapter(s):")
#         for chapter_path in chapter_files:
#             r2_key = f"chapters/{chapter_path.name}"
#             upload_file(client, chapter_path, r2_key, "text/markdown; charset=utf-8")

#     print()

#     # ── Upload quizzes ────────────────────────────────────────────────────────
#     quiz_files = sorted(QUIZZES_DIR.glob("quiz-*.json"))
#     if not quiz_files:
#         print(f"WARNING: No quiz files found in {QUIZZES_DIR}")
#     else:
#         print(f"Uploading {len(quiz_files)} quiz file(s):")
#         for quiz_path in quiz_files:
#             r2_key = f"quizzes/{quiz_path.name}"
#             upload_file(client, quiz_path, r2_key, "application/json")

#     print()
#     print("=" * 60)
#     print("Upload complete.")
#     print()
#     print("Verifying uploaded objects:")
#     paginator = client.get_paginator("list_objects_v2")
#     for page in paginator.paginate(Bucket=R2_BUCKET_NAME):
#         for obj in page.get("Contents", []):
#             size_kb = obj["Size"] // 1024
#             print(f"  {obj['Key']}  ({size_kb} KB)")
#     print("=" * 60)


# if __name__ == "__main__":
#     try:
#         main()
#     except KeyError as exc:
#         print(f"\nERROR: Missing environment variable: {exc}")
#         print("Make sure backend/.env has R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
#         sys.exit(1)
#     except ClientError as exc:
#         print(f"\nR2 ERROR: {exc}")
#         sys.exit(1)
