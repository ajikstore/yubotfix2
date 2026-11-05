import asyncio
import os
import time
from datetime import datetime, timedelta
import pytz

from pyrogram.enums import ChatType
from pyrogram.errors import (
    ChannelPrivate,
    ChatSendPlainForbidden,
    ChatWriteForbidden,
    FloodWait,
    Forbidden,
    PeerIdInvalid,
    SlowmodeWait,
    UserBannedInChannel,
)
from pyrogram.helpers import ikb

from config import BLACKLIST_GCAST, DEVS, BOT_ID
from kelra import bot
from kelra.database import dB, state
from kelra.helpers import CMD, Emoji, Tools, task
from kelra.helpers.emoji_logs import get_auto_effect

__MODULES__ = "Broadcast"
__HELP__ = """<blockquote>Command Help **Broadcast**</blockquote>

<blockquote expandable>    <u>**Send broadcast message to chats db**</u>
        `{0}bc db` (text/reply text)

    <u>**Send broadcast message to chats group**</u>
        `{0}bc group` (text/reply text)

    <u>**Send broadcast message to chats group and private**</u>
        `{0}bc all` (text/reply text)

    <u>**Send broadcast message to private chat**</u>
        `{0}bc private` (text/reply text)

    <u>**Add chat to blacklist broadcast**</u>
        `{0}addbl` (chatid)

    <u>**Delete chat from blacklist broadcast**</u>
        `{0}delbl` (chatid)

    <u>**View all chat from blacklist broadcast**</u>
        `{0}listbl`
   
    <u>**Add chat to broadcast db**</u>
        `{0}add-bcdb` (chatid)

    <u>**Delete chat to broadcast db**</u>
        `{0}del-bcdb` (chatid)

    <u>**View all chats on broadcast db**</u>
        `{0}list-bcdb`

    <u>**Cancel broadcast message, give taskid**</u>
        `{0}cancel` (taskid)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

# Fungsi generate text Progress Bar
def get_progress_text(command, text_obj, current, total, done, failed, task_id, start_time):
    percent = int((current / total) * 100) if total > 0 else 0
    filled = int(15 * current // total) if total > 0 else 0
    bar = '█' * filled + '▒' * (15 - filled)

    elapsed_time = time.time() - start_time
    time_per_chat = elapsed_time / current if current > 0 else 0
    eta_seconds = (total - current) * time_per_chat

    m, s = divmod(int(eta_seconds), 60)
    eta_str = f"{m}m {s}s" if m > 0 else f"{s}s"
    if current == total:
        eta_str = "Selesai"

    text_preview = "Media/Tanpa Teks"
    if isinstance(text_obj, str):
        text_preview = text_obj
    elif hasattr(text_obj, 'text') and text_obj.text:
        text_preview = text_obj.text
    elif hasattr(text_obj, 'caption') and text_obj.caption:
        text_preview = text_obj.caption

    if len(text_preview) > 30:
        text_preview = text_preview[:30].replace('\n', ' ') + "..."
    else:
        text_preview = text_preview.replace('\n', ' ')

    title_type = command.upper()

    return (
        f"<emoji id=6291810261787481501>🚀</emoji> **PROGRES BROADCAST ({title_type})**\n\n"
        f"<emoji id=6138780272088322672>📝</emoji> **Teks:** {text_preview}\n"
        f"<emoji id=6138772137420263831>📊</emoji> **Progres:** {bar} {percent}%\n"
        f"<emoji id=6136347585431999570>🔄</emoji> **Detail:** {current} / {total} Chat\n"
        f"<emoji id=6084396322444544568>⏱</emoji> **Estimasi Selesai:** {eta_str}\n"
        f"<emoji id=6269163801178804220>✅</emoji> **Sukses:** {done}\n"
        f"<emoji id=6269316311172518259>❌</emoji> **Gagal:** {failed}\n"
        f"<emoji id=6114021507908767611>💠</emoji> **Task ID:** `{task_id}`"
    )

@CMD.UBOT("bc")
@CMD.FAKEDEV("bc")
async def bc_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<b><emoji id=5260342697075416641>🔄</emoji> Menyiapkan broadcast...</b>")

    command, text = client.extract_type_and_msg(message)

    if command not in ["group", "private", "all", "db"] or not text:
        return await proses.edit(f"<blockquote>{em.gagal}<code>{message.text.split()[0]}</code> <b>[group, private, all atau db]</b></blockquote>")
    
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    
    inline_deleted = False
    try:
        bot_username = bot.me.username
        inline = await client.get_inline_bot_results(bot_username, f"inline_cancel {task_id} {id(message)}")
        if inline and inline.results:
            await client.send_inline_bot_result(message.chat.id, inline.query_id, inline.results[0].id)
            inline_deleted = True
        else:
            raise Exception("Bot pendamping belum merespon query")
    except Exception as e:
        pass
        
    chats = await client.get_chat_id(command)
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"<blockquote>{em.gagal}**Error failed broadcast:**\n</blockquote>"
    muted_groups = []
    
    try:
        if command == "db":
            return await broadcast_db(client, message, em, prefix, done, failed, blacklist, task, task_id, proses)
            
        total_member = len(chats)
        start_time = time.time()
        for i, chat_id in enumerate(chats, start=1):
            if not task.is_active(task_id):
                break
            if chat_id in (blacklist or []) or chat_id in (BLACKLIST_GCAST or []) or chat_id in (DEVS or []):
                continue
            try:
                await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
                done += 1
            except ChannelPrivate:
                error += f"ChannelPrivate {chat_id}\n"
                continue
            except SlowmodeWait:
                error += f"SlowmodeWait {chat_id}\n"
                failed += 1
            except ChatWriteForbidden:
                error += f"ChatWriteForbidden {chat_id}\n"
                failed += 1
                muted_groups.append(f"ID: {chat_id}")
            except Forbidden:
                error += f"Forbidden {chat_id}\n"
                failed += 1
            except ChatSendPlainForbidden:
                error += f"ChatSendPlainForbidden {chat_id}\n"
                failed += 1
            except UserBannedInChannel:
                error += f"UserBannedInChannel {chat_id}\n"
                failed += 1
            except PeerIdInvalid:
                error += f"PeerIdInvalid {chat_id}\n"
                continue
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
                except Exception:
                    failed += 1
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"

            if i % 5 == 0 or i == total_member:
                teks_prog = get_progress_text(command, text, i, total_member, done, failed, task_id, start_time)
                try:
                    await proses.edit(teks_prog)
                except Exception:
                    pass

    finally:
        task.end_task(task_id)
        try:
            if inline_deleted:
                async for msg in client.get_chat_history(message.chat.id, limit=20):
                    if msg.via_bot and msg.via_bot.id == bot.me.id and str(task_id) in (msg.text or ""):
                        await msg.delete()
                        break
        except Exception:
            pass

    if error:
        error_dir = "storage/cache"
        os.makedirs(error_dir, exist_ok=True)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
            
    muted_link_text = ""
    if muted_groups:
        teks_muted = "Daftar Chat/Group yang Me-mute Bot (ChatWriteForbidden):\n\n" + "\n".join(muted_groups)
        try:
            link = await Tools.paste(teks_muted)
            muted_link_text = f"\n<emoji id=5954136131929902524>🚷</emoji> <b><a href='{link}'>List Mute (Klik Disini)</a></b>"
        except Exception:
            pass

    command_type = message.command[0] if message.command else "bc"
    final_msg = f"""<blockquote expandable><emoji id=5877499406969738023>⚠️</emoji> <b>Gcast Sukses</b>\n
<emoji id=5021905410089550576>✅</emoji> <b>Success:</b> {done}
<emoji id=5019523782004441717>❌</emoji> <b>Failed:</b> {failed}
<emoji id=6138780272088322672>✉️</emoji> <b>Type:</b> {command_type}
<emoji id=6138720224150559518>⚙️</emoji> <b>Task ID:</b> `{task_id}`
<emoji id=5249053508681883137>👤</emoji> <b>OWNER:</b> {owner_}{muted_link_text}</blockquote>\nType <code>{prefix[0]}bc-error</code>\n\n<emoji id=6089144627833611433>⚡️</emoji> <b>powered by : <a href="https://t.me/storegarf">@storegarf</a></b>"""
    
    return await proses.edit(final_msg, disable_web_page_preview=True)


@CMD.UBOT("gcast")
@CMD.FAKEDEV("gcast")
async def gcast_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()

    effect_id = get_auto_effect(client)
    proses = await message.reply(f"<b><emoji id=5260342697075416641>🔄</emoji> Menyiapkan broadcast...</b>")

    text = client.get_message(message)
    if not text:
        return await proses.edit(
            f"<blockquote>{em.gagal}<code>{message.text.split()[0]}</code> "
            f"<b>text or give text</b></blockquote>"
        )

    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)

    inline_deleted = False
    try:
        bot_username = bot.me.username
        inline = await client.get_inline_bot_results(bot_username, f"inline_cancel {task_id} {id(message)}")
        if inline and inline.results:
            await client.send_inline_bot_result(message.chat.id, inline.query_id, inline.results[0].id)
            inline_deleted = True
    except Exception as e:
        pass

    chats = await client.get_chat_id("group")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")

    done, failed = 0, 0
    error = f"<blockquote>{em.gagal}**Error failed broadcast:**\n</blockquote>"
    muted_groups = []

    wib = pytz.timezone("Asia/Jakarta")
    hari_map = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }

    total_member = len(chats)
    start_time = time.time()

    try:
        for i, chat_id in enumerate(chats, start=1):
            if not task.is_active(task_id):
                break
            if chat_id in (blacklist or []) or chat_id in (BLACKLIST_GCAST or []) or chat_id in (DEVS or []):
                continue

            try:
                now = datetime.now(wib)
                jam = now.strftime("%H:%M")
                tanggal = now.strftime("%d-%m-%Y")
                hari = hari_map[now.strftime("%A")]

                chat_info = await client.get_chat(chat_id)
                nama_group = chat_info.title if hasattr(chat_info, "title") else str(chat_id)

                if message.reply_to_message:
                    msg_to_send = text.text if hasattr(text, "text") and text.text else ""
                else:
                    msg_to_send = text

                if isinstance(msg_to_send, str):
                    msg_to_send = (
                        msg_to_send.replace("{gc}", nama_group).replace("{jam}", jam)
                        .replace("{tanggal}", tanggal).replace("{member}", str(total_member))
                        .replace("{hari}", hari).replace("{wib}", jam)
                    )

                if message.reply_to_message:
                    await text.copy(chat_id)
                else:
                    try:
                        await client.send_message(chat_id, msg_to_send, effect_id=effect_id, disable_web_page_preview=True)
                    except Exception:
                        await client.send_message(chat_id, msg_to_send, disable_web_page_preview=True)
                done += 1

            except ChannelPrivate:
                error += f"ChannelPrivate {chat_id}\n"
            except SlowmodeWait:
                error += f"SlowmodeWait {chat_id}\n"
                failed += 1
            except ChatWriteForbidden:
                error += f"ChatWriteForbidden {chat_id}\n"
                failed += 1
                muted_groups.append(f"Nama: {nama_group} | ID: {chat_id}")
            except Forbidden:
                error += f"Forbidden {chat_id}\n"
                failed += 1
            except ChatSendPlainForbidden:
                error += f"ChatSendPlainForbidden {chat_id}\n"
                failed += 1
            except UserBannedInChannel:
                error += f"UserBannedInChannel {chat_id}\n"
                failed += 1
            except PeerIdInvalid:
                error += f"PeerIdInvalid {chat_id}\n"
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    if message.reply_to_message:
                        await text.copy(chat_id)
                    else:
                        await client.send_message(chat_id, msg_to_send, disable_web_page_preview=True)
                except Exception:
                    failed += 1
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"
            
            if i % 5 == 0 or i == total_member:
                teks_prog = get_progress_text("GROUP", text, i, total_member, done, failed, task_id, start_time)
                try:
                    await proses.edit(teks_prog)
                except Exception:
                    pass

    finally:
        task.end_task(task_id)
        try:
            if inline_deleted:
                async for msg in client.get_chat_history(message.chat.id, limit=20):
                    if msg.via_bot and msg.via_bot.id == bot.me.id and str(task_id) in (msg.text or ""):
                        await msg.delete()
                        break
        except Exception:
            pass

    if error:
        error_dir = "storage/cache"
        os.makedirs(error_dir, exist_ok=True)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as f:
            f.write(error)
            
    muted_link_text = ""
    if muted_groups:
        teks_muted = "Daftar Grup yang Me-mute Bot (ChatWriteForbidden):\n\n" + "\n".join(muted_groups)
        try:
            link = await Tools.paste(teks_muted)
            muted_link_text = f"\n<emoji id=5954136131929902524>🚷</emoji> <b><a href='{link}'>List Grup Mute (Klik Disini)</a></b>"
        except Exception:
            pass

    command_type = message.command[0] if message.command else "gcast"
    final_msg = f"""<blockquote expandable><emoji id=5877499406969738023>⚠️</emoji> <b>Gcast Sukses</b>\n
<emoji id=5021905410089550576>✅</emoji> <b>Success:</b> {done}
<emoji id=5019523782004441717>❌</emoji> <b>Failed:</b> {failed}
<emoji id=6138780272088322672>✉️</emoji> <b>Type:</b> {command_type}
<emoji id=6138720224150559518>⚙️</emoji> <b>Task ID:</b> `{task_id}`
<emoji id=5249053508681883137>👤</emoji> <b>OWNER:</b> {owner_}{muted_link_text}</blockquote>\nType <code>{prefix[0]}bc-error</code>\n\n<emoji id=6089144627833611433>⚡️</emoji> <b>powered by : <a href="https://t.me/storegarf">@storegarf</a></b>"""

    return await proses.edit(final_msg, disable_web_page_preview=True)

@CMD.UBOT("ucast")
@CMD.FAKEDEV("ucast")
async def broadcast(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<b><emoji id=5260342697075416641>🔄</emoji> Menyiapkan broadcast...</b>")

    text = client.get_message(message)
    if not text:
        return await proses.edit(f"<blockquote>{em.gagal}<code>{message.text.split()[0]}</code> <b>text or give text</b></blockquote>")
    
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    
    inline_deleted = False
    try:
        bot_username = bot.me.username
        inline = await client.get_inline_bot_results(bot_username, f"inline_cancel {task_id} {id(message)}")
        if inline and inline.results:
            await client.send_inline_bot_result(message.chat.id, inline.query_id, inline.results[0].id)
            inline_deleted = True
    except Exception as e:
        pass
        
    chats = await client.get_chat_id("private")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done, failed = 0, 0
    error = f"<blockquote>{em.gagal}**Error failed broadcast:**\n</blockquote>"
    muted_groups = []
    total_member = len(chats)
    start_time = time.time()

    try:
        for i, chat_id in enumerate(chats, start=1):
            if not task.is_active(task_id):
                break
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
                done += 1
            except ChannelPrivate:
                error += f"ChannelPrivate {chat_id}\n"
                continue
            except SlowmodeWait:
                error += f"SlowmodeWait {chat_id}\n"
                failed += 1
            except ChatWriteForbidden:
                error += f"ChatWriteForbidden {chat_id}\n"
                failed += 1
                muted_groups.append(f"ID: {chat_id}")
            except Forbidden:
                error += f"Forbidden {chat_id}\n"
                failed += 1
            except ChatSendPlainForbidden:
                error += f"ChatSendPlainForbidden {chat_id}\n"
                failed += 1
            except UserBannedInChannel:
                error += f"UserBannedInChannel {chat_id}\n"
                failed += 1
            except PeerIdInvalid:
                error += f"PeerIdInvalid {chat_id}\n"
                continue
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
                except Exception:
                    failed += 1
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"
                
            if i % 5 == 0 or i == total_member:
                teks_prog = get_progress_text("PRIVATE", text, i, total_member, done, failed, task_id, start_time)
                try:
                    await proses.edit(teks_prog)
                except Exception:
                    pass
    finally:
        task.end_task(task_id)
        try:
            if inline_deleted:
                async for msg in client.get_chat_history(message.chat.id, limit=20):
                    if msg.via_bot and msg.via_bot.id == bot.me.id and str(task_id) in (msg.text or ""):
                        await msg.delete()
                        break
        except Exception:
            pass
            
    if error:
        error_dir = "storage/cache"
        os.makedirs(error_dir, exist_ok=True)
        with open(f"{error_dir}/{client.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
            
    muted_link_text = ""
    if muted_groups:
        teks_muted = "Daftar User/Private yang Me-mute Bot (ChatWriteForbidden):\n\n" + "\n".join(muted_groups)
        try:
            link = await Tools.paste(teks_muted)
            muted_link_text = f"\n<emoji id=5954136131929902524>🚷</emoji> <b><a href='{link}'>List Mute (Klik Disini)</a></b>"
        except Exception:
            pass
            
    command_type = message.command[0] if message.command else "ucast"
    final_msg = f"""<blockquote expandable><emoji id=5877499406969738023>⚠️</emoji> <b>Gcast Sukses</b>\n
<emoji id=5021905410089550576>✅</emoji> <b>Success:</b> {done}
<emoji id=5019523782004441717>❌</emoji> <b>Failed:</b> {failed}
<emoji id=6138780272088322672>✉️</emoji> <b>Type:</b> {command_type}
<emoji id=6138720224150559518>⚙️</emoji> <b>Task ID:</b> `{task_id}`
<emoji id=5249053508681883137>👤</emoji> <b>OWNER:</b> {owner_}{muted_link_text}</blockquote>\nType <code>{prefix[0]}bc-error</code>\n\n<emoji id=6089144627833611433>⚡️</emoji> <b>powered by : <a href="https://t.me/storegarf">@storegarf</a></b>"""
    
    return await proses.edit(final_msg, disable_web_page_preview=True)

@CMD.UBOT("bc-error")
@CMD.FAKEDEV("bc-error")
async def _(client, message):
    oy = await message.reply("<blockquote><b>Reading error logs...</b></blockquote>")
    try:
        error_file = f"storage/cache/{client.me.id}_errors.txt"
        try:
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in log file.</b>")
                return
            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = f"<blockquote><b>📋 Error Logs:</b>\n\n<code>{content}</code></blockquote>"

            return await oy.edit(message_text)

        except FileNotFoundError:
            return await oy.edit("<b>Error log file not found!</b></blockquote>")

    except Exception:
        try:
            error_file = f"storage/cache/{client.me.id}_error.txt"
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in fallback log file.</b>")
                return

            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = f"<blockquote><b>📋 Error Logs (from fallback):</b>\n\n<code>{content}</code></blockquote>"

            await client.send_message("me", message_text)
            return await oy.edit("<b>Cek saved message</b>")

        except Exception as e:
            return await oy.edit(f"<b>Failed to read error logs: {str(e)}</b>")


async def broadcast_db(client, message, em, prefix, done, failed, blacklist, task, task_id, proses):
    command, text = client.extract_type_and_msg(message)
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    chatsdb = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    if not chatsdb:
        try:
            await proses.delete()
        except:
            pass
        return await message.reply(f"<blockquote>{em.gagal}**You don't have broadcastdb !!Please type `{prefix[0]} add-bcdb 'in the group or user.**</blockquote>")
        
    total_member = len(chatsdb)
    muted_groups = []
    start_time = time.time()
    
    inline_deleted = False
    try:
        bot_username = bot.me.username
        inline = await client.get_inline_bot_results(bot_username, f"inline_cancel {task_id} {id(message)}")
        if inline and inline.results:
            await client.send_inline_bot_result(message.chat.id, inline.query_id, inline.results[0].id)
            inline_deleted = True
    except Exception:
        pass
    
    try:
        for i, chat_id in enumerate(chatsdb, start=1):
            if not task.is_active(task_id):
                break
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS:
                continue
            try:
                await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
                done += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await (text.copy(chat_id) if message.reply_to_message else client.send_message(chat_id, text))
            except ChatWriteForbidden:
                failed += 1
                muted_groups.append(f"ID: {chat_id}")
            except Exception:
                failed += 1
                continue
                
            if i % 5 == 0 or i == total_member:
                teks_prog = get_progress_text("DB", text, i, total_member, done, failed, task_id, start_time)
                try:
                    await proses.edit(teks_prog)
                except Exception:
                    pass
    finally:
        task.end_task(task_id)
        try:
            if inline_deleted:
                async for msg in client.get_chat_history(message.chat.id, limit=20):
                    if msg.via_bot and msg.via_bot.id == bot.me.id and str(task_id) in (msg.text or ""):
                        await msg.delete()
                        break
        except Exception:
            pass

    muted_link_text = ""
    if muted_groups:
        teks_muted = "Daftar Chat yang Me-mute Bot (ChatWriteForbidden):\n\n" + "\n".join(muted_groups)
        try:
            link = await Tools.paste(teks_muted)
            muted_link_text = f"\n<emoji id=5954136131929902524>🚷</emoji> <b><a href='{link}'>List Mute (Klik Disini)</a></b>"
        except Exception:
            pass

    final_msg = f"""<blockquote expandable><emoji id=5877499406969738023>⚠️</emoji> <b>Gcast Sukses</b>\n
<emoji id=5021905410089550576>✅</emoji> <b>Success:</b> {done}
<emoji id=5019523782004441717>❌</emoji> <b>Failed:</b> {failed}
<emoji id=6138780272088322672>✉️</emoji> <b>Type:</b> db
<emoji id=6138720224150559518>⚙️</emoji> <b>Task ID:</b> `{task_id}`
<emoji id=5249053508681883137>👤</emoji> <b>OWNER:</b> {owner_}{muted_link_text}</blockquote>\nType <code>{prefix[0]}bc-error</code>\n\n<emoji id=6089144627833611433>⚡️</emoji> <b>powered by : <a href="https://t.me/storegarf">@storegarf</a></b>"""

    return await proses.edit(final_msg, disable_web_page_preview=True)


@CMD.UBOT("cancel")
@CMD.FAKEDEV("cancel")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    prefix = client.get_prefix(client.me.id)
    if len(message.command) != 2:
        return await message.reply(f"<blockquote>{em.gagal}**Please provide a task ID to cancel.\nType `{prefix[0]}task` to view list task running.**</blockquote>")

    task_id = message.command[1]

    if not task.is_active(task_id):
        return await message.reply(f"<blockquote>{em.gagal}**No active task found with ID: #`{task_id}`**</blockquote>")
    task.end_task(task_id)
    return await message.reply(f"<blockquote>{em.sukses}**Ended task: #`{task_id}`**</blockquote>")


@CMD.UBOT("addbl")
@CMD.DEV_CMD("addbl")
@CMD.FAKEDEV("addbl")
async def addbl_cmd(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    pp = await message.reply(f"<blockquote>{em.proses}{proses_}</blockquote>")

    input_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    name = None

    try:
        chat_id = int(input_id)
        chat = await client.get_chat(chat_id)
    except ValueError:
        try:
            chat = await client.get_chat(input_id)
            chat_id = chat.id
        except PeerIdInvalid:
            return await pp.edit(f"<blockquote>{em.gagal}<b>ID, link, atau username tidak valid!</b></blockquote>")

    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        name = chat.title
    elif chat.type == ChatType.PRIVATE:
        name = f"{chat.first_name} {chat.last_name or ''}"
    else:
        name = str(chat_id)

    if chat_id in blacklist:
        return await pp.edit(f"<blockquote>{em.gagal}{name} already in the blacklist-Gcast!</blockquote>")

    await dB.add_to_var(client.me.id, "BLACKLIST_GCAST", chat_id)
    return await pp.edit(f"<blockquote>{em.sukses}<b>Successfully adding {name} into blacklist</b></blockquote>")


@CMD.UBOT("delbl")
@CMD.DEV_CMD("delbl")
@CMD.FAKEDEV("delbl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    pp = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")

    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")

    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        default_name = message.chat.title
    elif chat_type == ChatType.PRIVATE:
        default_name = f"{message.chat.first_name} {message.chat.last_name or ''}"
    else:
        default_name = "Unknown"

    try:
        if len(message.command) > 1 and message.command[1] == "all":
            for A in blacklist:
                await dB.remove_from_var(client.me.id, "BLACKLIST_GCAST", A)
            return await pp.edit(f"<blockquote>{em.sukses}<b>Successfully delete all blacklist-gcast lists!</b></blockquote>")

        if len(message.command) < 2:
            chat_id = message.chat.id
            name = default_name

            if chat_id not in blacklist:
                return await pp.edit(f"<blockquote>{em.gagal}**`{name}` is not in blacklists!**</blockquote>")

            await dB.remove_from_var(client.me.id, "BLACKLIST_GCAST", chat_id)
            return await pp.edit(f"<blockquote>{em.sukses}**Successfully delete `{name}` from the blacklist-gcast list!**</blockquote>")

        input_id = message.command[1]

        try:
            chat_id = int(input_id)
            chat = await client.get_chat(chat_id)
        except ValueError:
            try:
                chat = await client.get_chat(input_id)
                chat_id = chat.id
            except PeerIdInvalid:
                return await pp.edit(f"<blockquote>{em.gagal}**Invalid ID/link/username `{input_id}`!**</blockquote>")

        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            name = chat.title
        elif chat.type == ChatType.PRIVATE:
            name = f"{chat.first_name} {chat.last_name or ''}"
        else:
            name = str(chat_id)

        if chat_id not in blacklist:
            return await pp.edit(f"<blockquote>{em.gagal}`{name}` **Not in Blacklist-Gcast!**</blockquote>")

        await dB.remove_from_var(client.me.id, "BLACKLIST_GCAST", chat_id)
        return await pp.edit(f"<blockquote>{em.sukses}**Successfully delete `{name}` from the blacklist-gcast list!**</blockquote>")

    except Exception as er:
        return await pp.edit(f"<blockquote>{em.gagal}ERROR: `{str(er)}`!!</blockquote>")

@CMD.UBOT("listbl")
@CMD.FAKEDEV("listbl")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    pp = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    if blacklist == []:
        return await pp.edit(f"<blockquote>{em.gagal}**Your Blacklist-Gcast Data is still empty!**</blockquote>")
    msg = f"<blockquote expandable>{em.msg}Total Blacklist-Gcast: {len(blacklist)}\n\n</blockquote>"
    for num, x in enumerate(blacklist, 1):
        try:
            chat = await client.get_chat(x)
            name = chat.title or f"{chat.first_name} {chat.last_name or ''}"
            msg += f"{num}. {name}|`{chat.id}`\n"
        except Exception:
            msg += f"<blockquote expandable>{num}. `{x}`\n</blockquote>"
    if len(msg) > 4096:
        link = await Tools.paste(msg)
        await pp.edit(f"<blockquote>{em.proses}**Message is too long, uploading to pastebin...**</blockquote>")
        await asyncio.sleep(1)
        return await message.reply_text(
            f"<blockquote>{em.sukses}**<a href='{link}'>Click here </a> to see your blacklist-gcast list.</blockquote>**",
            disable_web_page_preview=True,
        )
    else:
        await pp.delete()
        return await message.reply_text(msg)


@CMD.UBOT("add-bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    pp = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        name = message.chat.title
    elif chat_type == ChatType.PRIVATE:
        name = f"{message.chat.first_name}{message.chat.last_name or ''}"
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await pp.edit(f"<blockquote>{em.gagal}**Chat_id must be a number!**</blockquote>")

    if chat_id in blacklist:
        return await pp.edit(f"<blockquote>{em.gagal}`{name}` **Already on Broadcast-DB!**</blockquote>")
    await dB.add_to_var(client.me.id, "BROADCASTDB", chat_id)
    return await pp.edit(f"<blockquote>{em.sukses}**Successfully added `{name}` into broadcast-db**</blockquote>")


@CMD.UBOT("del-bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    pp = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    chat_type = message.chat.type
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        name = message.chat.title
    elif chat_type == ChatType.PRIVATE:
        name = f"{message.chat.first_name}{message.chat.last_name or ''}"
    try:
        if len(message.command) < 2:
            chat_id = message.chat.id

            if chat_id not in blacklist:
                return await pp.edit(f"<blockquote>{em.gagal}`{name}` **is not in broadcast-db!**</blockquote>")
            await dB.remove_from_var(client.me.id, "BROADCASTDB", chat_id)
            return await pp.edit(f"<blockquote>{em.sukses}**Successfully delete `{name} 'from the broadcast list-db!**</blockquote>")
        else:
            if message.command[1] == "all":
                for A in blacklist:
                    await dB.remove_from_var(client.me.id, "BROADCASTDB", A)
                return await pp.edit(f"<blockquote>{em.sukses}Successfully delete all broadcast lists-DB!</blockquote>")
            else:
                chat_id = message.command[1]
                try:
                    chat_id = int(chat_id)
                except ValueError:
                    return await pp.edit(f"<blockquote>{em.gagal}**Please give a valid chat_id.Error `{chat_id}`!**</blockquote>")

                if chat_id not in blacklist:
                    return await pp.edit(f"<blockquote>{em.gagal}`{name}` **not in broadcast-db!**</blockquote>")
                await dB.remove_from_var(client.me.id, "BROADCASTDB", chat_id)
                return await pp.edit(f"<blockquote>{em.sukses}**Successfully delete `{name}` from the broadcast list-db!**</blockquote>")
    except Exception as er:
        return await pp.edit(f"{em.gagal}ERRORR: `{str(er)}`!!")


@CMD.UBOT("list-bcdb")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    blacklist = await dB.get_list_from_var(client.me.id, "BROADCASTDB")
    pp = await message.reply(f"{em.proses}**{proses_}**")
    if blacklist == []:
        return await pp.edit(f"<blockquote>{em.gagal}**Your broadcast-DB data is still empty!**</blockquote>")
    msg = f"<blockquote>{em.msg}**Total Broadcast-DB: {len(blacklist)}**\n\n</blockquote>"
    for num, x in enumerate(blacklist, 1):
        try:
            chat = await client.get_chat(x)
            name = chat.title or f"{chat.first_name} {chat.last_name or ''}"
            msg += f"**{num}. {name}|`{chat.id}`**\n"
        except Exception:
            msg += f"**{num}. `{x}`**\n"
    if len(msg) > 4096:
        link = await Tools.paste(msg)
        await pp.edit(f"<blockquote>{em.proses}**Message is too long, uploading to pastebin ...**</blockquote>")
        await asyncio.sleep(1)
        return await message.reply_text(
            f"<blockquote>{em.sukses}**<a href='{link}'>Click here </a> to see your broadcast list.**</blockquote>",
            disable_web_page_preview=True,
        )
    else:
        await pp.delete()
        return await message.reply_text(msg)


@CMD.UBOT("send")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if message.reply_to_message:
        chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
        try:
            if message.reply_to_message.reply_markup:
                state.set(client.me.id, "inline_send", id(message))
                query = f"inline_send {client.me.id}"
                
                bot_username = bot.me.username
                inline = await client.get_inline_bot_results(bot_username, query)
                if inline and inline.results:
                    await client.send_inline_bot_result(chat_id, inline.query_id, inline.results[0].id)
                    return await message.delete()
        except Exception as er:
            return await message.reply(f"<blockquote>{em.gagal}ERROR: {str(er)}</blockquote>")
        else:
            try:
                await message.reply_to_message.copy(chat_id)
                await message.delete()
                return
            except Exception as er:
                return await message.reply(f"<blockquote>{em.gagal}ERROR: {str(er)}</blockquote>")
    else:
        if len(message.command) < 3:
            return
        chat_id, chat_text = message.text.split(None, 2)[1:]
        try:
            if "/" in chat_id:
                to_chat, msg_id = chat_id.split("/")
                await client.send_message(to_chat, chat_text, reply_to_message_id=int(msg_id))
                await message.delete()
                return
            else:
                await client.send_message(chat_id, chat_text)
                await message.delete()
                return
        except Exception as er:
            return await message.reply(f"<blockquote>{em.gagal}ERROR: {str(er)}</blockquote>")
