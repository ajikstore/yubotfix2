from kelra import bot
from kelra.helpers import CMD, ButtonUtils, Emoji

__CATEGORY__ = "sʏsᴛᴇᴍ <emoji id=5316832430529722441>⚙</emoji>"

@CMD.UBOT("alive")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    query = "alive"
    try:
        inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, query)
        if inline:
            return await message.delete()
    except Exception as error:
        return await message.reply(f"<blockquote>{em.gagal}Error: {str(error)}</blockquote>")
