"""
PRAMAAN-SHIELD — Seal Token Extraction Utility
File: backend/app/utils/seal_extract.py
"""

import re
import json
from typing import Optional


# Matches both PRMN-2026-SEBI-DC892 (dashes) AND PRMN 2026 SEBI DC892 (spaces)
SEAL_TOKEN_REGEX = r'PRMN[-\s]\d{4}[-\s][A-Z0-9]{2,8}[-\s][0-9A-F]{5}'


def _normalize_token(raw: str) -> str:
    """Normalize PRMN token: convert spaces to dashes and uppercase."""
    return re.sub(r'\s+', '-', raw.strip()).upper()


def extract_seal_token(text: str) -> Optional[str]:
    """Extract a PRAMAAN seal token or JSON payload from raw text content."""
    if not text:
        return None

    cleaned = text.strip()

    # Check if input is a raw JSON payload containing seal_id
    if cleaned.startswith("{") and "seal_id" in cleaned:
        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "seal_id" in data:
                return _normalize_token(data["seal_id"])
        except Exception:
            pass

    # Regex search for PRMN-2026-SEBI-ABC12 or PRMN 2026 SEBI ABC12 style seal IDs
    match = re.search(SEAL_TOKEN_REGEX, text, re.IGNORECASE)
    if match:
        return _normalize_token(match.group(0))

    return None


def extract_seal_from_image(image_path: str) -> Optional[str]:
    """
    Extract PRAMAAN Seal token from an image or screenshot file via QR code decoding.
    Uses OpenCV's built-in QRCodeDetector (zero extra dependencies).
    """
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            return None

        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        if data:
            token = extract_seal_token(data)
            if token:
                return token
            # Direct PRMN token match in decoded QR data
            match = re.search(SEAL_TOKEN_REGEX, data, re.IGNORECASE)
            if match:
                return _normalize_token(match.group(0))
    except Exception:
        pass

    return None
