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
<title>SaveVideoBot</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#06060e;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.06);--accent:#0099ff;--accent2:#7b2ff2;--accent3:#ff2d7b;--glow:rgba(0,153,255,0.4);--text:#f0f0f8;--muted:#7a7a8e;--radius:24px}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);overflow-x:hidden;min-height:100vh;transition:.3s}}
::selection{{background:var(--accent);color:#fff}}

[data-theme='light']{{--bg:#ffffff;--card:#f0f0f8;--border:#e0e0e0;--text:#06060e;--muted:#555}}
canvas#bg{{position:fixed;inset:0;z-index:0;pointer-events:none}}
.aurora{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
.aurora div{{position:absolute;border-radius:50%;filter:blur(120px);opacity:.35;animation:aurora 20s ease-in-out infinite alternate}}
.a1{{width:600px;height:600px;background:radial-gradient(circle,var(--accent),transparent 70%);top:-200px;left:-100px;animation-delay:0s}}
.a2{{width:500px;height:500px;background:radial-gradient(circle,var(--accent2),transparent 70%);bottom:-150px;right:-100px;animation-delay:-7s}}
.a3{{width:400px;height:400px;background:radial-gradient(circle,var(--accent3),transparent 70%);top:40%;left:50%;animation-delay:-14s}}
@keyframes aurora{{0%{{transform:translate(0,0) scale(1)}}33%{{transform:translate(80px,-60px) scale(1.1)}}66%{{transform:translate(-40px,80px) scale(.9)}}100%{{transform:translate(60px,40px) scale(1.05)}}}}
.noise{{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.03;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}}
.container{{position:relative;z-index:2;max-width:1140px;margin:0 auto;padding:0 24px}}
nav{{position:fixed;top:0;left:0;right:0;z-index:100;padding:16px 0;backdrop-filter:blur(20px);background:rgba(6,6,14,.6);border-bottom:1px solid var(--border);transition:.3s}}
.nav-inner{{max-width:1140px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between}}
.logo{{font-size:22px;font-weight:900;letter-spacing:-1px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.nav-links{{display:flex;gap:28px;align-items:center}}
.nav-links a{{color:var(--muted);text-decoration:none;font-size:14px;font-weight:500;transition:.2s}}
.nav-links a:hover{{color:var(--text)}}
.btn-glow{{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;padding:10px 24px;border-radius:50px;font-size:14px;font-weight:700;text-decoration:none;transition:.3s;box-shadow:0 0 30px var(--glow);position:relative;overflow:hidden}}
.btn-glow::before{{content:'';position:absolute;inset:0;background:linear-gradient(135deg,transparent,rgba(255,255,255,.15),transparent);transform:translateX(-100%);transition:.5s}}
.btn-glow:hover::before{{transform:translateX(100%)}}
.btn-glow:hover{{transform:translateY(-2px) scale(1.03);box-shadow:0 0 50px var(--glow)}}
.hero{{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:120px 0 60px;position:relative}}
.hero-chip{{display:inline-flex;align-items:center;gap:8px;background:rgba(0,153,255,.08);border:1px solid rgba(0,153,255,.2);padding:8px 20px;border-radius:50px;font-size:13px;font-weight:600;color:var(--accent);margin-bottom:32px;backdrop-filter:blur(10px);animation:pulse-glow 3s ease-in-out infinite}}
@keyframes pulse-glow{{0%,100%{{box-shadow:0 0 20px rgba(0,153,255,.1)}}50%{{box-shadow:0 0 40px rgba(0,153,255,.25)}}}}
.hero-chip .dot{{width:8px;height:8px;border-radius:50%;background:#00ff88;animation:blink 2s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.hero h1{{font-size:clamp(40px,8vw,80px);font-weight:900;line-height:1.05;letter-spacing:-2px;margin-bottom:24px}}
.hero h1 .line{{display:block}}
.hero h1 .grad{{background:linear-gradient(135deg,var(--accent),var(--accent2),var(--accent3));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-size:200% 200%;animation:gradient-shift 4s ease infinite}}
@keyframes gradient-shift{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
.hero-desc{{font-size:18px;color:var(--muted);line-height:1.7;max-width:560px;margin:0 auto 40px}}
.hero-btns{{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}}
.btn-hero{{display:inline-flex;align-items:center;gap:10px;padding:18px 40px;border-radius:60px;font-size:17px;font-weight:700;text-decoration:none;transition:.3s;cursor:pointer;position:relative}}
.btn-hero.primary{{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;box-shadow:0 8px 40px var(--glow)}}
.btn-hero.primary:hover{{transform:translateY(-3px) scale(1.02);box-shadow:0 12px 50px var(--glow)}}
.btn-hero.secondary{{background:rgba(255,255,255,.05);color:var(--text);border:1px solid var(--border);backdrop-filter:blur(10px)}}
.btn-hero.secondary:hover{{border-color:var(--accent);background:rgba(0,153,255,.08)}}
.tags{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:40px 0 60px}}
.tag{{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:50px;padding:10px 24px;font-size:14px;font-weight:500;color:var(--muted);backdrop-filter:blur(8px);transition:.3s;cursor:default}}
.tag:hover{{border-color:var(--accent);color:var(--text);transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,0,0,.3)}}
.tag .emoji{{margin-right:6px}}
.phone-section{{perspective:1000px;margin:0 auto;max-width:340px}}
.phone-wrap{{transform:rotateY(-5deg) rotateX(3deg);transition:.5s ease;transform-style:preserve-3d}}
.phone-wrap:hover{{transform:rotateY(0deg) rotateX(0deg) translateY(-10px)}}
.phone{{background:linear-gradient(145deg,#1a1a2e,#0d0d1a);border-radius:40px;border:2px solid rgba(255,255,255,.08);padding:18px 14px;box-shadow:0 40px 80px rgba(0,0,0,.5),0 0 60px rgba(0,153,255,.1),inset 0 1px 0 rgba(255,255,255,.05)}}
.phone-notch{{width:120px;height:28px;background:#0d0d1a;border-radius:0 0 16px 16px;margin:0 auto 12px;position:relative}}
.phone-notch::after{{content:'';width:8px;height:8px;background:#1a1a3e;border-radius:50%;position:absolute;top:10px;left:50%;transform:translateX(-50%)}}
.phone-screen{{background:#0a0a14;border-radius:20px;padding:16px;min-height:280px}}
.pm-msg{{background:rgba(255,255,255,.04);border-radius:14px;padding:12px 14px;margin-bottom:10px;border:1px solid rgba(255,255,255,.03)}}
.pm-msg.sent{{background:linear-gradient(135deg,var(--accent),var(--accent2));border:none;margin-left:24px;text-align:center;font-weight:600;font-size:13px}}
.pm-msg .label{{font-size:10px;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:1px}}
.chips{{display:flex;gap:5px;flex-wrap:wrap}}
.chip{{background:rgba(255,255,255,.06);border-radius:20px;padding:5px 12px;font-size:10px;color:#aaa;border:1px solid rgba(255,255,255,.04);transition:.2s}}
.chip.active{{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 0 15px rgba(0,153,255,.3)}}
.pm-bar{{display:flex;gap:8px;margin-top:12px}}
.pm-input{{flex:1;background:rgba(255,255,255,.04);border-radius:20px;padding:10px 14px;font-size:11px;color:var(--muted);border:1px solid rgba(255,255,255,.03)}}
.pm-send{{background:linear-gradient(135deg,var(--accent),var(--accent2));width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;box-shadow:0 0 20px rgba(0,153,255,.3)}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin:80px auto;max-width:700px}}
.stat{{text-align:center;padding:32px 16px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);backdrop-filter:blur(10px);transition:.3s}}
.stat:hover{{border-color:rgba(0,153,255,.3);transform:translateY(-4px);box-shadow:0 20px 40px rgba(0,0,0,.3)}}
.stat-num{{font-size:clamp(32px,5vw,48px);font-weight:900;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.stat-label{{font-size:13px;color:var(--muted);margin-top:4px;font-weight:500}}
.section{{padding:100px 0}}
.section-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(0,153,255,.08);border:1px solid rgba(0,153,255,.15);padding:6px 16px;border-radius:50px;font-size:12px;font-weight:600;color:var(--accent);margin-bottom:16px}}
.section-title{{font-size:clamp(32px,5vw,52px);font-weight:900;letter-spacing:-1.5px;margin-bottom:14px;line-height:1.1}}
.section-title .grad{{background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.section-sub{{color:var(--muted);font-size:17px;max-width:520px;line-height:1.6;margin:0 auto 50px}}
.text-center{{text-align:center}}
.features-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
@media(max-width:800px){{.features-grid{{grid-template-columns:1fr}}}}
.fcard{{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:36px 28px;backdrop-filter:blur(10px);transition:.4s;position:relative;overflow:hidden}}
.fcard::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent),var(--accent2),transparent);opacity:0;transition:.4s}}
.fcard:hover{{border-color:rgba(0,153,255,.2);transform:translateY(-6px);box-shadow:0 24px 48px rgba(0,0,0,.3)}}
.fcard:hover::before{{opacity:1}}
.fcard-icon{{width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,rgba(0,153,255,.12),rgba(123,47,242,.12));display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:20px}}
.fcard-title{{font-size:18px;font-weight:700;margin-bottom:8px}}
.fcard-desc{{font-size:14px;color:var(--muted);line-height:1.7}}
.steps-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;position:relative}}
@media(max-width:700px){{.steps-grid{{grid-template-columns:1fr}}}}
.steps-grid::before{{content:'';position:absolute;top:48px;left:16%;right:16%;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));opacity:.2}}
.step{{text-align:center;padding:40px 24px;position:relative}}
.step-num{{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;margin:0 auto 20px;box-shadow:0 8px 30px var(--glow);position:relative;z-index:1}}
.step-title{{font-size:20px;font-weight:700;margin-bottom:10px}}
.step-desc{{font-size:14px;color:var(--muted);line-height:1.7}}
.marquee-wrap{{overflow:hidden;padding:40px 0;border-top:1px solid var(--border);border-bottom:1px solid var(--border);margin:60px 0}}
.marquee{{display:flex;gap:24px;animation:scroll 25s linear infinite;width:max-content}}
.marquee .tag{{flex-shrink:0;font-size:16px;padding:12px 28px}}
@keyframes scroll{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}
.faq-list{{max-width:720px;margin:0 auto}}
.faq-item{{background:var(--card);border:1px solid var(--border);border-radius:16px;margin-bottom:10px;overflow:hidden;transition:.3s;backdrop-filter:blur(10px)}}
.faq-item:hover{{border-color:rgba(0,153,255,.15)}}
.faq-q{{padding:22px 28px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;font-weight:600;font-size:16px}}
.faq-q .icon{{width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.04);display:flex;align-items:center;justify-content:center;transition:.3s;font-size:14px;color:var(--muted);flex-shrink:0}}
.faq-item.open .faq-q .icon{{background:var(--accent);color:#fff;transform:rotate(45deg)}}
.faq-a{{max-height:0;overflow:hidden;transition:.4s ease;padding:0 28px;font-size:14px;color:var(--muted);line-height:1.7}}
.faq-item.open .faq-a{{max-height:200px;padding:0 28px 22px}}
.cta{{text-align:center;padding:100px 0;position:relative}}
.cta-box{{background:linear-gradient(135deg,rgba(0,153,255,.08),rgba(123,47,242,.08));border:1px solid rgba(0,153,255,.15);border-radius:32px;padding:60px 40px;backdrop-filter:blur(20px);position:relative;overflow:hidden}}
.cta-box::before{{content:'';position:absolute;inset:-2px;border-radius:32px;background:linear-gradient(135deg,var(--accent),var(--accent2),var(--accent3));z-index:-1;opacity:.15}}
.cta h2{{font-size:clamp(28px,4vw,44px);font-weight:900;margin-bottom:16px;letter-spacing:-1px}}
.cta p{{color:var(--muted);font-size:17px;margin-bottom:32px}}
footer{{padding:60px 0 30px;border-top:1px solid var(--border);text-align:center}}
.footer-logo{{font-size:28px;font-weight:900;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px}}
footer p{{color:var(--muted);font-size:13px;line-height:1.8}}
footer a{{color:var(--accent);text-decoration:none}}
.toast{{position:fixed;bottom:30px;right:30px;background:rgba(20,20,35,.95);border:1px solid var(--border);border-radius:16px;padding:16px 24px;display:flex;align-items:center;gap:12px;z-index:200;backdrop-filter:blur(20px);box-shadow:0 20px 40px rgba(0,0,0,.4);transform:translateY(120%);transition:.5s cubic-bezier(.16,1,.3,1);max-width:340px}}
.toast.show{{transform:translateY(0)}}
.toast-icon{{font-size:24px;flex-shrink:0}}
.toast-text{{font-size:13px;color:var(--muted);line-height:1.5}}
.toast-text strong{{color:var(--text);display:block;margin-bottom:2px}}
.toast-close{{background:none;border:none;color:var(--muted);cursor:pointer;font-size:18px;padding:4px;flex-shrink:0}}
.reveal{{opacity:0;transform:translateY(40px);transition:.8s cubic-bezier(.16,1,.3,1)}}
.reveal.visible{{opacity:1;transform:translateY(0)}}
/* ── CUSTOM SCROLLBAR ── */
::-webkit-scrollbar{{width:8px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px}}
::-webkit-scrollbar-thumb:hover{{background:var(--accent)}}

/* ── CUSTOM SCROLLBAR ── */
::-webkit-scrollbar{{width:8px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px}}
::-webkit-scrollbar-thumb:hover{{background:var(--accent)}}

@media(max-width:600px){{.nav-links a:not(.btn-glow){{display:none}}.stats{{grid-template-columns:1fr;gap:12px}}.hero{{padding:100px 0 40px}}.features-grid{{grid-template-columns:1fr}}.steps-grid{{grid-template-columns:1fr}}.steps-grid::before{{display:none}}}}
</style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="aurora"><div class="a1"></div><div class="a2"></div><div class="a3"></div></div>
<div class="noise"></div>


<nav>
<div class="nav-inner">
  <div class="logo">SaveVideoBot</div>
  <div class="nav-links">
    <a href="#features">Возможности</a>
    <a href="#how">Как работает</a>
    <a href="#faq">FAQ</a>
    <button onclick="toggleTheme()" class="theme-toggle" style="background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:50px;padding:8px 12px;cursor:pointer;font-size:16px;color:var(--text)">🌙</button>
    <a href="{BOT_LINK}" target="_blank" class="btn-glow">Запустить</a>
  </div>
</div>
</nav>


<section class="hero container">
  <div class="hero-chip reveal"><span class="dot"></span> Бот онлайн · Работает 24/7</div>
  <h1 class="reveal">
    <span class="line">Скачивай видео</span>
    <span class="line grad">из TikTok, Reels, Shorts и VK</span>
  </h1>
  <p class="hero-desc reveal">Просто отправь ссылку — получи видео за секунды. Без регистрации, без рекламы, без ограничений.</p>
  <div class="hero-btns reveal">
    <a href="{BOT_LINK}" target="_blank" class="btn-hero primary">Открыть в Telegram</a>
    <a href="#features" class="btn-hero secondary">Узнать больше ↓</a>
  </div>
  <div class="tags reveal">
    <span class="tag"><span class="emoji">🎵</span>TikTok</span>
    <span class="tag"><span class="emoji">📸</span>Instagram Reels</span>
    <span class="tag"><span class="emoji">▶️</span>YouTube Shorts</span>
    <span class="tag"><span class="emoji">💬</span>VK Клипы</span>
  </div>
  <div class="phone-section reveal">
    <div class="phone-wrap">
      <div class="phone">
        <div class="phone-notch"></div>
        <div class="phone-screen">
          <div class="pm-msg"><div class="pm-link" style="color:#888;font-size:12px">🔗 <span style="color:var(--accent)">tiktok.com/</span>@user/video/123...</div></div>
          <div class="pm-msg">
            <div class="label">Качество</div>
            <div class="chips">
              <span class="chip">360p</span>
              <span class="chip">480p</span>
              <span class="chip active">720p</span>
              <span class="chip">1080p</span>
            </div>
            <div class="label" style="margin-top:8px">Звук</div>
            <div class="chips">
              <span class="chip active">🔊 Со звуком</span>
              <span class="chip">🔇 Без звука</span>
            </div>
          </div>
          <div class="pm-msg sent">⬇️ Скачать видео</div>
          <div class="pm-bar">
            <div class="pm-input">Написать сообщение...</div>
            <div class="pm-send">➤</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="marquee-wrap">
  <div class="marquee">
    <span class="tag"><span class="emoji">🎵</span> TikTok</span>
    <span class="tag"><span class="emoji">📸</span> Instagram</span>
    <span class="tag"><span class="emoji">▶️</span> YouTube</span>
    <span class="tag"><span class="emoji">💬</span> VK</span>
    <span class="tag"><span class="emoji">🎮</span> Twitch Clips</span>
    <span class="tag"><span class="emoji">🐦</span> Twitter/X</span>
    <span class="tag"><span class="emoji">📌</span> Pinterest</span>
    <span class="tag"><span class="emoji">💼</span> LinkedIn</span>
    <span class="tag"><span class="emoji">🎵</span> TikTok</span>
    <span class="tag"><span class="emoji">📸</span> Instagram</span>
    <span class="tag"><span class="emoji">▶️</span> YouTube</span>
    <span class="tag"><span class="emoji">💬</span> VK</span>
    <span class="tag"><span class="emoji">🎮</span> Twitch Clips</span>
    <span class="tag"><span class="emoji">🐦</span> Twitter/X</span>
    <span class="tag"><span class="emoji">📌</span> Pinterest</span>
    <span class="tag"><span class="emoji">💼</span> LinkedIn</span>
  </div>
</div>

<div class="container">
  <div class="stats reveal">
    <div class="stat"><div class="stat-num" data-target="100000">0</div><div class="stat-label">Видео скачано</div></div>
    <div class="stat"><div class="stat-num" data-target="50000">0</div><div class="stat-label">Пользователей</div></div>
    <div class="stat"><div class="stat-num" data-target="99">0</div><div class="stat-label">% Аптайм</div></div>
  </div>
</div>

<section class="section container" id="features">
  <div class="text-center">
    <div class="section-badge reveal">✦ Возможности</div>
    <h2 class="section-title reveal">Всё для <span class="grad">идеального</span> скачивания</h2>
    <p class="section-sub reveal">Мощный бот с простым интерфейсом. Выбирай качество, звук — получай видео мгновенно.</p>
  </div>
  <div class="features-grid">
    <div class="fcard reveal">
      <div class="fcard-icon">🎬</div>
      <div class="fcard-title">HD Качество</div>
      <div class="fcard-desc">Скачивай в 360p, 480p, 720p или 1080p — выбирай разрешение под свои нужды.</div>
    </div>
    <div class="fcard reveal">
      <div class="fcard-icon">🔊</div>
      <div class="fcard-title">Со звуком / Без</div>
      <div class="fcard-desc">Одна кнопка — видео с аудио или без. Полный контроль над скачиванием.</div>
    </div>
    <div class="fcard reveal">
      <div class="fcard-icon">⚡</div>
      <div class="fcard-title">Молниеносно</div>
      <div class="fcard-desc">Серверная обработка за секунды. Никакого ожидания — результат сразу.</div>
    </div>
    <div class="fcard reveal">
      <div class="fcard-icon">🌐</div>
      <div class="fcard-title">Все платформы</div>
      <div class="fcard-desc">TikTok, Instagram, YouTube, VK, Twitter — одна ссылка, любое видео.</div>
    </div>
    <div class="fcard reveal">
      <div class="fcard-icon">🆓</div>
      <div class="fcard-title">100% Бесплатно</div>
      <div class="fcard-desc">Никаких подписок, лимитов, скрытых платежей. Просто пользуйся.</div>
    </div>
    <div class="fcard reveal">
      <div class="fcard-icon">🔒</div>
      <div class="fcard-title">Без регистрации</div>
      <div class="fcard-desc">Отправь ссылку — получи видео. Никаких аккаунтов и паролей.</div>
    </div>
  </div>
</section>

<section class="section container" id="how">
  <div class="text-center">
    <div class="section-badge reveal">✦ Как это работает</div>
    <h2 class="section-title reveal">Три <span class="grad">простых</span> шага</h2>
    <p class="section-sub reveal">От копирования ссылки до готового видео — буквально 10 секунд</p>
  </div>
  <div class="steps-grid">
    <div class="step reveal">
      <div class="step-num">1</div>
      <div class="step-title">Скопируй ссылку</div>
      <div class="step-desc">Найди видео в TikTok, Reels, Shorts или VK и скопируй ссылку на него.</div>
    </div>
    <div class="step reveal">
      <div class="step-num">2</div>
      <div class="step-title">Настрой параметры</div>
      <div class="step-desc">Выбери качество (360p–1080p) и нажми «Со звуком» или «Без звука».</div>
    </div>
    <div class="step reveal">
      <div class="step-num">3</div>
      <div class="step-title">Получи видео</div>
      <div class="step-desc">Нажми «Скачать» — готовое видео моментально приходит в Telegram.</div>
    </div>
  </div>
</section>

<section class="section container" id="faq">
  <div class="text-center">
    <div class="section-badge reveal">✦ FAQ</div>
    <h2 class="section-title reveal">Частые <span class="grad">вопросы</span></h2>
    <p class="section-sub reveal">Ответы на всё, что тебя может заинтересовать</p>
  </div>
  <div class="faq-list">
    <div class="faq-item reveal">
      <div class="faq-q" onclick="toggleFaq(this.parentElement)"><span>Бот бесплатный?</span><div class="icon">+</div></div>
      <div class="faq-a">Да, на 100%. Никаких подписок, лимитов и скрытых платежей. Полностью бесплатно и навсегда.</div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-q" onclick="toggleFaq(this.parentElement)"><span>Какие платформы поддерживаются?</span><div class="icon">+</div></div>
      <div class="faq-a">TikTok, Instagram Reels, YouTube Shorts, VK Клипы, Twitter/X и многие другие.</div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-q" onclick="toggleFaq(this.parentElement)"><span>Есть ли ограничение по размеру?</span><div class="icon">+</div></div>
      <div class="faq-a">Telegram ограничивает файлы до 50 МБ. Если видео больше — бот сообщит об этом.</div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-q" onclick="toggleFaq(this.parentElement)"><span>Можно скачать без звука?</span><div class="icon">+</div></div>
      <div class="faq-a">Конечно! Выбери «Без звука» при настройке — получишь чистое видео без аудиодорожки.</div>
    </div>
    <div class="faq-item reveal">
      <div class="faq-q" onclick="toggleFaq(this.parentElement)"><span>Бот работает 24/7?</span><div class="icon">+</div></div>
      <div class="faq-a">Да! Бот размещён на облачном сервере и работает круглосуточно, 365 дней в году.</div>
    </div>
  </div>
</section>

<section class="cta">
  <div class="container">
    <div class="cta-box reveal">
      <h2>Готов скачать <span class="grad">свое первое видео</span>?</h2>
      <p>Просто открой бота в Telegram и отправь ссылку</p>
      <a href="{BOT_LINK}" target="_blank" class="btn-hero primary">Запустить бота</a>
    </div>
  </div>
</section>

<footer>
  <div class="container">
    <div class="footer-logo">SaveVideoBot</div>
    <p>Сделано с любовью для удобного скачивания видео</p>
    <p style="margin-top:4px">{BOT_USERNAME} · Работает 24/7</p>
    <p style="margin-top:16px;font-size:11px;color:#444">© 2026 SaveVideoBot. Все права защищены.</p>
  </div>
</footer>

<div class="toast" id="toast">
  <div class="toast-icon">🚀</div>
  <div class="toast-text"><strong>Добро пожаловать!</strong>Попробуй бота прямо сейчас — это бесплатно.</div>
  <button class="toast-close" onclick="document.getElementById('toast').classList.remove('show')">×</button>
</div>

<script>
var canvas = document.getElementById('bg');
var ctx = canvas.getContext('2d');
var w, h, particles = [];
function resize() {{
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
}}
resize();
window.addEventListener('resize', resize);

function Particle() {{
  this.x = Math.random() * w;
  this.y = Math.random() * h;
  this.vx = (Math.random() - 0.5) * 0.3;
  this.vy = (Math.random() - 0.5) * 0.3;
  this.r = Math.random() * 1.5 + 0.5;
  this.a = Math.random() * 0.3 + 0.1;
}}
Particle.prototype.update = function() {{
  this.x += this.vx;
  this.y += this.vy;
  if (this.x < 0 || this.x > w) this.vx *= -1;
  if (this.y < 0 || this.y > h) this.vy *= -1;
}};
Particle.prototype.draw = function() {{
  ctx.beginPath();
  ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0,153,255,' + this.a + ')';
  ctx.fill();
}};

for (var i = 0; i < 80; i++) {{ particles.push(new Particle()); }}

function animate() {{
  ctx.clearRect(0, 0, w, h);
  for (var i = 0; i < particles.length; i++) {{
    particles[i].update();
    particles[i].draw();
    for (var j = i + 1; j < particles.length; j++) {{
      var dx = particles[i].x - particles[j].x;
      var dy = particles[i].y - particles[j].y;
      var d = Math.sqrt(dx * dx + dy * dy);
      if (d < 120) {{
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.strokeStyle = 'rgba(0,153,255,' + (0.08 * (1 - d / 120)) + ')';
        ctx.stroke();
      }}
    }}
  }}
  requestAnimationFrame(animate);
}}
animate();



var observer = new IntersectionObserver(function(entries) {{
  entries.forEach(function(e) {{
    if (e.isIntersecting) e.target.classList.add('visible');
  }});
}}, {{ threshold: 0.1 }});
document.querySelectorAll('.reveal').forEach(function(el) {{ observer.observe(el); }});

setTimeout(function() {{ document.getElementById('toast').classList.add('show'); }}, 2000);
setTimeout(function() {{ document.getElementById('toast').classList.remove('show'); }}, 8000);

function toggleFaq(el) {{ el.classList.toggle('open'); }}
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
}}
function toggleTheme() {{
  const html = document.documentElement;
  const isLight = html.dataset.theme === 'light';
  html.dataset.theme = isLight ? 'dark' : 'light';
  document.querySelector('.theme-toggle').textContent = isLight ? '🌙' : '☀️';
}}

var counters = document.querySelectorAll('.stat-num');
var cObserver = new IntersectionObserver(function(entries) {{
  entries.forEach(function(e) {{
    if (e.isIntersecting) {{
      var t = +e.target.dataset.target;
      var c = 0;
      var step = t / 60;
      var timer = setInterval(function() {{
        c += step;
        if (c >= t) {{ c = t; clearInterval(timer); }}
        if (t === 99) {{
          e.target.textContent = Math.floor(c) + '%';
        }} else {{
          e.target.textContent = (c / 1000).toFixed(0) + 'K+';
        }}
      }}, 20);
    }}
  }});
}}, {{ threshold: 0.5 }});
counters.forEach(function(el) {{ cObserver.observe(el); }});
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
