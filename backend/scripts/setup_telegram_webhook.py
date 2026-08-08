import sys
import os
sys.path.insert(0, os.getcwd())

import httpx
import asyncio
from app.config import get_settings

async def main():
    settings = get_settings()
    bot_token = settings.TELEGRAM_BOT_TOKEN
    webhook_url = settings.TELEGRAM_WEBHOOK_URL
    webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET

    if not bot_token or "mock" in bot_token or "123456789" in bot_token:
        print("❌ TELEGRAM_BOT_TOKEN in .env is still a mock token.")
        print("👉 Please set a real bot token from @BotFather in backend/.env line 13!")
        return

    if not webhook_url or "localhost" in webhook_url:
        print("⚠️ TELEGRAM_WEBHOOK_URL is set to localhost or empty.")
        print("👉 Run `npx ngrok http 8000` to get a public HTTPS URL (e.g. https://xyz.ngrok-free.app/api/webhook)")
        return

    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    payload = {
        "url": webhook_url,
        "secret_token": webhook_secret
    }

    print(f"Connecting Telegram Bot Webhook to: {webhook_url}...")
    async with httpx.AsyncClient() as client:
        res = await client.post(api_url, json=payload)
        data = res.json()
        if data.get("ok"):
            print("✅ SUCCESS! Telegram Bot Webhook registered successfully!")
            print("Response:", data.get("description"))
        else:
            print("❌ Failed to register webhook:", data)

if __name__ == "__main__":
    asyncio.run(main())
