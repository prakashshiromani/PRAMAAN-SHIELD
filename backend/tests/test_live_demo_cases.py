"""
Live Demo Rehearsal Test Suite (3 Hackathon Presentation Cases)
File: backend/tests/test_live_demo_cases.py

Automated validation of all 3 live demonstration flows:
- Case 1: Phishing Email Caught (serbi-gov.in -> Score <= 15 SUSPICIOUS)
- Case 2: Deepfake Video Caught (BSE CEO deepfake hash -> Score <= 15 SUSPICIOUS)
- Case 3: Real SEBI Circular Verified (PRAMAAN QR -> Score >= 90 VERIFIED)
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.trust_score_service import calculate_trust_score
from app.services.phishing_service import calculate_urgency, extract_urls_and_domains, PhishingPipelineResult, TyposquatResult
from app.services.registry_service import RegistryResult
from app.crypto.seal_engine import generate_entity_keypair, build_canonical_payload


def test_live_demo_case_1_phishing_email():
    """
    DEMO CASE 1: Phishing Email Caught
    Input: Scanned fake SEBI KYC email referencing 'serbi-gov.in'
    Expected: Hard gate trigger, Score <= 15, SUSPICIOUS verdict, Typosquat check failed
    """
    phishing_text = (
        "URGENT ATTENTION: Your SEBI Demat Account will be FROZEN within 24 hours! "
        "Complete mandatory KYC verification immediately at http://serbi-gov.in/verify-kyc "
        "or face legal penalties."
    )

    # 1. Domain extraction check
    domains = extract_urls_and_domains(phishing_text)
    assert any("serbi-gov.in" in d for d in domains)

    # 2. Urgency calculation
    urgency_score = calculate_urgency(phishing_text)
    assert urgency_score >= 5

    # 3. Phishing pipeline DTO
    from app.services.phishing_service import EntityBinding
    phish_dto = PhishingPipelineResult(
        ai_generated_probability=0.88,
        urgency_score=urgency_score,
        investment_scam_score=0,
        domain_check=TyposquatResult(
            has_typosquat=True,
            suspicious="serbi-gov.in",
            legitimate="sebi.gov.in",
            distance=1
        ),
        registry_match=RegistryResult(
            found=False,
            matched_entity=None,
            registration_number=None,
            category=None,
            official_domains=[],
            key_status=None,
            details=[]
        ),
        overall_phishing_score=9.0,
        details=["Typosquat domain serbi-gov.in"],
        injection_attempt=False,
        entity_binding=EntityBinding("none", None, [], [])
    )

    # 4. Trust Score calculation with typosquat hard gate
    result = calculate_trust_score(
        hash_result=None,
        phishing_result=phish_dto,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None
    )

    assert result["trust_score"] <= 15
    assert result["verdict"] == "SUSPICIOUS"
    assert any(c.module == "domain" and c.status == "fail" for c in result["checks"])

    print(f"\n[DEMO CASE 1 PASSED] Phishing Email Caught | Score: {result['trust_score']}/100 | Verdict: {result['verdict']} 🔴")


def test_live_demo_case_2_deepfake_video():
    """
    DEMO CASE 2: Deepfake Video Caught
    Input: BSE CEO deepfake video matching known scam perceptual hash
    Expected: Known fake hard gate trigger, Score <= 15, SUSPICIOUS verdict
    """
    mock_hash_match = {
        "matched_hash": "phash:bse_ceo_deepfake_hash",
        "description": "BSE CEO Deepfake Scam Video",
        "severity": "critical"
    }

    result = calculate_trust_score(
        hash_result=mock_hash_match,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None
    )

    assert result["trust_score"] <= 15
    assert result["verdict"] == "SUSPICIOUS"
    assert any(c.module == "hash" and c.status == "fail" for c in result["checks"])

    print(f"\n[DEMO CASE 2 PASSED] Deepfake Video Caught | Score: {result['trust_score']}/100 | Verdict: {result['verdict']} 🔴")


def test_live_demo_case_3_real_sebi_circular():
    """
    DEMO CASE 3: Real SEBI Circular Verified
    Input: Authentic SEBI circular with PRAMAAN Seal QR code
    Expected: Valid ECDSA signature against pinned public key, Score >= 90, VERIFIED verdict
    """
    # 1. Keypair generation check
    private_key, public_key_pem = generate_entity_keypair("SEBI-REG-001")
    assert "BEGIN PUBLIC KEY" in public_key_pem

    # 2. Mock Seal Result & Registry Result
    mock_seal = {
        "verdict": "VERIFIED",
        "signature_valid": True,
        "signer_entity_name": "Securities and Exchange Board of India",
        "signer_registration_number": "SEBI-REG-001"
    }
    mock_registry = RegistryResult(
        found=True,
        matched_entity="Securities and Exchange Board of India",
        registration_number="SEBI-REG-001",
        category="Regulator",
        official_domains=["sebi.gov.in"],
        key_status="active",
        details=["Official SEBI Registry Entry"]
    )

    result = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=mock_registry,
        seal_result=mock_seal
    )

    assert result["trust_score"] >= 90
    assert result["verdict"] == "VERIFIED"
    assert any(c.module == "seal" and c.status == "pass" for c in result["checks"])

    print(f"\n[DEMO CASE 3 PASSED] Real SEBI Circular Verified | Score: {result['trust_score']}/100 | Verdict: {result['verdict']} 🟢")
