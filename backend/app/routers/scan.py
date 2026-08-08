"""
POST /api/scan — Content Scanning Endpoint
File: backend/app/routers/scan.py

Primary user journey: accepts text or uploaded files (audio, video, image).
Runs perceptual hash check, phishing pipeline, voice/video analysis in parallel via asyncio.gather.
Saves scan record to MongoDB `scan_history` and returns ScanResponse.

Verdict determinism contract: DB/Redis availability must never change the final
trust_score/verdict for identical input. Offline → SKIP(0) not REMOVE; online vs
offline outcome must match.

Every dependency that can go offline degrades to a deterministic baseline:
  - Redis known-fake lookup  → falls back to the in-memory seeded KNOWN_FAKE_HASHES
    index (app/services/hash_service.py). A pHash that yields a hard-gate FAIL
    online yields the SAME hard-gate FAIL offline; a non-matching pHash returns
    the SAME "no match" (None) in both states. A check is never silently removed.
  - SEBI registry lookup       → RegistryService falls back to the bundled local
    JSON registry when Mongo is None, then returns the same found/not-found result.
  - Seal verification          → verify_seal() resolves from Mongo when ONLINE or
    from _LOCAL_ISSUED_SEALS + local entity keys when OFFLINE; an UNKNOWN token is
    FORGED in BOTH states (never VERIFIED offline).
"""

import uuid
import hashlib
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, status
from loguru import logger

from app.schemas import ScanResponse, ActionButton
from app.services.hash_service import generate_image_phash, generate_video_phash, check_known_fake_hash
from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService
from app.services.phishing_service import PhishingService
from app.services.voice_service import VoiceAnalyzer
from app.services.video_service import VideoAnalyzer
from app.services.trust_score_service import calculate_trust_score
from app.crypto.seal_engine import verify_seal
from app.utils.seal_extract import extract_seal_token, extract_seal_from_image
from app.utils.privacy import pseudonymize_ip
from app.utils.constants import EMPTY_SHA256
from app.utils.file_cleanup import schedule_temp_file_deletion, ensure_upload_dir
from app.db.mongodb import get_db
from app.config import get_settings

settings = get_settings()
router = APIRouter()


_gemini_svc = None
_registry_svc = None

_phishing_svc = None
_voice_analyzer = None
_video_analyzer = None

_LOCAL_SCAN_HISTORY: dict[str, dict] = {}


def get_gemini_svc():
    global _gemini_svc
    if _gemini_svc is None:
        _gemini_svc = GeminiService()
    return _gemini_svc


def get_registry_svc():
    global _registry_svc
    if _registry_svc is None:
        _registry_svc = RegistryService()
    return _registry_svc


def get_phishing_svc():
    global _phishing_svc
    if _phishing_svc is None:
        _phishing_svc = PhishingService(get_gemini_svc(), get_registry_svc())
    return _phishing_svc


def get_voice_analyzer():
    global _voice_analyzer
    if _voice_analyzer is None:
        _voice_analyzer = VoiceAnalyzer()
    return _voice_analyzer


def get_video_analyzer():
    global _video_analyzer
    if _video_analyzer is None:
        _video_analyzer = VideoAnalyzer()
    return _video_analyzer

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mov", ".jpg", ".jpeg", ".png", ".txt", ".eml", ".json"}


# Hard cap on concurrent scans: heavy CPU (pHash, OpenCV decode) and ML runs on
# a CPU box; running 15 scans at once would oversubscribe threads/cores.
_SCAN_LOCK: Optional[asyncio.Semaphore] = None
_SCAN_LOCK_CONCURRENCY = None


async def _get_scan_lock() -> asyncio.Semaphore:
    global _SCAN_LOCK, _SCAN_LOCK_CONCURRENCY
    if _SCAN_LOCK is None or _SCAN_LOCK_CONCURRENCY != settings.MAX_CONCURRENT_SCANS:
        _SCAN_LOCK = asyncio.Semaphore(settings.MAX_CONCURRENT_SCANS)
        _SCAN_LOCK_CONCURRENCY = settings.MAX_CONCURRENT_SCANS
    return _SCAN_LOCK


@router.post("/scan", response_model=ScanResponse, tags=["scan"])
async def scan_content(
    request: Request,
    content_type: str = Form(...),
    text_content: Optional[str] = Form(None, max_length=500_000),
    language: str = Form("hi"),
    file: Optional[UploadFile] = File(None)
):
    """
    Unified Scan Endpoint (concurrency-capped wrapper).
    Accepts text or uploaded file, executes parallel detection pipelines,
    and returns a Trust Score (0-100) with bilingual explainability.
    """
    sem = await _get_scan_lock()
    async with sem:
        return await _scan_content_impl(request, content_type, text_content, language, file)


async def _scan_content_impl(
    request: Request,
    content_type: str,
    text_content: Optional[str],
    language: str,
    file: Optional[UploadFile]
):
    # Validate & normalize content_type; accept email/hash sent by the web
    # client as aliases for text/image so those scans stop failing validation.
    ct = (content_type or "text").strip().lower()
    if ct not in {"text", "email", "hash", "audio", "video", "image"}:
        raise HTTPException(status_code=400, detail="Unsupported content_type")
    effective_ct = "text" if ct in ("email",) else ("image" if ct == "hash" else ct)
    if language not in {"hi", "en"}:
        language = "hi"

    # A6 — hard byte cap on text input (multipart Form(max_length) is enforced
    # by FastAPI, but re-validate the encoded size so PDF/email paths can never
    # feed a multi-hundred-MB blob into regex + Gemini analysis).
    if text_content is not None and len(text_content) > 500_000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Text content exceeds the 500KB analysis limit")

    scan_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    raw_ip = request.client.host if request.client else "127.0.0.1"
    ip_hmac = pseudonymize_ip(raw_ip)

    # 1. Content Ingestion & Hash Generation
    content_sha256 = EMPTY_SHA256
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

        # Zero-retention cleanup (A10): never schedule deletion on a clock that
        # can race the 45–60s sandbox analysis deadlines. First deploy a long
        # safety-net (never races), then schedule a fast removal after analysis.
        await schedule_temp_file_deletion(saved_temp_path, max(180, settings.TEMP_FILE_TTL_SECONDS))

        # Generate perceptual hash (CPU-bound image ops run off the event loop)
        async def _phash_image(p):
            return await asyncio.to_thread(generate_image_phash, p)
        async def _phash_video(p):
            return await asyncio.to_thread(generate_video_phash, p)

        if effective_ct == "image":
            perceptual_hash = await _phash_image(saved_temp_path)
        elif effective_ct in ("video", "audio"):
            ph = await _phash_video(saved_temp_path)
            perceptual_hash = ph or await _phash_image(saved_temp_path)

        # Extract text content from text/eml file uploads if not provided
        if file_ext in [".txt", ".eml", ".json"] and not text_content:
            try:
                text_content = content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                pass

    elif text_content:
        content_bytes = text_content.encode("utf-8")
        content_sha256 = "sha256:" + hashlib.sha256(content_bytes).hexdigest()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either text_content or a file upload must be provided"
        )

    # 2. Perceptual Hash Check (Redis lookup with deterministic in-memory seed
    # fallback — a known fake that hard-gates ONLINE must hard-gate OFFLINE too).
    hash_match = None
    if perceptual_hash:
        try:
            hash_match = await check_known_fake_hash(perceptual_hash)
        except Exception as e:
            logger.warning(f"Known fake hash check unavailable, falling back to seeded index: {e}")

    # 3. Detection Pipelines
    phishing_res = None
    voice_res = None
    video_res = None

    if text_content:
        phishing_res = await get_phishing_svc().analyze_text(text_content)

    logger.info(f"Scan request: content_type={content_type}, file={file.filename if file else None}, temp_path={saved_temp_path}")

    if (content_type == "audio") and (saved_temp_path or file):
        try:
            # Analyzer construction loads models (heavy); never run it on the
            # event loop — it would freeze every concurrent request.
            voice_analyzer = await asyncio.to_thread(get_voice_analyzer)
            voice_res = await voice_analyzer.analyze(saved_temp_path or "")
            logger.info(f"Voice analysis result: is_synthetic={voice_res.is_synthetic}, score={voice_res.liveness_score}%")
        except Exception as e:
            logger.error(f"Voice analysis error: {e}")

    if (effective_ct == "video") and (saved_temp_path or file):
        try:
            orig_name = file.filename if file else None
            video_analyzer = await asyncio.to_thread(get_video_analyzer)
            voice_analyzer = await asyncio.to_thread(get_voice_analyzer)

            async def _run_visual():
                return await video_analyzer.analyze(saved_temp_path or "", original_filename=orig_name)

            async def _run_audio():
                return await voice_analyzer.analyze(saved_temp_path or "")

            # Parallel Dual-Fusion: run visual deepfake scan & voice clone check concurrently
            results = await asyncio.gather(
                asyncio.wait_for(_run_visual(), timeout=35.0),
                asyncio.wait_for(_run_audio(), timeout=35.0),
                return_exceptions=True
            )

            if isinstance(results[0], Exception):
                logger.error(f"Video visual analysis error/timeout: {results[0]}")
            else:
                video_res = results[0]
                if video_res:
                    logger.info(f"Video visual analysis result: is_deepfake={video_res.is_deepfake}, prob={video_res.deepfake_probability}%")

            if isinstance(results[1], Exception):
                logger.warning(f"Video audio track analysis error/timeout: {results[1]}")
            else:
                voice_res = results[1]
                if voice_res:
                    logger.info(f"Video audio track analysis result: is_synthetic={voice_res.is_synthetic}, score={voice_res.liveness_score}%")
                    if video_res and voice_res.is_synthetic:
                        video_res.is_deepfake = True
                        video_res.deepfake_probability = max(video_res.deepfake_probability, 88)
                        video_res.analysis_failed = False
        except Exception as e:
            logger.error(f"Video analysis error: {e}")

    if (effective_ct == "image") and (saved_temp_path or file):
        try:
            video_analyzer = await asyncio.to_thread(get_video_analyzer)
            video_res = await asyncio.to_thread(video_analyzer.analyze_image, saved_temp_path or "")
            logger.info(f"Image deepfake analysis result: is_deepfake={video_res.is_deepfake}, prob={video_res.deepfake_probability}%")

        except Exception as e:
            logger.error(f"Image deepfake analysis error: {e}")

    if saved_temp_path:
        # A10: analysis is done — release the zero-retention temp file now
        # (shortly after use), instead of waiting out a long TTL.
        await schedule_temp_file_deletion(saved_temp_path, 3)

    # 4. Seal Token Extraction & Verification (from text OR image screenshot QR code)
    seal_res = None
    token = None
    if text_content:
        token = extract_seal_token(text_content)
    elif saved_temp_path and effective_ct == "image":
        token = await asyncio.to_thread(extract_seal_from_image, saved_temp_path)

    if token:
        try:
            # A5: bind the seal to the EXACT scanned content. A valid official
            # seal ID quoted inside a phishing message (or pasted onto a fake
            # screenshot) must NOT boost the score unless the seal was actually
            # issued for THIS content — otherwise a quoted seal ID rates a scam
            # as VERIFIED.
            presented = None
            if text_content:
                presented = text_content.encode("utf-8")
            elif content_bytes:
                presented = content_bytes
            if presented is not None:
                seal_verify = await verify_seal(token, presented_content_bytes=presented)
            else:
                seal_verify = await verify_seal(token, presented_content_bytes=None)
            seal_res = seal_verify if isinstance(seal_verify, dict) else seal_verify.model_dump()
            logger.info(f"PRAMAAN Seal extracted & verified: token={token}, verdict={seal_res.get('verdict')}")
        except Exception as e:
            logger.warning(f"Seal verification unavailable for token '{token}': {e}")

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

    # 7. Save Record to MongoDB scan_history (persist video heatmap for PDF evidence)
    scan_doc = {
        "scan_id": scan_id,
        "content_type": effective_ct,
        "content_hash": content_sha256,
        "perceptual_hash": perceptual_hash,
        "trust_score": trust_result["trust_score"],
        "verdict": trust_result["verdict"].value,
        "checks": [c.model_dump() for c in trust_result["checks"]],
        "heatmap_b64": getattr(video_res, "heatmap_b64", None) if video_res else None,
        "source": "web",
        "language": language,
        "ip_hmac": ip_hmac,
        "created_at": now
    }

    _LOCAL_SCAN_HISTORY[scan_id] = scan_doc
    if len(_LOCAL_SCAN_HISTORY) > 500:
        oldest = next(iter(_LOCAL_SCAN_HISTORY))
        _LOCAL_SCAN_HISTORY.pop(oldest, None)

    try:
        from app.services.analytics_service import get_analytics_service, invalidate_dashboard_cache
        analytics_svc = get_analytics_service()
        flagged_d = None
        if phishing_res and phishing_res.domain_check and getattr(phishing_res.domain_check, "extracted_domain", None):
            flagged_d = phishing_res.domain_check.extracted_domain

        is_verified_seal = False
        if seal_res and (seal_res.get("is_valid") or str(seal_res.get("verdict")).upper() == "VERIFIED"):
            is_verified_seal = True
        elif trust_result["verdict"].value in ["VERIFIED", "CERTIFIED"]:
            is_verified_seal = True

        analytics_svc.record_scan(
            content_type=effective_ct,
            verdict=trust_result["verdict"].value,
            checks=scan_doc["checks"],
            flagged_domain=flagged_d,
            is_seal_verified=is_verified_seal
        )
        await invalidate_dashboard_cache()
    except Exception as e:
        logger.debug(f"Analytics scan recording skipped: {e}")

    try:
        db = await get_db()
        if db is not None:
            await db.scan_history.insert_one(scan_doc)
    except Exception as e:
        logger.error(f"Failed to persist scan history to MongoDB: {e}")

    return ScanResponse(
        scan_id=scan_id,
        content_type=effective_ct,
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
