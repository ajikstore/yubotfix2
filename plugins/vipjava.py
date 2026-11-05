import random
from pyrogram.enums import MessagesFilter
from kelra import *
from kelra.helpers import CMD, Emoji

__MODULES__ = "Vip java"
__HELP__ = """<blockquote>Command Help **Vipjava**</blockquote>
    
<blockquote expandable><u>**Get videos**</u>
    <u>**Get random vipjava video command**</u>
        `{0}vipjav`</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

@CMD.UBOT("vipjav")
async def video_asupan(client, message):
    y = await message.reply_text(f"<blockquote>jangan ngocok mulu dek....</blockquote>")
    try:
        asupannya = []
        async for asupan in client.search_messages(
            "@vvipeyjav", filter=MessagesFilter.VIDEO
        ):
            asupannya.append(asupan)
        video = random.choice(asupannya)
        await video.copy(message.chat.id, reply_to_message_id=message.id)
        await y.delete()
    except Exception as error:
        await y.edit(error)
