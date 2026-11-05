import os
import shutil
import traceback

import aiofiles
import aiohttp
from pyrogram.types import InputMediaPhoto

from config import API_MAELYN, COOKIE_BING
from kelra.helpers import CMD, Emoji
from kelra.logger import logger

__MODULES__ = "Bingai"
__HELP__ = """<blockquote>Command BingAI</blockquote>

<blockquote expandable>
Generate image:  
<code>{0}genai (prompt)</code>  
<code>{0}bingai (prompt)</code>
</blockquote>

<b>{1}</b>
"""
__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

# ============================
# LIST KATA BERBAHAYA (auto sanitasi)
# ============================
BLOCK_WORDS = {
    "nsfw": "artistic style",
    "naked": "bare skin",
    "nude": "bare skin",
    "sex": "romantic aesthetic",
    "sexy": "attractive",
    "hentai": "anime art style",
    "boobs": "chest",
    "ass": "hips",
    "tits": "chest",
    "porn": "sensual style",
    "lewd": "suggestive aesthetic",
}

def sanitize_prompt(prompt: str):
    lowered = prompt.lower()
    for bad, rep in BLOCK_WORDS.items():
        if bad in lowered:
            prompt = prompt.replace(bad, rep)
            prompt = prompt.replace(bad.capitalize(), rep)
    return prompt


# ============================
# GENERATE BING (Normal)
# ============================
async def bing_generate(prompt: str):
    url = "https://api.maelyn.sbs/api/bing/createimage"
    headers = {"mg-apikey": API_MAELYN}
    params = {"cookie": COOKIE_BING, "prompt": prompt, "aspectRatio": "1:1"}

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, params=params) as r:
                if r.status != 200:
                    logger.warning(f"BING API STATUS {r.status}")
                    return None

                data = await r.json()
                result = data.get("result")

                if isinstance(result, list):
                    valid = [u for u in result if isinstance(u, str) and u.startswith("http")]
                    return valid if valid else None
                return None
    except Exception as e:
        logger.error(f"BING ERROR: {e}")
        return None


# ============================
# FALLBACK (FLUX MODEL BEBAS FILTER)
# ============================
async def flux_generate(prompt: str):
    url = "https://api.maelyn.sbs/api/flux"
    headers = {"mg-apikey": API_MAELYN}
    params = {"prompt": prompt}

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, params=params) as r:
                if r.status != 200:
                    logger.warning(f"FLUX API STATUS {r.status}")
                    return None

                data = await r.json()
                result = data.get("result")

                if isinstance(result, list):
                    valid = [u for u in result if u.startswith("http")]
                    return valid
                return None
    except Exception as e:
        logger.error(f"FLUX ERROR: {e}")
        return None


# ============================
# DOWNLOAD GAMBAR
# ============================
async def download_images(folder, urls):
    os.makedirs(folder, exist_ok=True)
    paths = []

    async with aiohttp.ClientSession() as s:
        for url in urls:
            if not url.startswith("http"):
                logger.warning(f"INVALID URL SKIPPED: {url}")
                continue

            file_path = os.path.join(folder, f"gen_{len(paths)+1}.jpg")

            try:
                async with s.get(url) as r:
                    if r.status == 200:
                        async with aiofiles.open(file_path, "wb") as f:
                            await f.write(await r.read())
                        paths.append(file_path)
            except Exception as e:
                logger.error(f"DOWNLOAD ERROR: {e}")

            if len(paths) == 4:
                break

    return paths


# ============================
# MAIN HANDLER
# ============================
async def bing_ai_handler(client, message):
    emo = Emoji(client)
    await emo.get()

    raw = client.get_text(message)
    if not raw:
        return await message.reply(f"{emo.gagal} <b>Masukkan prompt!</b>")

    prompt = sanitize_prompt(raw)

    pros = await message.reply(f"{emo.proses} <b>Generate:</b> <code>{raw}</code>")

    folder = f"downloads/{client.me.id}/"

    try:
        # 1️⃣ Coba dulu pakai Bing
        result = await bing_generate(prompt)

        # 2️⃣ Kalau diblokir → langsung switch ke FLUX
        if not result:
            logger.warning("BING BLOCKED → FLUX FALLBACK")
            result = await flux_generate(prompt)

        if not result:
            return await pros.edit(f"{emo.gagal} <b>Gagal generate gambar.</b>")

        imgs = await download_images(folder, result)

        media = [
            InputMediaPhoto(media=p, caption=f"{emo.sukses} <b>Generated!</b>")
            for p in imgs
        ]

        await client.send_media_group(
            chat_id=message.chat.id,
            media=media,
            reply_to_message_id=message.id,
        )

        await pros.delete()

    except Exception as e:
        logger.error(traceback.format_exc())
        await pros.edit(
            f"{emo.gagal} <b>Error:</b> <code>{e}</code>"
        )

    finally:
        if os.path.exists(folder):
            shutil.rmtree(folder)


# ============================
# COMMANDS
# ============================
@CMD.UBOT("genai")
async def _(c, m):
    await bing_ai_handler(c, m)

@CMD.UBOT("bingai")
async def _(c, m):
    await bing_ai_handler(c, m)
