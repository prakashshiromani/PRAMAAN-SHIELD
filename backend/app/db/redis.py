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

import time
import redis.asyncio as aioredis
from loguru import logger
from app.config import get_settings

settings = get_settings()

redis_pool: aioredis.Redis = None
_last_redis_retry = 0.0


async def connect_to_redis():
    global redis_pool
    try:
        pool = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_timeout=0.5,
            socket_connect_timeout=0.5
        )
        await pool.ping()
        redis_pool = pool
        logger.info("Connected to Redis")
    except Exception as e:
        redis_pool = None
        logger.warning(f"Redis connection offline (using in-memory fallback): {e}")


async def close_redis_connection():
    global redis_pool
    if redis_pool:
        try:
            await redis_pool.aclose()
        except Exception:
            pass
        redis_pool = None
        logger.info("Redis connection closed")


async def get_redis() -> aioredis.Redis:
    """Return the Redis pool, lazily reconnecting if it dropped or never came
    up, so the app recovers without a restart (mirrors get_db() in mongodb.py).

    No per-request `ping()`: the pool object itself survives short blips and
    commands raise on failure — call sites already wrap in try/except, so we
    avoid one extra round-trip per scan (rate-limiter + hash check call this)."""
    global redis_pool, _last_redis_retry

    if redis_pool is not None:
        return redis_pool

    now = time.time()
    if now - _last_redis_retry < 5.0:
        return None
    _last_redis_retry = now

    await connect_to_redis()
    return redis_pool


# ── Key Builders ───────────────────────────────────────────────────────────

def key_image_hash(phash_hex: str) -> str:
    return f"hash:image:{phash_hex}"


def key_video_hash(vhash_hex: str) -> str:
    return f"hash:video:{vhash_hex}"


def key_hash_family(parent_hash: str) -> str:
    return f"hash:family:{parent_hash}"
