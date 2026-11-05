from kelra.helpers import CMD, Emoji, Tools

__MODULES__ = "Webshot"
__HELP__ = """<blockquote>Command Help **Webshot** </blockquote>

<blockquote expandable>        <u>**View webpage capture**</u>
    <u>**Get screenshot web from url**</u>
        `{0}webss` (url)</blockquote>
    
<b>   {1}</b>
"""


@CMD.UBOT("webss")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    if len(message.command) < 2:
        return await proses.edit(f"<blockquote>{em.gagal}**Please give valid link! Example: `{message.text.split()[0]}webss https://youtube.com`**</blockquote>")
    url = message.text.split(None, 1)[1] if len(message.command) < 3 else message.text.split(None, 2)[1]
    if "https://" not in url:
        return await proses.edit(f"<blockquote>{em.gagal}**Please give valid link!**</blockquote>")
    full = False if len(message.command) < 3 else True
    try:
        photo = await Tools.screen_web(url, full)
        if not photo:
            return await proses.edit(f"<blockquote>{em.gagal}**Something went wrong, please try again!**</blockquote>")

        await proses.delete()
        upload = await message.reply(f"<blockquote>{em.proses}**Uploading media...**</blockquote>")
        if not full:
            await message.reply_photo(photo)
        else:
            await message.reply_document(photo)
        return await upload.delete()
    except Exception as r:
        return await upload.edit(f"<blockquote>{em.gagal}**ERROR:** {str(r)}</blockquote>")
