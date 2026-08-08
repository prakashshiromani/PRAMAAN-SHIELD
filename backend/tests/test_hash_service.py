"""
Unit Tests for Perceptual Hashing & Hamming Distance Calculator
File: backend/tests/test_hash_service.py
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from app.services.hash_service import (
    hamming_distance,
    generate_image_phash,
    generate_video_phash,
    check_known_fake_hash,
)
from app.services.trust_score_service import calculate_trust_score

# Hashes drawn from the bundled seed data (app/db/seed.py KNOWN_FAKE_HASHES)
SEEDED_FAKE = "phash:a1b2c3d4e5f67890"   # BSE CEO deepfake — exact match
SEEDED_FAMILY = "phash:a1b2c3d4e5f67891"  # variant in its hash_family
UNKNOWN_HASH = "phash:0123456789abcdef0123456789abcdef"


def test_hamming_distance_identical():
    """Identical hashes must have distance 0."""
    h1 = "a1b2c3d4e5f67890"
    assert hamming_distance(h1, h1) == 0


def test_hamming_distance_one_bit_diff():
    """Hashes differing by 1 bit must return 1."""
    h1 = "0000000000000000"
    h2 = "0000000000000001"
    assert hamming_distance(h1, h2) == 1


def test_hamming_distance_invalid_fallback():
    """Invalid hex strings should return max fallback distance 999."""
    assert hamming_distance("invalid_hex", "a1b2") == 999


def test_generate_image_phash_undecodable_returns_none():
    """
    An undecodable image must not fall back to a fixed placeholder — a constant
    would be shared by every failed upload and collide with known-fake hashes
    seeded in Redis, flagging unrelated media as confirmed scams.
    """
    assert generate_image_phash("non_existent_file.png") is None


def test_generate_video_phash_undecodable_returns_none():
    """
    An undecodable video has no perceptual hash.

    It must not fall back to a fixed placeholder — a constant would be shared
    by every failed upload and collide with the known-fake hashes seeded in
    Redis, flagging unrelated videos as confirmed scam media.
    """
    assert generate_video_phash("non_existent_video.mp4") is None


# ── Verdict determinism: Redis ONLINE vs OFFLINE ─────────────────────────────

def _score_for_hashmatch(match):
    return calculate_trust_score(
        hash_result=match,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )


def test_known_fake_exact_match_redis_offline():
    """
    A seeded known fake must still resolve when Redis is None/offline (the
    get_redis() cooldown path that used to drop the check entirely).
    """
    async def run():
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=None)):
            return await check_known_fake_hash(SEEDED_FAKE)

    match = asyncio.run(run())
    assert match is not None
    assert match["match_type"] == "exact"
    assert match["matched_hash"] == SEEDED_FAKE
    score = _score_for_hashmatch(match)
    assert score["trust_score"] <= 15
    assert score["verdict"] == "SUSPICIOUS"


def test_known_fake_family_variant_redis_offline():
    """An offline lookup must still catch near-neighbor family variants."""
    async def run():
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=None)):
            return await check_known_fake_hash(SEEDED_FAMILY)

    match = asyncio.run(run())
    assert match is not None
    assert match["match_type"] == "family_variant"
    assert "hamming_distance" in match
    score = _score_for_hashmatch(match)
    assert score["trust_score"] <= 15
    assert score["verdict"] == "SUSPICIOUS"


def test_known_fake_online_offline_verdict_identical():
    """
    THE determinism contract: the same pHash must yield the same hard-gate
    trust_score & verdict whether Redis is ONLINE or OFFLINE.
    """
    async def offline():
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=None)):
            return await check_known_fake_hash(SEEDED_FAKE)

    async def online():
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None             # online but no direct key
        redis_mock.scan.return_value = ("0", [])
        redis_mock.smembers.return_value = set()
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=redis_mock)):
            return await check_known_fake_hash(SEEDED_FAKE)

    online_match = asyncio.run(online())
    offline_match = asyncio.run(offline())

    assert online_match is not None and offline_match is not None
    score_online = _score_for_hashmatch(online_match)
    score_offline = _score_for_hashmatch(offline_match)
    assert score_online["trust_score"] == score_offline["trust_score"] <= 15
    assert score_online["verdict"] == score_offline["verdict"] == "SUSPICIOUS"


def test_unknown_hash_no_match_redis_offline_and_online_identical():
    """A hash that is not known fake returns None in BOTH states (no partial)."""
    async def offline():
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=None)):
            return await check_known_fake_hash(UNKNOWN_HASH)

    async def online():
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.scan.return_value = ("0", [])
        redis_mock.smembers.return_value = set()
        with patch("app.services.hash_service.get_redis", new=AsyncMock(return_value=redis_mock)):
            return await check_known_fake_hash(UNKNOWN_HASH)

    off = asyncio.run(offline())
    on = asyncio.run(online())
    assert off is None
    assert on == off  # identical deterministic "no match" outcome
