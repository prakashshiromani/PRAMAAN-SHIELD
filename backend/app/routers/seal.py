"""
POST /api/seal/sign & GET /api/seal/{id}/qr — Seal Signing Router
File: backend/app/routers/seal.py
"""

import base64
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from app.schemas import IssueSealRequest, IssueSealResponse
from app.crypto.seal_engine import sign_communication
from app.dependencies import get_api_key
from app.db.mongodb import get_db

router = APIRouter()


@router.post("/seal/sign", response_model=IssueSealResponse, tags=["seal"])
async def sign_seal_endpoint(
    request_data: IssueSealRequest,
    request: Request,
    api_key: str = Depends(get_api_key)
):
    """
    Issue a new PRAMAAN Seal for an official communication.
    SECURITY: Entity identity comes from authenticated session / API key context.
    """
    # Demo/Hackathon default authenticated entity
    entity_name = "SEBI"
    reg_no = "REGULATOR"

    raw_ip = request.client.host if request.client else "127.0.0.1"
    content_bytes = request_data.content_hash.encode("utf-8")

    result = await sign_communication(
        content_bytes=content_bytes,
        entity_name=entity_name,
        reg_no=reg_no,
        content_type=request_data.content_type,
        content_title=request_data.content_title,
        validity_days=request_data.validity_days,
        actor_ip=raw_ip
    )

    return IssueSealResponse(
        seal_id=result["seal_id"],
        entity_name=result["entity_name"],
        registration_number=result["registration_number"],
        content_hash=result["content_hash"],
        signature=result["signature"],
        not_before=result["not_before"],
        not_after=result["not_after"],
        qr_data_base64=result["qr_data_base64"],
        qr_image_url=result["qr_image_url"]
    )


@router.get("/seal/{seal_id}/qr", tags=["seal"])
async def get_seal_qr_image(seal_id: str):
    """Serve the PNG QR code image for a Seal ID."""
    db = await get_db()
    rec = await db.seal_records.find_one({"seal_id": seal_id})

    if not rec or not rec.get("qr_data"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seal QR image not found")

    try:
        import json
        import qrcode
        from io import BytesIO

        qr_json = base64.b64decode(rec["qr_data"]).decode()
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(qr_json)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
