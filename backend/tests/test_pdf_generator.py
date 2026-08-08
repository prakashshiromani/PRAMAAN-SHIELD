"""
Unit and Integration Tests for PRAMAAN-SHIELD Evidence PDF Generator
File: backend/tests/test_pdf_generator.py
"""

import pytest
import pypdf
import io
from app.utils.pdf_generator import generate_evidence_pdf, _clean_pdf_text
from app.utils.constants import EMPTY_SHA256


def test_clean_pdf_text_markdown_and_emojis():
    raw = "🚨 [P1-उच्च आपातकाल] **बोल्ड टेक्स्ट** & <विशेष संकेत>\n• बुलेट बिंदु 1"
    cleaned = _clean_pdf_text(raw)
    assert "[ALERT]" in cleaned
    assert "<b>बोल्ड टेक्स्ट</b>" in cleaned
    assert "&amp;" in cleaned
    assert "&lt;" in cleaned
    assert "&bull;" in cleaned
    assert "<br/>" in cleaned


def test_generate_evidence_pdf_hindi():
    checks = [
        {
            "module": "SEBI_REGISTRY",
            "status": "fail",
            "label": "Impersonation Detected",
            "detail": "Domain is not registered in official SEBI intermediary database.",
            "detail_hi": "डोमेन आधिकारिक सेबी मध्यस्थ डेटाबेस में पंजीकृत नहीं है।",
            "contribution": -40
        },
        {
            "module": "SSL_SECURITY",
            "status": "pass",
            "label": "Valid Certificate",
            "detail": "HTTPS certificate is active.",
            "detail_hi": "प्रमाणपत्र सक्रिय है।",
            "contribution": 5
        }
    ]

    pdf_bytes = generate_evidence_pdf(
        report_id="rpt_test_12345",
        scan_id="ps_scan_12345",
        content_hash=EMPTY_SHA256,
        trust_score=20,
        verdict="SUSPICIOUS",
        checks=checks,
        scores_custom_text="**SEBI SCORES शिकायत**\n\nआदरणीय सेबी अधिकारी,\nयह एक जाली वेबसाइट है।",
        cyber_custom_text="**1930 साइबर अपराध हेल्पलाइन**\n\nसाइबर अपराध रिपोर्ट दर्ज करें।",
        language="hi"
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 5000

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1
    extracted_text = "".join(p.extract_text() for p in reader.pages)
    assert "ps_scan_12345" in extracted_text
    assert "20 / 100" in extracted_text
    assert "SUSPICIOUS" in extracted_text
    assert "SEBI_REGISTRY" in extracted_text


def test_generate_evidence_pdf_english():
    pdf_bytes = generate_evidence_pdf(
        report_id="rpt_en_67890",
        scan_id="ps_scan_67890",
        content_hash=EMPTY_SHA256,
        trust_score=85,
        verdict="VERIFIED",
        language="en"
    )

    assert pdf_bytes.startswith(b"%PDF")
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1
    extracted_text = "".join(p.extract_text() for p in reader.pages)
    assert "ps_scan_67890" in extracted_text
    assert "85 / 100" in extracted_text
    assert "VERIFIED" in extracted_text
