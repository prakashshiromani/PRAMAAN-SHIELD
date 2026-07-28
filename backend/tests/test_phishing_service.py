"""
Unit Tests for 4-Layer Phishing Pipeline & Urgency Calculator
File: backend/tests/test_phishing_service.py
"""

import pytest
from app.services.phishing_service import (
    calculate_urgency,
    extract_urls_and_domains,
    URGENCY_PATTERNS,
)


def test_calculate_urgency_clean_text():
    """Benign informational text should produce low urgency score (0-2)."""
    text = "Hello, please review the annual financial report attached for your reference."
    assert calculate_urgency(text) <= 2


def test_calculate_urgency_phishing_text():
    """Urgent threat text with exclamation marks should yield high urgency score (>= 6)."""
    text = "URGENT! Your demat account will be BLOCKED within 24 hours! Click immediately!"
    assert calculate_urgency(text) >= 6


def test_extract_urls_and_domains():
    """URL extractor should accurately identify embedded domain names."""
    text = "Visit official site http://sebi.gov.in or spoofed http://serbi-gov.in now"
    urls = extract_urls_and_domains(text)
    assert len(urls) == 2
    assert "http://sebi.gov.in" in urls
    assert "http://serbi-gov.in" in urls


def test_urgency_patterns_loaded():
    """Global URGENCY_PATTERNS list should be populated."""
    assert isinstance(URGENCY_PATTERNS, list)
    assert len(URGENCY_PATTERNS) > 0
