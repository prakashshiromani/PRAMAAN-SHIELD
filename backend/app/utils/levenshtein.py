"""
PRAMAAN-SHIELD — Typosquatting Domain Detection
File: backend/app/utils/levenshtein.py
"""

import json
from typing import List, Dict, Any
from Levenshtein import distance as levenshtein_distance
from app.utils.json_io import load_json_data

_LEGIT_FALLBACK = [
    "sebi.gov.in", "bseindia.com", "nseindia.com", "zerodha.com", "groww.in", "angelone.in"
]


def load_legitimate_domains() -> List[str]:
    """Load legitimate financial domain list from app/data/legitimate_domains.json"""
    data = load_json_data("legitimate_domains.json", default={"domains": _LEGIT_FALLBACK})
    return data.get("domains", _LEGIT_FALLBACK)


LEGITIMATE_DOMAINS = load_legitimate_domains()


def extract_domain(url_or_domain: str) -> str:
    """Extract clean domain from URL or raw string."""
    clean = url_or_domain.lower().strip().rstrip(".,!?:;")
    if "://" in clean:
        clean = clean.split("://")[1]
    if "/" in clean:
        clean = clean.split("/")[0]
    if "@" in clean:
        clean = clean.split("@")[-1]
    if ":" in clean:
        clean = clean.split(":")[0]
    return clean.rstrip(".,!?:;")


def check_typosquatting(urls_or_domains: List[str], threshold: int = 3) -> List[Dict[str, Any]]:
    """
    Check input domain(s) against legitimate domain list using Levenshtein distance.
    Returns matches with distance > 0 and <= threshold.
    Skipped if exact match with legitimate domain list.
    """
    results = []
    for item in urls_or_domains:
        domain = extract_domain(item)
        if not domain:
            continue
        if domain in LEGITIMATE_DOMAINS:
            continue  # Exact match with legitimate domain — NOT a typosquat!

        for legit in LEGITIMATE_DOMAINS:
            dist = levenshtein_distance(domain, legit)
            if 0 < dist <= threshold:
                results.append({
                    "suspicious_domain": domain,
                    "legitimate_domain": legit,
                    "distance": dist,
                    "is_typosquat": True
                })
    return results
