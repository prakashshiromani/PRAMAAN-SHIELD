"""
Test Social Media Coordination Module (Module A5)
File: backend/tests/test_social_service.py
"""

import pytest
from app.services.social_service import SocialService


@pytest.mark.asyncio
async def test_social_coordination_pump_and_dump():
    svc = SocialService()
    sample_scam = "BUY NOW! Target 2000% guaranteed upper circuit multibagger tip! Join t.me/fake_stocks"
    res = await svc.analyze_coordination(sample_scam)

    assert res.coordination_score >= 50
    assert res.is_coordinated_scam is True
    assert len(res.detected_patterns) > 0


@pytest.mark.asyncio
async def test_social_coordination_clean_text():
    svc = SocialService()
    clean_text = "SEBI circular on risk disclosure for algorithmic trading."
    res = await svc.analyze_coordination(clean_text)

    assert res.coordination_score < 50
    assert res.is_coordinated_scam is False
