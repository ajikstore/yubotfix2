__MODULES__ = "Img2text"
__HELP__ = """<blockquote>Command Help **Img2 Text**</blockquote>

<blockquote expandable>        <u>**Get prompt from image**</u>
    <u>**Get prompt command for generate image from reply image**</u>
        `{0}img2text` (reply to image)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

from config import API_BOTCHAX
from kelra.helpers import CMD, Emoji, Tools


@CMD.UBOT("img2text")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    rep = message.reply_to_message or message
    if len(message.command) < 2 and not rep:
        return await prs.edit(f"{em.gagal}**Please reply to image or give link.!!**")
    if rep and rep.media:
        arg = await Tools.upload_media(message)
    else:
        arg = client.get_text(message)
        if not arg.startswith("https://"):
            return await prs.edit(f"{em.gagal}**Please give valid link**")
    url = f"https://api.botcahx.eu.org/api/tools/img2prompt?url={arg}&apikey={API_BOTCHAX}"
    respon = await Tools.fetch.get(url)
    await prs.edit(f"{em.proses}**Scanning of image...**")
    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.delete()
            return await message.reply(
                f"{em.sukses}**Media:** <a href='{rep.link}'>Here</a>\n**Result:** `{data}`",
                disable_web_page_preview=True,
            )
        except Exception as er:
            await prs.delete()
            return await message.reply(f"{em.gagal}**ERROR:** {str(er)}")
    else:
        return await prs.edit(f"**{em.gagal}Please try again: {respon.status_code}!**")
