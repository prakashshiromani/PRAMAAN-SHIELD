"""
PRAMAAN-SHIELD — Hardened Trust Engine & Score Aggregator
File: backend/app/services/trust_score_service.py

SECURITY.md §7:
- Neutral baseline: 50
- Hard gates: Known Fake, Forged Seal, Typosquat, Injection → IMMEDIATE RED CAP (<= 15)
- Affirmative proof: Valid PRAMAAN Seal (+45), Exact SEBI Registry Match (+15) → GREEN (>= 70)
"""

from typing import Optional, List, Dict, Any
from app.schemas import CheckResult, CheckStatus, VerdictStatus
from app.services.phishing_service import PhishingPipelineResult
from app.services.voice_service import VoiceResult
from app.services.video_service import VideoResult
from app.services.registry_service import RegistryResult
from app.config import get_settings

settings = get_settings()


def generate_explanation_en(checks: List[CheckResult]) -> str:
    """Generate concise English explainability summary."""
    fails = [c for c in checks if c.status == CheckStatus.FAIL]
    passes = [c for c in checks if c.status == CheckStatus.PASS]

    if fails:
        reasons = " | ".join([f"🚫 {c.label}: {c.detail}" for c in fails])
        return f"Risk Flags Detected: {reasons}"
    elif passes:
        reasons = " | ".join([f"✅ {c.label}: {c.detail}" for c in passes])
        return f"Trust Confirmed: {reasons}"
    else:
        return "Neutral content — no strong risk markers or cryptographic seal found. Exercise normal caution."


def generate_explanation_hi(checks: List[CheckResult]) -> str:
    """Generate concise Hindi explainability summary."""
    fails = [c for c in checks if c.status == CheckStatus.FAIL]
    passes = [c for c in checks if c.status == CheckStatus.PASS]

    if fails:
        reasons = " | ".join([f"🚫 {c.label}: {c.detail}" for c in fails])
        return f"जोखिम के संकेत मिले: {reasons}"
    elif passes:
        reasons = " | ".join([f"✅ {c.label}: {c.detail}" for c in passes])
        return f"विश्वास की पुष्टि: {reasons}"
    else:
        return "सामान्य सामग्री — कोई क्रिप्टोग्राफिक Seal या गंभीर खतरा नहीं मिला। सामान्य सावधानी बरतें।"


def calculate_trust_score(
    hash_result: Optional[Dict[str, Any]],
    phishing_result: Optional[PhishingPipelineResult],
    voice_result: Optional[VoiceResult],
    video_result: Optional[VideoResult],
    registry_result: Optional[RegistryResult],
    seal_result: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Hardened Trust Engine Aggregator.
    Returns dict compatible with ScanResponse schema.
    """
    score = 50
    checks: List[CheckResult] = []
    hard_gate_triggered = False

    # 0. Baseline Ledger Entry
    checks.append(CheckResult(
        module="baseline",
        status=CheckStatus.SKIP,
        label="Neutral Baseline",
        label_hi="तटस्थ प्रारंभिक स्कोर",
        detail="Every scan starts at 50/100 baseline",
        detail_hi="प्रत्येक स्कैन 50/100 के तटस्थ स्कोर से शुरू होता है",
        contribution=50
    ))

    if phishing_result and getattr(phishing_result, "ai_degraded", False):
        checks.append(CheckResult(
            module="ai",
            status=CheckStatus.SKIP,
            label="AI Advisory Layer Unavailable",
            label_hi="AI विश्लेषण मोड (ऑफलाइन)",
            detail="Deterministic registry & pattern checks active",
            detail_hi="केवल नियम-आधारित और SEBI रजिस्ट्री जांच सक्रिय हैं",
            contribution=0
        ))

    # ── HARD GATES (Instant Red Cap <= 15) ──────────────────────────────────
    if hash_result:
        hard_gate_triggered = True
        checks.append(CheckResult(
            module="hash",
            status=CheckStatus.FAIL,
            label="Known Fake Media Detected",
            label_hi="ज्ञात फर्जी मीडिया पहचान",
            detail=f"{hash_result.get('description', 'Matches known scam media database')}",
            detail_hi="ज्ञात स्कैम मीडिया डेटाबेस से मेल खाता है",
            contribution=-50
        ))

    if seal_result and (seal_result.get("verdict") in ["FORGED", "TAMPERED", "UNVERIFIED"] or seal_result.get("is_valid") is False):
        hard_gate_triggered = True
        seal_verdict = seal_result.get('verdict', 'FORGED')
        checks.append(CheckResult(
            module="seal",
            status=CheckStatus.FAIL,
            label=f"PRAMAAN Seal {seal_verdict}",
            label_hi=f"प्रमाण सील {seal_verdict}",
            detail=seal_result.get("message_en", "Cryptographic signature validation failed"),
            detail_hi=seal_result.get("message_hi", "क्रिप्टोग्राफिक डिजिटल हस्ताक्षर विफल या नकली पाया गया"),
            contribution=-50
        ))

    if phishing_result and phishing_result.domain_check.has_typosquat:
        hard_gate_triggered = True
        checks.append(CheckResult(
            module="domain",
            status=CheckStatus.FAIL,
            label="Typosquat Domain Detected",
            label_hi="नकली डोमेन (Typosquat) मिला",
            detail=f"{phishing_result.domain_check.suspicious} → spoofing {phishing_result.domain_check.legitimate}",
            detail_hi=f"अमान्य डोमेन {phishing_result.domain_check.suspicious} असली {phishing_result.domain_check.legitimate} की नकल कर रहा है",
            contribution=-40
        ))

    if phishing_result and phishing_result.urgency_score >= 8:
        hard_gate_triggered = True
        checks.append(CheckResult(
            module="phishing",
            status=CheckStatus.FAIL,
            label="Critical Threat / Panic Language Scam",
            label_hi="गंभीर धमकी / पैनिक संदेश",
            detail=f"Urgency score: {phishing_result.urgency_score}/10 — Severe account block/freeze threat detected",
            detail_hi=f"आपातकालीन स्कोर: {phishing_result.urgency_score}/10 — खाता ब्लॉक/फ्रीज करने की धमकी मिली",
            contribution=-40
        ))

    if phishing_result and phishing_result.injection_attempt:
        hard_gate_triggered = True
        checks.append(CheckResult(
            module="security",
            status=CheckStatus.FAIL,
            label="Prompt Injection / Instruction Attack",
            label_hi="प्रॉम्प्ट इंजेक्शन हमला",
            detail="Content tried to manipulate AI model rules",
            detail_hi="सामग्री ने सुरक्षा नियमों में हेरफेर की कोशिश की",
            contribution=-30
        ))

    # ── ENTITY-DOMAIN BINDING EVALUATION ─────────────────────────────────────
    eb_status = "none"
    if phishing_result and hasattr(phishing_result, "entity_binding"):
        eb = phishing_result.entity_binding
        eb_status = eb.status
        if eb.status == "impersonation":
            hard_gate_triggered = True
            off_str = ", ".join(eb.offending_domains) if eb.offending_domains else "unverified link"
            impersonation_weight = getattr(settings, "WEIGHT_ENTITY_IMPERSONATION", 30)
            score -= impersonation_weight
            checks.append(CheckResult(
                module="registry",
                status=CheckStatus.FAIL,
                label="Entity Impersonation — Unofficial Link",
                label_hi="संस्था का अनधिकृत लिंक (धोखाधड़ी)",
                detail=f"Claims to be '{eb.entity}' but contains unofficial domain ({off_str})",
                detail_hi=f"मैसेज '{eb.entity}' का दावा करता है लेकिन लिंक अनधिकृत ({off_str}) है",
                contribution=-impersonation_weight
            ))
        elif eb.status == "unbound":
            checks.append(CheckResult(
                module="registry",
                status=CheckStatus.WARN,
                label="Entity Named but Unverified Link",
                label_hi="संस्था का नाम है पर लिंक असत्यापित",
                detail=f"Mentions '{eb.entity}' but links do not match official domains",
                detail_hi=f"मैसेज में '{eb.entity}' का उल्लेख है लेकिन लिंक आधिकारिक नहीं हैं",
                contribution=0
            ))

    # ── SOFT SIGNALS ────────────────────────────────────────────────────────
    if phishing_result:
        if 5 <= phishing_result.urgency_score < 8 or phishing_result.overall_phishing_score >= 5.0:
            deduction = 35 if phishing_result.urgency_score >= 5 else settings.WEIGHT_PHISHING_HIGH
            score -= deduction
            checks.append(CheckResult(
                module="phishing",
                status=CheckStatus.FAIL if phishing_result.urgency_score >= 5 else CheckStatus.WARN,
                label="High Urgency Scam Language",
                label_hi="उच्च दबाव / धोखाधड़ी की भाषा",
                detail=f"Urgency score: {phishing_result.urgency_score}/10 — Threat/panic language detected",
                detail_hi=f"आपातकालीन स्कोर: {phishing_result.urgency_score}/10 — जल्दबाजी का दबाव बनाया गया",
                contribution=-deduction
            ))

        elif hasattr(phishing_result, 'investment_scam_score') and phishing_result.investment_scam_score >= 4:
            score -= 20
            checks.append(CheckResult(
                module="phishing",
                status=CheckStatus.WARN,
                label="Unregulated Investment / Pump-and-Dump Tip",
                label_hi="गैर-नियामक निवेश सलाह / पंप-एंड-डंप",
                detail=f"Investment scam score: {phishing_result.investment_scam_score}/10 — Guaranteed returns/VIP calls",
                detail_hi=f"निवेश स्कैम स्कोर: {phishing_result.investment_scam_score}/10 — गारंटीकृत लाभ / टेलीग्राम कॉल",
                contribution=-20
            ))

    if voice_result and voice_result.is_synthetic:
        hard_gate_triggered = True
        voice_deduction = max(35, settings.WEIGHT_VOICE_SYNTHETIC)
        score -= voice_deduction
        checks.append(CheckResult(
            module="voice",
            status=CheckStatus.FAIL,
            label="Voice Synthetic / Cloned",
            label_hi="नकली / AI वॉयस क्लोनिंग",
            detail=voice_result.verdict,
            detail_hi="आवाज कृत्रिम या AI द्वारा क्लोन की गई पाई गई",
            contribution=-voice_deduction
        ))

    if video_result and video_result.is_deepfake:
        hard_gate_triggered = True
        video_deduction = max(35, settings.WEIGHT_VIDEO_DEEPFAKE)
        score -= video_deduction
        checks.append(CheckResult(
            module="video",
            status=CheckStatus.FAIL,
            label="Deepfake Manipulation Detected",
            label_hi="डीपफेक वीडियो हेरफेर पहचाना गया",
            detail=f"Facial & temporal manipulation probability: {video_result.deepfake_probability}%",
            detail_hi=f"वीडियो में AI चेहरे और हेरफेर की संभावना: {video_result.deepfake_probability}%",
            contribution=-video_deduction
        ))

    # ── AFFIRMATIVE PROOF (Boost to GREEN >= 70) ────────────────────────────
    if seal_result and seal_result.get("verdict") == "VERIFIED" and seal_result.get("signature_valid", True):
        score += settings.WEIGHT_SEAL_VALID
        checks.append(CheckResult(
            module="seal",
            status=CheckStatus.PASS,
            label="Valid PRAMAAN Seal",
            label_hi="सत्यापित प्रमाण सील (ECDSA)",
            detail=f"Signed by {seal_result.get('signer_entity_name', 'Registered Entity')} ({seal_result.get('signer_registration_number', 'SEBI')})",
            detail_hi=f"{seal_result.get('signer_entity_name', 'पंजीकृत संस्था')} ({seal_result.get('signer_registration_number', 'SEBI')}) द्वारा डिजिटल हस्ताक्षरित",
            contribution=+settings.WEIGHT_SEAL_VALID
        ))

    if registry_result and registry_result.found and (phishing_result is None or phishing_result.urgency_score < 5):
        if eb_status in ("bound", "none"):
            is_clean = (
                phishing_result is not None and
                phishing_result.urgency_score <= 2 and
                not phishing_result.domain_check.has_typosquat and
                phishing_result.overall_phishing_score < 4.0
            )
            bound_bonus = getattr(settings, "WEIGHT_DOMAIN_BOUND_BONUS", 20)
            boost = settings.WEIGHT_REGISTRY_MATCH + (bound_bonus if is_clean else 0)
            score += boost
            checks.append(CheckResult(
                module="registry",
                status=CheckStatus.PASS,
                label="SEBI Registered Entity Match",
                label_hi="SEBI पंजीकृत संस्था का सत्यापन",
                detail=f"Matched official registry: '{registry_result.matched_entity}' ({registry_result.registration_number})",
                detail_hi=f"आधिकारिक SEBI रजिस्टर से मेल मिला: '{registry_result.matched_entity}' ({registry_result.registration_number})",
                contribution=+boost
            ))

    # Gradated Hard Gate Ceiling
    if hard_gate_triggered:
        hard_gate_modules = {"hash", "seal", "domain", "phishing", "security", "registry", "video", "voice"}
        gate_count = sum(1 for c in checks if c.module in hard_gate_modules and c.status == CheckStatus.FAIL)
        hard_gate_cap = getattr(settings, "WEIGHT_HARD_GATE_CAP", 15)
        ceiling = max(0, hard_gate_cap - (gate_count - 1) * 5)
        score = min(score, ceiling)

    # Clamp Bounds [0, 100]
    score = max(0, min(100, score))

    # Verdict Classification
    if score >= 70:
        verdict = VerdictStatus.VERIFIED
    elif score >= 30:
        verdict = VerdictStatus.CAUTION
    else:
        verdict = VerdictStatus.SUSPICIOUS

    return {
        "trust_score": score,
        "verdict": verdict,
        "verdict_label_en": verdict.value,
        "verdict_label_hi": "सत्यापित" if verdict == VerdictStatus.VERIFIED else ("सावधानी" if verdict == VerdictStatus.CAUTION else "संदेहास्पद"),
        "checks": checks,
        "explainability_en": generate_explanation_en(checks),
        "explainability_hi": generate_explanation_hi(checks)
    }
