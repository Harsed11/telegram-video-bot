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
LOCAL_DOMAIN = LOCAL_DOMAIN.replace("https://", "").replace("http://", "").rstrip("/")


BOT_USERNAME = "@save_video_clip_bot"
BOT_LINK = "https://t.me/save_video_clip_bot"


LANDING_HTML = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaveVideoBot — Скачивай видео из TikTok, Reels, Shorts и VK</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {{
            --bg: #0a0a0f;
            --card: rgba(255,255,255,0.04);
            --border: rgba(255,255,255,0.06);
            --accent: #0088cc;
            --accent-glow: rgba(0,136,204,0.3);
            --text: #f0f0f5;
            --text-secondary: #9898a8;
            --radius: 20px;
        }}

        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }}

        .bg-grid {{
            position: fixed; inset: 0; z-index: 0;
            background-image:
                linear-gradient(rgba(0,136,204,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,136,204,0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }}

        .container {{ position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 0 24px; }}

        /* ─── Nav ─── */
        nav {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 20px 0; border-bottom: 1px solid var(--border);
        }}
        .logo {{ font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }}
        .logo span {{ color: var(--accent); }}

        /* ─── Hero ─── */
        .hero {{ text-align: center; padding: 80px 0 60px; }}
        .hero-badge {{
            display: inline-block; background: rgba(0,136,204,0.12); color: var(--accent);
            padding: 8px 18px; border-radius: 50px; font-size: 14px; font-weight: 600;
            border: 1px solid rgba(0,136,204,0.2); margin-bottom: 28px;
        }}
        .hero h1 {{
            font-size: clamp(36px, 7vw, 68px); font-weight: 900; line-height: 1.08;
            letter-spacing: -1.5px; margin-bottom: 20px;
        }}
        .hero h1 .gradient {{
            background: linear-gradient(135deg, #0088cc, #00b4ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .hero p {{
            font-size: 18px; color: var(--text-secondary); line-height: 1.6;
            max-width: 600px; margin: 0 auto 36px;
        }}
        .hero-buttons {{ display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }}
        .btn-primary {{
            display: inline-flex; align-items: center; gap: 10px;
            background: linear-gradient(135deg, #0088cc, #00a0e8);
            color: #fff; padding: 16px 36px; border-radius: 60px;
            font-size: 16px; font-weight: 700; text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 30px var(--accent-glow);
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 8px 40px var(--accent-glow); }}
        .btn-secondary {{
            display: inline-flex; align-items: center; gap: 10px;
            background: var(--card); color: var(--text); padding: 16px 36px;
            border-radius: 60px; font-size: 16px; font-weight: 600;
            text-decoration: none; border: 1px solid var(--border);
            transition: 0.2s;
        }}
        .btn-secondary:hover {{ border-color: var(--accent); }}

        /* ─── Phone mock ─── */
        .mock-wrap {{ margin: 60px auto 0; max-width: 320px; }}
        .phone-mock {{
            background: #111; border-radius: 36px; border: 3px solid #222;
            padding: 16px 12px; box-shadow: 0 20px 80px rgba(0,0,0,0.6);
        }}
        .pm-header {{ display: flex; align-items: center; gap: 8px; padding-bottom: 14px; }}
        .pm-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        .pm-dot.r {{ background: #ff5f56; }}
        .pm-dot.y {{ background: #ffbd2e; }}
        .pm-dot.g {{ background: #27c93f; }}
        .pm-title {{ flex:1; text-align:center; font-size:12px; color:#888; font-weight:600; }}
        .pm-screen {{ background: #0d0d0d; border-radius: 16px; padding: 16px; }}
        .pm-msg {{ background: #1a1a2e; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }}
        .pm-msg.sent {{ background: var(--accent); margin-left: 20%; }}
        .pm-msg .pm-link {{ color: #888; font-size: 12px; word-break: break-all; }}
        .pm-msg .pm-link span {{ color: var(--accent); }}
        .pm-msg.pm-settings {{ background: var(--card); border: 1px solid var(--border); }}
        .pm-row {{ display: flex; gap: 6px; margin: 8px 0; }}
        .pm-chip {{
            background: #222; border-radius: 20px; padding: 4px 10px; font-size: 10px; color: #ccc;
        }}
        .pm-chip.active {{ background: var(--accent); color: #fff; }}
        .pm-foot {{ display: flex; gap: 6px; margin-top: 10px; }}
        .pm-input {{ flex:1; background: #1a1a2e; border-radius: 20px; padding: 10px 14px; font-size: 12px; color: #888; }}
        .pm-send {{ background: var(--accent); width: 36px; height: 36px; border-radius: 50%; display: flex; align-items:center; justify-content:center; font-size:16px; }}

        /* ─── Features ─── */
        .section {{ padding: 80px 0; }}
        .section-title {{ text-align: center; font-size: clamp(28px, 4vw, 42px); font-weight: 800; margin-bottom: 12px; }}
        .section-sub {{ text-align: center; color: var(--text-secondary); font-size: 17px; max-width: 500px; margin: 0 auto 50px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }}
        .feature-card {{
            background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
            padding: 32px 24px; transition: 0.25s;
        }}
        .feature-card:hover {{ border-color: rgba(0,136,204,0.3); transform: translateY(-3px); }}
        .fc-icon {{ font-size: 36px; margin-bottom: 16px; }}
        .fc-title {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
        .fc-desc {{ font-size: 14px; color: var(--text-secondary); line-height: 1.6; }}

        /* ─── Steps ─── */
        .steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }}
        @media (max-width:700px) {{ .steps {{ grid-template-columns: 1fr; }} }}
        .step {{ text-align: center; padding: 32px 20px; background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); }}
        .step-num {{
            width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, var(--accent), #00a0e8);
            display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800;
            margin: 0 auto 16px;
        }}
        .step-title {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
        .step-desc {{ font-size: 14px; color: var(--text-secondary); line-height: 1.6; }}

        /* ─── FAQ ─── */
        .faq-list {{ max-width: 680px; margin: 0 auto; }}
        .faq-item {{
            background: var(--card); border: 1px solid var(--border); border-radius: 14px;
            padding: 20px 24px; margin-bottom: 10px; cursor: pointer;
        }}
        .faq-question {{ font-weight: 600; font-size: 16px; display: flex; justify-content: space-between; }}
        .faq-answer {{ font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-top: 10px; display: none; }}

        /* ─── Footer ─── */
        footer {{ text-align: center; padding: 50px 0 30px; border-top: 1px solid var(--border); }}
        footer p {{ color: var(--text-secondary); font-size: 14px; }}

        /* ─── Animations ─── */
        .fade-in {{ opacity:0; transform:translateY(20px); animation:fadeIn 0.6s forwards; }}
        @keyframes fadeIn {{ to {{ opacity:1; transform:translateY(0); }} }}
        .delay-1 {{ animation-delay:0.1s; }}
        .delay-2 {{ animation-delay:0.2s; }}
        .delay-3 {{ animation-delay:0.3s; }}

        /* ─── Platforms ─── */
        .platforms {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 30px; }}
        .platform-chip {{
            background: var(--card); border: 1px solid var(--border); border-radius: 40px;
            padding: 10px 22px; font-size: 14px; font-weight: 500; color: var(--text-secondary);
        }}
    </style>
</head>
<body>
<div class="bg-grid"></div>

<nav class="container">
    <div class="logo">Save<span>Video</span>Bot</div>
    <a href="{BOT_LINK}" target="_blank" class="btn-primary" style="padding:10px 24px;font-size:14px;">Открыть в Telegram</a>
</nav>

<section class="hero container">
    <div class="hero-badge fade-in">🚀 Бесплатно · Без рекламы · Без регистрации</div>
    <h1 class="fade-in delay-1">
        Скачивай видео<br>
        <span class="gradient">из TikTok, Reels, Shorts & VK</span>
    </h1>
    <p class="fade-in delay-2">
        Просто отправь ссылку боту — выбери качество и звук, получи готовый файл за секунды.
        Работает 24/7 прямо в Telegram.
    </p>
    <div class="hero-buttons fade-in delay-2">
        <a href="{BOT_LINK}" target="_blank" class="btn-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.02-1.96 1.25-5.54 3.69-.52.36-1 .53-1.42.52-.47-.01-1.37-.26-2.04-.48-.82-.27-1.47-.42-1.41-.88.03-.24.36-.49.99-.74 3.9-1.7 6.5-2.82 7.8-3.37 3.71-1.56 4.48-1.83 4.98-1.84.11 0 .36.03.52.17.13.12.17.28.18.45-.02.12-.03.25-.07.39z" fill="currentColor"/></svg>
            Запустить бота
        </a>
    </div>

    <div class="platforms fade-in delay-3">
        <span class="platform-chip">🎵 TikTok</span>
        <span class="platform-chip">📱 Instagram Reels</span>
        <span class="platform-chip">▶️ YouTube Shorts</span>
        <span class="platform-chip">💬 VK Клипы</span>
    </div>

    <div class="mock-wrap fade-in delay-3">
        <div class="phone-mock">
            <div class="pm-header">
                <div class="pm-dot r"></div><div class="pm-dot y"></div><div class="pm-dot g"></div>
                <div class="pm-title">SaveVideoBot</div>
            </div>
            <div class="pm-screen">
                <div class="pm-msg"><div class="pm-link">🔗 <span>tiktok.com/</span>@user/video/123...</div></div>
                <div class="pm-msg pm-settings">
                    <div style="font-size:10px;color:#888;">Качество</div>
                    <div class="pm-row">
                        <span class="pm-chip">1080p</span>
                        <span class="pm-chip active">720p</span>
                        <span class="pm-chip">480p</span>
                    </div>
                    <div style="font-size:10px;color:#888;margin-top:6px;">Звук</div>
                    <div class="pm-row">
                        <span class="pm-chip active">🔊 Со звуком</span>
                        <span class="pm-chip">🔇 Без звука</span>
                    </div>
                </div>
                <div class="pm-msg sent">⬇️ Скачать видео</div>
                <div class="pm-foot">
                    <div class="pm-input">Написать сообщение...</div>
                    <div class="pm-send">➤</div>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="section container">
    <h2 class="section-title fade-in">Возможности бота</h2>
    <p class="section-sub fade-in delay-1">Всё, что нужно для быстрого скачивания видео</p>
    <div class="grid">
        <div class="feature-card fade-in delay-1">
            <div class="fc-icon">🎬</div>
            <div class="fc-title">Выбор качества</div>
            <div class="fc-desc">Скачивай в 360p, 480p, 720p или 1080p — сам выбирай, что нужно.</div>
        </div>
        <div class="feature-card fade-in delay-2">
            <div class="fc-icon">🔊</div>
            <div class="fc-title">Со звуком или без</div>
            <div class="fc-desc">Отдельная кнопка — видео со звуком или полностью без аудиодорожки.</div>
        </div>
        <div class="feature-card fade-in delay-3">
            <div class="fc-icon">⚡</div>
            <div class="fc-title">Мгновенная скорость</div>
            <div class="fc-desc">Серверный движок обрабатывает видео за секунды, без ожидания.</div>
        </div>
        <div class="feature-card fade-in delay-1">
            <div class="fc-icon">📱</div>
            <div class="fc-title">Все платформы</div>
            <div class="fc-desc">TikTok, Instagram Reels, YouTube Shorts, VK — одна ссылка, любое видео.</div>
        </div>
        <div class="feature-card fade-in delay-2">
            <div class="fc-icon">🆓</div>
            <div class="fc-title">Полностью бесплатно</div>
            <div class="fc-desc">Никаких подписок, лимитов и скрытых платежей. Просто пользуйся.</div>
        </div>
        <div class="feature-card fade-in delay-3">
            <div class="fc-icon">🔒</div>
            <div class="fc-title">Без регистрации</div>
            <div class="fc-desc">Не нужно создавать аккаунт — просто отправь ссылку и получи видео.</div>
        </div>
    </div>
</section>

<section class="section container">
    <h2 class="section-title fade-in">Как это работает</h2>
    <p class="section-sub fade-in delay-1">Всего 3 шага</p>
    <div class="steps">
        <div class="step fade-in delay-1">
            <div class="step-num">1</div>
            <div class="step-title">Отправь ссылку</div>
            <div class="step-desc">Скопируй ссылку на видео из TikTok, Reels, Shorts или VK и отправь боту.</div>
        </div>
        <div class="step fade-in delay-2">
            <div class="step-num">2</div>
            <div class="step-title">Выбери настройки</div>
            <div class="step-desc">Укажи качество (720p, 1080p и т.д.) и нужно ли видео со звуком или без.</div>
        </div>
        <div class="step fade-in delay-3">
            <div class="step-num">3</div>
            <div class="step-title">Скачай готовый файл</div>
            <div class="step-desc">Нажми «Скачать» и сразу получи видео в Telegram — готово к просмотру!</div>
        </div>
    </div>
</section>

<section class="section container">
    <h2 class="section-title fade-in">Частые вопросы</h2>
    <p class="section-sub fade-in delay-1">Ответы на самое главное</p>
    <div class="faq-list">
        <div class="faq-item" onclick="toggleFaq(this)">
            <div class="faq-question"><span>Бот действительно бесплатный?</span><span style="color:#666;">+</span></div>
            <div class="faq-answer">Да, на 100%. Без лимитов, подписок и скрытых платежей.</div>
        </div>
        <div class="faq-item" onclick="toggleFaq(this)">
            <div class="faq-question"><span>Какие платформы поддерживаются?</span><span style="color:#666;">+</span></div>
            <div class="faq-answer">TikTok, Instagram Reels, YouTube Shorts, VK Клипы. Список постоянно расширяется.</div>
        </div>
        <div class="faq-item" onclick="toggleFaq(this)">
            <div class="faq-question"><span>Есть ли ограничение по размеру?</span><span style="color:#666;">+</span></div>
            <div class="faq-answer">Telegram ограничивает отправку файлов до 50 МБ. Если видео весит больше — бот сообщит об этом.</div>
        </div>
        <div class="faq-item" onclick="toggleFaq(this)">
            <div class="faq-question"><span>Можно ли скачать без звука?</span><span style="color:#666;">+</span></div>
            <div class="faq-answer">Да! При выборе параметров просто нажми «Без звука» — видео будет без аудиодорожки.</div>
        </div>
        <div class="faq-item" onclick="toggleFaq(this)">
            <div class="faq-question"><span>Почему видео не скачивается?</span><span style="color:#666;">+</span></div>
            <div class="faq-answer">Убедись что ссылка правильная и видео доступно. Если проблема остаётся — напиши в поддержку.</div>
        </div>
    </div>
</section>

<footer class="container">
    <div class="logo" style="margin-bottom:12px;">Save<span>Video</span>Bot</div>
    <p>Сделано с ❤️ для удобного скачивания видео</p>
    <p style="margin-top:6px;">Работает 24/7 · {BOT_USERNAME}</p>
</footer>

<script>
function toggleFaq(el) {{
    var answer = el.querySelector('.faq-answer');
    var sign = el.querySelector('.faq-question span:last-child');
    if (answer.style.display === 'block') {{
        answer.style.display = 'none';
        sign.textContent = '+';
    }} else {{
        answer.style.display = 'block';
        sign.textContent = '−';
    }}
}}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return LANDING_HTML, 200


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
