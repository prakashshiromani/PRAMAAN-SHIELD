"""
PRAMAAN-SHIELD — SEBI Registry Lookup Service
File: backend/app/services/registry_service.py

Matches extracted entities or domains against the official SEBI registry database.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from loguru import logger
from app.db.mongodb import get_db


@dataclass
class RegistryResult:
    found: bool
    registration_number: Optional[str]
    matched_entity: Optional[str]
    category: Optional[str]
    official_domains: List[str]
    key_status: Optional[str]
    details: str
    match_basis: Optional[str] = None   # "reg_no" | "domain" | "name" — how the match was made


import json
import re
from pathlib import Path

def load_local_sebi_registry() -> List[Dict[str, Any]]:
    path = Path("app/data/sebi_registry.json")
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

LOCAL_REGISTRY = load_local_sebi_registry()


# Corporate suffixes stripped before name comparison so
# "Zerodha" and "Zerodha Broking Limited" resolve to the same token set.
_NAME_NOISE_TOKENS = {
    "limited", "ltd", "private", "pvt", "plc", "inc", "corporation", "corp",
    "company", "co", "broking", "brokers", "securities", "capital", "services",
    "india", "of", "the", "and",
}


def normalize_entity_name(name: str) -> frozenset:
    """
    Reduce an entity name to a comparable token set.
    'Zerodha Broking Limited' -> {'zerodha'};  'BSE Limited' -> {'bse'}
    """
    tokens = re.split(r"[^a-z0-9]+", (name or "").lower())
    meaningful = {t for t in tokens if t and t not in _NAME_NOISE_TOKENS}
    # If stripping left nothing (e.g. "India Limited"), fall back to raw tokens
    return frozenset(meaningful or {t for t in tokens if t})


def names_match(candidate: str, registry_name: str) -> bool:
    """
    Token-set based name match. Requires the candidate's meaningful tokens to be a
    subset of the registry entity's tokens (or vice-versa) — NOT a bare substring
    check, which previously let short strings like 'SBI' or 'BSE' match loosely.
    """
    cand = normalize_entity_name(candidate)
    reg = normalize_entity_name(registry_name)
    if not cand or not reg:
        return False
    return cand <= reg or reg <= cand


class RegistryService:
    async def lookup_by_reg_no(self, reg_no: str) -> Optional[Dict[str, Any]]:
        """Exact lookup by SEBI registration number."""
        try:
            db = await get_db()
            match = await db.sebi_registry.find_one({"registration_number": reg_no})
            if match:
                return match
        except Exception:
            pass

        for item in LOCAL_REGISTRY:
            if item.get("registration_number", "").upper() == reg_no.upper():
                return item
        return None

    @staticmethod
    def _build_result(item: Dict[str, Any], basis: str, details: str) -> RegistryResult:
        """Assemble a RegistryResult from a registry row (Mongo doc or local JSON)."""
        return RegistryResult(
            found=True,
            registration_number=item.get("registration_number"),
            matched_entity=item.get("entity_name"),
            category=item.get("category"),
            official_domains=[d.lower() for d in item.get("official_domains", [])],
            key_status=item.get("key_status", "active"),
            details=details,
            match_basis=basis
        )

    async def check_entities(self, candidate_entities: List[Dict[str, Optional[str]]], domains: List[str] = None) -> RegistryResult:
        """Check candidate entities or domains against the SEBI registry."""
        candidate_names = [c.get("name") for c in candidate_entities if c.get("name")]
        candidate_reg_nos = [c.get("reg_no") for c in candidate_entities if c.get("reg_no")]
        candidate_domains = [d.lower() for d in (domains or [])]

        # Sort candidate registration numbers so specific numbers (e.g. INZ000031633) come before generic "REGULATOR"
        candidate_reg_nos.sort(key=lambda r: 1 if r.upper() in ("REGULATOR", "BSE", "NSE", "MCX") else 0)

        # ── 1. MongoDB (same three-pass priority) ──────────────────────────
        try:
            db = await get_db()

            for reg_no in candidate_reg_nos:
                match = await db.sebi_registry.find_one({"registration_number": reg_no})
                if match:
                    return self._build_result(
                        match, "reg_no",
                        f"Exact match on registration number '{reg_no}'"
                    )

            for domain in candidate_domains:
                match = await db.sebi_registry.find_one({"official_domains": domain})
                if match:
                    return self._build_result(
                        match, "domain",
                        f"Matched official domain '{domain}' for '{match.get('entity_name')}'"
                    )

            for name in candidate_names:
                async for item in db.sebi_registry.find({}):
                    if names_match(name, item.get("entity_name", "")):
                        return self._build_result(
                            item, "name",
                            f"Entity name '{item.get('entity_name')}' referenced in content"
                        )
        except Exception:
            pass

        # ── 2. Local JSON fallback (same three-pass priority) ──────────────
        for reg_no in candidate_reg_nos:
            for item in LOCAL_REGISTRY:
                if reg_no and reg_no.upper() == item.get("registration_number", "").upper():
                    return self._build_result(
                        item, "reg_no",
                        f"Exact match on registration number '{reg_no}'"
                    )

        for domain in candidate_domains:
            for item in LOCAL_REGISTRY:
                if domain in [d.lower() for d in item.get("official_domains", [])]:
                    return self._build_result(
                        item, "domain",
                        f"Matched official SEBI domain '{domain}' for '{item.get('entity_name')}'"
                    )

        for name in candidate_names:
            for item in LOCAL_REGISTRY:
                if names_match(name, item.get("entity_name", "")):
                    return self._build_result(
                        item, "name",
                        f"Entity name '{item.get('entity_name')}' referenced in content"
                    )

        return RegistryResult(
            found=False,
            registration_number=None,
            matched_entity=None,
            category=None,
            official_domains=[],
            key_status=None,
            details="No SEBI registered entity match found",
            match_basis=None
        )
