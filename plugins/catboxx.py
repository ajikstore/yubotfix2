from telegraph.aio import Telegraph

from kelra import bot
from kelra.helpers import CMD, Emoji, Tools

__MODULES__ = "Catbox"
__HELP__ = """<blockquote>Command Help **Catbox**</blockquote>

<blockquote>**Upload text media to catbox**</blockquote>
    **You can upload text or media to catbox then get url**
        `{0}tourl` (reply text/reply media)

<b>   {1}</b>
"""

__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

async def post_to_telegraph(is_media: bool, title=None, content=None, media=None):
    telegraph = Telegraph()
    if telegraph.get_access_token() is None:
        await telegraph.create_account(short_name=bot.me.username)
    if is_media:
        response = await telegraph.upload_file(media)
        return f"https://img.yasirweb.eu.org{response[0]['src']}"
    response = await telegraph.create_page(
        title,
        html_content=content,
        author_url=f"https://t.me/{bot.me.username}",
        author_name=bot.me.username,
    )
    return f"https://graph.org/{response['path']}"


@CMD.UBOT("tourl|tg")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    proses_ = await emo.get_costum_text()
    XD = await message.reply(f"{emo.proses}**{proses_[4]}**")
    if not message.reply_to_message:
        return await XD.edit(f"{emo.gagal}**Please reply to message text or video!**")
    if message.reply_to_message.text:
        page_title = f"{client.me.first_name} {client.me.last_name or ''}"
        page_text = message.reply_to_message.text
        page_text = page_text.replace("\n", "<br>")
        try:
            url = await post_to_telegraph(False, page_title, page_text)
        except Exception as exc:
            return await XD.edit(f"{emo.gagal}**{exc}**")
        return await XD.edit(
            f"{emo.sukses}**Successfully Uploaded: <a href='{url}'>Click Here</a>**",
            disable_web_page_preview=True,
        )
    else:
        try:
            url = await Tools.upload_media(message)
        except Exception as exc:
            return await XD.edit(f"{emo.gagal}**{exc}**")
        return await XD.edit(
            f"{emo.sukses}**Successfully Uploaded: <a href='{url}'>Click Here</a>**",
            disable_web_page_preview=True,
        )
