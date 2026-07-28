"""
POST /api/webhook — Telegram Bot Webhook Endpoint
File: backend/app/routers/webhook.py

SECURITY.md §M3:
Validates X-Telegram-Bot-Api-Secret-Token header matching TELEGRAM_WEBHOOK_SECRET.
Runs actual text phishing pipeline and trust engine aggregation.
"""

from fastapi import APIRouter, Header, Request, HTTPException, status
from loguru import logger
from app.config import get_settings
from app.services.telegram_service import format_telegram_response
from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService
from app.services.phishing_service import PhishingService
from app.services.trust_score_service import calculate_trust_score

router = APIRouter()
settings = get_settings()

gemini_svc = GeminiService()
registry_svc = RegistryService()
phishing_svc = PhishingService(gemini_svc, registry_svc)


@router.post("/webhook", tags=["webhook"])
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default=None)
):
    """
    Telegram webhook receiver.
    Enforces header secret token match to block forged updates.
    Runs real detection pipeline on incoming text message.
    """
    if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Rejected unauthorized Telegram webhook request: invalid secret token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret token"
        )

    try:
        update = await request.json()
        logger.info(f"Received Telegram update ID: {update.get('update_id')}")

        message = update.get("message", {})
        text = message.get("text", "")

        if not text:
            reply_html = "⚠️ <b>प्रमाण शील्ड:</b> कृपया केवल टेक्स्ट संदेश या मीडिया फॉरवर्ड करें।"
            return {"ok": True, "status": "processed", "reply": reply_html}

        # 1. Run real phishing detection pipeline
        phishing_res = await phishing_svc.analyze_text(text)
        registry_res = phishing_res.registry_match if phishing_res else None

        # 2. Calculate trust score
        trust_result = calculate_trust_score(
            hash_result=None,
            phishing_result=phishing_res,
            voice_result=None,
            video_result=None,
            registry_result=registry_res,
            seal_result=None
        )

        scan_res_formatted = {
            "trust_score": trust_result["trust_score"],
            "verdict": trust_result["verdict"].value,
            "explainability_hi": trust_result["explainability_hi"],
            "explainability_en": trust_result["explainability_en"]
        }

        reply_html = format_telegram_response(scan_res_formatted, lang="hi")

        return {
            "ok": True,
            "status": "processed",
            "reply": reply_html
        }
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"ok": False, "error": str(e)}
