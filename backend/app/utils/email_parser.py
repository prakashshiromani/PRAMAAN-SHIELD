"""
PRAMAAN-SHIELD — Email Authentication Header Parser
File: backend/app/utils/email_parser.py

Parses raw .eml file bytes to extract SPF, DKIM, and DMARC authentication
results from email headers. Uses Python's built-in `email` module — no
external dependency required.

References:
  - RFC 7208 (SPF)
  - RFC 6376 (DKIM)
  - RFC 7489 (DMARC)
"""

import email
from email import policy
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class EmailAuthResult:
    """Authentication verdict for a raw email."""
    spf_pass: bool
    dkim_pass: bool
    dmarc_pass: bool
    from_domain: str
    return_path_domain: str
    subject: str
    authentication_summary: str
    all_pass: bool                        # True only when all three pass


def parse_eml_headers(eml_bytes: bytes) -> EmailAuthResult:
    """
    Parse .eml file bytes and extract SPF/DKIM/DMARC authentication results.

    Looks at the following headers added by receiving mail servers:
      - Authentication-Results (composite)
      - Received-SPF
      - DKIM-Signature
    """
    try:
        msg = email.message_from_bytes(eml_bytes, policy=policy.default)

        # ── Gather raw header values ──────────────────────────────────────
        auth_results = (msg.get("Authentication-Results", "") or "").lower()
        received_spf = (msg.get("Received-SPF", "") or "").lower()
        dkim_sig     = msg.get("DKIM-Signature", "") or ""

        # ── SPF check ─────────────────────────────────────────────────────
        spf_pass = (
            "pass" in received_spf
            or "spf=pass" in auth_results
        )

        # ── DKIM check ────────────────────────────────────────────────────
        dkim_pass = (
            "dkim=pass" in auth_results
            or bool(dkim_sig.strip())
        )

        # ── DMARC check ───────────────────────────────────────────────────
        dmarc_pass = "dmarc=pass" in auth_results

        # ── Extract sender domain ─────────────────────────────────────────
        from_header = msg.get("From", "")
        from_domain = ""
        if "@" in from_header:
            from_domain = from_header.split("@")[-1].strip("> \t\n")

        return_path = msg.get("Return-Path", "")
        return_path_domain = ""
        if "@" in return_path:
            return_path_domain = return_path.split("@")[-1].strip("> \t\n")

        subject = msg.get("Subject", "(no subject)")

        # ── Summary string for ledger display ─────────────────────────────
        spf_icon   = "✅" if spf_pass   else "❌"
        dkim_icon  = "✅" if dkim_pass  else "❌"
        dmarc_icon = "✅" if dmarc_pass else "❌"
        summary = f"SPF: {spf_icon} | DKIM: {dkim_icon} | DMARC: {dmarc_icon}"

        all_pass = spf_pass and dkim_pass and dmarc_pass

        logger.info(
            f"Email auth parsed — From: {from_domain}, "
            f"SPF={spf_pass}, DKIM={dkim_pass}, DMARC={dmarc_pass}"
        )

        return EmailAuthResult(
            spf_pass=spf_pass,
            dkim_pass=dkim_pass,
            dmarc_pass=dmarc_pass,
            from_domain=from_domain,
            return_path_domain=return_path_domain,
            subject=subject,
            authentication_summary=summary,
            all_pass=all_pass,
        )
    except Exception as e:
        logger.error(f"Email header parsing failed: {e}")
        return EmailAuthResult(
            spf_pass=False,
            dkim_pass=False,
            dmarc_pass=False,
            from_domain="",
            return_path_domain="",
            subject="(parse error)",
            authentication_summary="SPF: ❌ | DKIM: ❌ | DMARC: ❌ (parse error)",
            all_pass=False,
        )
