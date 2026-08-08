"""
PRAMAAN-SHIELD — Redressal & Auto-Complaint Template Service
File: backend/app/services/redressal_service.py
"""

import uuid
import hmac
import hashlib
import time
from datetime import datetime, timezone
from typing import List
from loguru import logger
from app.db.mongodb import get_db
from app.schemas import GenerateReportResponse, ComplaintTemplate
from app.services.trust_score_service import derive_priority_code
from app.utils.constants import EMPTY_SHA256
from app.config import get_settings

_settings = get_settings()

# 10-minute lifetime — long enough to open the evidence package, short enough
# that a leaked link can't be replayed indefinitely.
_REPORT_TOKEN_TTL = 600


def _signed_report_url(report_id: str) -> str:
    """Server-issued, expiring download token. The HMAC secret NEVER leaves the
    server (unlike the old NEXT_PUBLIC_* client-minted token, which any browser
    could forge)."""
    exp = int(time.time()) + _REPORT_TOKEN_TTL
    body = f"{report_id}.{exp}"
    sig = hmac.new(
        _settings.resolved_report_access_secret().encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"/api/report/{report_id}/pdf?token={body}.{sig}"


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

        if scan_doc is None:
            try:
                from app.routers.scan import _LOCAL_SCAN_HISTORY
                scan_doc = _LOCAL_SCAN_HISTORY.get(scan_id)
            except Exception:
                pass

        content_hash = (scan_doc.get("content_hash") if scan_doc else None) or EMPTY_SHA256
        evidence_available = scan_doc is not None
        # When no stored scan record exists we have NO verifiable evidence on
        # this server. Score/verdict must stay neutral so we do not label an
        # unsubstantiated complaint as a P1 emergency.
        trust_score = scan_doc.get("trust_score") if (scan_doc and scan_doc.get("trust_score") is not None) else 50
        verdict = (scan_doc.get("verdict") if scan_doc else None) or "UNKNOWN"
        checks = (scan_doc.get("checks") if scan_doc else None) or []

        now = datetime.now(timezone.utc)
        report_id = f"rpt_{uuid.uuid4().hex[:8]}"

        # Determine Priority Level: P1 (Critical), P2 (Medium), P3 (Low/General)
        # Single shared classifier — must stay in sync with the PDF report path.
        # Without stored verification evidence we never claim an emergency: the
        # complaint becomes a general (P3) information record instead.
        if not evidence_available:
            priority_code = "P3_LOW"
        else:
            priority_code = derive_priority_code(trust_score, verdict, checks)

        if priority_code == "P1_CRITICAL":
            priority_label_hi = "🔴 प्राथमिकता: P1 - उच्च आपातकाल (CRITICAL EMERGENCY)"
            priority_label_en = "🔴 PRIORITY: P1 - HIGH EMERGENCY (CRITICAL SCAM)"
        elif priority_code == "P2_MEDIUM":
            priority_label_hi = "🟡 प्राथमिकता: P2 - मध्यम जोखिम (MEDIUM RISK)"
            priority_label_en = "🟡 PRIORITY: P2 - MEDIUM RISK (SUSPICIOUS ADVISORY)"
        else:
            priority_label_hi = "🟢 प्राथमिकता: P3 - सामान्य सूचना (GENERAL ADVISORY)"
            priority_label_en = "🟢 PRIORITY: P3 - GENERAL ADVISORY (ROUTINE LOG)"

        # Extract specific risk reasons from checks
        fail_reasons_hi = []
        fail_reasons_en = []
        for c in checks:
            if isinstance(c, dict) and c.get("status") in ["fail", "FAIL"]:
                if c.get("detail_hi"):
                    fail_reasons_hi.append(c["detail_hi"])
                if c.get("detail"):
                    fail_reasons_en.append(c["detail"])

        risk_str_hi = " | ".join(fail_reasons_hi) if fail_reasons_hi else "अनधिकृत वित्तीय फ़िशिंग / जाली संस्था"
        risk_str_en = " | ".join(fail_reasons_en) if fail_reasons_en else "Unauthorized financial phishing / spoofed entity"

        templates: List[ComplaintTemplate] = []

        if "sebi_scores" in target_portals:
            if priority_code == "P1_CRITICAL":
                subj_hi = f"🚨 [P1-उच्च आपातकाल SEBI SCORES] वित्तीय धोखाधड़ी व जाली संस्था की शिकायत (Scan ID: {scan_id[:8]})"
                subj_en = f"🚨 [P1-HIGH EMERGENCY SEBI SCORES] Critical Financial Scam & Impersonation Report (Scan ID: {scan_id[:8]})"
                body_hi = (
                    f"{priority_label_hi}\n\n"
                    f"आदरणीय SEBI अधिकारी,\n\n"
                    f"प्रमाण शील्ड (PRAMAAN-SHIELD) सुरक्षा तंत्र द्वारा एक **उच्च-जोखिम वित्तीय धोखाधड़ी (P1 HIGH PRIORITY)** की पहचान की गई है।\n\n"
                    f"📌 **अपराध विवरण (Scam Details)**:\n"
                    f"• स्कैन ID: {scan_id}\n"
                    f"• PRAMAAN ट्रस्ट स्कोर: {trust_score}/100 ({verdict})\n"
                    f"• मुख्य खतरा: {risk_str_hi}\n"
                    f"• सामग्री SHA-256 हैश: {content_hash}\n"
                    f"• दिनांक/समय: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"⚠️ **तत्काल कार्रवाई का अनुरोध**:\n"
                    f"1. संबंधित अनधिकृत संस्था के खिलाफ SEBI अधिनियम के तहत आपातकालीन जांच शुरू की जाए।\n"
                    f"2. अनधिकृत चैनल व धोखाधड़ी वाले बैंक खातों को ब्लॉक किया जाए।\n\n"
                    f"धन्यवाद,\n"
                    f"प्रमाण शील्ड स्वचालित निवारण प्रणाली (SEBI TechSprint 2026)"
                )
                body_en = (
                    f"{priority_label_en}\n\n"
                    f"Respected SEBI Official,\n\n"
                    f"A **High-Severity Financial Scam / Impersonation (P1 EMERGENCY)** has been flagged by PRAMAAN-SHIELD.\n\n"
                    f"📌 **Scam Evidence Log**:\n"
                    f"• Scan ID: {scan_id}\n"
                    f"• PRAMAAN Trust Index: {trust_score}/100 ({verdict})\n"
                    f"• Primary Risk Flags: {risk_str_en}\n"
                    f"• Content SHA-256 Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"⚠️ **Urgent Action Requested**:\n"
                    f"1. Initiate immediate regulatory investigation against the impersonating entity.\n"
                    f"2. Issue blocking/freeze orders for associated unauthorized communication channels.\n\n"
                    f"Sincerely,\n"
                    f"PRAMAAN-SHIELD Automated Complaint Engine (SEBI TechSprint 2026)"
                )
            elif priority_code == "P2_MEDIUM":
                subj_hi = f"⚠️ [P2-मध्यम जोखिम SEBI SCORES] असत्यापित सलाह व फ़िशिंग रिपोर्ट (Scan ID: {scan_id[:8]})"
                subj_en = f"⚠️ [P2-MEDIUM RISK SEBI SCORES] Unverified Advisory & Phishing Inquiry (Scan ID: {scan_id[:8]})"
                body_hi = (
                    f"{priority_label_hi}\n\n"
                    f"आदरणीय SEBI अधिकारी,\n\n"
                    f"प्रमाण शील्ड द्वारा एक **संदिग्ध वित्तीय संदेश (P2 MEDIUM RISK)** दर्ज किया गया है।\n\n"
                    f"📌 **विवरण**:\n"
                    f"• स्कैन ID: {scan_id}\n"
                    f"• PRAMAAN ट्रस्ट स्कोर: {trust_score}/100 ({verdict})\n"
                    f"• जोखिम संकेत: {risk_str_hi}\n"
                    f"• सामग्री हैश: {content_hash}\n"
                    f"• समय: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"कृपया संस्था के लाइसेंस व लिंक की पुष्टि करें।"
                )
                body_en = (
                    f"{priority_label_en}\n\n"
                    f"Respected SEBI Official,\n\n"
                    f"A **Suspicious Financial Communication (P2 MEDIUM RISK)** has been logged.\n\n"
                    f"📌 **Details**:\n"
                    f"• Scan ID: {scan_id}\n"
                    f"• Trust Index: {trust_score}/100 ({verdict})\n"
                    f"• Risk Markers: {risk_str_en}\n"
                    f"• Content Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"Kindly verify registration status."
                )
            else:
                subj_hi = f"ℹ️ [P3-सामान्य सूचना SEBI SCORES] सुरक्षा सत्यापन लॉग (Scan ID: {scan_id[:8]})"
                subj_en = f"ℹ️ [P3-INFORMATIONAL SEBI SCORES] Routine Security Verification Log (Scan ID: {scan_id[:8]})"
                body_hi = (
                    f"{priority_label_hi}\n\n"
                    f"आदरणीय SEBI अधिकारी,\n\n"
                    f"सामान्य सुरक्षा जांच एवं सत्यापन लॉग रिकॉर्ड:\n"
                    f"• स्कैन ID: {scan_id}\n"
                    f"• PRAMAAN ट्रस्ट स्कोर: {trust_score}/100 ({verdict})\n"
                    f"• सामग्री हैश: {content_hash}\n"
                    f"• समय: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )
                body_en = (
                    f"{priority_label_en}\n\n"
                    f"Respected SEBI Official,\n\n"
                    f"Routine security analysis and verification record:\n"
                    f"• Scan ID: {scan_id}\n"
                    f"• Trust Index: {trust_score}/100 ({verdict})\n"
                    f"• Content Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )

            templates.append(ComplaintTemplate(
                portal_id="sebi_scores",
                portal_name="SEBI SCORES Portal",
                subject=subj_hi if language == "hi" else subj_en,
                body_text=body_hi if language == "hi" else body_en,
                evidence_attached={
                    "scan_id": scan_id,
                    "content_hash": content_hash,
                    "trust_score": trust_score,
                    "priority": priority_code,
                    "evidence_available": evidence_available,
                    "timestamp": now.isoformat()
                }
            ))

        if "cybercrime_1930" in target_portals:
            if priority_code == "P1_CRITICAL":
                subj_1930_hi = f"🚨 [P1-उच्च आपातकाल 1930 REPORT] साइबर अपराध व वित्तीय धोखाधड़ी शिकायत (Scan ID: {scan_id[:8]})"
                subj_1930_en = f"🚨 [P1-HIGH EMERGENCY 1930 REPORT] Cybercrime Financial Scam & Deepfake Alert (Scan ID: {scan_id[:8]})"
                body_1930_hi = (
                    f"{priority_label_hi}\n\n"
                    f"साइबर अपराध हेल्पलाइन 1930 (National Cyber Crime Reporting Portal),\n\n"
                    f"प्रमाण शील्ड तंत्र द्वारा **गंभीर साइबर अपराध / वित्तीय फ़िशिंग (P1 EMERGENCY)** की सूचना दी जा रही है।\n\n"
                    f"📌 **अपराध साक्ष्य (Evidence Log)**:\n"
                    f"• प्राथमिक स्कैन ID: {scan_id}\n"
                    f"• साइबर जोखिम स्कोर: {trust_score}/100 (गंभीर खतरा / SUSPICIOUS)\n"
                    f"• फॉरेंसिक निष्कर्ष: {risk_str_hi}\n"
                    f"• साक्ष्य SHA-256 हैश: {content_hash}\n"
                    f"• समय: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"🚨 **तत्काल सुरक्षा आग्रह**:\n"
                    f"• वित्तीय नुकसान रोकने हेतु धोखाधड़ी वाले खातों व चैनलों पर तत्काल आपातकालीन कार्रवाई की जाए।"
                )
                body_1930_en = (
                    f"{priority_label_en}\n\n"
                    f"National Cyber Crime Reporting Portal (1930 Helpline),\n\n"
                    f"A **Critical Cybercrime / Financial Scam (P1 HIGH EMERGENCY)** is reported.\n\n"
                    f"📌 **Evidence Log**:\n"
                    f"• Primary Scan ID: {scan_id}\n"
                    f"• Risk Score: {trust_score}/100 (HIGH RISK / SUSPICIOUS)\n"
                    f"• Forensic Indicators: {risk_str_en}\n"
                    f"• Evidence SHA-256 Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}\n\n"
                    f"🚨 **Action Requested**:\n"
                    f"• Emergency tracking and blocking of fraudulent channels and accounts."
                )
            elif priority_code == "P2_MEDIUM":
                subj_1930_hi = f"⚠️ [P2-मध्यम जोखिम 1930 REPORT] संदिग्ध साइबर फ़िशिंग रिपोर्ट (Scan ID: {scan_id[:8]})"
                subj_1930_en = f"⚠️ [P2-MEDIUM RISK 1930 REPORT] Suspicious Cyber Phishing Alert (Scan ID: {scan_id[:8]})"
                body_1930_hi = (
                    f"{priority_label_hi}\n\n"
                    f"साइबर अपराध हेल्पलाइन 1930,\n\n"
                    f"संदिग्ध वित्तीय फ़िशिंग विवरण:\n"
                    f"• स्कैन ID: {scan_id}\n"
                    f"• ट्रस्ट स्कोर: {trust_score}/100\n"
                    f"• जोखिम संकेत: {risk_str_hi}\n"
                    f"• सामग्री हैश: {content_hash}\n"
                    f"• समय: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )
                body_1930_en = (
                    f"{priority_label_en}\n\n"
                    f"National Cyber Crime Portal (1930),\n\n"
                    f"Suspicious cyber phishing details:\n"
                    f"• Scan ID: {scan_id}\n"
                    f"• Trust Index: {trust_score}/100\n"
                    f"• Risk Indicators: {risk_str_en}\n"
                    f"• Content Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )
            else:
                subj_1930_hi = f"ℹ️ [P3-सामान्य सूचना 1930 REPORT] सुरक्षा विश्लेषण रिकॉर्ड (Scan ID: {scan_id[:8]})"
                subj_1930_en = f"ℹ️ [P3-INFORMATIONAL 1930 REPORT] Cyber Security Analysis Log (Scan ID: {scan_id[:8]})"
                body_1930_hi = (
                    f"{priority_label_hi}\n\n"
                    f"साइबर सुरक्षा रिकॉर्ड:\n"
                    f"• स्कैन ID: {scan_id}\n"
                    f"• ट्रस्ट स्कोर: {trust_score}/100\n"
                    f"• सामग्री हैश: {content_hash}\n"
                    f"• समय: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )
                body_1930_en = (
                    f"{priority_label_en}\n\n"
                    f"Cyber security log record:\n"
                    f"• Scan ID: {scan_id}\n"
                    f"• Trust Index: {trust_score}/100\n"
                    f"• Content Hash: {content_hash}\n"
                    f"• Timestamp: {now.strftime('%d-%m-%Y %H:%M UTC')}"
                )

            templates.append(ComplaintTemplate(
                portal_id="cybercrime_1930",
                portal_name="National Cyber Crime Reporting Portal (1930)",
                subject=subj_1930_hi if language == "hi" else subj_1930_en,
                body_text=body_1930_hi if language == "hi" else body_1930_en,
                evidence_attached={
                    "scan_id": scan_id,
                    "content_hash": content_hash,
                    "trust_score": trust_score,
                    "priority": priority_code,
                    "evidence_available": evidence_available,
                    "timestamp": now.isoformat()
                }
            ))

        # No stored evidence: be transparent in the template body so a reader
        # can never mistake this for a server-verified emergency report.
        if not evidence_available:
            preface_hi = ("⚠️ सूचना: इस सर्वर पर इस स्कैन का कोई संग्रहीत साक्ष्य उपलब्ध नहीं है। "
                          "नीचे दी गई जानकारी केवल उपयोगकर्ता द्वारा सत्र के दौरान सबमिट की गई थी।\n\n")
            preface_en = ("⚠️ NOTE: No stored scan evidence was found on this server for this session. "
                          "Details below reflect only what the user submitted.\n\n")
            for tpl in templates:
                if language == "hi":
                    tpl.body_text = preface_hi + tpl.body_text
                else:
                    tpl.body_text = preface_en + tpl.body_text

        # Save to user_reports collection
        report_doc = {
            "report_id": report_id,
            "scan_id": scan_id,
            "target_portals": target_portals,
            "language": language,
            "templates": [t.model_dump() for t in templates],
            "template_text_selected": templates[0].body_text if templates else "",
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
            pdf_download_url=_signed_report_url(report_id),
            created_at=now
        )
