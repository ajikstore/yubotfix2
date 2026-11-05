import os

import aiofiles

from kelra.helpers import CMD, Emoji, Tools

__MODULES__ = "Pastebin"
__HELP__ = """<blockquote>Command Help **Pastebin** </blockquote>

<blockquote expandable>        <u>**Upload text to bin**</u>
    <u>**You can post text to pastebin**</u>
        `{0}paste` (reply text/document)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

@CMD.UBOT("bin|paste")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if not message.reply_to_message:
        return await proses.edit(f"{em.gagal}**Please reply to message!!**")
    r = message.reply_to_message
    if not r.text and not r.document:
        return await proses.edit(f"{em.gagal}**Please reply to message text or document!!**")
    if r.text:
        content = str(r.text)
    else:
        if r.document.file_size > 40000:
            return await proses.edit(f"{em.gagal}**Maximum size is 40000!!**")
        doc = await message.reply_to_message.download()
        async with aiofiles.open(doc, mode="r") as f:
            content = await f.read()
        os.remove(doc)
    link = await Tools.paste(content)
    photo = await Tools.screen_web(link, True)
    try:
        await message.reply_document(photo, caption=f"{em.sukses}<b>Succesed <a href='{link}'>link</a></b>")
        return await proses.delete()
    except Exception:
        await message.reply(f"{em.sukses}<b>Succesed <a href='{link}'>link</a></b>")
        return await proses.delete()
