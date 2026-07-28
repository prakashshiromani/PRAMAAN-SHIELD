"""
PRAMAAN-SHIELD — Redis Connection Pool & Key Schema Helpers
File: backend/app/db/redis.py

Redis key schema:
  hash:image:<phash_hex>     → JSON (known fake image payload)
  hash:video:<vhash_hex>     → JSON (known fake video payload)
  hash:family:<parent_phash> → SET of variant hashes
  rate:<ip_hmac>             → INT counter (max 30 per 60s)
  scan:cache:<content_hash>  → JSON ScanResponse (dedup cache)
  stats:total_scans          → INT (global counter)
  stats:fakes_detected       → INT (global counter)
"""

import redis.asyncio as aioredis
from loguru import logger
from app.config import get_settings

settings = get_settings()

redis_pool: aioredis.Redis = None


async def connect_to_redis():
    global redis_pool
    redis_pool = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20
    )
    await redis_pool.ping()
    logger.info("Connected to Redis")


async def close_redis_connection():
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        logger.info("Redis connection closed")


async def get_redis() -> aioredis.Redis:
    return redis_pool


# ── Key Builders ───────────────────────────────────────────────────────────

def key_image_hash(phash_hex: str) -> str:
    return f"hash:image:{phash_hex}"


def key_video_hash(vhash_hex: str) -> str:
    return f"hash:video:{vhash_hex}"


def key_hash_family(parent_hash: str) -> str:
    return f"hash:family:{parent_hash}"


def key_rate_limit(ip_hmac: str) -> str:
    return f"rate:{ip_hmac}"


def key_scan_cache(content_hash: str) -> str:
    return f"scan:cache:{content_hash}"
