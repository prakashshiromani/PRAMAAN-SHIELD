"""
PRAMAAN-SHIELD — Telegram Bot Polling Runner
File: backend/scripts/run_telegram_polling.py

Listens to messages sent to @Pramaanshield_bot on Telegram
and replies with live PRAMAAN Trust Scores & Explainability.
"""

import sys
import os
sys.path.insert(0, os.getcwd())

import asyncio
import httpx
from loguru import logger

from app.config import get_settings
from app.services.telegram_service import format_telegram_response
from app.services.gemini_service import GeminiService
from app.services.registry_service import RegistryService
from app.services.phishing_service import PhishingService
from app.services.trust_score_service import calculate_trust_score

settings = get_settings()
bot_token = settings.TELEGRAM_BOT_TOKEN
api_url = f"https://api.telegram.org/bot{bot_token}"

gemini_svc = GeminiService()
registry_svc = RegistryService()
phishing_svc = PhishingService(gemini_svc, registry_svc)

async def start_polling():
    print(f"🤖 Starting Telegram Bot Polling (@Pramaanshield_bot)...")
    print("👉 Send any message or link to @Pramaanshield_bot on Telegram!")
    
    offset = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Delete webhook first to allow long polling
        await client.post(f"{api_url}/deleteWebhook")
        
        while True:
            try:
                res = await client.get(f"{api_url}/getUpdates", params={"offset": offset, "timeout": 20})
                data = res.json()
                if not data.get("ok"):
                    await asyncio.sleep(3)
                    continue

                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")

                    if not chat_id or not text:
                        continue

                    print(f"📩 Received message from chat_id {chat_id}: {text[:40]}...")

                    if text.startswith("/start"):
                        welcome_msg = (
                            "🛡️ <b>PRAMAAN-SHIELD (प्रमाण शील्ड) AI Security Bot</b>\n\n"
                            "आप किसी भी संदिग्ध वित्तीय संदेश, लिंक, या एडवाइजरी को यहाँ फॉरवर्ड करें।\n\n"
                            "Forward any suspicious advisory or link here for instant AI verification!"
                        )
                        await client.post(f"{api_url}/sendMessage", json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "HTML"})
                        continue

                    # Run Detection Pipeline
                    phishing_res = await phishing_svc.analyze_text(text)
                    registry_res = phishing_res.registry_match if phishing_res else None

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
                    await client.post(f"{api_url}/sendMessage", json={"chat_id": chat_id, "text": reply_html, "parse_mode": "HTML"})
                    print(f"✅ Replied to chat_id {chat_id} with Trust Score: {trust_result['trust_score']}/100")

            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(start_polling())
    except KeyboardInterrupt:
        print("\nBot polling stopped.")
