"""
Cloudflare R2 service — S3-compatible read/write via boto3.

All public API is async (runs boto3 calls in a thread-pool executor so the
FastAPI event loop is never blocked).  A simple TTL cache (5 minutes) sits in
front of `get_chapter` and `list_chapters` to reduce billable R2 reads.
"""
import asyncio
import json
import time
from functools import partial
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

# ── Local content fallback (development / no R2 credentials) ─────────────────
# Path: backend/content/{chapters,quizzes}/
_LOCAL_CONTENT = Path(__file__).parent.parent.parent / "content"


def _local_chapter(chapter_id: str) -> str | None:
    """Read chapter markdown from local content/ folder."""
    key = chapter_id if chapter_id.endswith(".md") else f"{chapter_id}.md"
    path = _LOCAL_CONTENT / "chapters" / key
    return path.read_text(encoding="utf-8") if path.exists() else None


def _local_quiz(quiz_id: str) -> dict | None:
    """Read quiz JSON from local content/ folder."""
    key = quiz_id if quiz_id.endswith(".json") else f"{quiz_id}.json"
    path = _LOCAL_CONTENT / "quizzes" / key
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

# ── TTL cache ─────────────────────────────────────────────────────────────────
_CACHE_TTL = 300  # seconds (5 minutes)

_cache: dict[str, tuple[Any, float]] = {}


def _cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    value, ts = entry
    if time.monotonic() - ts > _CACHE_TTL:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (value, time.monotonic())


def cache_invalidate(key: str) -> None:
    """Manually evict a single cache entry (e.g. after an upload)."""
    _cache.pop(key, None)


def cache_clear() -> None:
    """Flush the entire cache."""
    _cache.clear()


# ── boto3 S3 client (Cloudflare R2 endpoint) ─────────────────────────────────
def _make_client():
    endpoint = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


# Lazily initialised once per worker process
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = _make_client()
    return _client


# ── helpers ───────────────────────────────────────────────────────────────────
async def _run_in_executor(func, *args):
    """Run a blocking boto3 call off the event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, partial(func, *args))


def _chapter_key(chapter_id: str) -> str:
    """Normalise chapter_id to its R2 object key."""
    if not chapter_id.endswith(".md"):
        chapter_id = f"{chapter_id}.md"
    return f"chapters/{chapter_id}"


def _quiz_key(quiz_id: str) -> str:
    if not quiz_id.endswith(".json"):
        quiz_id = f"{quiz_id}.json"
    return f"quizzes/{quiz_id}"


# ── public async API ──────────────────────────────────────────────────────────

async def get_chapter(chapter_id: str) -> str | None:
    """
    Fetch a chapter's markdown content.
    Primary: Cloudflare R2.  Fallback: local content/ folder (dev mode).
    Returns the markdown string, or None if not found anywhere.
    Results are cached for 5 minutes.
    """
    cache_key = f"chapter:{chapter_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    # ── Try R2 first (skip if credentials are not configured) ────────────────
    if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID:
        r2_key = _chapter_key(chapter_id)
        try:
            def _fetch():
                resp = _get_client().get_object(
                    Bucket=settings.R2_BUCKET_NAME, Key=r2_key
                )
                return resp["Body"].read().decode("utf-8")

            content = await _run_in_executor(_fetch)
            _cache_set(cache_key, content)
            return content
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in ("NoSuchKey", "404"):
                raise
        except Exception:
            pass  # R2 unreachable — fall through to local

    # ── Local fallback ────────────────────────────────────────────────────────
    content = _local_chapter(chapter_id)
    if content is not None:
        _cache_set(cache_key, content)
    return content


async def get_quiz(quiz_id: str) -> dict | None:
    """
    Fetch a quiz JSON.
    Primary: Cloudflare R2.  Fallback: local content/ folder (dev mode).
    Returns parsed dict, or None if not found anywhere.
    Results are cached for 5 minutes.
    """
    cache_key = f"quiz:{quiz_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    # ── Try R2 first ──────────────────────────────────────────────────────────
    if settings.R2_ACCOUNT_ID and settings.R2_ACCESS_KEY_ID:
        r2_key = _quiz_key(quiz_id)
        try:
            def _fetch():
                resp = _get_client().get_object(
                    Bucket=settings.R2_BUCKET_NAME, Key=r2_key
                )
                return json.loads(resp["Body"].read().decode("utf-8"))

            data = await _run_in_executor(_fetch)
            _cache_set(cache_key, data)
            return data
        except ClientError as exc:
            if exc.response["Error"]["Code"] not in ("NoSuchKey", "404"):
                raise
        except Exception:
            pass  # fall through to local

    # ── Local fallback ────────────────────────────────────────────────────────
    data = _local_quiz(quiz_id)
    if data is not None:
        _cache_set(cache_key, data)
    return data


async def list_chapters() -> list[str]:
    """
    List all chapter object keys in the R2 bucket under the chapters/ prefix.
    Returns a list of R2 keys, e.g. ['chapters/chapter-01.md', ...].
    Result is cached for 5 minutes.
    """
    cache_key = "list:chapters"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    def _list():
        paginator = _get_client().get_paginator("list_objects_v2")
        keys = []
        for page in paginator.paginate(
            Bucket=settings.R2_BUCKET_NAME, Prefix="chapters/"
        ):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    keys = await _run_in_executor(_list)
    _cache_set(cache_key, keys)
    return keys


async def upload_content(key: str, content: str | bytes) -> None:
    """
    Upload content to R2 at the given key.
    `key` should be the full R2 object key, e.g. 'chapters/chapter-01.md'.
    Automatically invalidates the corresponding cache entry.
    """
    if isinstance(content, str):
        body = content.encode("utf-8")
    else:
        body = content

    # Determine content type
    if key.endswith(".md"):
        content_type = "text/markdown; charset=utf-8"
    elif key.endswith(".json"):
        content_type = "application/json"
    else:
        content_type = "application/octet-stream"

    def _put():
        _get_client().put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=body,
            ContentType=content_type,
        )

    await _run_in_executor(_put)

    # Bust relevant cache entries
    cache_invalidate("list:chapters")
    if key.startswith("chapters/"):
        chapter_id = key.removeprefix("chapters/").removesuffix(".md")
        cache_invalidate(f"chapter:{chapter_id}")
    elif key.startswith("quizzes/"):
        quiz_id = key.removeprefix("quizzes/").removesuffix(".json")
        cache_invalidate(f"quiz:{quiz_id}")
