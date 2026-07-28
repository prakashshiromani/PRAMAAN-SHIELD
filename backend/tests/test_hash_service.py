"""
Unit Tests for Perceptual Hashing & Hamming Distance Calculator
File: backend/tests/test_hash_service.py
"""

import pytest
from app.services.hash_service import (
    hamming_distance,
    generate_image_phash,
    generate_video_phash,
)


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


def test_generate_image_phash_prefix():
    """Generated perceptual hash string should start with 'phash:'."""
    res = generate_image_phash("non_existent_file.png")
    assert res.startswith("phash:")


def test_generate_video_phash_undecodable_returns_none():
    """
    An undecodable video has no perceptual hash.

    It must not fall back to a fixed placeholder — a constant would be shared
    by every failed upload and collide with the known-fake hashes seeded in
    Redis, flagging unrelated videos as confirmed scam media.
    """
    assert generate_video_phash("non_existent_video.mp4") is None
