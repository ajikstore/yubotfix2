__MODULES__ = "Download"
__HELP__ = """<blockquote>Command Help **Downloads**</blockquote>

<blockquote expandable>        <u>**Download media from anywhere**</u>
    <u>**You can download any media from twitter, instagram, pinterest, tiktok**</u>
        `{0}dl` (url/query)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

import re
import traceback
from itertools import islice
from typing import List
from uuid import uuid4

from pyrogram.types import InputMediaPhoto, InputMediaVideo

from config import API_BOTCHAX
from kelra import bot
from kelra.database import state
from kelra.helpers import CMD, ButtonUtils, Emoji, Tools
from kelra.logger import logger


def chunk_media_group(media_list: list, chunk_size: int = 4) -> List[list]:
    """Split media list into chunks of specified size"""
    media_chunks = []
    iterator = iter(media_list)
    while chunk := list(islice(iterator, chunk_size)):
        media_chunks.append(chunk)
    return media_chunks


def detect_platform(url_or_query):
    """Detect platform based on URL or return 'search' for queries"""
    if not url_or_query.startswith("https://"):
        # Check if it's a tiktok search query
        return "tiktok_search"

    url_patterns = {"twitter": [r"twitter\.com", r"x\.com"], "instagram": [r"instagram\.com"], "pinterest": [r"pinterest\.com", r"pin\.it"], "tiktok": [r"tiktok\.com", r"vt\.tiktok\.com"]}

    for platform, patterns in url_patterns.items():
        for pattern in patterns:
            if re.search(pattern, url_or_query, re.IGNORECASE):
                return platform

    return "pinterest_search"  # Default untuk query non-tiktok


@CMD.UBOT("dl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    arg = client.get_text(message)

    if not arg:
        return await message.reply(
            f"{em.gagal}<b>Please give URL or search query!!\n"
            f"Supported platforms: Twitter/X, Instagram, Pinterest, TikTok\n"
            f"Example: `{message.text.split()[0]} https://x.com/user/status/123` or `{message.text.split()[0]} video lucu`</b>"
        )

    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    platform = detect_platform(arg)

    await proses.edit(f"<blockquote>{em.proses}**Detecting platform: {platform.replace('_', ' ').title()}...**</blockquote>")

    try:
        if platform == "twitter":
            await handle_twitter(client, message, proses, arg, em)
        elif platform == "instagram":
            await handle_instagram(client, message, proses, arg, em)
        elif platform == "pinterest":
            await handle_pinterest_url(client, message, proses, arg, em)
        elif platform == "tiktok":
            await handle_tiktok_url(client, message, proses, arg, em)
        elif platform == "tiktok_search":
            await handle_tiktok_search(client, message, proses, arg, em)
        elif platform == "pinterest_search":
            await handle_pinterest_search(client, message, proses, arg, em)
        else:
            await proses.edit(f"<blockquote>{em.gagal}**Platform not supported or invalid URL**</blockquote>")

    except Exception as er:
        logger.error(f"<blockquote>dl: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR:** {str(er)}</blockquote>")


async def handle_twitter(client, message, proses, arg, em):
    await proses.edit(f"<blockquote>{em.proses}**Processing Twitter/X link...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/download/twitter2?url={arg}&apikey={API_BOTCHAX}"
    response = await Tools.fetch.get(url)

    if response.status_code != 200:
        return await proses.edit(f"<blockquote>{em.gagal}**Request failed with status code {response.status_code}**</blockquote>")

    data = response.json()
    if not data.get("result"):
        return await proses.edit(f"<blockquote>{em.gagal}**No result data in response**</blockquote>")

    result = data["result"]
    media_urls = result.get("mediaURLs", [])
    caption = result.get("text", "")

    if not media_urls:
        return await proses.edit(f"<blockquote>{em.gagal}**No media found in the tweet**</blockquote>")

    await proses.edit(f"<blockquote>{em.proses}**Preparing media for sending...**</blockquote>")
    media_group = []

    for url in media_urls:
        if url.endswith((".mp4", ".MP4")):
            media = await Tools.get_media_data(url, "mp4")
            media_group.append(InputMediaVideo(media=media, caption=caption if len(media_group) == 0 else ""))
        else:
            media = await Tools.get_media_data(url, "jpg")
            media_group.append(InputMediaPhoto(media=media, caption=caption if len(media_group) == 0 else ""))

    if media_group:
        await proses.delete()
        await client.send_media_group(chat_id=message.chat.id, media=media_group)
    else:
        await proses.edit(f"<blockquote>{em.gagal}**Failed to prepare media for sending**</blockquote>")


async def handle_instagram(client, message, proses, arg, em):
    await proses.edit(f"<blockquote>{em.proses}**Processing Instagram link...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/dowloader/igdowloader?url={arg}&apikey={API_BOTCHAX}"
    response = await Tools.fetch.get(url)

    if response.status_code != 200:
        return await proses.edit(f"<blockquote>{em.gagal}**Request failed with status code {response.status_code}**</blockquote>")

    data = response.json()
    if not data.get("result"):
        return await proses.edit(f"<blockquote>{em.gagal}**No result data in response**</blockquote>")

    media_urls = data.get("result", [])
    if not media_urls:
        return await proses.edit(f"<blockquote>{em.gagal}**No media found in the instagram link**</blockquote>")

    await proses.edit(f"<blockquote>{em.proses}**Preparing media for sending...**</blockquote>")
    media_group = []

    for X in media_urls:
        url = X["url"]
        type_ = Tools.extract_filename(url)
        if type_.endswith((".jpg", ".JPEG")):
            media = await Tools.get_media_data(url, "jpg")
            media_group.append(InputMediaPhoto(media=media))
        else:
            media = await Tools.get_media_data(url, "mp4")
            media_group.append(InputMediaVideo(media=media))

    if not media_group:
        return await proses.edit(f"<blockquote>{em.gagal}**Failed to prepare media for sending**</blockquote>")

    media_chunks = chunk_media_group(media_group)
    await proses.delete()

    for i, chunk in enumerate(media_chunks, 1):
        try:
            await client.send_media_group(chat_id=message.chat.id, media=chunk)
            return await message.reply(f"<blockquote>{em.sukses}**Successfully sent {len(media_chunks)} media.**</blockquote>")
        except Exception as chunk_error:
            logger.error(f"Error sending chunk {i}: {str(chunk_error)}")
            return await message.reply(f"<blockquote>{em.gagal}**Error sending media group {i}:** {str(chunk_error)}</blockquote>")


async def handle_pinterest_url(client, message, proses, arg, em):
    await proses.edit(f"<blockquote>{em.proses}**Processing Pinterest URL...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/download/pinterest?url={arg}&apikey={API_BOTCHAX}"
    response = await Tools.fetch.get(url)

    if response.status_code == 200:
        data = response.json()
        result = data.get("result", {}).get("data", {})

        if result.get("media_type") == "image":
            await message.reply_photo(result["image"], caption=result["title"] or "")
        elif result.get("media_type") == "video/mp4":
            await message.reply_video(result["video"], caption=result["title"] or "")

        return await proses.delete()
    else:
        return await proses.edit(f"<blockquote>{em.gagal}**Failed to download from Pinterest URL.**</blockquote>")


async def handle_pinterest_search(client, message, proses, prompt, em):
    await proses.edit(f"<blockquote>{em.proses}**Searching Pinterest for: {prompt}...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/search/pinterest?text1={prompt}&apikey={API_BOTCHAX}"
    response = await Tools.fetch.get(url)

    if response.status_code == 200:
        data = response.json()
        uniq = f"{str(uuid4())}"
        state.set(uniq.split("-")[0], uniq.split("-")[0], data["result"])

        inline = await ButtonUtils.send_inline_bot_result(
            message,
            message.chat.id,
            bot.me.username,
            f"inline_pinsearch {uniq.split('-')[0]}",
        )
        if inline:
            return await proses.delete()

    return await proses.edit(f"<blockquote>{em.gagal}**No images were found for these keywords!**</blockquote>")


async def handle_tiktok_url(client, message, proses, arg, em):
    await proses.edit(f"<blockquote>{em.proses}**Processing TikTok URL...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/dowloader/tiktok?url={arg}&apikey={API_BOTCHAX}"
    try:
        response = await Tools.fetch.get(url)
        if response.status_code == 200:
            data = response.json()["result"]
            state.set(client.me.id, "result_ttdownload", data)
            state.set(client.me.id, "idm_ttdownload", id(message))
            inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, "inline_ttdownload")
            if inline:
                return await proses.delete()
        else:
            return await proses.edit(f"<blockquote>{em.gagal}**Please try again {response.status_code}**</blockquote>")

    except Exception as er:
        logger.error(f"tiktok_dl: {traceback.format_exc()}")
        return await proses.edit(f"<blockquote>{em.gagal}**An error: `{str(er)}`**</blockquote>")


async def handle_tiktok_search(client, message, proses, arg, em):
    await proses.edit(f"<blockquote>{em.proses}**Searching TikTok for: {arg}...**</blockquote>")

    url = f"https://api.botcahx.eu.org/api/search/tiktoks?query={arg}&apikey={API_BOTCHAX}"
    try:
        response = await Tools.fetch.get(url)
        uniq = f"{str(uuid4())}"
        if response.status_code == 200:
            data = response.json()["result"]
            if len(data["data"]) == 0:
                return await proses.edit(f"<blockquote>{em.gagal}**Try another word, no videos found `{arg}`**</blockquote>")
            state.set(client.me.id, uniq.split("-")[0], data["data"])
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                message.chat.id,
                bot.me.username,
                f"inline_ttsearch {uniq.split('-')[0]}",
            )
            if inline:
                await proses.delete()
            return
        else:
            return await proses.edit(f"<blockquote>{em.gagal}**Please try again {response.status_code}**</blockquote>")
    except Exception as er:
        logger.error(f"tiktok_search: {traceback.format_exc()}")
        return await proses.edit(f"<blockquote>{em.gagal}**An error: `{str(er)}`**</blockquote>")
