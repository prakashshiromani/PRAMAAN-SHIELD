"""
POST /api/verify — PRAMAAN Seal Verification Router
File: backend/app/routers/verify.py
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import VerifySealRequest, VerifySealResponse, SealVerdict
from app.crypto.seal_engine import verify_seal

router = APIRouter()


@router.post("/verify", response_model=VerifySealResponse, tags=["verify"])
async def verify_seal_endpoint(request_data: VerifySealRequest):
    """
    Verify a PRAMAAN Seal by seal_id or raw QR payload JSON.
    Executes the 5 mandatory checks:
    1. Resolve trust anchor from sebi_registry
    2. ECDSA signature verification under pinned key
    3. Presented content re-hashing
    4. Revocation status check
    5. Validity window (not_before / not_after) check
    """
    seal_input = request_data.seal_id or request_data.qr_payload
    if not seal_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either seal_id or qr_payload must be provided"
        )

    presented_bytes = None
    if request_data.presented_content_hash:
        presented_bytes = request_data.presented_content_hash.encode("utf-8")

    result = await verify_seal(seal_input, presented_bytes)

    try:
        from app.services.analytics_service import get_analytics_service
        analytics_svc = get_analytics_service()
        analytics_svc.record_seal_verification(is_valid=result.get("is_valid", False))
    except Exception:
        pass

    def _to_str(val):
        if val is None:
            return None
        if hasattr(val, "isoformat"):
            return val.isoformat()
        return str(val)

    return VerifySealResponse(
        verdict=SealVerdict(result["verdict"]),
        is_valid=result.get("is_valid", False),
        seal_id=result.get("seal_id"),
        entity_name=result.get("entity_name") or result.get("signer_entity_name"),
        registration_number=result.get("registration_number") or result.get("signer_registration_number"),
        signer_entity_name=result.get("signer_entity_name"),
        signer_registration_number=result.get("signer_registration_number"),
        signed_at=_to_str(result.get("signed_at")),
        not_before=_to_str(result.get("not_before")),
        not_after=_to_str(result.get("not_after")),
        content_match=result.get("content_match", False),
        message_hi=result.get("message_hi", ""),
        message_en=result.get("message_en", "")
    )
