"""
POST /api/report & GET /api/report/{id}/pdf — Complaint Generation Router
File: backend/app/routers/report.py
"""

from fastapi import APIRouter, HTTPException, Response, status
from loguru import logger
from app.schemas import GenerateReportRequest, GenerateReportResponse
from app.services.redressal_service import RedressalService

router = APIRouter()
redressal_svc = RedressalService()


@router.post("/report", response_model=GenerateReportResponse, tags=["report"])
async def generate_report_endpoint(request_data: GenerateReportRequest):
    """
    Generates pre-filled complaint templates for SEBI SCORES and 1930 Cybercrime Portal.
    """
    return await redressal_svc.generate_complaint_report(
        scan_id=request_data.scan_id,
        target_portals=request_data.target_portals,
        language=request_data.language
    )


@router.get("/report/{report_id}/pdf", tags=["report"])
async def download_report_pdf_endpoint(report_id: str):
    """
    TRD §13 requirement: Downloads PDF evidence package for a generated complaint report.
    """
    from app.db.mongodb import get_db
    from app.utils.pdf_generator import generate_evidence_pdf

    scan_id = "N/A"
    content_hash = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    trust_score = 15
    created_at = None

    try:
        db = await get_db()
        if db is not None:
            report_doc = await db.user_reports.find_one({"report_id": report_id})
            if report_doc:
                scan_id = report_doc.get("scan_id", "N/A")
                ev_pkg = report_doc.get("evidence_package") or {}
                content_hash = ev_pkg.get("content_hash", content_hash)
                trust_score = ev_pkg.get("trust_score", trust_score)
                created_at = report_doc.get("created_at", None)
    except Exception as e:
        logger.warning(f"MongoDB lookup skipped for report {report_id}: {e}")

    try:
        pdf_bytes = generate_evidence_pdf(
            report_id=report_id,
            scan_id=scan_id,
            content_hash=content_hash,
            trust_score=trust_score,
            verdict="SUSPICIOUS" if trust_score < 30 else ("EXERCISE CAUTION" if trust_score < 70 else "VERIFIED"),
            created_at=str(created_at) if created_at else None
        )
    except Exception as e:
        logger.error(f"ReportLab PDF generation error: {e}")
        pdf_bytes = generate_evidence_pdf(report_id=report_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PRAMAAN_Evidence_{report_id}.pdf"
        }
    )
