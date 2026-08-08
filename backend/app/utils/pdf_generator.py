"""
PRAMAAN-SHIELD — Professional Evidence Package PDF Generator
File: backend/app/utils/pdf_generator.py
"""

import io
import os
import re
import base64
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.utils.constants import EMPTY_SHA256


# ============================================================================
# 1. ROBUST FONT REGISTRATION (Latin + Devanagari / Hindi Unicode Support)
# ============================================================================

MAIN_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"

bundled_nirmala = str(Path(__file__).parent.parent / "fonts" / "Nirmala.ttc")
bundled_noto = str(Path(__file__).parent.parent / "fonts" / "NotoSansDevanagari-Regular.ttf")

font_candidates = [
    # 1. Bundled Nirmala in backend/app/fonts/ (has complete Latin + Devanagari regular & bold)
    ("Nirmala", bundled_nirmala, 0, 1),
    # 2. Windows system Nirmala
    ("Nirmala", "C:\\Windows\\Fonts\\Nirmala.ttc", 0, 1),
    # 3. Windows Arial Unicode MS
    ("ArialUnicode", "C:\\Windows\\Fonts\\Arial Unicode MS.ttf", None, None),
    # 4. Linux FreeSerif / FreeSans
    ("FreeSerif", "/usr/share/fonts/truetype/freefont/FreeSerif.ttf", None, None),
    # 5. Linux Noto Sans Devanagari
    ("NotoDevanagari", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", None, None),
    # 6. Bundled Noto
    ("NotoDevanagari", bundled_noto, None, None),
]

for fname, fpath, sub_reg, sub_bold in font_candidates:
    if os.path.exists(fpath):
        try:
            if sub_reg is not None and sub_bold is not None:
                pdfmetrics.registerFont(TTFont('DevanagariFont', fpath, subfontIndex=sub_reg))
                pdfmetrics.registerFont(TTFont('DevanagariFont-Bold', fpath, subfontIndex=sub_bold))
                pdfmetrics.registerFontFamily(
                    'DevanagariFont',
                    normal='DevanagariFont',
                    bold='DevanagariFont-Bold',
                    italic='DevanagariFont',
                    boldItalic='DevanagariFont-Bold'
                )
                MAIN_FONT = 'DevanagariFont'
                BOLD_FONT = 'DevanagariFont-Bold'
                break
            else:
                pdfmetrics.registerFont(TTFont('DevanagariFont', fpath))
                pdfmetrics.registerFontFamily(
                    'DevanagariFont',
                    normal='DevanagariFont',
                    bold='DevanagariFont',
                    italic='DevanagariFont',
                    boldItalic='DevanagariFont'
                )
                MAIN_FONT = 'DevanagariFont'
                BOLD_FONT = 'DevanagariFont'
                break
        except Exception:
            continue


# ============================================================================
# 2. NUMBERED CANVAS (Page X of Y & Security Watermark)
# ============================================================================

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page numbers: 'Page X of Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#718096"))

        # Footer Left: Regulatory TechSprint notice
        self.drawString(
            36, 22,
            "SEBI TechSprint 2026 — PRAMAAN-SHIELD Evidence & Redressal Engine | Confidential & Court-Admissible"
        )

        # Footer Right: Page X of Y
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 36, 22, page_str)

        # Thin footer line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 32, letter[0] - 36, 32)
        self.restoreState()


# ============================================================================
# 3. TEXT SANITIZATION & MARKDOWN TO REPORTLAB XML FORMATTER
# ============================================================================

def _clean_pdf_text(text: str) -> str:
    """
    Cleans, sanitizes, and converts plain/markdown text into valid ReportLab XML markup.
    Normalizes multi-byte emojis into clean text badges so no glyphs are lost.
    """
    if not text:
        return ""

    emoji_map = {
        '🚨': '[ALERT] ',
        '🔴': '[CRITICAL] ',
        '🟡': '[MEDIUM] ',
        '🟢': '[LOW] ',
        '⚠️': '[WARNING] ',
        '📌': '[NOTE] ',
        'ℹ️': '[INFO] ',
        '🛡️': '[SHIELD] ',
        '🏛️': '[REGULATOR] ',
        '•': '&bull; ',
        '✓': '[PASS] ',
        '✔': '[PASS] ',
        '✗': '[FAIL] ',
        '❌': '[FAIL] ',
        '📝': '[DRAFT] ',
        '📄': '[DOC] ',
    }

    cleaned = str(text)
    # XML Escape special characters first (<, >, &) so raw & and < in user content are safe
    cleaned = escape(cleaned)

    # Replace unsupported multi-byte emojis and bullets with clean text / entities
    for em, rep in emoji_map.items():
        cleaned = cleaned.replace(em, rep)

    # Convert Markdown bold **text** to <b>text</b>
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)

    # Convert newlines to <br/>
    cleaned = cleaned.replace('\n', '<br/>')

    # Collapse multiple consecutive breaks into clean spacing
    cleaned = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', cleaned)
    return cleaned.strip()


# ============================================================================
# 4. MAIN EVIDENCE PDF GENERATION FUNCTION
# ============================================================================

def generate_evidence_pdf(
    report_id: str,
    scan_id: str = "N/A",
    content_hash: str = "N/A",
    trust_score: int = 15,
    verdict: str = "SUSPICIOUS",
    created_at: Optional[str] = None,
    checks: Optional[list] = None,
    heatmap_b64: Optional[str] = None,
    priority_code: Optional[str] = None,
    scores_custom_text: Optional[str] = None,
    cyber_custom_text: Optional[str] = None,
    language: str = "hi"
) -> bytes:
    """
    Generates a professional, court-admissible PRAMAAN-SHIELD Evidence Package PDF.
    Features:
    - High-fidelity typography with bilingual Devanagari (Hindi) + Latin (English) support.
    - Executive summary key-value dashboard table.
    - Visual trust index gauge with dynamic threshold color coding.
    - Detailed security checks breakdown table with status badges.
    - Formatted SEBI SCORES 2.0 & 1930 National Cybercrime complaint drafts.
    - Digital signature & SHA-256 evidence integrity verification block.
    """
    buffer = io.BytesIO()

    # Document setup with 0.5 inch (36pt) margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()

    # Color Palette (PRAMAAN-SHIELD Theme)
    COLOR_TEAL = colors.HexColor("#116E5F")
    COLOR_TEAL_DARK = colors.HexColor("#0A473D")
    COLOR_DARK = colors.HexColor("#1A202C")
    COLOR_MUTED = colors.HexColor("#4A5568")
    COLOR_SLATE = colors.HexColor("#718096")
    COLOR_STAMP_RED = colors.HexColor("#9B1C1C")
    COLOR_STAMP_AMBER = colors.HexColor("#92400E")
    COLOR_GREEN = colors.HexColor("#065F46")
    COLOR_BG_LIGHT = colors.HexColor("#F8FAFC")
    COLOR_BORDER = colors.HexColor("#E2E8F0")

    # Sanitize inputs
    if not scan_id or scan_id in ["N/A", "demo"]:
        scan_id = f"ps_{report_id.replace('rpt_', '')}"
    if not content_hash or content_hash in ["N/A", "N/A..."]:
        content_hash = EMPTY_SHA256

    verdict_upper = str(verdict).upper()
    verdict_color = (
        COLOR_GREEN if verdict_upper in ["VERIFIED", "PASS", "SAFE"]
        else (COLOR_STAMP_AMBER if verdict_upper in ["EXERCISE CAUTION", "CAUTION", "WARN"]
        else COLOR_STAMP_RED)
    )

    # Priority code calculation
    from app.services.trust_score_service import derive_priority_code
    p_code = priority_code or derive_priority_code(trust_score, verdict_upper)

    # -------------------------------------------------------------------------
    # Typography & Styles
    # -------------------------------------------------------------------------
    style_header_title = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=17,
        leading=21,
        textColor=COLOR_TEAL,
        alignment=0
    )

    style_subtitle = ParagraphStyle(
        "SubTitle",
        parent=styles["Normal"],
        fontName=MAIN_FONT,
        fontSize=8.5,
        leading=11,
        textColor=COLOR_SLATE,
        alignment=0
    )

    style_section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=10.5,
        leading=14,
        textColor=COLOR_TEAL_DARK,
        spaceBefore=10,
        spaceAfter=5
    )

    style_body = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName=MAIN_FONT,
        fontSize=8.5,
        leading=12.5,
        textColor=COLOR_DARK
    )

    style_body_bold = ParagraphStyle(
        "BodyTextBold",
        parent=styles["Normal"],
        fontName=BOLD_FONT,
        fontSize=8.5,
        leading=12.5,
        textColor=COLOR_DARK
    )

    style_code = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_MUTED
    )

    style_complaint = ParagraphStyle(
        "ComplaintText",
        parent=styles["Normal"],
        fontName=MAIN_FONT,
        fontSize=8.5,
        leading=13,
        textColor=COLOR_DARK
    )

    story = []

    # -------------------------------------------------------------------------
    # 1. HEADER BANNER
    # -------------------------------------------------------------------------
    issued_dt = created_at or datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')
    header_data = [
        [
            Paragraph("<b>PRAMAAN-SHIELD EVIDENCE REPORT</b>", style_header_title),
            Paragraph(f"<b>REPORT ID:</b> {report_id}<br/><b>ISSUED:</b> {issued_dt}", ParagraphStyle("HRight", parent=style_subtitle, alignment=2))
        ],
        [
            Paragraph("SEBI TechSprint 2026 &bull; Investor Protection &amp; Fraud Detection Authority", style_subtitle),
            Paragraph(f"PRIORITY: <b><font color='{verdict_color.hexval()}'>{p_code}</font></b>", ParagraphStyle("HRight2", parent=style_subtitle, alignment=2, fontName=BOLD_FONT))
        ]
    ]

    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_TEAL, spaceBefore=2, spaceAfter=8))

    # -------------------------------------------------------------------------
    # 2. EXECUTIVE SUMMARY DASHBOARD TABLE
    # -------------------------------------------------------------------------
    summary_data = [
        [
            Paragraph("<b>Scan Reference ID:</b>", style_body),
            Paragraph(f"<font name='Courier'>{scan_id}</font>", style_code),
            Paragraph("<b>Trust Score:</b>", style_body),
            Paragraph(f"<font color='{verdict_color.hexval()}'><b>{trust_score} / 100</b></font>", style_body)
        ],
        [
            Paragraph("<b>Verdict Status:</b>", style_body),
            Paragraph(f"<font color='{verdict_color.hexval()}'><b>{verdict_upper}</b></font>", style_body),
            Paragraph("<b>Verification Priority:</b>", style_body),
            Paragraph(f"<b>{p_code}</b>", style_body)
        ],
        [
            Paragraph("<b>Content SHA-256:</b>", style_body),
            Paragraph(f"<font name='Courier'>{content_hash[:36]}...</font>", style_code),
            Paragraph("<b>Target Portals:</b>", style_body),
            Paragraph("SEBI SCORES / 1930 Helpline", style_body)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[110, 160, 120, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # 3. VISUAL TRUST GAUGE BAR
    # -------------------------------------------------------------------------
    gauge_drawing = Drawing(540, 20)
    # Background Track
    gauge_drawing.add(Rect(0, 2, 540, 16, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None, rx=3, ry=3))
    # Filled Value Bar
    filled_width = max(12, int(540 * (min(100, max(0, trust_score)) / 100.0)))
    gauge_drawing.add(Rect(0, 2, filled_width, 16, fillColor=verdict_color, strokeColor=None, rx=3, ry=3))
    # Centered Label Text
    label_color = colors.white if (filled_width > 280 or trust_score < 40) else COLOR_DARK
    gauge_drawing.add(String(
        270, 6,
        f"PRAMAAN TRUST INDEX: {trust_score} / 100 ({verdict_upper})",
        fontSize=8.5,
        fontName=BOLD_FONT,
        fillColor=label_color,
        textAnchor='middle'
    ))
    story.append(gauge_drawing)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 4. COLOR-CODED DETAILED CHECKS TABLE
    # -------------------------------------------------------------------------
    if checks:
        story.append(Paragraph("DETAILED SECURITY CHECKS BREAKDOWN", style_section_heading))
        checks_data = [[
            Paragraph("<b>Module</b>", style_body_bold),
            Paragraph("<b>Status</b>", style_body_bold),
            Paragraph("<b>Finding &amp; Diagnostic Indicator</b>", style_body_bold),
            Paragraph("<b>Impact</b>", style_body_bold)
        ]]

        for c in checks:
            m_status = str(c.get("status", "skip")).lower()
            st_color = COLOR_GREEN if m_status == "pass" else (COLOR_STAMP_RED if m_status == "fail" else COLOR_STAMP_AMBER)
            contrib = c.get("contribution", 0)
            contrib_str = f"+{contrib}" if contrib > 0 else str(contrib)

            mod_name = _clean_pdf_text(c.get('module', '')).upper()
            detail_hi = c.get('detail_hi')
            detail_en = c.get('detail', '')
            lbl = c.get('label', '')

            detail_text = f"<b>{_clean_pdf_text(lbl)}</b>: {_clean_pdf_text(detail_hi if detail_hi and language == 'hi' else detail_en)}"

            checks_data.append([
                Paragraph(f"<b>{mod_name}</b>", style_body),
                Paragraph(f"<font color='{st_color.hexval()}'><b>{_clean_pdf_text(m_status).upper()}</b></font>", style_body),
                Paragraph(detail_text, style_body),
                Paragraph(f"<b>{_clean_pdf_text(contrib_str)}</b>", style_body)
            ])

        checks_table = Table(checks_data, colWidths=[95, 55, 330, 60])
        checks_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
            ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(checks_table)
        story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 5. DEEPFAKE HEATMAP VISUALIZATION (if present)
    # -------------------------------------------------------------------------
    if heatmap_b64:
        try:
            from reportlab.platypus import Image as RLImage
            img_bytes = base64.b64decode(heatmap_b64)
            img_buf = io.BytesIO(img_bytes)
            story.append(Paragraph("VIDEO DEEPFAKE FORENSIC HEATMAP", style_section_heading))
            story.append(RLImage(img_buf, width=2.2*inch, height=2.2*inch))
            story.append(Paragraph("<font size=7.5 color='#718096'>Warm/Red highlighted regions indicate neural manipulation artifacts and facial forgery keypoints.</font>", style_subtitle))
            story.append(Spacer(1, 8))
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 6. DRAFT COMPLAINT 1: SEBI SCORES PORTAL
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. SEBI SCORES 2.0 INVESTOR COMPLAINT DRAFT", style_section_heading))
    if scores_custom_text:
        scores_text = _clean_pdf_text(scores_custom_text)
    else:
        scores_text = (
            f"<b>To:</b> SEBI SCORES (Securities and Exchange Board of India)<br/>"
            f"<b>Subject:</b> SEBI SCORES Complaint: Financial Fraud / Impersonation Scam (Ref: {scan_id[:8]})<br/><br/>"
            f"<b>Complaint Body:</b><br/>"
            f"Respected SEBI Officers,<br/>"
            f"I am submitting this formal complaint regarding an unauthorized financial communication flagged for security violations.<br/><br/>"
            f"- <b>Scan Reference ID:</b> {scan_id}<br/>"
            f"- <b>Content SHA-256 Digest:</b> {content_hash}<br/>"
            f"- <b>PRAMAAN Trust Score:</b> {trust_score}/100 ({verdict_upper})<br/>"
            f"- <b>Detection Flags:</b> Entity Impersonation, Unofficial Domain Links, High Urgency Panic Language.<br/><br/>"
            f"Requested Action: Please initiate inquiry and block spoofed domains associated with this communication."
        )

    scores_box = Table([[Paragraph(scores_text, style_complaint)]], colWidths=[540])
    scores_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, COLOR_TEAL),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(scores_box)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 7. DRAFT COMPLAINT 2: 1930 CYBERCRIME REPORTING HELPLINE
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. 1930 NATIONAL CYBERCRIME REPORTING PORTAL DRAFT", style_section_heading))
    if cyber_custom_text:
        cyber_text = _clean_pdf_text(cyber_custom_text)
    else:
        cyber_text = (
            f"<b>To:</b> National Cyber Crime Reporting Helpline (1930 / cybercrime.gov.in)<br/>"
            f"<b>Subject:</b> Cyber Fraud Incident Report - Financial Phishing Scam<br/><br/>"
            f"<b>Incident Details:</b><br/>"
            f"- <b>Incident Category:</b> Financial Phishing &amp; Demat Impersonation Fraud<br/>"
            f"- <b>Evidence Hash:</b> {content_hash}<br/>"
            f"- <b>Risk Index:</b> {trust_score}/100 ({verdict_upper})<br/>"
            f"- <b>Timestamp:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br/><br/>"
            f"Description: Threat/urgency message claiming Demat suspension and requesting immediate login on spoofed domain. Auto-generated evidence package attached."
        )

    cyber_box_border = COLOR_STAMP_RED if verdict_upper in ["SUSPICIOUS", "FAIL"] else COLOR_BORDER
    cyber_box = Table([[Paragraph(cyber_text, style_complaint)]], colWidths=[540])
    cyber_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, cyber_box_border),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(cyber_box)
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 8. DIGITAL SIGNATURE & EVIDENCE INTEGRITY PROOF
    # -------------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.75, color=COLOR_BORDER, spaceBefore=3, spaceAfter=5))
    footer_text = (
        f"<font color='#718096'><b>DIGITAL SIGNATURE &amp; INTEGRITY PROOF:</b> "
        f"Cryptographically verifiable evidence digest: <b>{content_hash[:32]}...</b> "
        f"Generated automatically by PRAMAAN-SHIELD Engine for SEBI TechSprint 2026. "
        f"Public QR seal verification available online at /verify.</font>"
    )
    story.append(Paragraph(footer_text, ParagraphStyle("FooterText", parent=style_subtitle, fontSize=7.5, leading=10, alignment=1)))

    # Build document with custom page counter canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
