"""
PRAMAAN-SHIELD — Telegram Bot Service (@PramaanikBot)
File: backend/app/services/telegram_service.py
"""

from typing import Dict, Any
from loguru import logger
from app.schemas import TelegramVerdictReply, VerdictStatus


def format_telegram_response(scan_res: Dict[str, Any], lang: str = "hi") -> str:
    """Format Telegram MarkdownV2 / HTML message reply."""
    score = scan_res.get("trust_score", 50)
    verdict = scan_res.get("verdict", VerdictStatus.CAUTION)

    if score >= 70:
        emoji = "🟢"
        verdict_str = "सत्यापित / सुरक्षित" if lang == "hi" else "VERIFIED / SAFE"
    elif score >= 30:
        emoji = "🟡"
        verdict_str = "सावधान रहें" if lang == "hi" else "EXERCISE CAUTION"
    else:
        emoji = "🔴"
        verdict_str = "संदिग्ध / धोखा" if lang == "hi" else "SUSPICIOUS / SCAM"

    explainability = scan_res.get("explainability_hi" if lang == "hi" else "explainability_en", "")

    return (
        f"<b>🛡️ PRAMAAN-SHIELD प्रमाण परिणाम</b>\n\n"
        f"<b>ट्रस्ट स्कोर:</b> {emoji} <b>{score}/100</b>\n"
        f"<b>फैसला:</b> {verdict_str}\n\n"
        f"<b>विवरण:</b>\n{explainability}\n\n"
        f"<i>रिपोर्ट दर्ज करने या प्रमाण पत्र सत्यापित करने के लिए हमारी वेबसाइट पर जाएँ।</i>"
    )
