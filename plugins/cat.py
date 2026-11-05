__MODULES__ = "Cat"
__HELP__ = """<blockquote>Command Help **Cat**</blockquote>

<blockquote expandable>        <u>**Get random cats image**</u>
    <u>**You can get random image cute cats**</u>
        `{0}cats`</blockquote>
    
<b>   {1}</b>
"""


from kelra import bot
from kelra.helpers import CMD, ButtonUtils


@CMD.UBOT("cats")
async def _(_, message):
    try:
        inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, "inline_cat")
        if inline:
            return await message.delete()
    except Exception as er:
        return await message.reply(f"<blockquote>**ERROR**: {str(er)}</blockquote>")
