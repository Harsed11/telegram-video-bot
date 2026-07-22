import asyncio
import os
import re
import glob
import logging
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
import yt_dlp

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

dp = Dispatcher()
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

URL_REGEX = re.compile(r"https?://[^\s]+")

# Хранилище временных настроек пользователей
# {user_id: {"url", "quality", "audio", "qualities", "title", "formats"}}
user_settings = {}

QUALITY_PRESETS = ["1080", "720", "480", "360"]


class ConfigCallback(CallbackData, prefix="cfg"):
    action: str  # "quality", "audio", "download"
    value: str   # "1080", "720", "480", "360", "yes", "no", "start"


def get_available_qualities(formats: list) -> list[str]:
    heights = sorted(
        {f.get("height") for f in formats if f.get("height") and f.get("vcodec") not in (None, "none")},
        reverse=True,
    )
    if not heights:
        return ["720", "480", "360"]

    max_height = max(heights)
    available = [preset for preset in QUALITY_PRESETS if int(preset) <= max_height]
    return available or [str(max_height)]


def has_video(format_info: dict) -> bool:
    return format_info.get("vcodec") not in (None, "none")


def has_audio(format_info: dict) -> bool:
    return format_info.get("acodec") not in (None, "none")


def pick_format_selector(formats: list, quality: str, with_audio: bool) -> tuple[str, bool]:
    """
    Возвращает format selector для yt-dlp и флаг, нужно ли удалять звук после скачивания.
    """
    target_height = int(quality)
    video_formats = [f for f in formats if has_video(f) and f.get("height")]

    if not video_formats:
        if with_audio:
            return "best", False
        return "best", True

    def height_rank(fmt: dict) -> tuple[int, int]:
        height = fmt["height"]
        if height <= target_height:
            return (0, -height)
        return (1, height)

    if with_audio:
        combined = [f for f in video_formats if has_audio(f)]
        if combined:
            chosen = min(combined, key=height_rank)
            return str(chosen["format_id"]), False

        video_only = [f for f in video_formats if not has_audio(f)]
        audio_only = [f for f in formats if has_audio(f) and not has_video(f)]
        if video_only and audio_only:
            video_fmt = min(video_only, key=height_rank)
            audio_fmt = max(audio_only, key=lambda f: f.get("abr") or f.get("tbr") or 0)
            return f"{video_fmt['format_id']}+{audio_fmt['format_id']}", False

        chosen = min(video_formats, key=height_rank)
        return str(chosen["format_id"]), False

    video_only = [f for f in video_formats if not has_audio(f)]
    if video_only:
        chosen = min(video_only, key=height_rank)
        return str(chosen["format_id"]), False

    chosen = min(video_formats, key=height_rank)
    return str(chosen["format_id"]), True


def get_ffmpeg_path() -> str | None:
    path = shutil.which("ffmpeg")
    if path:
        return path

    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def strip_audio_sync(input_path: str) -> str:
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        raise RuntimeError(
            "ffmpeg не найден — установите ffmpeg или выполните: pip install imageio-ffmpeg"
        )

    base, _ = os.path.splitext(input_path)
    output_path = f"{base}_muted.mp4"
    result = subprocess.run(
        [ffmpeg_path, "-y", "-i", input_path, "-c:v", "copy", "-an", output_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "ffmpeg не смог удалить звук")

    os.remove(input_path)
    return output_path


def get_settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    settings = user_settings.get(user_id, {"quality": "720", "audio": True, "qualities": QUALITY_PRESETS[:3]})
    q = settings["quality"]
    audio = settings["audio"]
    qualities = settings.get("qualities", QUALITY_PRESETS[:3])

    quality_buttons = [
        InlineKeyboardButton(
            text=f"{'✅ ' if q == preset else ''}{preset}p",
            callback_data=ConfigCallback(action="quality", value=preset).pack()
        )
        for preset in qualities
    ]

    btn_audio_yes = InlineKeyboardButton(
        text=f"{'✅ ' if audio else ''}🔊 Со звуком",
        callback_data=ConfigCallback(action="audio", value="yes").pack()
    )
    btn_audio_no = InlineKeyboardButton(
        text=f"{'✅ ' if not audio else ''}🔇 Без звука",
        callback_data=ConfigCallback(action="audio", value="no").pack()
    )

    btn_download = InlineKeyboardButton(
        text="⬇️ Скачать видео",
        callback_data=ConfigCallback(action="download", value="start").pack()
    )

    rows = [quality_buttons[i:i + 3] for i in range(0, len(quality_buttons), 3)]
    rows.append([btn_audio_yes, btn_audio_no])
    rows.append([btn_download])

    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 <b>Привет! Я бот для скачивания видео.</b>\n\n"
        "Отправь мне ссылку на видео из <b>TikTok</b>, <b>YouTube Shorts</b>, <b>Reels</b> или <b>VK</b>, "
        "выбери качество и звук!"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
        "1. Отправь ссылку на видео.\n"
        "2. Выбери качество (1080p, 720p, 480p, 360p — доступные для видео) и звук (со звуком / без звука).\n"
        "3. Нажми кнопку <b>«Скачать видео»</b>.\n"
    )



@dp.message(F.text)
async def handle_url(message: types.Message):
    match = URL_REGEX.search(message.text)
    if not match:
        await message.answer("⚠️ Пожалуйста, отправь мне ссылку на видео.")
        return

    url = match.group(0)
    user_id = message.from_user.id

    status_msg = await message.answer("🔍 <b>Анализирую видео...</b>")

    try:
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, extract_video_info_sync, url)
        formats = info.get("formats") or []
        qualities = get_available_qualities(formats)
        default_quality = qualities[0] if qualities else "720"
        title = info.get("title", "Видео")
        if len(title) > 100:
            title = title[:97] + "..."

        user_settings[user_id] = {
            "url": url,
            "quality": default_quality,
            "audio": True,
            "qualities": qualities,
            "title": title,
            "formats": formats,
        }

        await status_msg.edit_text(
            f"⚙️ <b>Выбери параметры для скачивания:</b>\n\n"
            f"🎬 {title}\n"
            f"📐 Доступные качества: <b>{', '.join(f'{q}p' for q in qualities)}</b>",
            reply_markup=get_settings_keyboard(user_id)
        )
    except yt_dlp.utils.DownloadError as de:
        logging.warning(f"Info extraction error: {de}")
        user_settings[user_id] = {
            "url": url,
            "quality": "720",
            "audio": True,
            "qualities": ["1080", "720", "480"],
            "title": "Видео",
            "formats": [],
        }
        await status_msg.edit_text(
            "⚙️ <b>Выбери параметры для скачивания:</b>\n\n"
            "⚠️ Не удалось определить доступные форматы — показаны стандартные варианты.",
            reply_markup=get_settings_keyboard(user_id)
        )
    except Exception as e:
        logging.error(f"Error extracting video info: {e}", exc_info=True)
        await status_msg.edit_text("❌ <b>Не удалось обработать ссылку.</b> Проверьте URL и попробуйте снова.")



@dp.callback_query(ConfigCallback.filter())
async def handle_config_callback(callback: types.CallbackQuery, callback_data: ConfigCallback):
    user_id = callback.from_user.id

    if user_id not in user_settings:
        await callback.answer("⚠️ Ссылка устарела. Отправь ссылку на видео заново.", show_alert=True)
        return

    action = callback_data.action
    value = callback_data.value

    if action == "quality":
        user_settings[user_id]["quality"] = value
        settings = user_settings[user_id]
        await callback.message.edit_text(
            f"⚙️ <b>Выбери параметры для скачивания:</b>\n\n"
            f"🎬 {settings.get('title', 'Видео')}\n"
            f"📐 Качество: <b>{value}p</b> | {'🔊 Со звуком' if settings['audio'] else '🔇 Без звука'}",
            reply_markup=get_settings_keyboard(user_id),
        )
        await callback.answer(f"Качество: {value}p")

    elif action == "audio":
        user_settings[user_id]["audio"] = (value == "yes")
        settings = user_settings[user_id]
        audio_label = "Со звуком" if settings["audio"] else "Без звука"
        await callback.message.edit_text(
            f"⚙️ <b>Выбери параметры для скачивания:</b>\n\n"
            f"🎬 {settings.get('title', 'Видео')}\n"
            f"📐 Качество: <b>{settings['quality']}p</b> | {'🔊' if settings['audio'] else '🔇'} {audio_label}",
            reply_markup=get_settings_keyboard(user_id),
        )
        await callback.answer(audio_label)

    elif action == "download":
        await callback.answer()
        settings = user_settings[user_id]
        url = settings["url"]
        quality = settings["quality"]
        audio = settings["audio"]
        formats = settings.get("formats", [])

        logging.info(
            "Download request user=%s quality=%sp audio=%s formats=%s",
            user_id, quality, audio, len(formats),
        )

        status_msg = await callback.message.edit_text(
            f"⏳ <b>Скачиваю видео...</b>\n"
            f"Качество: <b>{quality}p</b> | {'🔊 Со звуком' if audio else '🔇 Без звука'}"
        )

        base_prefix = f"video_{user_id}_{callback.message.message_id}"
        output_template = str(DOWNLOAD_DIR / f"{base_prefix}.%(ext)s")

        try:
            loop = asyncio.get_running_loop()
            info = await loop.run_in_executor(
                None, download_video_sync, url, output_template, quality, audio, formats
            )

            search_pattern = str(DOWNLOAD_DIR / f"{base_prefix}.*")
            downloaded_files = glob.glob(search_pattern)

            if not downloaded_files:
                await status_msg.edit_text("❌ <b>Не удалось скачать видео.</b>\nФайл слишком большой или недоступен.")
                return

            target_file = downloaded_files[0]

            if not audio:
                target_file = await loop.run_in_executor(None, strip_audio_sync, target_file)

            actual_height = info.get("height")
            if not actual_height and info.get("requested_formats"):
                for fmt in info["requested_formats"]:
                    if has_video(fmt) and fmt.get("height"):
                        actual_height = fmt["height"]
                        break
            quality_label = f"{actual_height}p" if actual_height else f"{quality}p"
            title = info.get("title", "Видео")
            if len(title) > 200:
                title = title[:197] + "..."

            audio_status = "🔊 Со звуком" if audio else "🔇 Без звука"
            caption = f"🎬 <b>{title}</b>\n⚙️ Качество: <b>{quality_label}</b> | {audio_status}"

            await status_msg.edit_text("📤 <b>Отправляю видео...</b>")

            video = FSInputFile(target_file)
            await callback.message.answer_video(video=video, caption=caption)
            await status_msg.delete()

        except RuntimeError as re_err:
            logging.warning(f"RuntimeError: {re_err}")
            await status_msg.edit_text(f"❌ <b>Ошибка:</b> {re_err}")
        except yt_dlp.utils.DownloadError as de:
            logging.warning(f"DownloadError: {de}")
            await status_msg.edit_text("❌ <b>Ошибка при скачивании.</b> Проверьте ссылку или попробуйте другое качество.")
        except Exception as e:
            logging.error(f"Error downloading: {e}", exc_info=True)
            await status_msg.edit_text("❌ <b>Произошла ошибка при обработке видео.</b>")
        finally:
            search_pattern = str(DOWNLOAD_DIR / f"{base_prefix}.*")
            for f in glob.glob(search_pattern):
                try:
                    os.remove(f)
                except Exception:
                    pass
            muted_pattern = str(DOWNLOAD_DIR / f"{base_prefix}_muted.mp4")
            if os.path.exists(muted_pattern):
                try:
                    os.remove(muted_pattern)
                except Exception:
                    pass


def download_video_sync(
    url: str,
    output_template: str,
    quality: str,
    audio: bool,
    formats: list | None = None,
) -> dict:
    if not formats:
        info = extract_video_info_sync(url)
        formats = info.get("formats") or []

    if formats:
        format_selector, _ = pick_format_selector(formats, quality, audio)
    else:
        format_selector = build_format_string(quality, audio)

    logging.info("Using format selector: %s (quality=%sp, audio=%s)", format_selector, quality, audio)

    ydl_opts = {
        **get_base_ydl_opts(output_template),
        "format": format_selector,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=True)


def build_format_string(quality: str, audio: bool) -> str:
    height = quality
    if audio:
        return (
            f"best[height<={height}][ext=mp4]/"
            f"bestvideo[height<={height}]+bestaudio/"
            f"best[height<={height}]"
        )
    return (
        f"bestvideo[height<={height}][ext=mp4]/"
        f"best[height<={height}][ext=mp4]/"
        f"best[height<={height}]"
    )


def get_base_ydl_opts(output_template: str) -> dict:
    return {
        "outtmpl": output_template,
        "max_filesize": 50 * 1024 * 1024,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
        "socket_timeout": 30,
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }


def extract_video_info_sync(url: str) -> dict:
    ydl_opts = {
        **get_base_ydl_opts(str(DOWNLOAD_DIR / "tmp_%(id)s.%(ext)s")),
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


async def main():
    if not TOKEN or TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("❌ Ошибка: Укажи корректный BOT_TOKEN в файле .env!")
        return

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    print("🚀 Бот успешно запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
