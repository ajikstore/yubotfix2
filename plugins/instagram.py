__MODULES__ = "Instadl"
__HELP__ = """<blockquote>Command Help **Instadl**</blockquote>

<blockquote expandable>    <u>**Download media from instagram**</u>
        `{0}instadl` (url)</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

import traceback
from itertools import islice
from typing import List

from pyrogram.types import InputMediaPhoto, InputMediaVideo

from config import API_BOTCHAX
from kelra.helpers import CMD, Emoji, Tools
from kelra.logger import logger


def chunk_media_group(media_list: list, chunk_size: int = 4) -> List[list]:
    """Split media list into chunks of specified size"""
    media_chunks = []
    iterator = iter(media_list)
    while chunk := list(islice(iterator, chunk_size)):
        media_chunks.append(chunk)
    return media_chunks


@CMD.UBOT("instadl|igdl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    arg = client.get_text(message)

    if not arg:
        return await message.reply(
            f"{em.gagal}<b>Please give word or links!!\nExample: `{message.text.split()[0]} https://www.instagram.com/p/DFf2z72yBEq/?utm_source=ig_web_copy_link`</b>"
        )

    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    if not arg.startswith("https://"):
        return await proses.edit(
            f"{em.gagal}**Please provide link.\nExample: `{message.text.split()[0]} https://www.instagram.com/p/DFf2z72yBEq/?utm_source=ig_web_copy_link`**"
        )

    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")

    try:
        url = f"https://api.botcahx.eu.org/api/dowloader/igdowloader?url={arg}&apikey={API_BOTCHAX}"
        response = await Tools.fetch.get(url)
        if response.status_code != 200:
            return await proses.edit(
                f"{em.gagal}**Request failed with status code {response.status_code}**"
            )

        data = response.json()
        if not data.get("result"):
            return await proses.edit(f"{em.gagal}**No result data in response**")

        media_urls = data.get("result", [])
        if not media_urls:
            return await proses.edit(
                f"{em.gagal}**No media found in the instagram links**"
            )

        await proses.edit(f"{em.proses}**Preparing media for sending...**")
        media_group = []

        for X in media_urls:
            url = X["url"]
            type_ = Tools.extract_filename(url)
            if type_.endswith((".jpg", ".JPEG")):
                media = await Tools.get_media_data(url, "jpg")
                media_group.append(
                    InputMediaPhoto(
                        media=media,
                    )
                )
            else:
                media = await Tools.get_media_data(url, "mp4")
                media_group.append(
                    InputMediaVideo(
                        media=media,
                    )
                )

        if not media_group:
            return await proses.edit(
                f"{em.gagal}**Failed to prepare media for sending**"
            )

        media_chunks = chunk_media_group(media_group)

        await proses.delete()

        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
                return await message.reply(
                    f"{em.sukses}**Succesfully sent {len(media_chunks)} media.**"
                )
            except Exception as chunk_error:
                logger.error(f"Error sending chunk {i}: {str(chunk_error)}")
                return await message.reply(
                    f"{em.gagal}**Error sending media group {i}:** {str(chunk_error)}"
                )

    except Exception as er:
        logger.error(f"instadl: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
