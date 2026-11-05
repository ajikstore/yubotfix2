import random
from pyrogram.enums import MessagesFilter
from kelra import *
from kelra.helpers import CMD, Emoji

__MODULES__ = "Vip indo"
__HELP__ = """<blockquote>Command Help **Vipindo**</blockquote>
    
<blockquote expandable><u>**Get videos**</u>
    <u>**Get random vipindo video command**</u>
        `{0}vipindo`</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

@CMD.UBOT("vipindo")
async def video_asupan(client, message):
    y = await message.reply_text(f"<blockquote>jangan ngocok mulu dek....</blockquote>")
    try:
        asupannya = []
        async for asupan in client.search_messages(
            "@anuanuyuk", filter=MessagesFilter.VIDEO
        ):
            asupannya.append(asupan)
        video = random.choice(asupannya)
        await video.copy(message.chat.id, reply_to_message_id=message.id)
        await y.delete()
    except Exception as error:
        await y.edit(error)
