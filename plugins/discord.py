__MODULES__ = "Discorddl"
__HELP__ = """<b>Command Help Discorddl</b>

<blockquote>Download media from Discord CDN link</blockquote>

<b>Usage:</b>
  <code>.dcdl</code> (url)
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

import traceback
import os
import requests

from kelra.helpers import CMD, Emoji
from kelra.logger import logger


@CMD.UBOT("discord|dcdl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    arg = client.get_text(message)

    if not arg:
        return await message.reply(
            f"<blockquote>{em.gagal}<b>Please provide a Discord CDN link!\nExample: `{message.text.split()[0]} https://cdn.discordapp.com/attachments/...`</b></blockquote>"
        )

    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    await proses.edit(f"<blockquote>{em.proses}**Downloading from Discord...**</blockquote>")

    try:
        filename = arg.split("/")[-1]
        filepath = f"downloads/{filename}"

        response = requests.get(arg)
        if response.status_code != 200:
            return await proses.edit(
                f"<blockquote>{em.gagal}**Failed to download. HTTP {response.status_code}**</blockquote>"
            )

        with open(filepath, "wb") as f:
            f.write(response.content)

        await message.reply_document(filepath, caption="<blockquote>{em.sukses} Downloaded from Discord CDN.</blockquote>")
        await proses.delete()
        os.remove(filepath)

    except Exception as er:
        logger.error(f"discorddl: {traceback.format_exc()}")
        await proses.edit(f"<blockquote>{em.gagal}**Error:** `{er}`</blockquote>")
