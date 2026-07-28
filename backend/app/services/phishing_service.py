"""
PRAMAAN-SHIELD — 4-Layer Phishing Detection Pipeline
File: backend/app/services/phishing_service.py
"""

import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
from loguru import logger

from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService, RegistryResult
from app.utils.levenshtein import check_typosquatting, extract_domain, LEGITIMATE_DOMAINS


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
    path = Path("app/data/urgency_patterns.json")
    if not path.exists():
        return ["blocked", "suspended", "urgent", "2000%", "guaranteed returns", "खाता बंद"]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
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

        # Layer 1: AI-Generated Text Detection
        ai_res = await self.gemini.detect_ai_text(text)
        if ai_res.probability > 0.7:
            details.append(f"AI-Generated Text: {round(ai_res.probability * 100)}% probability ({ai_res.perplexity} perplexity)")

        # Layer 2: Urgency & Phishing Pattern Classifier
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

        # Layer 4: SEBI Registry Cross-Check
        ner_res = await self.gemini.extract_entities(text)
        reg_res = await self.registry.check_entities(ner_res.entities, domains=found_urls)
        if reg_res.found:
            details.append(f"SEBI Registry Match: Matched official entity '{reg_res.matched_entity}' ({reg_res.registration_number})")

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

                if not offending:
                    binding_status = "bound"
                else:
                    legit_offending = [d for d in offending if d in LEGITIMATE_DOMAINS]
                    if len(legit_offending) == len(offending):
                        binding_status = "unbound"
                    else:
                        binding_status = "impersonation"
                        offending_domains = [d for d in offending if d not in LEGITIMATE_DOMAINS]

        # Check for SEBI registration number mismatch in text (e.g. INZ000032623 vs official INZ000031633)
        text_reg_matches = re.findall(r'IN[ZBFPA0-9]{8,10}', text, re.IGNORECASE)

        if reg_res.found and text_reg_matches:
            expected_reg = (reg_res.registration_number or "").strip().upper()
            found_reg = text_reg_matches[0].strip().upper()
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

        # Calculate Aggregate Phishing Score (0.0 - 10.0)
        overall_score = 0.0
        if ai_res.probability > 0.5:
            overall_score += ai_res.probability * 3.0
        if urgency_score > 4:
            overall_score += (urgency_score / 10.0) * 3.0
        if typo_res.has_typosquat:
            overall_score += 4.0
        if binding_status == "impersonation":
            overall_score += 4.0
        if not reg_res.found and len(ner_res.entities) > 0:
            overall_score += 2.0

        overall_score = min(10.0, round(overall_score, 1))

        ai_degraded = getattr(ai_res, "degraded", False) or getattr(ner_res, "degraded", False)

        return PhishingPipelineResult(
            ai_generated_probability=ai_res.probability,
            urgency_score=urgency_score,
            investment_scam_score=investment_scam_score,
            domain_check=typo_res,
            registry_match=reg_res,
            overall_phishing_score=overall_score,
            details=details,
            injection_attempt=ai_res.injection_attempt or ner_res.injection_attempt,
            entity_binding=entity_binding,
            ai_degraded=ai_degraded
        )
