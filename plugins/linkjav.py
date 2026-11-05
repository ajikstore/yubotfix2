__MODULES__ = "XnxxRandom"
__HELP__ = """<blockquote>Command Help JavRandom**</blockquote>

<blockquote expandable><u>**Mengambil link streaming okep**</u>
    <u>**random video**</u>
        `{0}getjav` `{0}getbarat`
        `{0}getindo` `{0}getviona` (url)</blockquote>
<b>   {1}</b>
"""

__CATEGORY__ = "ᴛᴏᴏʟs <emoji id=5435961551871813164>🛠</emoji>"

import traceback
import random
import httpx
import os
import asyncio

from kelra.helpers import CMD, Emoji
from kelra.logger import logger
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def remux_video(input_path, output_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-c", "copy",
        "-movflags", "+faststart",
        output_path
    ]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.communicate()


async def download_and_send(client, message, proses, search_query):
    em = Emoji(client)
    await em.get()

    try:
        api_url = f"https://api.wannnv.web.id/search/xnxx?q={search_query}"

        async with httpx.AsyncClient(timeout=60) as session:
            res = await session.get(api_url)
            res.raise_for_status()
            api = res.json()

        results = api.get("result", [])
        if not results:
            return await proses.edit(f"<blockquote>{em.gagal} Tidak ada hasil untuk: <code>{search_query}</code></blockquote>")

        data = random.choice(results)
        title = data.get("title", "N/A")
        link = data.get("link")

        await proses.edit(f"<blockquote>{em.proses} Mengunduh video: <code>{title}</code></blockquote>")

        download_api = f"https://api.wannnv.web.id/download/xnxx?url={link}"

        async with httpx.AsyncClient(timeout=120) as session:
            dl_res = await session.get(download_api)
            dl_res.raise_for_status()
            dl_data = dl_res.json()
            video_url = dl_data.get("result", {}).get("files", {}).get("high")

        if not video_url:
            return await proses.edit(f"<blockquote>{em.gagal} Gagal mendapatkan URL video dari API!</blockquote>")

        video_path = "downloads/xnxx_temp.mp4"
        remuxed_path = "downloads/xnxx_fixed.mp4"

        async with httpx.AsyncClient(timeout=120) as session:
            async with session.stream("GET", video_url) as resp:
                resp.raise_for_status()
                with open(video_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(1024 * 256):
                        f.write(chunk)

        await remux_video(video_path, remuxed_path)

        caption = (
            f"<blockquote expandable>{em.sukses} <b>{title}</b>\n"
            f"{em.uptime} Views: <code>{data.get('views', 'N/A')}</code>\n"
            f"{em.owner} Duration: <code>{data.get('duration', 'N/A')}</code>\n"
            f"🔗 <a href='{link}'>Source</a></blockquote>"
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏪ Previous", callback_data=f"getjav|{search_query}"),
                InlineKeyboardButton("⏩ Next", callback_data=f"getjav|{search_query}")
            ]
        ])

        await client.send_video(
            chat_id=message.chat.id,
            video=remuxed_path,
            caption=caption,
            reply_markup=buttons,
            reply_to_message_id=message.id,
            supports_streaming=False
        )

        await proses.delete()

        for file in [video_path, remuxed_path]:
            if os.path.exists(file):
                os.remove(file)

    except Exception as e:
        logger.error(f"XNXX GETJAV Error: {traceback.format_exc()}")
        await proses.edit(f"{em.gagal} Error:\n<code>{e}</code>")
        for file in ["downloads/xnxx_temp.mp4", "downloads/xnxx_fixed.mp4"]:
            if os.path.exists(file):
                os.remove(file)


@CMD.UBOT("getjav")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    keywords = ["jav", "japanese", "uncensored", "japan teen", "japan hd", "japan school", "jav squirt", "jav piston"]
    search_query = random.choice(keywords)

    proses = await message.reply(f"<blockquote>{em.proses} Mencari video untuk: <code>{search_query}</code>...</blockquote>")
    await download_and_send(client, message, proses, search_query)

@CMD.UBOT("getviona")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    keywords = ["asian"]
    search_query = random.choice(keywords)

    proses = await message.reply(f"<blockquote>{em.proses} Mencari video untuk: <code>{search_query}</code>...</blockquote>")
    await download_and_send(client, message, proses, search_query)

@CMD.UBOT("getindo")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    keywords = ["indo", "sepong", "indo viral", "colmek", "wot", "ngewe", "indo muncrat", "nyepong", "ngentot"]
    search_query = random.choice(keywords)

    proses = await message.reply(f"<blockquote>{em.proses} Mencari video untuk: <code>{search_query}</code>...</blockquote>")
    await download_and_send(client, message, proses, search_query)

@CMD.UBOT("getbarat")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    keywords = ["teen", "big dick", "squat", "compilation", "ride", "riding", "ebony", "latina", "bbc"]
    search_query = random.choice(keywords)

    proses = await message.reply(f"<blockquote>{em.proses} Mencari video untuk: <code>{search_query}</code>...</blockquote>")
    await download_and_send(client, message, proses, search_query)

@CMD.CALLBACK("getjav")
async def _(client, callback_query):
    em = Emoji(client)
    await em.get()

    search_query = callback_query.data.split("|", 1)[1]

    await callback_query.answer(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>", show_alert=False)

    proses = await callback_query.message.reply(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>")
    await download_and_send(client, callback_query.message, proses, search_query)

    try:
        await callback_query.message.delete()
    except:
        pass

CMD.CALLBACK("getviona")
async def _(client, callback_query):
    em = Emoji(client)
    await em.get()

    search_query = callback_query.data.split("|", 1)[1]

    await callback_query.answer(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>", show_alert=False)

    proses = await callback_query.message.reply(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>")
    await download_and_send(client, callback_query.message, proses, search_query)

    try:
        await callback_query.message.delete()
    except:
        pass

@CMD.CALLBACK("getindo")
async def _(client, callback_query):
    em = Emoji(client)
    await em.get()

    search_query = callback_query.data.split("|", 1)[1]

    await callback_query.answer(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>", show_alert=False)

    proses = await callback_query.message.reply(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>")
    await download_and_send(client, callback_query.message, proses, search_query)

    try:
        await callback_query.message.delete()
    except:
        pass

@CMD.CALLBACK("getbarat")
async def _(client, callback_query):
    em = Emoji(client)
    await em.get()

    search_query = callback_query.data.split("|", 1)[1]

    await callback_query.answer(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>", show_alert=False)

    proses = await callback_query.message.reply(f"<blockquote>{em.proses} Mengambil video baru...</blockquote>")
    await download_and_send(client, callback_query.message, proses, search_query)

    try:
        await callback_query.message.delete()
    except:
        pass
