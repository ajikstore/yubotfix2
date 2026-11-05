import asyncio
import random
from random import choice
from pyrogram.enums import MessagesFilter
from config import OWNER_ID
from pyrogram import enums, types

from kelra.helpers import CMD, Emoji

__MODULES__ = "Bokep"
__HELP__ = """<blockquote>Command Help **Bokep**</blockquote>
    
<blockquote><u>**Get videos**</u>
    <u>**Get random bokep video**</u>
        `{0}bokep`</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

CHANNEL_LINK = "https://t.me/+endO3QWv2mZmYzU9"   # link/username channel sumber
CHANNEL_ID = -1003578509777                   # ganti dengan chat_id asli

@CMD.UBOT("bokep")
async def _(client, message):
    y = await message.reply_text(
        "<blockquote>**mencari video bokep**...</blockquote>", 
        quote=True
    )
    try:
        # join channel kalau belum join
        await client.join_chat(CHANNEL_LINK)
    except Exception:
        pass

    try:
        bokepnya = []
        # cari video dari channel
        async for bokep in client.search_messages(
            CHANNEL_ID, filter=MessagesFilter.VIDEO
        ):
            bokepnya.append(bokep)

        if not bokepnya:
            return await y.edit("<b>Tidak ada video ditemukan.</b>")

        video = random.choice(bokepnya)
        await video.copy(message.chat.id, reply_to_message_id=message.id)
        await y.delete()
    except Exception as error:
        await y.edit(str(error))

    # kalau bukan owner, leave channel
    if client.me.id != OWNER_ID:
        try:
            await client.leave_chat(CHANNEL_ID)
        except Exception:
            pass
