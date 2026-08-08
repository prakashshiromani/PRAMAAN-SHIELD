"""
PRAMAAN-SHIELD — 4-Layer Phishing Detection Pipeline
File: backend/app/services/phishing_service.py
"""

import re
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from loguru import logger

from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService, RegistryResult, validate_reg_no_format
from app.utils.levenshtein import check_typosquatting, extract_domain, LEGITIMATE_DOMAINS
from app.utils.json_io import load_json_data


@dataclass
class TyposquatResult:
    has_typosquat: bool
    suspicious: Optional[str]
    legitimate: Optional[str]
    distance: int


@dataclass
class EntityBinding:
    """
    Does the content actually PROVE a link to the registered entity it names?

    Naming a SEBI-registered entity is free — any scammer can type "SEBI" or
    "Zerodha". A trust boost is only justified when the links in the content are
    domains that entity actually owns.

    status:
      "none"          — no registry match at all
      "bound"         — every link belongs to the matched entity's official_domains
      "unbound"       — entity named, but nothing verifiable (no links, or links
                        belong to some other legitimate financial domain)
      "impersonation" — entity named, but a link points at a domain nobody in the
                        legitimate ecosystem owns. This is the phishing signature.
    """
    status: str
    entity: Optional[str]
    offending_domains: List[str]
    official_domains: List[str]


@dataclass
class PhishingPipelineResult:
    ai_generated_probability: float
    urgency_score: int                   # 0 - 10
    investment_scam_score: int           # 0 - 10 (pump & dump / unregulated tips)
    domain_check: TyposquatResult
    registry_match: RegistryResult
    overall_phishing_score: float        # 0.0 - 10.0
    details: List[str]
    injection_attempt: bool
    entity_binding: EntityBinding = field(
        default_factory=lambda: EntityBinding("none", None, [], [])
    )
    ai_degraded: bool = False            # True when the Gemini advisory layer was unreachable


def load_urgency_patterns() -> List[str]:
    """Load Hindi and English urgency keywords."""
    data = load_json_data("urgency_patterns.json", default=None)
    if not data:
        return ["blocked", "suspended", "urgent", "2000%", "guaranteed returns", "खाता बंद"]
    patterns = data.get("patterns", {})
    return patterns.get("en", []) + patterns.get("hi", [])


URGENCY_PATTERNS = load_urgency_patterns()

# Investment scam (pump & dump) specific keywords — these indicate CAUTION not full RED threat
INVESTMENT_SCAM_KEYWORDS = [
    "sure shot", "jackpot call", "upper circuit", "guaranteed return", "guaranteed profit",
    "risk free", "risk-free", "vip channel", "private group", "insider tip", "confidential tip",
    "100% return", "200% return", "2000%", "500%", "double your money",
    "join our group", "join our channel", "limited seats", "telegram channel",
    "whatsapp group", "t.me/", "sure profit", "jackpot stock",
    "गारंटीड रिटर्न", "गारंटीकृत लाभ", "जैकपॉट कॉल", "प्राइवेट ग्रुप",
    "गुप्त ट्रेडिंग", "जोखिम मुक्त"
]

# Account threat keywords — these indicate HIGH URGENCY / RED SUSPICIOUS
ACCOUNT_THREAT_KEYWORDS = [
    "account will be blocked", "account freeze", "account suspended", "demat account",
    "kyc expire", "kyc verification", "kyc validation", "frozen", "within 24 hours",
    "legal penalties", "legal action", "urgent attention", "last chance",
    "खाता बंद", "खाता ब्लॉक", "खाता फ्रीज", "डीमैट खाता", "केवाईसी",
    "24 घंटे", "अंतिम चेतावनी", "कानूनी कार्रवाई", "तत्काल"
]

# Deterministic prompt-injection / instruction-override detector. This is a HARD
# GATE, so it runs on EVERY scan regardless of Gemini health. Previously the
# injection gate read `injection_attempt` ONLY from the LLM, and gemini_service
# forces that flag to False on every degraded path — so the same input scanned
# while the LLM was down silently dropped a red hard gate that a healthy scan
# fired. HIGH PRECISION by design: patterns require explicit meta-instructions
# ("ignore previous instructions", "system: you are", ...) and never bare words
# like "ignore" or "system", so ordinary scam copy does not false-positive.
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions?|messages?)"),
    re.compile(r"ignore\s+(the\s+)?(system|developer|above|prior)\s+(prompt|instructions?|message)"),
    re.compile(r"ignore\s+your\s+(instructions?|guidelines|rules|prompt)"),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+(instructions?|messages?|rules)"),
    re.compile(r"disregard\s+your\s+(instructions?|rules|guidelines)"),
    re.compile(r"forget\s+(all\s+)?(your|the)\s+(rules|instructions?|guidelines|previous|above)"),
    re.compile(r"forget\s+everything\s+(above|before|previously)"),
    re.compile(r"override\s+(your\s+|the\s+|system\s+)?(instructions?|rules|guidelines|prompt|settings|safeguards?)"),
    re.compile(r"bypass\s+(your\s+|the\s+)?(rules|guidelines|restrictions|safeguards?|security)"),
    re.compile(r"do\s+not\s+(follow|obey|honou?r)\s+(your\s+|the\s+)?(rules|instructions?|guidelines)"),
    re.compile(r"you\s+are\s+now\s+(an?\s+)?(not|no\s+longer|free\s+from|a\s+new)"),
    re.compile(r"act\s+as\s+if\s+you\s+(have\s+no|don'?t\s+have)\s+(rules|restrictions|limits)"),
    re.compile(r"(system|developer)\s*(prompt)?\s*:\s*(you\s+are|forget|ignore)"),
    re.compile(r"new\s+system\s+(prompt|instructions?)"),
    re.compile(r"jailbreak"),
]


def detect_prompt_injection(text: str) -> bool:
    """Deterministic heuristic for instruction-override / prompt-injection text.

    Returns True only on an unambiguous override instruction. Gemini's own
    injection assessment remains available as an advisory detail line and can
    never ADD or REMOVE this gate — so the verdict is byte-identical whether the
    LLM is healthy or degraded.
    """
    if not text:
        return False
    lowered = text.lower()
    return any(p.search(lowered) for p in _INJECTION_PATTERNS)


def calculate_investment_scam_score(text: str) -> int:
    """Calculate investment/pump-and-dump scam score (0-10)."""
    text_lower = text.lower()
    score = 0
    for kw in INVESTMENT_SCAM_KEYWORDS:
        if kw.lower() in text_lower:
            score += 2
    return min(10, score)


def calculate_urgency(text: str) -> int:
    """Calculate urgency score (0-10) based on pattern matches and exclamations."""
    text_lower = text.lower()
    score = 0
    for pattern in URGENCY_PATTERNS:
        if pattern.lower() in text_lower:
            score += 2

    # Exclamation & ALL CAPS check
    score += min(3, text.count("!"))
    words = text.split()
    caps_count = sum(1 for w in words if w.isupper() and len(w) > 2)
    if caps_count >= 2:
        score += 2

    return min(10, score)


def extract_urls_and_domains(text: str) -> List[str]:
    """Extract clean URLs or domains from text content."""
    url_pattern = r'https?://[^\s>"]+|www\.[^\s>"]+|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    matches = re.findall(url_pattern, text)
    cleaned = []
    for m in matches:
        domain = m.rstrip(".,!?:;")
        if domain and domain not in cleaned:
            cleaned.append(domain)
    return cleaned


class PhishingService:
    def __init__(self, gemini_service: GeminiService, registry_service: RegistryService):
        self.gemini = gemini_service
        self.registry = registry_service

    async def analyze_text(self, text: str) -> PhishingPipelineResult:
        """Run the 4-layer phishing detection pipeline."""
        details = []

        # Layer 1 & 4 (AI-text + NER) are two independent LLM calls — run them
        # concurrently to halve total LLM latency for a scan.
        ai_task = self.gemini.detect_ai_text(text)
        ner_task = self.gemini.extract_entities(text)
        ai_res, ner_res = await asyncio.gather(ai_task, ner_task)
        # Determinism contract: a degraded advisory layer (Gemini blocked/404/timeout)
        # MUST contribute nothing to the pipeline result. `ai_res.probability` is
        # already 0.0 and both `injection_attempt` flags are False on every degraded
        # return path in gemini_service.py — but we gate the math explicitly anyway so
        # a future non-zero degraded probability can never leak a non-deterministic
        # contribution into overall_phishing_score.
        ai_degraded = getattr(ai_res, "degraded", False) or getattr(ner_res, "degraded", False)
        if not ai_degraded and ai_res.probability > 0.7:
            details.append(f"AI-Generated Text: {round(ai_res.probability * 100)}% probability ({ai_res.perplexity} perplexity)")
        # Deterministic prompt-injection HARD GATE — computed from the local regex
        # detector above, never from the LLM. The LLM's own injection verdict is
        # advisory only: it can add a detail line but can never flip the gate, so
        # a degraded LLM cannot silently drop the red gate (see detect_prompt_injection).
        heuristic_injection = detect_prompt_injection(text)
        if not ai_degraded and (ai_res.injection_attempt or ner_res.injection_attempt):
            details.append("Prompt injection attempt detected against AI analysis (advisory — heuristic gate is authoritative)")
        # Separate urgency scores: account threats vs investment scam tips
        text_lower = text.lower()
        account_threat_hits = sum(1 for kw in ACCOUNT_THREAT_KEYWORDS if kw.lower() in text_lower)
        urgency_score = calculate_urgency(text)
        # If mostly investment scam keywords (not account threat), cap urgency at 4 so it lands in CAUTION
        investment_scam_score = calculate_investment_scam_score(text)
        if investment_scam_score >= 4 and account_threat_hits == 0:
            # Pure investment scam (pump & dump) — dampen urgency to prevent RED false positive
            urgency_score = min(urgency_score, 4)
        if urgency_score >= 6:
            details.append(f"High Urgency/Threat Language: Score {urgency_score}/10")

        # Layer 3: Domain & Sender Typosquatting Check
        found_urls = extract_urls_and_domains(text)
        typo_matches = check_typosquatting(found_urls)
        
        if typo_matches:
            match = typo_matches[0]
            typo_res = TyposquatResult(
                has_typosquat=True,
                suspicious=match["suspicious_domain"],
                legitimate=match["legitimate_domain"],
                distance=match["distance"]
            )
            details.append(f"Typosquat Domain Detected: '{match['suspicious_domain']}' spoofing '{match['legitimate_domain']}'")
        else:
            typo_res = TyposquatResult(False, None, None, 0)

        # Layer 4: SEBI Registry Cross-Check.
        # DETERMINISM: the score-affecting registry match must be identical whether
        # or not Gemini is healthy. LLM NER (ner_res.entities) is a superset when
        # healthy and a fixed heuristic set when degraded, so a boost keyed on it
        # would flip with Gemini health. Instead the check ALWAYS runs on the
        # deterministic heuristic entity set (covers the full offline registry);
        # LLM NER remains advisory (detail line / response metadata) and can never
        # change the registry boost or entity binding.
        deterministic_entities = self.gemini._heuristic_entity_fallback(text)
        reg_res = await self.registry.check_entities(deterministic_entities, domains=found_urls)
        if reg_res.found:
            details.append(f"SEBI Registry Match: Matched official entity '{reg_res.matched_entity}' ({reg_res.registration_number})")
        elif not ai_degraded and ner_res.entities:
            llm_names = ", ".join(e.get("name", "") for e in ner_res.entities if e.get("name"))
            if llm_names:
                details.append(f"LLM advisory: content references '{llm_names}' — no deterministic registry match")

        # Layer 4.5: Entity-Domain Binding Evaluation
        binding_status = "none"
        offending_domains = []
        official_domains = reg_res.official_domains if reg_res.found else []

        if reg_res.found:
            text_domains = [extract_domain(u) for u in found_urls if extract_domain(u)]
            if not text_domains:
                binding_status = "unbound"
            else:
                offending = []
                for dom in text_domains:
                    is_official = any(dom == off_dom or dom.endswith("." + off_dom) for off_dom in official_domains)
                    if not is_official:
                        offending.append(dom)

                # Exclude standard email recipient/test domains (example.com, gmail.com, etc.)
                SAFE_RECIPIENT_DOMAINS = {"example.com", "example.org", "example.net", "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}
                real_offending = [d for d in offending if d not in SAFE_RECIPIENT_DOMAINS]

                if not real_offending:
                    binding_status = "bound"
                else:
                    legit_offending = [d for d in real_offending if d in LEGITIMATE_DOMAINS]
                    if len(legit_offending) == len(real_offending):
                        binding_status = "unbound"
                    else:
                        binding_status = "impersonation"
                        offending_domains = [d for d in real_offending if d not in LEGITIMATE_DOMAINS]

        # Check for SEBI registration number mismatch in text (e.g. INZ000032623 vs official INZ000031633)
        raw_reg_matches = re.findall(r'\b(?:IN[ZBFPAHMR0-9\-\s]{8,18})\b', text, re.IGNORECASE)
        from app.services.registry_service import canonicalize_reg_no
        text_reg_matches = [canonicalize_reg_no(m) for m in raw_reg_matches if validate_reg_no_format(m)]

        if reg_res.found and text_reg_matches:
            expected_reg = canonicalize_reg_no(reg_res.registration_number)
            found_reg = canonicalize_reg_no(text_reg_matches[0])
            if expected_reg and found_reg != expected_reg:
                binding_status = "impersonation"
                offending_domains.append(f"Fake Reg: {found_reg}")
                details.append(f"SEBI Registration Mismatch: Text has '{found_reg}', official for '{reg_res.matched_entity}' is '{expected_reg}'")

        entity_binding = EntityBinding(
            status=binding_status,
            entity=reg_res.matched_entity if reg_res.found else None,
            offending_domains=offending_domains,
            official_domains=official_domains
        )

        # Calculate Aggregate Phishing Score (0.0 - 10.0) — FULLY DETERMINISTIC.
        # The LLM probability term and the LLM injection bump used to be added on
        # the healthy path only, so overall_phishing_score (and the soft deduction
        # it gates in trust_score_service) differed by Gemini health. Now the
        # aggregate is built ONLY from deterministic signals (urgency, typosquat,
        # entity binding, registry miss). LLM output still surfaces as the advisory
        # ai_generated_probability field and detail lines — it can never move the
        # composite trust score, so identical input → identical score and verdict
        # whether Gemini is up, down, or flapping.
        overall_score = 0.0
        if urgency_score > 4:
            overall_score += (urgency_score / 10.0) * 3.0
        if typo_res.has_typosquat:
            overall_score += 4.0
        if binding_status == "impersonation":
            overall_score += 4.0
        if not reg_res.found and len(deterministic_entities) > 0:
            overall_score += 2.0

        overall_score = min(10.0, round(overall_score, 1))

        return PhishingPipelineResult(
            ai_generated_probability=ai_res.probability,
            urgency_score=urgency_score,
            investment_scam_score=investment_scam_score,
            domain_check=typo_res,
            registry_match=reg_res,
            overall_phishing_score=overall_score,
            details=details,
            injection_attempt=heuristic_injection,
            entity_binding=entity_binding,
            ai_degraded=ai_degraded
        )
