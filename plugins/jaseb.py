import asyncio
import os
from datetime import datetime
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

# Sesuaikan dengan struktur Kelra[span_2](start_span)[span_2](end_span)[span_3](start_span)[span_3](end_span)
from config import BLACKLIST_GCAST, DEVS
from kelra import bot
from kelra.database import dB
from kelra.helpers import CMD, Emoji
from kelra.helpers.emoji_logs import get_auto_effect

# Database lokal memori Jaseb
JASEB_MSG = {}
JASEB_IS_REPLY = {}
JASEB_RUNNING = {}
JASEB_TASKS = {}

__MODULES__ = "Jaseb"
__HELP__ = """<blockquote>Command Help **Jaseb**</blockquote>

<blockquote expandable>    <u>**Set / Start Auto-Broadcast**</u>
        `.jaseb` (text/reply text)
        Menyimpan pesan ke database dan memunculkan menu durasi via Inline Bot.

    <u>**Mengaktifkan Jaseb**</u>
        `.jaseb on`
        Memunculkan menu durasi untuk pesan yang sudah tersimpan.

    <u>**Mematikan Jaseb**</u>
        `.jaseb off`
        Menghentikan proses Auto-Broadcast secara paksa.

    <u>**Menghapus Database Jaseb**</u>
        `.deljaseb`
        Menghapus pesan tersimpan dari database.</blockquote>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

@CMD.UBOT("jaseb")
@CMD.FAKEDEV("jaseb")
async def cmd_jaseb_main(client, message):
    em = Emoji(client)
    await em.get() 
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text() 
    user_id = client.me.id

    cmd_arg = message.command[1].lower() if len(message.command) > 1 else ""

    if cmd_arg == "off":
        if JASEB_RUNNING.get(user_id, False):
            JASEB_RUNNING[user_id] = False
            if user_id in JASEB_TASKS and JASEB_TASKS[user_id]:
                JASEB_TASKS[user_id].cancel()
                del JASEB_TASKS[user_id]
            return await message.reply(f"<blockquote>{em.sukses} **Jaseb Auto-Broadcast berhasil DIMATIKAN.**</blockquote>")
        else:
            return await message.reply(f"<blockquote>{em.gagal} **Tidak ada Jaseb yang sedang berjalan.**</blockquote>")

    elif cmd_arg == "on":
        if user_id not in JASEB_MSG or not JASEB_MSG[user_id]:
            return await message.reply(f"<blockquote>{em.gagal} **Database Jaseb kosong!**\nSilakan reply/ketik pesan dengan `.jaseb (pesan)` terlebih dahulu.</blockquote>")
        proses = await message.reply(f"<blockquote>{em.proses} **Memuat menu Jaseb...**</blockquote>")
    else:
        # Ekstrak pesan dari command atau reply
        text = client.get_message(message) 
        if not text: 
            return await message.reply(f"<blockquote>{em.gagal}<code>{message.text.split()[0]}</code> <b>text or give text / on / off</b></blockquote>") 
        
        JASEB_MSG[user_id] = text 
        JASEB_IS_REPLY[user_id] = bool(message.reply_to_message) 
        
        proses = await message.reply(f"<blockquote>{em.sukses} **Pesan disimpan!**\n{em.proses} Memuat menu durasi...</blockquote>")

    # LOGIC PROPER: Panggil Bot Assistant untuk render tombol
    try:
        bot_username = bot.me.username
        inline = await client.get_inline_bot_results(bot_username, f"jaseb_menu_{user_id}")
        
        if inline and inline.results:
            await client.send_inline_bot_result(message.chat.id, inline.query_id, inline.results[0].id)
            if 'proses' in locals():
                await proses.delete()
        else:
            raise Exception("Bot pendamping tidak merespon query inline.")
    except Exception as e:
        await message.reply(f"<blockquote>{em.gagal} **Gagal memuat tombol!**\nPastikan Assistant Bot aktif dan file `inline.py` sudah diupdate.\nError: {str(e)}</blockquote>")

@CMD.UBOT("deljaseb")
@CMD.FAKEDEV("deljaseb")
async def cmd_deljaseb(client, message):
    em = Emoji(client)
    await em.get() 
    user_id = client.me.id

    if user_id in JASEB_MSG:
        del JASEB_MSG[user_id]
        if user_id in JASEB_IS_REPLY:
            del JASEB_IS_REPLY[user_id]
        return await message.reply(f"<blockquote>{em.sukses} **Database pesan Jaseb berhasil DIHAPUS.**</blockquote>")
    else:
        return await message.reply(f"<blockquote>{em.gagal} **Database Jaseb sudah kosong.**</blockquote>")

# --- FUNGSI BACKGROUND LOOP ---
async def run_jaseb_loop(client, user_id, interval):
    em = Emoji(client)
    await em.get() 
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text() 
    effect_id = get_auto_effect(client) 
    
    saved_msg = JASEB_MSG.get(user_id)
    is_reply = JASEB_IS_REPLY.get(user_id, False)

    if not saved_msg:
        return

    # Setup variabel dinamis format WIB
    wib = pytz.timezone("Asia/Jakarta") 
    hari_map = { 
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }

    while JASEB_RUNNING.get(user_id, False):
        chats = await client.get_chat_id("group") 
        blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") 
        
        done, failed = 0, 0 
        error_log = f"<blockquote>{em.gagal}**Error failed jaseb:**\n</blockquote>" 
        total_member = len(chats) 

        # Mengirim notif murni teks ke "me" (tanpa inline button agar tidak error di UBOT)
        try:
            await client.send_message("me", f"<blockquote>{em.proses} <b>Memulai Jaseb Auto-Broadcast...</b>\n<i>Ketik <code>.jaseb off</code> di obrolan mana saja untuk mematikan.</i></blockquote>")
        except:
            pass

        for chat_id in chats: 
            if not JASEB_RUNNING.get(user_id, False):
                break
            
            if chat_id in blacklist or chat_id in BLACKLIST_GCAST or chat_id in DEVS: 
                continue

            try:
                now = datetime.now(wib) 
                jam = now.strftime("%H:%M") 
                tanggal = now.strftime("%d-%m-%Y") 
                hari = hari_map[now.strftime("%A")] 

                chat_info = await client.get_chat(chat_id) 
                nama_group = chat_info.title if hasattr(chat_info, "title") else str(chat_id) 

                if is_reply: 
                    msg_to_send = saved_msg.text if hasattr(saved_msg, "text") and saved_msg.text else "" 
                else:
                    msg_to_send = saved_msg.text if hasattr(saved_msg, "text") else str(saved_msg)

                # Replace variabel dinamis (hanya jika ada teks)
                if msg_to_send:
                    msg_to_send = (
                        msg_to_send
                        .replace("{gc}", nama_group) 
                        .replace("{jam}", jam) 
                        .replace("{tanggal}", tanggal) 
                        .replace("{member}", str(total_member)) 
                        .replace("{hari}", hari) 
                        .replace("{wib}", jam) 
                    )

                if is_reply: 
                    await saved_msg.copy(chat_id) 
                else:
                    try:
                        await client.send_message( 
                            chat_id,
                            msg_to_send,
                            effect_id=effect_id, 
                            disable_web_page_preview=True, 
                        )
                    except Exception:
                        await client.send_message( 
                            chat_id,
                            msg_to_send,
                            disable_web_page_preview=True, 
                        )
                done += 1 
                await asyncio.sleep(0.5)

            except ChannelPrivate:
                error_log += f"ChannelPrivate {chat_id}\n" 
            except SlowmodeWait:
                error_log += f"SlowmodeWait {chat_id}\n" 
                failed += 1 
            except ChatWriteForbidden:
                error_log += f"ChatWriteForbidden {chat_id}\n" 
                failed += 1 
            except Forbidden:
                error_log += f"Forbidden {chat_id}\n" 
                failed += 1 
            except ChatSendPlainForbidden:
                error_log += f"ChatSendPlainForbidden {chat_id}\n" 
                failed += 1 
            except UserBannedInChannel:
                error_log += f"UserBannedInChannel {chat_id}\n" 
                failed += 1 
            except PeerIdInvalid:
                error_log += f"PeerIdInvalid {chat_id}\n" 
            except FloodWait as e:
                await asyncio.sleep(e.value) 
                try:
                    if is_reply: 
                        await saved_msg.copy(chat_id) 
                    else:
                        await client.send_message(chat_id, msg_to_send, effect_id=effect_id, disable_web_page_preview=True) 
                    done += 1
                except Exception:
                    failed += 1 
            except Exception as err:
                failed += 1 
                error_log += f"{str(err)}\n" 

        if JASEB_RUNNING.get(user_id, False):
            report_text = (
                f"<blockquote expandable><b> {em.warn}{sukses_} (JASEB DONE)</b>\n"
                f"<b>{em.sukses}Success: {done}</b>\n" 
                f"<b>{em.gagal}Failed: {failed}</b>\n" 
                f"<b>{em.msg}Type: Auto-Group</b>\n"
                f"<b>{em.profil}{owner_}</b>\n\n" 
                f"<i>⏱ Menunggu putaran selanjutnya...\nKetik <code>.jaseb off</code> untuk menghentikan total.</i></blockquote>"
            )
            try:
                await client.send_message("me", report_text)
            except:
                pass
            
            try:
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
