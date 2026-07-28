"""
PRAMAAN-SHIELD — Typosquatting Domain Detection
File: backend/app/utils/levenshtein.py
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from Levenshtein import distance as levenshtein_distance
from loguru import logger


def load_legitimate_domains() -> List[str]:
    """Load legitimate financial domain list from app/data/legitimate_domains.json"""
    file_path = Path("app/data/legitimate_domains.json")
    if not file_path.exists():
        logger.warning("legitimate_domains.json not found, using fallback defaults")
        return ["sebi.gov.in", "bseindia.com", "nseindia.com", "zerodha.com", "groww.in", "angelone.in"]

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("domains", [])


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
