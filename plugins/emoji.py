from pyrogram import types
from pyrogram.enums import ParseMode

from kelra.database import dB
from kelra.helpers import CMD, Emoji

__MODULES__ = "Emoji"
__HELP__ = """<blockquote>Command Help **Emoji**</blockquote>

<blockquote expandable>    <u>**Set emoji ping**</u>
        `{0}setemoji ping` (emoji)

    <u>**Set emoji uptime**</u>
        `{0}setemoji uptime` (emoji)

    <u>**Set emoji profil**</u>
        `{0}setemoji profil` (emoji)

    <u>**Set emoji robot**</u>
        `{0}setemoji robot` (emoji)

    <u>**Set emoji msg**</u>
        `{0}setemoji msg` (emoji)

    <u>**Set emoji warn**</u>
        `{0}setemoji warn` (emoji)

    <u>**Set emoji block**</u>
        `{0}setemoji block` (emoji)

    <u>**Set emoji gagal**</u>
        `{0}setemoji gagal` (emoji)

    <u>**Set emoji sukses**</u>
        `{0}setemoji sukses` (emoji)

    <u>**Set emoji owner**</u>
        `{0}setemoji owner` (emoji)

    <u>**Set emoji klip**</u>
        `{0}setemoji klip` (emoji)

    <u>**Set emoji net**</u>
        `{0}setemoji net` (emoji)

    <u>**Set emoji up**</u>
        `{0}setemoji up` (emoji)

    <u>**Set emoji down**</u>
        `{0}setemoji down` (emoji)

    <u>**Set emoji speed**</u>
        `{0}setemoji speed` (emoji)

    <u>**Set emoji proses**</u>
        `{0}setemoji proses` (emoji)

    <u>**Set emoji status**</u>
        `{0}setemoji status` (emoji)

    <u>**Get id from message**</u>
        `{0}id` (reply message)

    <u>**Get status emoji**</u>
        `{0}getemoji`
    
<u>**Note**: Emoji only working on premium users.</u></blockquote>
    
<b>   {1}</b>
"""


@CMD.UBOT("id")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    # Basic information
    chat = message.chat
    your_id = message.from_user if message.from_user else message.sender_chat
    message_id = message.id
    reply = message.reply_to_message

    text = f"**Message ID:** `{message_id}`\n"
    text += f"**Your ID:** `{your_id.id}`\n"
    text += f"**Chat ID:** `{chat.id}`\n"

    if reply:
        replied_user_id = reply.from_user.id if reply.from_user else reply.sender_chat.id if reply.sender_chat else None
        text += f"**Replied Message Information:**\n"
        text += f"**├ Message ID:** `{reply.id}`\n"
        if replied_user_id:
            text += f"**├ User ID:** `{replied_user_id}`\n"

        if reply.entities:
            for entity in reply.entities:
                if entity.custom_emoji_id:
                    text += f"<blockquote>**╰ Emoji ID:** `{entity.custom_emoji_id}`\n</blockquote>"

        if reply.photo:
            text += f"**╰ Photo File ID:** `{reply.photo.file_id}`\n"
        elif reply.video:
            text += f"**╰ Video File ID:** `{reply.video.file_id}`\n"
        elif reply.sticker:
            text += f"**╰ Sticker File ID:** `{reply.sticker.file_id}`\n"
        elif reply.animation:
            text += f"**╰ GIF File ID:** `{reply.animation.file_id}`\n"
        elif reply.document:
            text += f"**╰ Document File ID:** `{reply.document.file_id}`\n"

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"<blockquote>\n**Mentioned User ID:** `{user_id}`\n</blockquote>"
        except Exception:
            return await message.reply_text(f"<blockquote>{em.gagal}**User tidak ditemukan.**</blockquote>")

    return await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


@CMD.UBOT("setemoji|getemoji")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await emo.get_costum_text()
    prem = client.me.is_premium
    pros = await message.reply(f"<blockquote>{emo.proses}**{proses_}**</blockquote>")
    if message.command[0] == "getemoji":
        return await pros.edit(
            f"<blockquote expandable><b>Emoji anda saat ini:</b>\n├ Ping: {emo.ping}\n├ Msg: {emo.msg}\n├ Sukses: {emo.sukses}\n├ Gagal: {emo.gagal}\n├ Proses: {emo.proses}\n├ Warn: {emo.warn}\n├ Block: {emo.block}\n├ Owner: {emo.owner}\n├ Uptime: {emo.uptime}\n├ Robot: {emo.robot}\n├ Klip: {emo.klip}\n├ Net: {emo.net}\n├ Up: {emo.up}\n├ Down: {emo.down}\n├ Speed: {emo.speed}\n╰ Profil: {emo.profil}</b></blockquote>"
        )

    elif len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Gunakan Format : <code>setemoji [value]</code></b></blockquote>")
    variable = message.command[1].lower() if len(message.command) > 1 else None
    value = None
    emoji_id = None

    if message.reply_to_message:
        value = message.reply_to_message.text or message.reply_to_message.caption
        if prem and message.reply_to_message.entities:
            for entity in message.reply_to_message.entities:
                if entity.custom_emoji_id:
                    emoji_id = entity.custom_emoji_id
                    break
    elif len(message.command) >= 3:
        value = " ".join(message.command[2:])
        if prem and message.entities:
            for entity in message.entities:
                if entity.custom_emoji_id:
                    emoji_id = entity.custom_emoji_id
                    break

    valid_variables = [
        "ping",
        "msg",
        "warn",
        "block",
        "proses",
        "gagal",
        "sukses",
        "profil",
        "owner",
        "robot",
        "klip",
        "net",
        "up",
        "down",
        "speed",
        "uptime",
    ]
    if not variable or variable not in valid_variables or not value and variable != "status":
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Query tidak ditemukan!</b>!</blockquote>")
    if variable == "status":
        return await set_emoji_status(client, message)

    if prem and emoji_id:
        await dB.set_var(client.me.id, f"emo_{variable}", emoji_id)
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Berhasil set Emoji {variable.capitalize()} menjadi:</b> <emoji id={emoji_id}>{value}</emoji></blockquote>")

    await dB.set_var(client.me.id, f"emo_{variable}", value)
    return await pros.edit(f"<blockquote>{emo.sukses}<b>Berhasil set Emoji {variable.capitalize()} menjadi:</b> {value}</blockquote>")


async def set_emoji_status(client, message):
    emo = Emoji(client)
    await emo.get()
    prem = client.me.is_premium
    if not prem:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Anda bukan pengguna Telegram Premium.</b></blockquote>")
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await emo.get_costum_text()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>{proses_}</b></blockquote>")

    rep = message.reply_to_message
    if not rep:
        rep = message
    emoji_id = None

    if rep.entities:
        for entity in rep.entities:
            if entity.custom_emoji_id:
                emoji_id = entity.custom_emoji_id
    else:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Silahkan balas Custom Emoji Premium.</b></blockquote>")

    if prem is True:
        if emoji_id:
            await client.set_emoji_status(types.EmojiStatus(custom_emoji_id=emoji_id))
            return await pros.edit(f"<blockquote>{emo.sukses}<b>Berhasil mengubah status Emoji menjadi: <emoji id={emoji_id}>😭</emoji></b></blockquote>")
    else:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Anda bukan pengguna Telegram Premium.</b></blockquote>")
