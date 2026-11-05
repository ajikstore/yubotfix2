import asyncio
import re
import traceback

from pyrogram.enums import ParseMode

from kelra import bot, kelra
from kelra.database import dB, state
from kelra.helpers import CMD, ButtonUtils, Emoji, Message, Tools
from kelra.logger import logger

__MODULES__ = "Filters"
__HELP__ = """<blockquote>Command Help **Filters**</blockquote>

<blockquote expandable>    <u>**Save filter**</u>
        `{0}filter` (name) (reply message)

    <u>**Get list filters**</u>
        `{0}filters`

    <u>**Get raw filter**</u>
        `{0}getfilter` (name) raw

    <u>**Stop filter**</u>
        `{0}stop` (name)

    <u>**Stop all filter**</u>
        `{0}stop all`</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

@CMD.NO_CMD("REP_BLOCK", kelra)
async def _(client, message):
    em = Emoji(client)
    await em.get()
    return await message.reply_text(f"{em.block}**You've blocked me, don't reply or tag me fuvk it!!**")


@CMD.UBOT("filter")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    xx = await message.reply(f"{em.proses}**{proses_}**")
    rep = message.reply_to_message
    if len(message.command) < 2 or not rep:
        return await xx.edit(f"{em.gagal}**Please reply message and give filter name**")
    nama = message.text.split()[1]
    getfilter = await dB.get_var(client.me.id, nama, "filter")
    if getfilter:
        return await xx.edit(f"{em.gagal}**Filter {nama} already exist!**")
    value = None

    text = rep.text or rep.caption or ""
    entities = rep.entities or rep.caption_entities
    _, button = ButtonUtils.parse_msg_buttons(text)
    if button:
        if rep.media:
            copy = await rep.copy(bot.me.username)
            sent = await client.send_message(bot.me.username, f"/id {nama}", reply_to_message_id=copy.id)
            await asyncio.sleep(1)
            await sent.delete()
            await copy.delete()
            extract = Tools.dump_entity(text, entities)
            type = state.get(client.me.id, nama)
            value = {
                "type": type["type"],
                "file_id": type["file_id"],
                "result": extract,
            }
        else:
            extract = Tools.dump_entity(text, entities)
            value = {"type": "text", "file_id": "", "result": extract}
    else:
        if rep.media:
            media = Tools.get_file_id(rep)
            extract = Tools.dump_entity(text, entities)
            value = {
                "type": media["message_type"],
                "file_id": media["file_id"],
                "result": extract,
            }
        else:
            extract = Tools.dump_entity(text, entities)
            value = {"type": "text", "file_id": "", "result": extract}
    if value:
        await dB.set_var(client.me.id, nama, value, "filter")
        return await xx.edit(f"{em.sukses}**Saved {nama} filter!!**")
    else:
        return await xx.edit(f"{em.gagal}**Please reply message and give filter name**")


@CMD.UBOT("getfilter")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    xx = await message.reply(f"{em.proses}**{proses_}**")

    try:
        if len(message.text.split()) == 3 and (message.text.split())[2] in [
            "noformat",
            "raw",
        ]:
            filter = message.text.split()[1]
            data = await dB.get_var(client.me.id, filter, "filter")
            if not data:
                return await xx.edit(f"{em.gagal}**Filter {filter} not found!**")
            return await get_raw_filter(client, message, xx, filter, data)
        else:
            return await xx.edit(f"{em.gagal}**Please valid command.\nExample: `{message.text.split()[0]} ciah noformat`.**")
    except Exception as e:
        return await xx.edit(f"{em.gagal}**ERROR**: {str(e)}")


async def get_raw_filter(client, message, xx, filter, data):
    em = Emoji(client)
    await em.get()
    thetext = data["result"].get("text")
    _, button = ButtonUtils.parse_msg_buttons(thetext)
    try:
        if button:
            type = data["type"]
            file_id = data["file_id"]
            if type == "text":
                await message.reply(
                    data["result"].get("text"),
                    parse_mode=ParseMode.DISABLED,
                    reply_to_message_id=Message.ReplyCheck(message),
                )
            else:
                kwargs = {
                    "photo": bot.send_photo,
                    "voice": bot.send_voice,
                    "audio": bot.send_audio,
                    "video": bot.send_video,
                    "animation": bot.send_animation,
                    "document": bot.send_document,
                }
                if type in kwargs:
                    disend = await kwargs[type](
                        client.me.id,
                        file_id,
                        caption=data["result"].get("text"),
                        parse_mode=ParseMode.DISABLED,
                    )
                    async for copy_msg in client.search_messages(bot.id, limit=1):
                        await copy_msg.copy(message.chat.id)
                        break
                    await disend.delete()

        else:
            type = data["type"]
            file_id = data["file_id"]

            if type == "text":
                await message.reply(
                    data["result"].get("text"),
                    parse_mode=ParseMode.DISABLED,
                    reply_to_message_id=Message.ReplyCheck(message),
                )
            elif type == "sticker":
                await message.reply_sticker(
                    file_id,
                    reply_to_message_id=Message.ReplyCheck(message),
                )
            elif type == "video_filter":
                await message.reply_video_filter(file_id, reply_to_message_id=Message.ReplyCheck(message))
            else:
                kwargs = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                }

                if type in kwargs:
                    await kwargs[type](
                        file_id,
                        caption=data["result"].get("text"),
                        parse_mode=ParseMode.DISABLED,
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
    except Exception as er:
        logger.info(f"ERROR: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**ERROR**: {str(er)}")
    return await xx.delete()


@CMD.UBOT("filters")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    xx = await message.reply(f"{em.proses}**{proses_}**")
    getfilter = await dB.all_var(client.me.id, "filter")
    if not getfilter:
        return await xx.edit(f"{em.gagal}**You dont have any filter!**")
    rply = f"{em.msg}**List of Filters:**\n\n"
    for x, data in getfilter.items():
        type = await dB.get_var(client.me.id, x, "filter")
        rply += f"**• Name: `{x}` | Type: `{type['type']}`**\n"
    return await xx.edit(rply)


@CMD.UBOT("stop")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    args = client.get_arg(message).split(",")
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    xx = await message.reply(f"{em.proses}**{proses_}**")

    if len(args) == 0 or (len(args) == 1 and args[0].strip() == ""):
        return await xx.edit(f"{em.gagal}**Which filter do you want to delete?**")
    if message.command[1] == "all":
        if not await dB.all_var(client.me.id, "filter"):
            return await xx.edit(f"{em.gagal}**You dont have any filter!**")
        for nama in await dB.all_var(client.me.id, "filter"):
            data = await dB.get_var(client.me.id, nama, "filter")
            await dB.remove_var(client.me.id, nama, "filter")
        return await xx.edit(f"{em.sukses}**Succesfully deleted all filter!**")
    else:
        gagal_list = []
        sukses_list = []

        for arg in args:
            arg = arg.strip()
            if not arg:
                continue
            data = await dB.get_var(client.me.id, arg, "filter")
            if not data:
                gagal_list.append(arg)
            else:
                await dB.remove_var(client.me.id, arg, "filter")
                sukses_list.append(arg)

        if sukses_list:
            return await xx.edit(f"{em.sukses}**Filter `{', '.join(sukses_list)}` successfully deleted.**")

        if gagal_list:
            return await xx.edit(f"{em.gagal}**Filter `{', '.join(gagal_list)}` not found!**")


@CMD.NO_CMD("FILTERS", kelra)
@CMD.capture_err
async def _(client, message):
    try:
        text = message.text
        if not text:
            return

        getfilter = await dB.all_var(client.me.id, "filter")
        if not getfilter:
            return
        reply = message.from_user or message.sender_chat
        reply.id
        for word in getfilter:
            pattern = rf"\b{re.escape(word)}\b"
            if not re.search(pattern, text, flags=re.IGNORECASE):
                continue

            _filter = await dB.get_var(client.me.id, word, "filter")
            data_type, file_id = _filter["type"], _filter.get("file_id")
            data = _filter["result"].get("text")
            teks = await Tools.escape_filter(message, data, Tools.parse_words)
            if data_type != "text" and not file_id:
                continue

            if data_type:
                if data_type == "text":
                    await message.reply_text(
                        text=teks,
                        disable_web_page_preview=True,
                        parse_mode=ParseMode.HTML,
                    )
                elif data_type == "sticker":
                    await message.reply_sticker(sticker=file_id)
                elif data_type == "animation":
                    await message.reply_animation(animation=file_id, caption=teks, parse_mode=ParseMode.HTML)
                elif data_type == "photo":
                    await message.reply_photo(photo=file_id, caption=teks, parse_mode=ParseMode.HTML)
                elif data_type == "document":
                    await message.reply_document(document=file_id, caption=teks, parse_mode=ParseMode.HTML)
                elif data_type == "video":
                    await message.reply_video(video=file_id, caption=teks, parse_mode=ParseMode.HTML)
                elif data_type == "video_note":
                    await message.reply_video_note(video_note=file_id)
                elif data_type == "audio":
                    await message.reply_audio(audio=file_id, caption=teks, parse_mode=ParseMode.HTML)
                elif data_type == "voice":
                    await message.reply_voice(voice=file_id, caption=teks, parse_mode=ParseMode.HTML)
    except Exception:
        logger.error(f"Eror filter pada pesan: {message.text}\n{traceback.format_exc()}")
