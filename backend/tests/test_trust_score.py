"""
Unit Tests for Hardened Trust Engine & Score Aggregator
File: backend/tests/test_trust_score.py
"""

import pytest
from app.services.trust_score_service import calculate_trust_score


def test_calculate_trust_score_neutral_baseline():
    """Content with no risk markers or affirmative proofs starts at 50 (NEUTRAL)."""
    res = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None
    )
    assert res["trust_score"] == 50
    assert res["verdict"] == "EXERCISE CAUTION"


def test_calculate_trust_score_hard_gate_known_fake():
    """Known fake perceptual hash match must cap score in RED (<= 15)."""
    mock_hash_match = {"matched_hash": "phash:1234", "first_flagged": "2026-01-01"}
    res = calculate_trust_score(
        hash_result=mock_hash_match,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None
    )
    assert res["trust_score"] <= 15
    assert res["verdict"] == "SUSPICIOUS"


def test_calculate_trust_score_affirmative_seal():
    """Verified PRAMAAN Seal boosts score into GREEN (>= 70)."""
    mock_seal_result = {"verdict": "VERIFIED", "signature_valid": True, "entity_name": "SEBI"}
    res = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=mock_seal_result
    )
    assert res["trust_score"] >= 70
    assert res["verdict"] == "VERIFIED"
