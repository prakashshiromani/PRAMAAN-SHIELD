"""
PRAMAAN-SHIELD — Entity Domain Binding & Impersonation Bypass Test Suite
File: backend/tests/test_entity_binding.py
"""

import pytest
import asyncio
from app.services.phishing_service import PhishingService
from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService
from app.services.trust_score_service import calculate_trust_score


@pytest.fixture
def phishing_service():
    return PhishingService(GeminiService(), RegistryService())


@pytest.mark.asyncio
async def test_sebi_impersonation_bypass_blocked(phishing_service):
    """
    TEST: 'Advisory from SEBI. Complete your account update at https://sebi-kyc-portal.xyz/update'
    EXPECTED: Impersonation hard gate triggered, score <= 20, verdict SUSPICIOUS.
    """
    text = "Advisory from SEBI. Complete your account update at https://sebi-kyc-portal.xyz/update at your convenience."
    result = await phishing_service.analyze_text(text)

    assert result.entity_binding.status == "impersonation"
    assert "sebi-kyc-portal.xyz" in result.entity_binding.offending_domains

    trust = calculate_trust_score(
        hash_result=None,
        phishing_result=result,
        voice_result=None,
        video_result=None,
        registry_result=result.registry_match,
        seal_result=None
    )

    assert trust["trust_score"] <= 20
    assert trust["verdict"].value == "SUSPICIOUS"
    assert any(c.module == "registry" and c.status == "fail" for c in trust["checks"])


@pytest.mark.asyncio
async def test_zerodha_impersonation_bypass_blocked(phishing_service):
    """
    TEST: 'Zerodha Broking Limited notice. Deposit funds via https://zerodha-secure-payments.info/pay'
    EXPECTED: Impersonation hard gate triggered, score <= 20, verdict SUSPICIOUS.
    """
    text = "Zerodha Broking Limited notice. Please deposit funds via https://zerodha-secure-payments.info/pay"
    result = await phishing_service.analyze_text(text)

    assert result.entity_binding.status == "impersonation"
    assert "zerodha-secure-payments.info" in result.entity_binding.offending_domains

    trust = calculate_trust_score(
        hash_result=None,
        phishing_result=result,
        voice_result=None,
        video_result=None,
        registry_result=result.registry_match,
        seal_result=None
    )

    assert trust["trust_score"] <= 20
    assert trust["verdict"].value == "SUSPICIOUS"
    assert any(c.module == "registry" and c.status == "fail" for c in trust["checks"])


@pytest.mark.asyncio
async def test_genuine_zerodha_advisory_verified(phishing_service):
    """
    TEST: Authentic Zerodha advisory with zerodha.com link & reg no INZ000031633.
    EXPECTED: Bound entity, score >= 70, verdict VERIFIED, matched entity 'Zerodha Broking Limited'.
    """
    text = (
        "Official Advisory from Zerodha Broking Limited (SEBI Reg: INZ000031633). "
        "Please never share your password, OTP, or PIN with anyone. "
        "Always verify trading activity directly on zerodha.com or kite.zerodha.com."
    )
    result = await phishing_service.analyze_text(text)

    assert result.entity_binding.status == "bound"
    assert result.registry_match.found is True
    assert result.registry_match.matched_entity == "Zerodha Broking Limited"

    trust = calculate_trust_score(
        hash_result=None,
        phishing_result=result,
        voice_result=None,
        video_result=None,
        registry_result=result.registry_match,
        seal_result=None
    )

    assert trust["trust_score"] >= 70
    assert trust["verdict"].value == "VERIFIED"


@pytest.mark.asyncio
async def test_unbound_entity_name_no_link(phishing_service):
    """
    TEST: Message names SEBI but contains no links.
    EXPECTED: Unbound status, boost = 0, WARN check item.
    """
    text = "Important notice regarding SEBI compliance guidelines for retail investors."
    result = await phishing_service.analyze_text(text)

    assert result.entity_binding.status == "unbound"

    trust = calculate_trust_score(
        hash_result=None,
        phishing_result=result,
        voice_result=None,
        video_result=None,
        registry_result=result.registry_match,
        seal_result=None
    )

    # Base 50, zero boost
    assert trust["trust_score"] == 50
    assert any(c.module == "registry" and c.status == "warn" and c.contribution == 0 for c in trust["checks"])
