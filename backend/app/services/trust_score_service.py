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


def verdict_for_score(score: int) -> VerdictStatus:
    """Single source of truth for the >=70 / >=30 verdict bands."""
    if score >= 70:
        return VerdictStatus.VERIFIED
    if score >= 30:
        return VerdictStatus.CAUTION
    return VerdictStatus.SUSPICIOUS


def derive_priority_code(trust_score: int, verdict: str, checks=None) -> str:
    """Right-of-way classification P1/P2/P3 — shared by redressal & PDF report."""
    if checks is not None and any(
        isinstance(c, dict) and c.get("status") in ("fail", "FAIL")
        and c.get("module") in ("seal", "video", "voice", "domain", "security")
        for c in checks
    ):
        return "P1_CRITICAL"
    if trust_score <= 25 or verdict == "SUSPICIOUS":
        return "P1_CRITICAL"
    if trust_score <= 60 or verdict in ("EXERCISE CAUTION", "CAUTION"):
        return "P2_MEDIUM"
    return "P3_LOW"


def _add_check(checks, module, status, label, label_hi, detail, detail_hi, contribution) -> None:
    """Append a single ledger CheckResult (deduplicates the 20 identical blocks)."""
    checks.append(CheckResult(
        module=module,
        status=status,
        label=label,
        label_hi=label_hi,
        detail=detail,
        detail_hi=detail_hi,
        contribution=contribution
    ))


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

    DETERMINISM CONTRACT — verdict is HARD-GATE-FIRST; AI/LLM/ML contributions are
    advisory only and CAPPED:
      1. Any hard gate (known-fake hash, forged/tampered seal, typosquat, urgency>=8,
         prompt injection, voice-clone, deepfake>=50) fires the Gradated Hard Gate
         Ceiling below.
      2. The ceiling is applied as the FINAL score adjustment for the hard-gate path:
         it runs AFTER every affirmative boost (+45 seal, +30/+50 registry, +50 voice,
         +50 video) and just before the [0,100] clamp. Reading the module, the boosts
         all occur before the "# Gradated Hard Gate Ceiling" block, so no advisory or
         affirmative contribution can ever push a hard-gated score above
         WEIGHT_HARD_GATE_CAP (<= 15).
      3. The phishing aggregate is deterministic when the AI advisory layer is degraded
         (see phishing_service.analyze_text) — degraded LLM output contributes exactly
         0.0 to overall_phishing_score.
      4. Therefore: identical input → identical verdict regardless of AI health.
    """
    score = 50
    checks: List[CheckResult] = []
    hard_gate_triggered = False

    # 0. Baseline Ledger Entry
    _add_check(checks, "baseline", CheckStatus.SKIP, "Neutral Baseline", "तटस्थ प्रारंभिक स्कोर",
               "Every scan starts at 50/100 baseline", "प्रत्येक स्कैन 50/100 के तटस्थ स्कोर से शुरू होता है", 50)

    if phishing_result and getattr(phishing_result, "ai_degraded", False):
        _add_check(checks, "ai", CheckStatus.SKIP, "AI Advisory Layer Unavailable", "AI विश्लेषण मोड (ऑफलाइन)",
                   "Deterministic registry & pattern checks active", "केवल नियम-आधारित और SEBI रजिस्ट्री जांच सक्रिय हैं", 0)

    # ── HARD GATES (Instant Red Cap <= 15) ──────────────────────────────────
    if hash_result:
        hard_gate_triggered = True
        _add_check(checks, "hash", CheckStatus.FAIL, "Known Fake Media Detected", "ज्ञात फर्जी मीडिया पहचान",
                   f"{hash_result.get('description', 'Matches known scam media database')}",
                   "ज्ञात स्कैम मीडिया डेटाबेस से मेल खाता है", -50)

    if seal_result and (seal_result.get("verdict") in ["FORGED", "TAMPERED", "UNVERIFIED"] or seal_result.get("is_valid") is False):
        hard_gate_triggered = True
        seal_verdict = seal_result.get('verdict', 'FORGED')
        _add_check(checks, "seal", CheckStatus.FAIL, f"PRAMAAN Seal {seal_verdict}", f"प्रमाण सील {seal_verdict}",
                   seal_result.get("message_en", "Cryptographic signature validation failed"),
                   seal_result.get("message_hi", "क्रिप्टोग्राफिक डिजिटल हस्ताक्षर विफल या नकली पाया गया"), -50)

    if phishing_result and phishing_result.domain_check.has_typosquat:
        hard_gate_triggered = True
        _add_check(checks, "domain", CheckStatus.FAIL, "Typosquat Domain Detected", "नकली डोमेन (Typosquat) मिला",
                   f"{phishing_result.domain_check.suspicious} → spoofing {phishing_result.domain_check.legitimate}",
                   f"अमान्य डोमेन {phishing_result.domain_check.suspicious} असली {phishing_result.domain_check.legitimate} की नकल कर रहा है", -40)

    if phishing_result and phishing_result.urgency_score >= 8:
        hard_gate_triggered = True
        _add_check(checks, "phishing", CheckStatus.FAIL, "Critical Threat / Panic Language Scam", "गंभीर धमकी / पैनिक संदेश",
                   f"Urgency score: {phishing_result.urgency_score}/10 — Severe account block/freeze threat detected",
                   f"आपातकालीन स्कोर: {phishing_result.urgency_score}/10 — खाता ब्लॉक/फ्रीज करने की धमकी मिली", -40)

    if phishing_result and phishing_result.injection_attempt:
        hard_gate_triggered = True
        _add_check(checks, "security", CheckStatus.FAIL, "Prompt Injection / Instruction Attack", "प्रॉम्प्ट इंजेक्शन हमला",
                   "Content tried to manipulate AI model rules",
                   "सामग्री ने सुरक्षा नियमों में हेरफेर की कोशिश की", -30)

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
            _add_check(checks, "registry", CheckStatus.FAIL, "Entity Impersonation — Unofficial Link",
                       "संस्था का अनधिकृत लिंक (धोखाधड़ी)",
                       f"Claims to be '{eb.entity}' but contains unofficial domain ({off_str})",
                       f"मैसेज '{eb.entity}' का दावा करता है लेकिन लिंक अनधिकृत ({off_str}) है",
                       -impersonation_weight)
        elif eb.status == "unbound":
            _add_check(checks, "registry", CheckStatus.WARN, "Entity Named but Unverified Link",
                       "संस्था का नाम है पर लिंक असत्यापित",
                       f"Mentions '{eb.entity}' but links do not match official domains",
                       f"मैसेज में '{eb.entity}' का उल्लेख है लेकिन लिंक आधिकारिक नहीं हैं", 0)

    # ── SOFT SIGNALS ────────────────────────────────────────────────────────
    if phishing_result:
        if 5 <= phishing_result.urgency_score < 8 or phishing_result.overall_phishing_score >= 5.0:
            deduction = 35 if phishing_result.urgency_score >= 5 else settings.WEIGHT_PHISHING_HIGH
            score -= deduction
            _add_check(checks, "phishing", CheckStatus.FAIL if phishing_result.urgency_score >= 5 else CheckStatus.WARN,
                       "High Urgency Scam Language", "उच्च दबाव / धोखाधड़ी की भाषा",
                       f"Urgency score: {phishing_result.urgency_score}/10 — Threat/panic language detected",
                       f"आपातकालीन स्कोर: {phishing_result.urgency_score}/10 — जल्दबाजी का दबाव बनाया गया",
                       -deduction)

        elif hasattr(phishing_result, 'investment_scam_score') and phishing_result.investment_scam_score >= 4:
            score -= 20
            _add_check(checks, "phishing", CheckStatus.WARN, "Unregulated Investment / Pump-and-Dump Tip",
                       "गैर-नियामक निवेश सलाह / पंप-एंड-डंप",
                       f"Investment scam score: {phishing_result.investment_scam_score}/10 — Guaranteed returns/VIP calls",
                       f"निवेश स्कैम स्कोर: {phishing_result.investment_scam_score}/10 — गारंटीकृत लाभ / टेलीग्राम कॉल", -20)

    if voice_result:
        if getattr(voice_result, "analysis_failed", False):
            # ML layer errored — we have NO signal. Never certify as "authentic":
            # a coding/decoding failure must not push the score toward VERIFIED.
            _add_check(checks, "voice", CheckStatus.SKIP, "Voice Analysis Unavailable", "वॉयस विश्लेषण अनुपलब्ध",
                       "Model error / unparsable audio — no liveness signal",
                       "मॉडल त्रुटि / असंसाधनीय ऑडियो — कोई लाइवनेस संकेत नहीं", 0)
        elif voice_result.is_synthetic:
            hard_gate_triggered = True
            voice_deduction = max(35, settings.WEIGHT_VOICE_SYNTHETIC)
            score -= voice_deduction
            _add_check(checks, "voice", CheckStatus.FAIL, "Voice Synthetic / Cloned", "नकली / AI वॉयस क्लोनिंग",
                       voice_result.verdict, "आवाज कृत्रिम या AI द्वारा क्लोन की गई पाई गई", -voice_deduction)
        else:
            voice_boost = 50 if voice_result.liveness_score >= 60 else 35
            voice_model = getattr(voice_result, "model_mode", "forensics")
            score += voice_boost
            _add_check(checks, "voice", CheckStatus.PASS, "Authentic Voice Confirmed", "प्रामाणिक आवाज - कोई AI क्लोनिंग नहीं",
                       f"Acoustic waveform analysis confirmed genuine voice (liveness: {voice_result.liveness_score}%, model: {voice_model})",
                       f"ध्वनि तरंग विश्लेषण से आवाज असली पाई गई (लाइवनेस: {voice_result.liveness_score}%, मॉडल: {voice_model})", +voice_boost)

    if video_result and not getattr(video_result, "analysis_failed", False):
        confidence = getattr(video_result, "confidence_level", "medium")
        prob = video_result.deepfake_probability

        if video_result.is_deepfake:
            # Gradated penalty: 70+ clear / 50-69 moderate (both hard-gate) / <50 mild
            if prob >= 50:
                hard_gate_triggered = True
            deduction = max(40, settings.WEIGHT_VIDEO_DEEPFAKE) if prob >= 70 else (30 if prob >= 50 else 20)
            # Reduce penalty if confidence is low — uncertain analysis
            if confidence == "low":
                deduction = max(10, deduction - 10)
            score -= deduction
            _add_check(checks, "video", CheckStatus.FAIL, "Deepfake Manipulation Detected",
                       "डीपफेक वीडियो हेरफेर पहचाना गया",
                       f"Facial & temporal manipulation probability: {prob}% (confidence: {confidence}, model: {video_result.mode})",
                       f"वीडियो में AI चेहरे और हेरफेर की संभावना: {prob}% (विश्वास: {confidence}, मॉडल: {video_result.mode})",
                       -deduction)
        else:
            # Full +50 boost for authentic media so real videos reach 100/100.
            boost = 50 if prob <= 35 else 40
            score += boost
            _add_check(checks, "video", CheckStatus.PASS, "Authentic Media - No Deepfake Detected",
                       "प्रामाणिक मीडिया - कोई डीपफेक नहीं मिला",
                       f"Facial & pixel analysis shows genuine media (manipulation risk: {prob}%, confidence: {confidence}, model: {video_result.mode})",
                       f"चेहरे और सिग्नल विश्लेषण से मीडिया प्रामाणिक पाया गया (हेराफेरी संभावना: {prob}%, विश्वास: {confidence}, मॉडल: {video_result.mode})",
                       +boost)
    elif video_result:
        # ML layer errored (undecodable container, no frames, model OOM).
        # Neutral — never certify as authentic, never flag as fake blindly.
        _add_check(checks, "video", CheckStatus.SKIP, "Video Analysis Unavailable", "वीडियो विश्लेषण अनुपलब्ध",
                   "Model error / undecodable media — no deepfake signal",
                   "मॉडल त्रुटि / असंसाधनीय मीडिया — कोई डीपफेक संकेत नहीं", 0)

    # ── AFFIRMATIVE PROOF (Boost to GREEN >= 70) ────────────────────────────
    # A5: a cryptographically valid seal only counts as affirmative proof when
    # it was actually issued FOR this presented content. If the quoted seal ID
    # refers to different content (content_match False), the seal is real but
    # irrelevant to this message — awarding +45 would let phishers paste a valid
    # seal ID into a scam and have it certified as VERIFIED. Such a seal is
    # treated as neutral at best.
    if seal_result and seal_result.get("verdict") == "VERIFIED":
        if seal_result.get("signature_valid", True) and seal_result.get("content_match") is not False:
            score += settings.WEIGHT_SEAL_VALID
            _add_check(checks, "seal", CheckStatus.PASS, "Valid PRAMAAN Seal", "सत्यापित प्रमाण सील (ECDSA)",
                       f"Signed by {seal_result.get('signer_entity_name', 'Registered Entity')} ({seal_result.get('signer_registration_number', 'SEBI')})",
                       f"{seal_result.get('signer_entity_name', 'पंजीकृत संस्था')} ({seal_result.get('signer_registration_number', 'SEBI')}) द्वारा डिजिटल हस्ताक्षरित",
                       +settings.WEIGHT_SEAL_VALID)
        else:
            _add_check(checks, "seal", CheckStatus.SKIP, "Seal Valid but Not Bound to This Content",
                       "सील मान्य परंतु इस सामग्री से संबद्ध नहीं",
                       "The seal signature is authentic, but it was issued for different content — it cannot authenticate this message.",
                       "सील हस्ताक्षर प्रामाणिक है, परंतु यह सील किसी अन्य सामग्री के लिए जारी थी — यह इस संदेश को प्रमाणित नहीं करता।",
                       0)

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
            _add_check(checks, "registry", CheckStatus.PASS, "SEBI Registered Entity Match",
                       "SEBI पंजीकृत संस्था का सत्यापन",
                       f"Matched official registry: '{registry_result.matched_entity}' ({registry_result.registration_number})",
                       f"आधिकारिक SEBI रजिस्टर से मेल मिला: '{registry_result.matched_entity}' ({registry_result.registration_number})",
                       +boost)

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
    verdict = verdict_for_score(score)

    return {
        "trust_score": score,
        "verdict": verdict,
        "verdict_label_en": verdict.value,
        "verdict_label_hi": "सत्यापित" if verdict == VerdictStatus.VERIFIED else ("सावधानी" if verdict == VerdictStatus.CAUTION else "संदेहास्पद"),
        "checks": checks,
        "explainability_en": generate_explanation_en(checks),
        "explainability_hi": generate_explanation_hi(checks)
    }
