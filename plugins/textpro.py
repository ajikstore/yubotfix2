from kelra import bot
from kelra.database import state
from kelra.helpers import CMD, ButtonUtils, Emoji

__MODULES__ = "Textpro"
__HELP__ = """<blockquote>Command Help **Text Pro**</blockquote>

<blockquote expandable>        <u>**Make custom text**</u>
    <u>**Generate text image from command**</u>
        `{0}textpro` (text/reply text)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"

@CMD.UBOT("textpro")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    text = client.get_text(message)
    if not text:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Please give text or reply to text:\n\nExample: <code>{message.text.split()[0]}</code> [text or reply to text]</b></blockquote>")
    proses_ = await emo.get_costum_text()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>{proses_[4]}</b></blockquote>")
    query = f"inline_textpro"
    state.set(client.me.id, "TEXT_PRO", text)
    try:
        inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, query)
        if inline:
            await pros.delete()
            return await message.delete()
    except Exception as error:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code></blockquote>")
