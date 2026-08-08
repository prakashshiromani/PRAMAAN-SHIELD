"""
Golden Oracle Determinism Suite — locks the Trust Engine scoring contract
File: backend/tests/test_determinism.py

Purpose: pin the scoring contract so that the "sometimes right, sometimes
wrong" AI-drift bug can never silently return. Every test here is fully
deterministic: no network, no LLM, no Redis, no Mongo (no get_db), no asyncio
timeouts, no on-disk fixtures. All assertions run against real module
functions imported from app.services / app.utils.

NOTE on verdict bands: the module docstring of verdict_for_score declares
">=70 / >=30" — i.e. the CAUTION band begins at 30, NOT 40. These tests lock
the ACTUAL executable contract (30 is CAUTION, 29 is SUSPICIOUS). If the
intent is for 39 to read SUSPICIOUS, that is a production change in
trust_score_service.verdict_for_score, out of scope for a pure test add.
"""

import types

from app.config import get_settings
from app.schemas import CheckStatus, VerdictStatus
from app.services.phishing_service import EntityBinding, PhishingPipelineResult, TyposquatResult
from app.services.registry_service import RegistryResult
from app.services.trust_score_service import calculate_trust_score, verdict_for_score
from app.utils.levenshtein import check_typosquatting

settings = get_settings()


def _neutral_phishing(ai_degraded: bool = False, ai_probability: float = 0.0) -> PhishingPipelineResult:
    """A risk-free ingest that never trips a hard gate or a soft deduction."""
    return PhishingPipelineResult(
        ai_generated_probability=ai_probability,
        urgency_score=2,
        investment_scam_score=0,
        domain_check=TyposquatResult(False, None, None, 0),
        registry_match=RegistryResult(
            found=False,
            registration_number=None,
            matched_entity=None,
            category=None,
            official_domains=[],
            key_status=None,
            details="No SEBI registered entity match found",
            match_basis=None,
        ),
        overall_phishing_score=1.5,
        details=[],
        injection_attempt=False,
        entity_binding=EntityBinding("none", None, [], []),
        ai_degraded=ai_degraded,
    )


def _authentic_voice(liveness: int = 90) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        analysis_failed=False,
        is_synthetic=False,
        liveness_score=liveness,
        verdict="LIKELY GENUINE",
        model_mode="production",
    )


def _authentic_video() -> types.SimpleNamespace:
    return types.SimpleNamespace(
        analysis_failed=False,
        is_deepfake=False,
        deepfake_probability=10,
        confidence_level="high",
        mode="production",
    )


def test_ai_degraded_does_not_change_verdict():
    """Verdict for a non-scam input must be identical whether or not the AI
    advisory layer is up. AI health only adds a 0-contribution SKIP check."""
    degraded = calculate_trust_score(
        hash_result=None,
        phishing_result=_neutral_phishing(ai_degraded=True, ai_probability=0.0),
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )
    healthy_low_confidence = calculate_trust_score(
        hash_result=None,
        phishing_result=_neutral_phishing(ai_degraded=False, ai_probability=0.3),
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )

    assert degraded["trust_score"] == healthy_low_confidence["trust_score"]
    assert degraded["trust_score"] == 50
    assert degraded["verdict"] == healthy_low_confidence["verdict"]
    assert degraded["verdict"] == VerdictStatus.CAUTION
    assert degraded["verdict"] != VerdictStatus.VERIFIED


def test_offline_skips_do_not_flip_verdict():
    """A SKIP check with 0 contribution must leave score & verdict untouched."""
    no_voice_result = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )

    offline_voice = types.SimpleNamespace(
        analysis_failed=True,
        is_synthetic=False,
        liveness_score=0,
        verdict="Voice Analysis Skipped due to processing error",
        model_mode="forensics",
    )
    with_voice_skip = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=offline_voice,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )

    assert with_voice_skip["trust_score"] == no_voice_result["trust_score"]
    assert with_voice_skip["trust_score"] == 50
    assert with_voice_skip["verdict"] == no_voice_result["verdict"]
    assert with_voice_skip["verdict"] == VerdictStatus.CAUTION

    voice_checks = [c for c in with_voice_skip["checks"] if c.module == "voice"]
    assert voice_checks, "voice SKIP check must exist when voice analysis is offline"
    assert all(c.status == CheckStatus.SKIP for c in voice_checks)
    assert all(c.contribution == 0 for c in voice_checks)


def test_hard_gate_cap_is_final():
    """Hard gates must be a final ceiling: massive positive boosts (valid seal
    +45, authentic voice +50, authentic video +50) cannot lift a known-fake
    hash out of the capped red zone."""
    known_fake_hash = {
        "matched_hash": "phash:deadbeefcafebabe",
        "description": "Known scam media from Sebi AMBER list",
        "first_flagged": "2026-01-01",
    }
    seal_verified = {
        "verdict": "VERIFIED",
        "signature_valid": True,
        "content_match": True,
        "signer_entity_name": "SEBI",
        "signer_registration_number": "REGULATOR",
    }

    res = calculate_trust_score(
        hash_result=known_fake_hash,
        phishing_result=None,
        voice_result=_authentic_voice(90),
        video_result=_authentic_video(),
        registry_result=None,
        seal_result=seal_verified,
    )

    assert res["trust_score"] <= settings.WEIGHT_HARD_GATE_CAP
    assert res["trust_score"] <= 15
    assert res["verdict"] != VerdictStatus.VERIFIED
    assert res["verdict"] == VerdictStatus.SUSPICIOUS
    assert any(c.module == "hash" and c.status == CheckStatus.FAIL for c in res["checks"])
    assert any(c.module == "seal" and c.status == CheckStatus.PASS for c in res["checks"])


def test_verdict_threshold_boundaries():
    """Exact band mapping locked against the real verdict_for_score.
    Verified live contract: VERIFIED >= 70, CAUTION >= 30, SUSPICIOUS < 30."""
    assert verdict_for_score(69) == VerdictStatus.CAUTION          # not VERIFIED
    assert verdict_for_score(70) == VerdictStatus.VERIFIED
    assert verdict_for_score(40) == VerdictStatus.CAUTION
    assert verdict_for_score(39) == VerdictStatus.CAUTION          # floor is 30, not 40
    assert verdict_for_score(30) == VerdictStatus.CAUTION          # exact CAUTION floor
    assert verdict_for_score(29) == VerdictStatus.SUSPICIOUS       # exact SUSPICIOUS ceiling
    assert verdict_for_score(0) == VerdictStatus.SUSPICIOUS


def test_duplicate_scans_identical_score():
    """Running the aggregator twice on identical inputs must yield an identical
    score and verdict (fully deterministic)."""
    scan_inputs = dict(
        hash_result=None,
        phishing_result=_neutral_phishing(),
        voice_result=_authentic_voice(80),
        video_result=None,
        registry_result=None,
        seal_result={"verdict": "VERIFIED", "signature_valid": True, "content_match": True},
    )

    first = calculate_trust_score(**scan_inputs)
    second = calculate_trust_score(**scan_inputs)

    assert first["trust_score"] == second["trust_score"]
    assert first["verdict"] == second["verdict"]
    assert first["verdict"] == VerdictStatus.VERIFIED  # seal +45 & voice +50 => >= 70
    assert first["explainability_en"] == second["explainability_en"]
    assert [c.contribution for c in first["checks"]] == [c.contribution for c in second["checks"]]


def test_typosquat_0byte_audio_no_forgery():
    """Regression: a silent/0-byte audio must mark analysis_failed -> SKIP (0
    contribution, never a boost); a seib.gov.in typo must invoke the real
    typosquat matcher and trip the domain hard gate."""

    # 1. silent / 0-byte audio -> analysis_failed -> SKIP, never boosts.
    silent_audio = types.SimpleNamespace(
        analysis_failed=True,
        is_synthetic=False,
        liveness_score=0,
        verdict="Voice Analysis Failed: audio is silent or too short",
        model_mode="forensics",
    )
    res_silent = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=silent_audio,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )
    assert res_silent["trust_score"] == 50
    silent_voice_checks = [c for c in res_silent["checks"] if c.module == "voice"]
    assert silent_voice_checks
    assert all(c.status == CheckStatus.SKIP for c in silent_voice_checks)
    assert all(c.contribution == 0 for c in silent_voice_checks)
    assert not any(c.status == CheckStatus.PASS for c in silent_voice_checks)

    # control: genuine audio DOES boost, proving silence was not boosted.
    res_genuine = calculate_trust_score(
        hash_result=None,
        phishing_result=None,
        voice_result=_authentic_voice(95),
        video_result=None,
        registry_result=None,
        seal_result=None,
    )
    assert res_genuine["trust_score"] == 100
    assert any(c.status == CheckStatus.PASS and c.contribution == 50 for c in res_genuine["checks"])

    # 2. seib.gov.in is a one-swap typo of official sebi.gov.in.
    matches = check_typosquatting(["seib.gov.in"])
    assert matches, "seib.gov.in must be flagged as a typosquat of sebi.gov.in"
    assert matches[0]["suspicious_domain"] == "seib.gov.in"
    assert matches[0]["legitimate_domain"] == "sebi.gov.in"
    assert matches[0]["distance"] == 2

    typo_phishing = PhishingPipelineResult(
        ai_generated_probability=0.0,
        urgency_score=0,
        investment_scam_score=0,
        domain_check=TyposquatResult(True, "seib.gov.in", "sebi.gov.in", 2),
        registry_match=RegistryResult(
            found=False, registration_number=None, matched_entity=None,
            category=None, official_domains=[], key_status=None,
            details="No match", match_basis=None,
        ),
        overall_phishing_score=4.0,
        details=["Typosquat domain detected"],
        injection_attempt=False,
        entity_binding=EntityBinding("none", None, [], []),
    )
    res_typo = calculate_trust_score(
        hash_result=None,
        phishing_result=typo_phishing,
        voice_result=None,
        video_result=None,
        registry_result=None,
        seal_result=None,
    )
    assert res_typo["trust_score"] <= 15
    assert res_typo["verdict"] == VerdictStatus.SUSPICIOUS
    assert any(c.module == "domain" and c.status == CheckStatus.FAIL for c in res_typo["checks"])