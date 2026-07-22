import os
import sys
import asyncio
import logging
import requests
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from aiogram.filters import CommandStart, Command
import bot as bot_module

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("❌ Ошибка: Укажи корректный BOT_TOKEN в Secrets (Replit → Tools → Secrets)")
    sys.exit(1)

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot_instance = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = bot_module.dp

RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")
REPLIT_DOMAIN = os.environ.get("REPLIT_DOMAINS", "").split(",")[0].strip() if os.environ.get("REPLIT_DOMAINS") else None
LOCAL_DOMAIN = RENDER_URL or os.environ.get("DOMAIN") or REPLIT_DOMAIN or "localhost"


@app.route("/")
def index():
    return "✅ Telegram Video Bot is running!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.model_validate(request.get_json(force=True), context={"bot": bot_instance})
    loop.run_until_complete(dp.feed_update(bot_instance, update))
    return "OK", 200


@app.route("/set-webhook", methods=["GET"])
def set_webhook_route():
    if not LOCAL_DOMAIN or LOCAL_DOMAIN == "localhost":
        return "❌ DOMAIN не задан", 400
    webhook_url = f"https://{LOCAL_DOMAIN}/webhook"
    resp = requests.get(
        f"https://api.telegram.org/bot{TOKEN}/setWebhook",
        params={"url": webhook_url},
        timeout=10,
    )
    return resp.json()


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    if LOCAL_DOMAIN and LOCAL_DOMAIN != "localhost":
        webhook_url = f"https://{LOCAL_DOMAIN}/webhook"
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/setWebhook",
                params={"url": webhook_url},
                timeout=10,
            )
            logging.info(f"Webhook установлен: {webhook_url} — {resp.json()}")
        except Exception as e:
            logging.warning(f"Не удалось установить webhook: {e}")
    else:
        logging.warning("DOMAIN не задан — установи webhook вручную через /set-webhook")

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
