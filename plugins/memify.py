import os

from kelra.helpers import CMD, Emoji, Sticker

__MODULES__ = "Memify"
__HELP__ = """<blockquote>Command Help **Memifiy**</blockquote> 

<blockquote expandable>        <u>**Add text to sticker**</u>
    <u>**Add text on top the sticker**</u>
        `{0}mmf text` (reply sticker)
    <u>**Add text on bottom the sticker**</u>
        `{0}mmf ;text` (reply sticker)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"

@CMD.UBOT("mmf|memify")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    rep = message.reply_to_message
    meme = None
    file = None

    if not rep:
        return await message.reply(f"{emo.gagal}<b>Use the command by replying to a photo/sticker/video.</b>")

    if not (rep.photo or rep.animation or rep.video or rep.sticker):
        return await message.reply(f"{emo.gagal}<b>Reply to a photo, sticker, or video.</b>")

    try:
        file = await client.download_media(rep)
        if not file:
            return await message.reply(f"{emo.gagal}<b>Failed to download media.</b>")

        pros = await message.reply(f"{emo.proses}<b>Processing adding text to media ..</b>")

        text = client.get_text(message)
        if len(message.command) < 2:
            await pros.edit(
                f"{emo.gagal}<b>Use the command by adding text after the command.\n\nExample:\n<code>{x}mmf Hi;Love!</code>\n\nThen the text <i><u>Hi</u></i> will be at the top of the media, and the text <i><u>Love!</u></i> will be at the bottom of the media.</b>"
            )
            return

        if rep.animation or rep.video:
            meme = await Sticker.add_text_to_video(file, text)
        else:
            meme = await Sticker.add_text_img(file, text)

        await client.send_sticker(message.chat.id, sticker=meme, reply_to_message_id=message.id)
        await pros.delete()

    except Exception as e:
        await message.reply(f"{emo.gagal}<b>Error processing media: {str(e)}</b>")
        if "pros" in locals():
            await pros.delete()

    finally:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass

        if meme and os.path.exists(meme):
            try:
                os.remove(meme)
            except Exception:
                pass
