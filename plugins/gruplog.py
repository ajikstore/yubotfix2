import asyncio
import sys
from datetime import datetime, timezone

from pyrogram import enums
from pyrogram.errors import (
    ChannelPrivate,
    ChatForwardsRestricted,
    ChatWriteForbidden,
    FloodWait,
    MessageEmpty,
    MessageIdInvalid,
    ChannelInvalid,
    PeerIdInvalid
)
from pyrogram.helpers import ikb
from pytz import timezone

from config import OWNER_ID, DATABASE 
from kelra import bot, kelra
from kelra.database import dB, state
from kelra.helpers import CMD, Emoji, Tools
from kelra.logger import logger

__MODULES__ = "Logs"
__HELP__ = """<blockquote>Command Help **Logs**</blockquote>

<blockquote expandable><u>**On off gruplogs**</u>
    <u>**Set your gruplog, if you set on, you will create gruplog and receive message from bot
    for incoming private message or tag in chat group**</u>
        `{0}logs` (on/off)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "sʏsᴛᴇᴍ <emoji id=5316832430529722441>⚙</emoji>"

logger_cache = {}
reply_cache = []


def get_reply_data(reply):
    data = state.get(reply.id, "REPLY")
    if data:
        chat_id = int(data["chat"])
        message_id = int(data["id"])
        return chat_id, message_id
    else:
        return None, None


@CMD.UBOT("logs")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    cek = client.get_arg(message)
    status = await dB.get_var(client.me.id, "GRUPLOG")
    if cek.lower() == "on":
        if not status:
            try:
                link = await Tools.create_logs(client)
                if "ERROR" in link:
                    return await proses.edit(f"{link}")
                return await proses.edit(
                    f"{em.sukses}**Succesfully enabled pm and tag logs!! Please check {link}**",
                    disable_web_page_preview=True,
                )
            except Exception as er:
                return await proses.edit(f"{em.gagal}**ERROR: `{str(er)}`, Silahkan lapor ke admins.**")
        else:
            return await proses.edit(f"{em.sukses}<b>Pm and tag logs already enable!!</b>")
    if cek.lower() == "off":
        if status:
            await dB.remove_var(client.me.id, "GRUPLOG")
            return await proses.edit(f"{em.sukses}<b>Succesfully disabled pm and tag logs!!</b>")
        else:
            return await proses.edit(f"{em.gagal}<b>Pm and tag logs already disabled!!</b>")

    else:
        return await proses.edit(f"{em.gagal}<b>Please give query on or off!!</b>")


async def curi_data_user(client, message):
    try:
        if message.chat.type == enums.ChatType.PRIVATE:
            dia = message.sender_chat or message.from_user
            nama_dia = message.sender_chat.title if message.sender_chat else message.from_user.first_name
            rpk = f"[{nama_dia}](tg://openmessage?user_id={dia.id})"
            gw = f"[{client.me.first_name}](tg://openmessage?user_id={client.me.id})"
            data = {
                "id_pengirim": dia.id,
                "penerima": gw,
                "pengirim": rpk,
                "id_penerima": client.me.id,
            }
            logger_cache[client.me.id] = data
            type_mapping = {
                "text": (Tools.Types.TEXT.value, message.text),
                "photo": (Tools.Types.PHOTO.value, message.photo),
                "voice": (Tools.Types.VOICE.value, message.voice),
                "audio": (Tools.Types.AUDIO.value, message.audio),
                "video": (Tools.Types.VIDEO.value, message.video),
                "video_note": (Tools.Types.VIDEO_NOTE.value, message.video_note),
                "animation": (Tools.Types.ANIMATION.value, message.animation),
                "sticker": (Tools.Types.STICKER.value, message.sticker),
                "document": (Tools.Types.DOCUMENT.value, message.document),
                "contact": (Tools.Types.CONTACT.value, message.contact),
            }
            for key, (msgtype, media) in type_mapping.items():
                if media:
                    send_id = logger_cache.get(client.me.id)["id_pengirim"]
                    receive = logger_cache.get(client.me.id)["penerima"]
                    id_penerima = logger_cache.get(client.me.id)["id_penerima"]
                    send_ms = logger_cache.get(client.me.id)["pengirim"]
                    caption = f"""#USER_LOG
<b>Penerima: {receive}
ID Penerima: {id_penerima}
Pengirim: {send_ms}
ID Pengirim: {send_id}
Text: {message.text or message.caption or ''}</b>"""
                    bot_send_to = await Tools.send_media(bot, msgtype)
                    if msgtype not in (
                        Tools.Types.TEXT.value,
                        Tools.Types.STICKER.value,
                        Tools.Types.CONTACT.value,
                        Tools.Types.ANIMATED_STICKER.value,
                    ):
                        file_path = await client.download_media(media)
                        if msgtype == Tools.Types.VIDEO_NOTE.value:
                            uh = await bot_send_to(DATABASE, file_path)
                            return await bot.send_message(
                                DATABASE,
                                caption,
                                reply_to_message_id=uh.id,
                            )
                        else:
                            return await bot_send_to(DATABASE, file_path, caption=caption)
    except Exception as er:
        logger.error(f"{str(er)}. Line: {sys.exc_info()[-1].tb_lineno}")


async def message_mapping(client, message, userid):
    type_mapping = {
        "text": bot.send_message,
        "photo": bot.send_photo,
        "voice": bot.send_voice,
        "audio": bot.send_audio,
        "video": bot.send_video,
        "video_note": bot.send_video_note,
        "animation": bot.send_animation,
        "sticker": bot.send_sticker,
        "document": bot.send_document,
    }
    type_mapping_users = {
        "photo": (Tools.Types.PHOTO.value, message.photo),
        "voice": (Tools.Types.VOICE.value, message.voice),
        "audio": (Tools.Types.AUDIO.value, message.audio),
        "video": (Tools.Types.VIDEO.value, message.video),
    }
    if message.text:
        send_function = type_mapping["text"]
        return message.text, "text", send_function

    if message.location:
        return None, None, None

    try:
        try:
            send = await message.copy(bot.me.username)
            todel = await client.send_message(bot.me.username, f"/id {userid}", reply_to_message_id=send.id)

            await asyncio.sleep(1)

            data = state.get(client.me.id, f"{userid}")
            if not data:
                return None, None, None

            file_id = str(data["file_id"])
            type = str(data["type"])

            send_function = type_mapping.get(type)
            if not send_function:
                return None, None, None

            await send.delete()
            await todel.delete()

            return file_id, type, send_function

        except Exception:
            for key, (msgtype, media) in type_mapping_users.items():
                if media:
                    client_send_to = await Tools.send_media(client, msgtype)
                    file_path = await client.download_media(media)
                    send = await client_send_to(bot.id, file_path, caption=message.caption or "")
                    todel = await client.send_message(bot.me.username, f"/id {userid}", reply_to_message_id=send.id)
                    await asyncio.sleep(1)

                    data = state.get(client.me.id, f"{userid}")
                    if not data:
                        return None, None, None

                    file_id = str(data["file_id"])
                    type = str(data["type"])

                    send_function = type_mapping.get(type)
                    if not send_function:
                        return None, None, None

                    await send.delete()
                    await todel.delete()

                    return file_id, type, send_function

            return None, None, None

    except Exception as e:
        logger.error(f"Error in message_mapping: {str(e)}")
        return None, None, None


@CMD.NO_CMD("LOGS_GROUP", kelra)
@CMD.capture_err
async def _(client, message):
    await curi_data_user(client, message)
    log = await dB.get_var(client.me.id, "GRUPLOG")
    if not log or message.chat.id == 777000:
        return
    from_user = message.chat if message.chat.type == enums.ChatType.PRIVATE else message.from_user
    if message.sender_chat:
        if message.sender_chat.username is None:
            user_link = f"{message.sender_chat.title}"
        else:
            user_link = f"[{message.sender_chat.title}](https://t.me/{message.sender_chat.username}"
    else:
        user_link = f"[{message.from_user.first_name} {message.from_user.last_name or ''}](tg://user?id={message.from_user.id})"
    message_link = message.link if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP) else f"tg://openmessage?user_id={from_user.id}&message_id={message.id}"
    tanggal = datetime.now(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
    txt = message.text or message.caption or ""
    file_path, message_type, send_function = await message_mapping(client, message, from_user.id)
    if None in (file_path, message_type, send_function):
        return
    await asyncio.sleep(1)
    state.set(from_user.id, "BEFORE", txt)
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        button = ikb([[("Link Message", f"{message_link}", "url")]])
        text = f"""
📨 <b><u>Group Notifications</u></b>

• <b>Name Group: {message.chat.title}</b>
• <b>ID Group:</b> <code>{message.chat.id}</code>
• <b>From User: {user_link}</b>

• <b>From User ID: `{from_user.id}`</b>
• <b>Message:</b> <blockquote>{txt}</blockquote>
• <b>Message Type:</b> <u><b>{message_type}</b></u>

• <b>Date:</b> <b>{tanggal}</b>
"""
        try:
            if message_type in ["sticker", "video_note"]:
                kwargs = {
                    "chat_id": int(log),
                    message_type: file_path,
                    "reply_markup": button,
                }
                sent = await send_function(**kwargs)
            elif message_type in [
                "photo",
                "voice",
                "audio",
                "video",
                "animation",
                "document",
            ]:
                kwargs = {
                    "chat_id": int(log),
                    message_type: file_path,
                    "reply_markup": button,
                    "caption": text,
                }
                sent = await send_function(**kwargs)
            else:
                sent = await send_function(
                    int(log),
                    text,
                    disable_web_page_preview=True,
                    reply_markup=button,
                )

            data = {"chat": message.chat.id, "id": message.id}
            state.set(sent.id, "REPLY", data)

            return
            
        except (ChannelInvalid, PeerIdInvalid, KeyError):
            await dB.remove_var(client.me.id, "GRUPLOG")
            return f"Error ChannelInvalid: Grup Log tidak valid/telah dihapus."
        except ChatForwardsRestricted:
            return f"Error ChatForwardsRestricted {message.chat.id}"
        except MessageIdInvalid:
            return f"Error MessageIdInvalid {message.chat.id}"
        except ChannelPrivate:
            return f"Error ChannelPrivate {message.chat.id}"
        except FloodWait as e:
            await asyncio.sleep(e.value)
            if message_type in ["sticker", "video_note"]:
                kwargs = {
                    "chat_id": int(log),
                    message_type: file_path,
                    "reply_markup": button,
                }
                sent = await send_function(**kwargs)
            elif message_type in [
                "photo",
                "voice",
                "audio",
                "video",
                "animation",
                "document",
            ]:
                kwargs = {
                    "chat_id": int(log),
                    message_type: file_path,
                    "reply_markup": button,
                    "caption": text,
                }
                sent = await send_function(**kwargs)
            else:
                sent = await send_function(
                    int(log),
                    text,
                    disable_web_page_preview=True,
                    reply_markup=button,
                )

            data = {"chat": message.chat.id, "id": message.id}
            state.set(sent.id, "REPLY", data)

            return

    else:
        text = f"""
📨 <b><u>Private Notifications</u></b>

• <b>From: {user_link}</b>
• <b>From User ID: <code>{from_user.id}</code></b>

• <b>Message:</b> <blockquote>{txt}</blockquote>
• <b>Message Type:</b> <u><b>{message_type}</b></u>

• <b>Date:</b> <b>{tanggal}</b>
"""
        if send_function is not None:
            return await send_to_pm(
                client,
                message,
                text,
                log,
                message_link,
                message_type,
                file_path,
                send_function,
            )


async def send_to_pm(client, message, text, log, message_link, media_type, file_path, send_function):
    button = ikb([[("Link Message", f"{message_link}", "url")]])
    try:
        await asyncio.sleep(0.5)
        if media_type == "text":
            sent = await send_function(
                int(log),
                text,
                disable_web_page_preview=True,
                reply_markup=button,
            )

            data = {"chat": message.chat.id, "id": message.id}
            state.set(sent.id, "REPLY", data)

        elif media_type in ["sticker", "video_note"]:
            kwargs = {
                "chat_id": int(log),
                media_type: file_path,
                "reply_markup": button,
            }
            send = await send_function(**kwargs)
            sent = await bot.send_message(
                int(log),
                text,
                reply_markup=button,
                reply_to_message_id=send.id,
            )

            data = {"chat": message.chat.id, "id": message.id}
            state.set(sent.id, "REPLY", data)

            return

        else:
            kwargs = {
                "chat_id": int(log),
                media_type: file_path,
                "caption": text,
                "reply_markup": button,
            }
            sent = await send_function(**kwargs)
            data = {"chat": message.chat.id, "id": message.id}
            state.set(sent.id, "REPLY", data)

    except (ChannelInvalid, PeerIdInvalid, KeyError):
        await dB.remove_var(client.me.id, "GRUPLOG")
        return f"Error ChannelInvalid: Grup Log tidak valid/telah dihapus."
    except (
        ChatForwardsRestricted,
        MessageIdInvalid,
        ChatWriteForbidden,
        MessageEmpty,
    ) as err:
        return f"Error: {str(err)}"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_to_pm(
            client,
            message,
            text,
            log,
            message_link,
            media_type,
            file_path,
            send_function,
        )


@CMD.NO_CMD("REPLY", kelra)
@CMD.IS_LOG
async def _(client, message):
    log = await dB.get_var(client.me.id, "GRUPLOG")
    if log is None:
        return
    reply = message.reply_to_message
    chat_id, reply_message_id = get_reply_data(reply)
    if chat_id is None:
        return
    args = {
        "photo": message.photo,
        "voice": message.voice,
        "audio": message.audio,
        "video": message.video,
        "video_note": message.video_note,
        "animation": message.animation,
        "sticker": message.sticker,
        "document": message.document,
    }
    kwargs = {
        "photo": client.send_photo,
        "voice": client.send_voice,
        "audio": client.send_audio,
        "video": client.send_video,
        "video_note": client.send_video_note,
        "animation": client.send_animation,
        "document": client.send_document,
        "sticker": client.send_sticker,
    }
    if message.text:
        await client.send_message(chat_id, message.text, reply_to_message_id=reply_message_id)
    elif message.sticker:
        await client.send_sticker(chat_id, message.sticker.file_id, reply_to_message_id=reply_message_id)
    elif message.video_note:
        await client.send_video_note(
            chat_id,
            message.video_note.file_id,
            reply_to_message_id=reply_message_id,
        )
    else:
        media_type = next((key for key, value in args.items() if value), None)
        if media_type:
            await kwargs[media_type](
                chat_id,
                args[media_type].file_id,
                caption=message.caption or "",
                reply_to_message_id=reply_message_id,
            )


@CMD.EDITED()
async def _(client, message):
    log = await dB.get_var(client.me.id, "GRUPLOG")
    if not log or message.chat.id == 777000:
        return
    from_user = message.chat if message.chat.type == enums.ChatType.PRIVATE else message.from_user
    file_path, message_type, send_function = await message_mapping(
        client,
        message,
        from_user.id,
    )
    if None in (file_path, message_type, send_function):
        return
    tanggal = datetime.now(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
    txt = message.text or message.caption or ""
    from_user = message.chat if message.chat.type == enums.ChatType.PRIVATE else message.from_user
    if message.sender_chat:
        if message.sender_chat.username is None:
            user_link = f"{message.sender_chat.title}"
        else:
            user_link = f"[{message.sender_chat.title}](https://t.me/{message.sender_chat.username}"
    else:
        user_link = f"[{message.from_user.first_name} {message.from_user.last_name or ''}](tg://user?id={message.from_user.id})"
    message_link = message.link if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP) else f"tg://openmessage?user_id={from_user.id}&message_id={message.id}"
    edited = state.get(from_user.id, "BEFORE")
    text = f"""
📨 <b><u>Edited Message</u></b>

• <b>From: {user_link}</b>
• <b>From User ID: `{from_user.id}`</b>

• <b>Before:</b> <blockquote>{edited}</blockquote>
• <b>After:</b> <blockquote>{txt}</blockquote>

• <b>Message Type:</b> <u><b>{message_type}</b></u>
• <b>Date:</b> <b>{tanggal}</b>"""
    button = ikb([[("Link Message", f"{message_link}", "url")]])
    return await bot.send_message(int(log), text, disable_web_page_preview=True, reply_markup=button)


# @CMD.DELETED()
async def _(client, messages):
    return await bot.send_message(OWNER_ID, messages)

    """
    log = await dB.get_var(client.me.id, "GRUPLOG")
    for message in messages:
        try:
            if not log or not message or not message.chat:
                continue

            is_private = message.chat.type == enums.ChatType.PRIVATE
            mentions = bool(
                message.entities
                and any(entity.type == "mention" for entity in message.entities)
            )
            tanggal = datetime.now(timezone("Asia/Jakarta")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if not (is_private or mentions):
                continue

            text = f"
📨 **Deleted Message** 
- Chat: {"Private" if is_private else "Group"} 
- Chat ID: `{message.chat.id}`
- Date: `{tanggal}`
"
            await bot.send_message(int(log), text)

        except AttributeError:
            continue
    """


@CMD.NO_CMD("ADD_ME", kelra)
async def _(client, message):
    log = await dB.get_var(client.me.id, "GRUPLOG")
    if not log:
        return
    try:
        for members in message.new_chat_members:
            if members.id == client.me.id:
                count = await client.get_chat_members_count(message.chat.id)
                username = message.chat.username if message.chat.username else "Private"
                msg = f"""
<blockquote><b>#New_Group</b>

<b>Chat Name:</b> {message.chat.title}
<b>Chat ID:</b> `{message.chat.id}`

<b>Chat Username:</b> @{username}
<b>Chat Member Count:</b> {count}

<b>Added By:</b> {message.from_user.mention}
<b>Added By ID:</b> `{message.from_user.id}`</blockquote>"""
                return await bot.send_message(
                    log,
                    text=msg,
                    reply_markup=ikb(
                        [
                            [
                                (
                                    f"Added Bye",
                                    f"tg://openmessage?user_id={message.from_user.id}",
                                    "url",
                                )
                            ]
                        ]
                    ),
                )
            else:
                dbgban = await dB.get_list_from_var(client.me.id, "GBANNED")
                if members.id in dbgban:
                    try:
                        await client.ban_chat_member(message.chat.id, members.id)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        await client.ban_chat_member(message.chat.id, members.id)
                    except Exception:
                        pass
    except Exception as e:
        return await bot.send_message(log, f"Error: {str(e)}")


@CMD.NO_CMD("KICK_ME", kelra)
async def _(client, message):
    log = await dB.get_var(client.me.id, "GRUPLOG")
    if not log:
        return
    try:
        left_chat_member = message.left_chat_member
        if left_chat_member and left_chat_member.id == client.me.id:
            if message.sender_chat:
                if message.sender_chat.username is None:
                    user_link = f"{message.sender_chat.title}"
                else:
                    user_link = f"[{message.sender_chat.title}](https://t.me/{message.sender_chat.username}"
            else:
                user_link = f"[{message.from_user.first_name} {message.from_user.last_name or ''}](tg://user?id={message.from_user.id})"
            title = message.chat.title
            username = f"@{message.chat.username}" if message.chat.username else "Private"
            chat_id = message.chat.id
            left = f"<blockquote>✫ <b><u>#Left_Group</u></b> ✫\nChat Name: {title}\nChat Username: {username}\nChat ID: {chat_id}\n\nRemoved By: {user_link}</blockquote>"
            return await bot.send_message(
                log,
                text=left,
                reply_markup=ikb(
                    [
                        [
                            (
                                f"Kicked Bye",
                                f"tg://openmessage?user_id={message.from_user.id}",
                                "url",
                            )
                        ]
                    ]
                ),
            )
    except Exception as e:
        return await bot.send_message(log, f"Error: {str(e)}")
