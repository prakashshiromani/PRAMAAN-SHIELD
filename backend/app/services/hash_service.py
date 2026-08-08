"""
PRAMAAN-SHIELD — Perceptual Hash Engine & Redis Lookup
File: backend/app/services/hash_service.py

Performs sub-50ms check against known fakes using Redis in-memory lookup
and Hamming distance calculation.

Verdict determinism contract: Redis/DB availability must never change the
final trust_score/verdict for identical input. When Redis is ONLINE the check
is answered from the Redis index; when Redis is OFFLINE (or inside the
get_redis() reconnect cooldown) it is answered from the SAME seeded known-fake
known-fake list (app.db.seed.KNOWN_FAKE_HASHES) materialized in memory here —
so an identical pHash produces the identical hard-gate FAIL both online and
offline. A match is never silently dropped; a non-match deterministically
returns None in both states.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Set
import cv2
import imagehash
import numpy as np
from PIL import Image
from loguru import logger

from app.db.redis import get_redis
from app.utils.frame_extract import extract_frames
from app.config import get_settings

settings = get_settings()

# Guard against decompression-bomb DoS: a tiny PNG that expands to a huge
# bitmap can exhaust CPU/RAM during phash. Reject anything above the ceiling
# instead of decoding it fully.
Image.MAX_IMAGE_PIXELS = 25_000_000  # ~250 MP

_IMAGE_MAX_PIXELS = 25_000_000

# ── Deterministic offline known-fake index ──────────────────────────────────
# Seed data (app/db/seed.py KNOWN_FAKE_HASHES) is materialized in-memory so the
# known-fake gate survives a Redis outage / reconnect cooldown WITHOUT the check
# silently disappearing. The same hashes Redis was seeded from are answered here.
_EMBEDDED_EXACT: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None
_EMBEDDED_FAMILIES: Optional[Dict[str, Set[str]]] = None


def _load_seeded_known_fakes() -> bool:
    """
    Materialize the in-memory known-fake index from the bundled seed data.
    Returns True when seed data loads, False when it is genuinely absent.
    """
    global _EMBEDDED_EXACT, _EMBEDDED_FAMILIES
    if _EMBEDDED_EXACT is not None and _EMBEDDED_FAMILIES is not None:
        _EMBEDDED_EXACT.setdefault("image", {})
        _EMBEDDED_EXACT.setdefault("video", {})
        return True
    try:
        from app.db.seed import KNOWN_FAKE_HASHES
    except Exception as e:
        logger.warning(f"Known-fake seed unavailable ({e}); no in-memory fallback index (offline → None)")
        _EMBEDDED_EXACT = {"image": {}, "video": {}}
        _EMBEDDED_FAMILIES = {}
        return False

    exact: Dict[str, Dict[str, Dict]] = {"image": {}, "video": {}}
    families: Dict[str, Set[str]] = {}
    for fake in KNOWN_FAKE_HASHES:
        hex_hash = str(fake.get("perceptual_hash") or "").replace("phash:", "").strip().lower()
        if not hex_hash:
            continue
        # Same kind mapping used by seed.py when it keys Redis:
        # content_type == "image" → hash:image:, everything else → hash:video:
        kind = "image" if fake.get("content_type") == "image" else "video"
        first_flagged = fake.get("first_flagged")
        exact[kind][hex_hash] = {
            "description": fake.get("description"),
            "first_flagged": first_flagged.isoformat() if hasattr(first_flagged, "isoformat") else first_flagged,
            "flagged_by": fake.get("flagged_by"),
            "detection_count": fake.get("detection_count"),
            "severity": fake.get("severity"),
        }
        family = {
            str(m).replace("phash:", "").strip().lower()
            for m in (fake.get("hash_family") or [])
            if str(m).replace("phash:", "").strip()
        }
        if family:
            families[hex_hash] = family

    _EMBEDDED_EXACT = exact
    _EMBEDDED_FAMILIES = families
    return True


def _seeded_fake_match(clean_hash: str, phash: str) -> Optional[Dict[str, Any]]:
    """
    Deterministic offline answer for a known-fake lookup, mirroring the dict
    shape the Redis path would return (exact match or family_variant).
    Returns None only when there is genuinely no match in the seeded data.
    """
    _load_seeded_known_fakes()
    for kind in ("image", "video"):
        data = _EMBEDDED_EXACT[kind].get(clean_hash)
        if data:
            return {**data, "matched_hash": phash, "match_type": "exact"}
    for _parent, members in _EMBEDDED_FAMILIES.items():
        for member in members:
            dist = hamming_distance(clean_hash, member)
            if dist <= settings.HASH_HAMMING_THRESHOLD:
                return {
                    "matched_hash": f"phash:{member}",
                    "match_type": "family_variant",
                    "hamming_distance": dist,
                    "description": "Variant of known fake media (cropped/re-encoded)",
                    "severity": "critical",
                }
    return None


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculate Hamming distance between two hex hash strings."""
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count('1')
    except Exception:
        return 999


def generate_image_phash(image_path_or_bytes) -> Optional[str]:
    """Generate a 64-bit DCT perceptual hash for an image.

    Returns None on any failure — NEVER a constant placeholder — so different
    unparseable/corrupted images don't collapse onto one shared hash (which
    would collide with seeded known-fake families and mis-flag unrelated media).
    """
    try:
        img = Image.open(image_path_or_bytes)
        img.load()                      # force decode to trip MAX_IMAGE_PIXELS
        if img.width * img.height > _IMAGE_MAX_PIXELS:
            logger.warning("Image exceeds pixel ceiling; skipping phash")
            return None
        phash_str = str(imagehash.phash(img))
        return f"phash:{phash_str}"
    except Exception as e:
        logger.error(f"Image pHash generation failed: {e}")
        return None


def _keyframe_phash(frames: List[np.ndarray]) -> Optional[str]:
    """
    Collapse sampled keyframes into a single 64-bit DCT hash.

    Each frame gets its own 8x8 DCT pHash; the bits are then combined by
    majority vote across frames. Re-encoding or cropping perturbs individual
    frames but rarely flips the majority, so the result stays within the
    Hamming radius used for family matching.
    """
    frame_bits = []
    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_bits.append(imagehash.phash(Image.fromarray(rgb)).hash.flatten())

    if not frame_bits:
        return None

    majority = np.mean(np.array(frame_bits, dtype=np.float32), axis=0) >= 0.5
    value = 0
    for bit in majority:
        value = (value << 1) | int(bit)
    return f"{value:016x}"


def generate_video_phash(video_path: str) -> Optional[str]:
    """
    Generate a 64-bit perceptual hash for a video file.

    Returns None when no frame can be decoded. It deliberately does NOT fall
    back to a fixed placeholder: a constant would be identical for every
    undecodable upload and collide with the known-fake hashes seeded in Redis,
    flagging unrelated videos as confirmed scam media.
    """
    # Primary path (TRD §8.1) — requires a system ffmpeg binary on PATH.
    try:
        from videohash import VideoHash
        vh = VideoHash(path=video_path)
        digest = str(vh.hash_hex).lower().removeprefix("0x")
        return f"phash:{digest}"
    except Exception as e:
        logger.warning(f"VideoHash unavailable ({e}); using OpenCV keyframe pHash")

    # Fallback — OpenCV keyframe sampling, no external binary needed.
    try:
        digest = _keyframe_phash(extract_frames(video_path))
        if digest:
            return f"phash:{digest}"
        logger.error(f"No decodable frames in {video_path}; perceptual hash unavailable")
    except Exception as e:
        logger.error(f"Video pHash generation failed: {e}")

    return None


async def check_known_fake_hash(phash: str) -> Optional[Dict[str, Any]]:
    """
    Check if a perceptual hash matches any known fake.
    1. Direct key match: O(1)
    2. Hamming distance <= HASH_HAMMING_THRESHOLD scan
    3. In-memory seeded-index fallback when Redis is offline (remove-proof)

    Redis availability never changes the outcome for a seeded known fake: a
    pHash that matches ONLINE also matches OFFLINE (deterministic hard-gate),
    and a pHash that matches neither deterministically returns None in both.
    """
    clean_hash = phash.replace("phash:", "").strip().lower()

    # ── 1. Redis (primary) ─────────────────────────────────────────────────
    redis = None
    try:
        redis = await get_redis()
    except Exception as e:
        logger.warning(f"Redis health check failed ({e}); using in-memory known-fake index")

    if redis is not None:
        try:
            # Direct match check
            for prefix in ["hash:image:", "hash:video:"]:
                direct = await redis.get(f"{prefix}{clean_hash}")
                if direct:
                    logger.info(f"Instant O(1) Redis match for hash: {phash}")
                    data = json.loads(direct)
                    data["matched_hash"] = phash
                    data["match_type"] = "exact"
                    return data

            # Scan for near-neighbor Hamming match using SCAN cursors, never KEYS.
            # KEYS blocks Redis for the whole keyspace on every request (O(N)/DoS);
            # SCAN yields results in small batches without blocking writers.
            family_keys = []
            cursor = "0"
            while True:
                cursor, batch = await redis.scan(cursor=cursor, match="hash:family:*", count=100)
                family_keys.extend(batch)
                if not cursor:
                    break

            for key in family_keys:
                # Family members set check
                members = await redis.smembers(key)
                for member in members:
                    dist = hamming_distance(clean_hash, member)
                    if dist <= settings.HASH_HAMMING_THRESHOLD:
                        logger.info(f"Near-neighbor family match: dist={dist} for {phash}")
                        return {
                            "matched_hash": f"phash:{member}",
                            "match_type": "family_variant",
                            "hamming_distance": dist,
                            "description": "Variant of known fake media (cropped/re-encoded)",
                            "severity": "critical",
                        }
        except Exception as e:
            logger.warning(f"Redis hash check failed ({e}); falling back to in-memory known-fake index")

    # ── 2. Deterministic in-memory seed fallback ────────────────────────────
    # Redis is None/offline (cooldown) OR found no match. Consult the SAME
    # seeded data Redis was populated from so the offline answer equals what an
    # online lookup would have returned — a known fake is NEVER silently dropped.
    match = _seeded_fake_match(clean_hash, phash)
    if match:
        logger.info(f"In-memory seeded known-fake match for hash: {phash} (Redis {'online' if redis is not None else 'offline'})")
        return match

    return None

