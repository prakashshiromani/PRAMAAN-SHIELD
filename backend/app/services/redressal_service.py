"""
PRAMAAN-SHIELD — Redressal & Auto-Complaint Template Service
File: backend/app/services/redressal_service.py
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from loguru import logger
from app.db.mongodb import get_db
from app.schemas import GenerateReportResponse, ComplaintTemplate


class RedressalService:
    async def generate_complaint_report(
        self,
        scan_id: str,
        target_portals: List[str],
        language: str = "hi"
    ) -> GenerateReportResponse:
        """
        Generates pre-filled complaint templates and evidence packages
        for SEBI SCORES and 1930 Cybercrime Portal.
        """
        db = await get_db()
        scan_doc = None
        if db is not None:
            try:
                scan_doc = await db.scan_history.find_one({"scan_id": scan_id})
            except Exception as e:
                logger.warning(f"MongoDB scan_history lookup skipped: {e}")

        content_hash = scan_doc.get("content_hash", "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") if scan_doc else "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        trust_score = scan_doc.get("trust_score", 15) if scan_doc else 15
        verdict = scan_doc.get("verdict", "SUSPICIOUS") if scan_doc else "SUSPICIOUS"

        now = datetime.now(timezone.utc)
        report_id = f"rpt_{uuid.uuid4().hex[:8]}"

        templates: List[ComplaintTemplate] = []

        if "sebi_scores" in target_portals:
            subj_hi = f"SEBI SCORES शिकायत: वित्तीय धोखाधड़ी का संदेह (Scan ID: {scan_id[:8]})"
            body_hi = (
                f"आदरणीय SEBI अधिकारी,\n\n"
                f"मैं प्रमाण शील्ड द्वारा चिन्हित संदिग्ध वित्तीय धोखाधड़ी/अनधिकृत संस्था की रिपोर्ट कर रहा हूँ।\n"
                f"सामग्री हैश: {content_hash}\n"
                f"PRAMAAN ट्रस्ट स्कोर: {trust_score}/100 ({verdict})\n"
                f"दिनांक: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                f"कृपया इस संस्था/सामग्री की जांच करें।"
            )
            templates.append(ComplaintTemplate(
                portal_id="sebi_scores",
                portal_name="SEBI SCORES Portal",
                subject=subj_hi if language == "hi" else f"SEBI SCORES Complaint: Financial Scam Suspected ({scan_id[:8]})",
                body_text=body_hi,
                evidence_attached={
                    "scan_id": scan_id,
                    "content_hash": content_hash,
                    "trust_score": trust_score,
                    "timestamp": now.isoformat()
                }
            ))

        if "cybercrime_1930" in target_portals:
            subj_1930 = f"1930 साइबर अपराध रिपोर्ट: वित्तीय धोखाधड़ी (Scan ID: {scan_id[:8]})"
            body_1930 = (
                f"साइबर अपराध हेल्पलाइन 1930,\n\n"
                f"संदिग्ध वित्तीय फ़िशिंग/डीपफेक धोखाधड़ी का विवरण:\n"
                f"स्कैन ID: {scan_id}\n"
                f"सामग्री हैश: {content_hash}\n"
                f"ट्रस्ट स्कोर: {trust_score}/100\n"
                f"समय: {now.strftime('%d-%m-%Y %H:%M UTC')}"
            )
            templates.append(ComplaintTemplate(
                portal_id="cybercrime_1930",
                portal_name="National Cyber Crime Reporting Portal (1930)",
                subject=subj_1930,
                body_text=body_1930,
                evidence_attached={
                    "scan_id": scan_id,
                    "content_hash": content_hash,
                    "trust_score": trust_score,
                    "timestamp": now.isoformat()
                }
            ))

        # Save to user_reports collection
        report_doc = {
            "report_id": report_id,
            "scan_id": scan_id,
            "target_portals": target_portals,
            "template_text_en": templates[0].body_text if templates else "",
            "template_text_hi": templates[0].body_text if templates else "",
            "evidence_package": {
                "content_hash": content_hash,
                "trust_score": trust_score,
                "timestamp": now
            },
            "status": "generated",
            "created_at": now
        }

        try:
            if db is not None:
                await db.user_reports.insert_one(report_doc)
        except Exception as e:
            logger.error(f"Failed to persist user report to MongoDB: {e}")

        return GenerateReportResponse(
            report_id=report_id,
            scan_id=scan_id,
            templates=templates,
            pdf_download_url=f"/api/report/{report_id}/pdf",
            created_at=now
        )
