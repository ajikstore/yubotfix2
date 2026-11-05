__MODULES__ = "Tiktokdl"
__HELP__ = """<blockquote>Command Help Tiktokdl**</blockquote>

<blockquote expandable>        <u>**Download media from tiktok**</u>
    <u>**You can download media from tiktok without watermark,</u>
    <u>or download media from url**</u>
        `{0}ttdl` (url)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "Fun <emoji id=5316832430529722441>🕹</emoji>"

import traceback
from uuid import uuid4

from config import API_BOTCHAX
from kelra import bot
from kelra.database import state
from kelra.helpers import CMD, ButtonUtils, Emoji, Tools
from kelra.logger import logger


@CMD.UBOT("tiktok|ttdl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    arg = client.get_text(message)
    if not arg:
        return await message.reply(
            f"<blockquote>{em.gagal}<b>Please give word or links!!\nExample: `{message.text.split()[0]} https://vt.tiktok.com/ZSeJ7P56G` or `{message.text.split()[0]} video lucu`</b></blockquote>"
        )
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    await proses.edit(f"<blockquote>{em.proses}**Wait a minute this takes some time...**</blockquote>")
    if arg.startswith("https://"):
        url = f"https://api.botcahx.eu.org/api/dowloader/tiktok?url={arg}&apikey={API_BOTCHAX}"
        try:
            response = await Tools.fetch.get(url)
            if response.status_code == 200:
                data = response.json()["result"]
                state.set(client.me.id, "result_ttdownload", data)
                state.set(client.me.id, "idm_ttdownload", id(message))
                inline = await ButtonUtils.send_inline_bot_result(
                    message, message.chat.id, bot.me.username, "inline_ttdownload"
                )
                if inline:
                    return await proses.delete()
            else:
                return await proses.edit(
                    f"<blockquote>{em.gagal}**Please try again {response.status_code}**</blockquote>"
                )

        except Exception as er:
            logger.error(f"ttdl: {traceback.format_exc()}")
            return await proses.edit(f"<blockquote>{em.gagal}**An error: `{str(er)}`**</blockquote>")
    else:
        url = f"https://api.botcahx.eu.org/api/search/tiktoks?query={arg}&apikey={API_BOTCHAX}"
        try:
            response = await Tools.fetch.get(url)
            uniq = f"{str(uuid4())}"
            if response.status_code == 200:
                data = response.json()["result"]
                if len(data["data"]) == 0:
                    return await proses.edit(
                        f"<blockquote>{em.gagal}**Try another word, no videos found `{arg}`**</blockquote>"
                    )
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
                return await proses.edit(
                    f"<blockquote>{em.gagal}**Please try again {response.status_code}**</blockquote>"
                )
        except Exception as er:
            logger.error(f"ttdl: {traceback.format_exc()}")
            return await proses.edit(f"<blockquote>{em.gagal}**An error: `{str(er)}`**</blockquote>")
