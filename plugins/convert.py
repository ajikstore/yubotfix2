import os

from pyrogram.enums import MessageMediaType

from kelra.helpers import CMD, Emoji, Tools

__MODULES__ = "Convert"
__HELP__ = """<blockquote>Command Help **Convert**</blockquote>

    <blockquote expandable>    <u>**Convert sticker to image**</u>
        `{0}toimg` (reply sticker)

    <u>**Convert image to sticker**</u>
        `{0}tosticker` (reply image)

    <u>**Convert video to gif**</u>
        `{0}togif` (reply video)

    <u>**Convert video to audio**</u>
        `{0}toaudio` (reply video)</blockquote>
 
<b>   {1}</b>
"""

CATEGORY = "ᴛᴏᴏʟs <emoji id=5435961551871813164>🛠</emoji>"

@CMD.UBOT("toimg")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    reply = message.reply_to_message
    try:
        file_io = await Tools.dl_pic(client, reply)
        file_io.name = "sticker.png"
        await message.reply_photo(file_io)
        return await proses.delete()
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


@CMD.UBOT("tosticker")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await proses.edit(f"<b>{em.gagal}**Please reply to photo!!**</b>")
        sticker = await client.download_media(
            message.reply_to_message.photo.file_id,
            f"sticker_{message.from_user.id}.webp",
        )
        await message.reply_sticker(sticker)
        os.remove(sticker)
        return await proses.delete()
    except Exception as e:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(e)}")


@CMD.UBOT("togif")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if not message.reply_to_message.sticker:
        return await proses.edit(f"<b>{em.gagal}Please reply to sticker!!</b>")
    file = await client.download_media(
        message.reply_to_message,
        f"gift_{message.from_user.id}.mp4",
    )
    try:
        await client.send_animation(message.chat.id, file, reply_to_message_id=message.id)
        os.remove(file)
        return await proses.delete()
    except Exception as error:
        return await proses.edit(f"{em.gagal}**ERROR:** {str(error)}")


@CMD.UBOT("toaudio")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    replied = message.reply_to_message
    if not replied:
        return await proses.edit(f"<b>{em.gagal}Please reply to message video!</b>")
    if replied.media == MessageMediaType.VIDEO:
        await proses.edit(f"<b>{em.proses}Downloading video...</b>")
        file = await client.download_media(
            message=replied,
            file_name=f"toaudio_{replied.id}",
        )
        out_file = f"{file}.mp3"
        try:
            await proses.edit(f"<b>{em.proses}Converting audio...</b>")
            cmd = f"ffmpeg -i {file} -q:a 0 -map a {out_file}"
            await client.run_cmd(cmd)
            await proses.edit(f"<b>{em.proses}Try to sending audio...</b>")
            await client.send_voice(
                message.chat.id,
                voice=out_file,
                reply_to_message_id=message.id,
            )
            os.remove(file)
            return await proses.delete()
        except Exception as error:
            await proses.edit(f"{em.gagal}**ERROR:** {str(error)}")
    else:
        return await proses.edit(f"<b>{em.gagal}Please reply to video!!</b>")
