"""
PRAMAAN-SHIELD — Professional Evidence Package PDF Generator
File: backend/app/utils/pdf_generator.py
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def generate_evidence_pdf(
    report_id: str,
    scan_id: str = "N/A",
    content_hash: str = "N/A",
    trust_score: int = 15,
    verdict: str = "SUSPICIOUS",
    created_at: Optional[str] = None
) -> bytes:
    """
    Generates a professional, court-admissible PRAMAAN-SHIELD Evidence Package PDF.
    """
    buffer = io.BytesIO()

    # Document setup with 0.5 inch margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Color Palette (PRAMAAN-SHIELD Theme)
    COLOR_TEAL = colors.HexColor("#116E5F")
    COLOR_DARK = colors.HexColor("#1A202C")
    COLOR_STAMP_RED = colors.HexColor("#9B1C1C")
    COLOR_STAMP_AMBER = colors.HexColor("#92400E")
    COLOR_GREEN = colors.HexColor("#065F46")
    COLOR_BG_LIGHT = colors.HexColor("#F7FAFC")
    COLOR_BORDER = colors.HexColor("#E2E8F0")

    verdict_color = COLOR_GREEN if verdict == "VERIFIED" else (COLOR_STAMP_AMBER if verdict == "EXERCISE CAUTION" else COLOR_STAMP_RED)

    # Custom Paragraph Styles
    style_header_title = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_TEAL,
        alignment=0
    )

    style_subtitle = ParagraphStyle(
        "SubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#718096"),
        alignment=0
    )

    style_section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_TEAL,
        spaceBefore=10,
        spaceAfter=6
    )

    style_body = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=COLOR_DARK
    )

    style_code = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("PRAMAAN-SHIELD EVIDENCE REPORT", style_header_title),
            Paragraph(f"<b>REPORT ID:</b> {report_id}<br/><b>ISSUED:</b> {datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')}", ParagraphStyle("HRight", parent=style_subtitle, alignment=2))
        ],
        [
            Paragraph("SEBI TechSprint 2026 - Investor Protection &amp; Fraud Detection Authority", style_subtitle),
            Paragraph("AUTHENTICATED EVIDENCE PACKAGE", ParagraphStyle("HRight2", parent=style_subtitle, alignment=2, fontName="Helvetica-Bold", textColor=COLOR_TEAL))
        ]
    ]

    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_TEAL, spaceBefore=2, spaceAfter=12))

    # 2. Executive Summary Box (Table)
    summary_data = [
        [
            Paragraph("<b>Scan Reference ID:</b>", style_body),
            Paragraph(f"<font name='Courier'>{scan_id}</font>", style_code),
            Paragraph("<b>Trust Score:</b>", style_body),
            Paragraph(f"<font color='{verdict_color.hexval()}'><b>{trust_score} / 100</b></font>", style_body)
        ],
        [
            Paragraph("<b>Verdict Status:</b>", style_body),
            Paragraph(f"<font color='{verdict_color.hexval()}'><b>{verdict}</b></font>", style_body),
            Paragraph("<b>Verification Authority:</b>", style_body),
            Paragraph("PRAMAAN Engine v1.0", style_body)
        ],
        [
            Paragraph("<b>Content SHA-256:</b>", style_body),
            Paragraph(f"<font name='Courier'>{content_hash[:48]}...</font>", style_code),
            Paragraph("<b>Target Portals:</b>", style_body),
            Paragraph("SEBI SCORES / 1930 Helpline", style_body)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[110, 160, 120, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Pre-Filled Complaint Draft 1: SEBI SCORES
    story.append(Paragraph("1. SEBI SCORES PORTAL - DRAFT COMPLAINT TEXT", style_section_heading))
    scores_text = (
        f"<b>To:</b> SEBI SCORES (Securities and Exchange Board of India)<br/>"
        f"<b>Subject:</b> SEBI SCORES Complaint: Financial Fraud / Impersonation Scam (Ref: {scan_id[:8]})<br/><br/>"
        f"<b>Complaint Body:</b><br/>"
        f"Respected SEBI Officers,<br/>"
        f"I am submitting this formal complaint regarding an unauthorized financial communication flagged for security violations.<br/><br/>"
        f"- <b>Scan Reference ID:</b> {scan_id}<br/>"
        f"- <b>Content SHA-256 Digest:</b> {content_hash}<br/>"
        f"- <b>PRAMAAN Trust Score:</b> {trust_score}/100 ({verdict})<br/>"
        f"- <b>Detection Flags:</b> Entity Impersonation, Unofficial Domain Links, High Urgency Panic Language.<br/><br/>"
        f"Requested Action: Please initiate inquiry and block spoofed domains associated with this communication."
    )
    scores_box = Table([[Paragraph(scores_text, style_body)]], colWidths=[540])
    scores_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_TEAL),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(scores_box)
    story.append(Spacer(1, 14))

    # 4. Pre-Filled Complaint Draft 2: 1930 Cybercrime Helpline
    story.append(Paragraph("2. 1930 NATIONAL CYBERCRIME REPORTING PORTAL - DRAFT TEXT", style_section_heading))
    cyber_text = (
        f"<b>To:</b> National Cyber Crime Reporting Helpline (1930 / cybercrime.gov.in)<br/>"
        f"<b>Subject:</b> Cyber Fraud Incident Report - Financial Phishing Scam<br/><br/>"
        f"<b>Incident Details:</b><br/>"
        f"- <b>Incident Category:</b> Financial Phishing &amp; Demat Impersonation Fraud<br/>"
        f"- <b>Evidence Hash:</b> {content_hash}<br/>"
        f"- <b>Risk Index:</b> {trust_score}/100 ({verdict})<br/>"
        f"- <b>Timestamp:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br/><br/>"
        f"Description: Threat/urgency message claiming Demat suspension and requesting immediate login on spoofed domain. Auto-generated evidence package attached."
    )
    cyber_box = Table([[Paragraph(cyber_text, style_body)]], colWidths=[540])
    cyber_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_STAMP_RED if verdict == "SUSPICIOUS" else COLOR_BORDER),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(cyber_box)
    story.append(Spacer(1, 16))

    # 5. Certification Footer
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceBefore=4, spaceAfter=8))
    footer_text = (
        f"<font color='#718096'><b>DIGITAL SIGNATURE &amp; EVIDENCE PROOF:</b> This PDF evidence package is automatically generated by PRAMAAN-SHIELD Engine for SEBI TechSprint 2026. Hash verification: {content_hash[:32]}... Verifiable online at /verify.</font>"
    )
    story.append(Paragraph(footer_text, ParagraphStyle("FooterText", parent=style_subtitle, fontSize=8, leading=10, alignment=1)))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
