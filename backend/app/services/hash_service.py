"""
PRAMAAN-SHIELD — Perceptual Hash Engine & Redis Lookup
File: backend/app/services/hash_service.py

Performs sub-50ms check against known fakes using Redis in-memory lookup
and Hamming distance calculation.
"""

import json
from typing import Optional, Dict, Any, List
import cv2
import imagehash
import numpy as np
from PIL import Image
from loguru import logger

from app.db.redis import get_redis, key_image_hash, key_video_hash
from app.utils.frame_extract import extract_frames
from app.config import get_settings

settings = get_settings()


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculate Hamming distance between two hex hash strings."""
    try:
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count('1')
    except Exception:
        return 999


def generate_image_phash(image_path_or_bytes) -> str:
    """Generate 64-bit DCT perceptual hash for an image."""
    try:
        if isinstance(image_path_or_bytes, str):
            img = Image.open(image_path_or_bytes)
        else:
            img = Image.open(image_path_or_bytes)
        phash_str = str(imagehash.phash(img))
        return f"phash:{phash_str}"
    except Exception as e:
        logger.error(f"Image pHash generation failed: {e}")
        return "phash:0000000000000000"


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
    Check if a perceptual hash matches any known fake in Redis.
    1. Direct key match: O(1)
    2. Hamming distance <= HASH_HAMMING_THRESHOLD scan
    """
    try:
        redis = await get_redis()
        if not redis:
            logger.warning("Redis instance is offline/None, skipping known fake hash check")
            return None
        clean_hash = phash.replace("phash:", "")

        # Direct match check
        for prefix in ["hash:image:", "hash:video:"]:
            direct = await redis.get(f"{prefix}{clean_hash}")
            if direct:
                logger.info(f"Instant O(1) Redis match for hash: {phash}")
                data = json.loads(direct)
                data["matched_hash"] = phash
                data["match_type"] = "exact"
                return data

        # Scan for near-neighbor Hamming match
        keys = await redis.keys("hash:*")
        for key in keys:
            if key.startswith("hash:family:"):
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
                            "severity": "critical"
                        }
    except Exception as e:
        logger.warning(f"Redis hash check skipped (Redis offline): {e}")
        return None

    return None

