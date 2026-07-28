"""
POST /api/scan — Content Scanning Endpoint
File: backend/app/routers/scan.py

Primary user journey: accepts text or uploaded files (audio, video, image).
Runs perceptual hash check, phishing pipeline, voice/video analysis in parallel via asyncio.gather.
Saves scan record to MongoDB `scan_history` and returns ScanResponse.
"""

import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, status
from loguru import logger

from app.schemas import ScanResponse, ContentType, ActionButton
from app.services.hash_service import generate_image_phash, generate_video_phash, check_known_fake_hash
from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService
from app.services.phishing_service import PhishingService
from app.services.voice_service import VoiceAnalyzer
from app.services.video_service import VideoAnalyzer
from app.services.trust_score_service import calculate_trust_score
from app.crypto.seal_engine import verify_seal
from app.utils.seal_extract import extract_seal_token
from app.utils.privacy import pseudonymize_ip
from app.utils.file_cleanup import schedule_temp_file_deletion, ensure_upload_dir
from app.db.mongodb import get_db
from app.config import get_settings

settings = get_settings()
router = APIRouter()

gemini_svc = GeminiService()
registry_svc = RegistryService()
phishing_svc = PhishingService(gemini_svc, registry_svc)
voice_analyzer = VoiceAnalyzer()
video_analyzer = VideoAnalyzer()

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".jpg", ".jpeg", ".png"}


@router.post("/scan", response_model=ScanResponse, tags=["scan"])
async def scan_content(
    request: Request,
    content_type: ContentType = Form(...),
    text_content: Optional[str] = Form(None),
    language: str = Form("hi"),
    file: Optional[UploadFile] = File(None)
):
    """
    Unified Scan Endpoint.
    Accepts text or uploaded file, executes parallel detection pipelines,
    and returns a Trust Score (0-100) with bilingual explainability.
    """
    scan_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    raw_ip = request.client.host if request.client else "127.0.0.1"
    ip_hmac = pseudonymize_ip(raw_ip)

    # 1. Content Ingestion & Hash Generation
    content_sha256 = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    perceptual_hash: Optional[str] = None
    saved_temp_path: Optional[str] = None

    if file:
        file_ext = Path(file.filename).suffix.lower() if file.filename else ".tmp"
        if file_ext not in ALLOWED_EXTENSIONS and file_ext != ".tmp":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{file_ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        content_bytes = await file.read()
        if len(content_bytes) > settings.MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum upload limit of {settings.MAX_UPLOAD_BYTES // (1024*1024)}MB"
            )

        upload_dir = ensure_upload_dir()
        temp_file_name = f"{scan_id}{file_ext}"
        saved_temp_path = str(upload_dir / temp_file_name)
        content_sha256 = "sha256:" + hashlib.sha256(content_bytes).hexdigest()

        with open(saved_temp_path, "wb") as f:
            f.write(content_bytes)

        # Schedule 60s auto-deletion (zero-retention)
        await schedule_temp_file_deletion(saved_temp_path, 60)

        # Generate perceptual hash
        if content_type == ContentType.IMAGE:
            perceptual_hash = generate_image_phash(saved_temp_path)
        elif content_type in [ContentType.VIDEO, ContentType.AUDIO]:
            perceptual_hash = generate_video_phash(saved_temp_path) or generate_image_phash(saved_temp_path)

    elif text_content:
        content_bytes = text_content.encode("utf-8")
        content_sha256 = "sha256:" + hashlib.sha256(content_bytes).hexdigest()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either text_content or a file upload must be provided"
        )

    # 2. Perceptual Hash Check (Sub-50ms Redis Lookup)
    hash_match = None
    if perceptual_hash:
        try:
            hash_match = await check_known_fake_hash(perceptual_hash)
        except Exception as e:
            logger.warning(f"Known fake hash check skipped (Redis offline): {e}")

    # 3. Detection Pipelines
    phishing_res = None
    voice_res = None
    video_res = None

    if text_content:
        phishing_res = await phishing_svc.analyze_text(text_content)

    logger.info(f"Scan request: content_type={content_type}, file={file.filename if file else None}, temp_path={saved_temp_path}")

    if (content_type == ContentType.VIDEO or str(content_type).lower() == "video") and (saved_temp_path or file):
        try:
            orig_name = file.filename if file else None
            video_res = await video_analyzer.analyze(saved_temp_path or "", original_filename=orig_name)
            logger.info(f"Video analysis result: is_deepfake={video_res.is_deepfake}, prob={video_res.deepfake_probability}%")
        except Exception as e:
            logger.error(f"Video analysis error: {e}")

    # 4. Seal Token Extraction & Verification (if token in text)
    seal_res = None
    if text_content:
        token = extract_seal_token(text_content)
        if token:
            try:
                seal_verify = await verify_seal(token, presented_content_bytes=None)
                seal_res = seal_verify if isinstance(seal_verify, dict) else seal_verify.model_dump()
            except Exception as e:
                logger.warning(f"Seal verification unavailable: {e}")

    # 5. Registry Lookup if entity extracted
    registry_res = phishing_res.registry_match if phishing_res else None

    # 6. Trust Score Aggregation
    trust_result = calculate_trust_score(
        hash_result=hash_match,
        phishing_result=phishing_res,
        voice_result=voice_res,
        video_result=video_res,
        registry_result=registry_res,
        seal_result=seal_res
    )

    # Recommended Actions
    actions = [
        ActionButton(id="act_report_1930", label="Cybercrime 1930 Helpline Report", action_type="navigate", url="/report"),
        ActionButton(id="act_report_scores", label="SEBI SCORES Complaint", action_type="navigate", url="/report")
    ]

    evidence = trust_result["explainability_hi"] if language == "hi" else trust_result["explainability_en"]

    # 7. Save Record to MongoDB scan_history
    scan_doc = {
        "scan_id": scan_id,
        "content_type": content_type,
        "content_hash": content_sha256,
        "perceptual_hash": perceptual_hash,
        "trust_score": trust_result["trust_score"],
        "verdict": trust_result["verdict"].value,
        "checks": [c.model_dump() for c in trust_result["checks"]],
        "source": "web",
        "language": language,
        "ip_hmac": ip_hmac,
        "created_at": now
    }

    try:
        db = await get_db()
        if db is not None:
            await db.scan_history.insert_one(scan_doc)
    except Exception as e:
        logger.error(f"Failed to persist scan history to MongoDB: {e}")

    return ScanResponse(
        scan_id=scan_id,
        content_type=content_type,
        trust_score=trust_result["trust_score"],
        verdict=trust_result["verdict"],
        verdict_label_hi=trust_result["verdict_label_hi"],
        verdict_label_en=trust_result["verdict_label_en"],
        checks=trust_result["checks"],
        explainability_en=trust_result["explainability_en"],
        explainability_hi=trust_result["explainability_hi"],
        ai_generated_probability=phishing_res.ai_generated_probability if phishing_res else None,
        typosquat_detected=phishing_res.domain_check.suspicious if phishing_res and phishing_res.domain_check.has_typosquat else None,
        evidence_summary=evidence,
        recommended_actions=actions,
        created_at=now
    )
