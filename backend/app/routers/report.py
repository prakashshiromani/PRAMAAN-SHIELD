"""
POST /api/report & GET /api/report/{id}/pdf — Complaint Generation Router
File: backend/app/routers/report.py
"""

from typing import Optional, Tuple
import hmac
import hashlib
import re
import time
from fastapi import APIRouter, HTTPException, Response, Query
from loguru import logger
from app.schemas import GenerateReportRequest, GenerateReportResponse
from app.services.redressal_service import RedressalService
from app.services.trust_score_service import verdict_for_score
from app.utils.constants import EMPTY_SHA256
from app.config import get_settings

router = APIRouter()
redressal_svc = RedressalService()
settings = get_settings()

_REPORT_TOKEN_TTL = 600  # must match _REPORT_TOKEN_TTL in redressal_service


def _report_token_valid(report_id: str, token: str) -> bool:
    """Verify a server-issued `{report_id}.{exp}.{sig}` download token."""
    try:
        body, sig = token.rsplit(".", 1)
        # rpartition so a report_id containing '.' never breaks parsing
        rid, _, exp = body.rpartition(".")
        if rid != report_id:
            return False
        if int(exp) < int(time.time()):
            return False
        expected = hmac.new(
            settings.resolved_report_access_secret().encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


def _portal_kind(portal_id: str) -> Optional[str]:
    """Classify a complaint template as 'scores' / 'cyber' (or None)."""
    p = str(portal_id).lower()
    if "scores" in p or "sebi" in p:
        return "scores"
    if "1930" in p or "cyber" in p:
        return "cyber"
    return None


def _extract_portal_texts(templates, *, as_dict: bool) -> Tuple[Optional[str], Optional[str]]:
    """Map stored complaint templates → SCORES / Cybercrime custom text."""
    scores = None
    cyber = None
    for tpl in templates:
        t = tpl if as_dict else tpl.model_dump(exclude_none=True)
        p_code = str(t.get("portal_id") or t.get("portal_code") or t.get("portal_name") or "")
        formatted = f"**{t.get('subject', '')}**\n\n{t.get('body_text', '')}"
        kind = _portal_kind(p_code)
        if kind == "scores":
            scores = formatted
        elif kind == "cyber":
            cyber = formatted
    return scores, cyber


@router.post("/report", response_model=GenerateReportResponse, tags=["report"])
async def generate_report_endpoint(request_data: GenerateReportRequest):
    """
    Generates pre-filled complaint templates for SEBI SCORES and 1930 Cybercrime Portal.
    """
    res = await redressal_svc.generate_complaint_report(
        scan_id=request_data.scan_id,
        target_portals=request_data.target_portals,
        language=request_data.language
    )

    try:
        from app.services.analytics_service import get_analytics_service, invalidate_dashboard_cache
        analytics_svc = get_analytics_service()
        analytics_svc.record_report_generated()
        await invalidate_dashboard_cache()
    except Exception as e:
        logger.warning(f"Analytics report generation recording skipped: {e}")

    return res


@router.get("/report/{report_id}/pdf", tags=["report"])
async def download_report_pdf_endpoint(
    report_id: str,
    lang: Optional[str] = None,
    token: str = Query(default="")
):
    """
    TRD §13 requirement: Downloads PDF evidence package for a generated complaint report.
    Requires a signed download token to avoid guessable-ID evidence disclosure.
    """
    from app.db.mongodb import get_db
    from app.utils.pdf_generator import generate_evidence_pdf

    # Signed, expiring download gate. Tokens are minted server-side at report
    # creation time; the HMAC secret never leaves the server, so an IDOR via a
    # guessed report_id no longer yields another victim's evidence package.
    if not token or not _report_token_valid(report_id, token):
        raise HTTPException(status_code=403, detail="Invalid or expired download token")

    scan_id = "N/A"
    content_hash = EMPTY_SHA256
    trust_score = 15
    created_at = None
    checks = None
    heatmap_b64 = None
    priority_code = None
    scores_custom_text = None
    cyber_custom_text = None

    report_lang = lang or ""

    try:
        db = await get_db()
        report_doc = None
        scan_doc = None
        if db is not None:
            report_doc = await db.user_reports.find_one({"report_id": report_id})
            if report_doc:
                scan_id = report_doc.get("scan_id", scan_id)
                ev_pkg = report_doc.get("evidence_package") or {}
                content_hash = ev_pkg.get("content_hash", content_hash)
                trust_score = ev_pkg.get("trust_score", trust_score)
                priority_code = ev_pkg.get("priority")
                created_at = report_doc.get("created_at", None)
                if not lang:
                    report_lang = report_doc.get("language", "hi")

                scores_custom_text, cyber_custom_text = _extract_portal_texts(
                    report_doc.get("templates", []), as_dict=True
                )

                if scan_id and scan_id != "N/A":
                    scan_doc = await db.scan_history.find_one({"scan_id": scan_id})
    except Exception as e:
        logger.warning(f"MongoDB lookup skipped for report {report_id}: {e}")

    # Prefer the requested language; otherwise fall back to the language the
    # report was generated in (stored with the record); last resort Hindi.
    report_lang = report_lang or "hi"

    if scan_doc:
        checks = scan_doc.get("checks")
        heatmap_b64 = scan_doc.get("heatmap_b64")
        if not content_hash or content_hash.startswith("sha256:e3b0c44"):
            content_hash = scan_doc.get("content_hash", content_hash)
        trust_score = scan_doc.get("trust_score", trust_score)

    if not scores_custom_text and not cyber_custom_text:
        try:
            fallback_res = await redressal_svc.generate_complaint_report(
                scan_id=scan_id if scan_id != "N/A" else "demo",
                target_portals=["sebi_scores", "cybercrime_1930"],
                language=report_lang
            )
            scores_custom_text, cyber_custom_text = _extract_portal_texts(fallback_res.templates, as_dict=False)
        except Exception as e:
            logger.warning(f"Fallback report generation error: {e}")

    try:
        pdf_bytes = generate_evidence_pdf(
            report_id=report_id,
            scan_id=scan_id,
            content_hash=content_hash,
            trust_score=trust_score,
            verdict=verdict_for_score(trust_score).value,
            created_at=str(created_at) if created_at else None,
            checks=checks,
            heatmap_b64=heatmap_b64,
            priority_code=priority_code,
            scores_custom_text=scores_custom_text,
            cyber_custom_text=cyber_custom_text,
            language=report_lang
        )
    except Exception as e:
        logger.error(f"ReportLab PDF generation error: {e}")
        pdf_bytes = generate_evidence_pdf(report_id=report_id, language=report_lang)

    safe_report_id = re.sub(r"[^A-Za-z0-9_-]", "", report_id) or "report"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PRAMAAN_Evidence_{safe_report_id}.pdf"
        }
    )
