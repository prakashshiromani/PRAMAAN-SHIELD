"""
PRAMAAN-SHIELD — SEBI Registry Lookup Service
File: backend/app/services/registry_service.py

Matches extracted entities or domains against the official SEBI registry database.
"""

from dataclasses import dataclass
import re
from typing import Optional, List, Dict, Any
from loguru import logger
from app.db.mongodb import get_db
from app.utils.json_io import load_json_data


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


def load_local_sebi_registry() -> List[Dict[str, Any]]:
    return load_json_data("sebi_registry.json", default=[])

LOCAL_REGISTRY = load_local_sebi_registry()


SEBI_REG_FORMATS = [
    r'^INZ\d{9}$',                 # Stock Broker (e.g. INZ000031633)
    r'^INB\d{9}$',                 # Stock Broker (legacy)
    r'^INF\d{9}$',                 # Derivatives / MF Distributor
    r'^INP\d{9}$',                 # Portfolio Manager
    r'^INA\d{9}$',                 # Investment Adviser
    r'^INR\d{9}$',                 # Research Analyst
    r'^INM\d{9}$',                 # Merchant Banker
    r'^INH\d{9}$',                 # RA (alternate)
    r'^IN-DP-(CDSL|NSDL)-\d{5}$',  # Depository Participant
]

def canonicalize_reg_no(reg_no: str) -> str:
    """Normalize and format registration number to official SEBI representation."""
    if not reg_no:
        return ""
    # Strip spaces and hyphens first to get bare characters
    bare = re.sub(r'[^A-Z0-9]', '', reg_no.strip().upper())
    
    # Check if it matches standard broker/analyst format (starts with IN followed by 10 alphanumeric)
    if re.match(r'^IN[ZBFPARMH]\d{9}$', bare):
        return bare
    
    # Check if it's a depository participant (IN + DP + CDSL/NSDL + 5 digits)
    dp_match = re.match(r'^INDP(CDSL|NSDL)(\d{5})$', bare)
    if dp_match:
        return f"IN-DP-{dp_match.group(1)}-{dp_match.group(2)}"
        
    return reg_no.strip().upper()


def validate_reg_no_format(reg_no: str) -> bool:
    """Check if a string matches official SEBI registration number formats."""
    if not reg_no:
        return False
    clean = canonicalize_reg_no(reg_no)
    return any(re.match(pattern, clean) for pattern in SEBI_REG_FORMATS)


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
        candidate_reg_nos = [canonicalize_reg_no(c.get("reg_no")) for c in candidate_entities if c.get("reg_no")]
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
                if reg_no and canonicalize_reg_no(reg_no) == canonicalize_reg_no(item.get("registration_number", "")):
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
