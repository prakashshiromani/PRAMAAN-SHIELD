"""
PRAMAAN-SHIELD — IP Pseudonymization (DPDP Act 2023 Compliance)
File: backend/app/utils/privacy.py

SECURITY.md §11 Finding M1:
  SHA256(IP) is reversible (2^32 IPv4 space = trivial rainbow table).
  Fix: keyed HMAC-SHA256(IP, secret_salt) — cannot be reversed without knowing the salt.
"""

import hmac
import hashlib
from app.config import get_settings

settings = get_settings()


def pseudonymize_ip(ip_address: str) -> str:
    """
    Produces a keyed HMAC-SHA256 of the IP address.

    Args:
        ip_address: Raw IP string e.g. "203.0.113.42" or "::1"

    Returns:
        64-char hex HMAC digest. Cannot be reversed without IP_HMAC_SALT.
    """
    return hmac.new(
        key=settings.IP_HMAC_SALT.encode("utf-8"),
        msg=ip_address.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()
