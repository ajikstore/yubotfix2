from kelra import kelra
from kelra.helpers import AFK_, CMD, Emoji

__MODULES__ = "AFK"
__HELP__ = """<blockquote>Command Help **AFK**</blockquote>

<blockquote expandable>    <u>**Enable afk mode**</u>
        `{0}afk` (reason)
    
    <u>**Disable afk mode**</u>
        `{0}unafk`</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

@CMD.NO_CMD("REP_BLOCK", kelra)
async def _(client, message):
    em = Emoji(client)
    await em.get()
    return await message.reply_text(f"<blockquote>{em.block}**woi jawa kaga usah reply apalagi tag gue, lo udah block gue ANAK KONTOL!!**</blockquote>")


@CMD.UBOT("afk")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    rep = message.reply_to_message
    if not rep:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Please reply to message!!</b></blockquote>")
    return await AFK_.set_afk(client, message, emo)


@CMD.NO_CMD("AFK", kelra)
@CMD.capture_err
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    return await AFK_.get_afk(client, message, emo)


@CMD.UBOT("unafk")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    return await AFK_.unset_afk(client, message, emo)
