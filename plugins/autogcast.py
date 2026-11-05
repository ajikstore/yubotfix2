import asyncio
import random
import gc
import time
from datetime import datetime, timedelta

import pytz
from pyrogram import raw
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from config import BLACKLIST_GCAST
from kelra import kelra
from kelra.database import dB
from kelra.helpers import CMD, Emoji
from kelra.logger import logger

from .spambot import spam_bot

__MODULES__ = "Autobc"
__HELP__ = """<blockquote>Command Help **Autobc**</blockquote>

<blockquote expandable>    <u>**Add text for autobc**</u>
        `{0}autobc add` (reply text)

    <u>**Set auto bc on or off**</u>
        `{0}autobc` (on/off)

    <u>**Delete text autobc**</u>
        `{0}autobc del` (number)

    <u>**Autobc cek limit**</u>
        `{0}autobc limit` (on/off)

    <u>**Set delay autobc**</u>
        `{0}autobc delay` (number)

    <u>**View text autobc**</u>
        `{0}autobc get`
 
<b><u>**Note**: Sistem kebal Restart, Auto-Pause jika kena limit, & Log VPS Bersih.</u></b></blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

AG = []
LT = []

def extract_type_and_text(message):
    args = message.text.split(None, 2)
    if len(args) < 2:
        return None, None
    type = args[1]
    msg = message.reply_to_message.text if message.reply_to_message else args[2] if len(args) > 2 else None
    return type, msg

async def text_autogcast(client):
    auto_text_vars = await dB.get_var(client.me.id, "AUTO_GCAST")
    list_text = []
    if auto_text_vars:
        for data in auto_text_vars:
            try:
                msg = await client.get_messages("me", int(data["message_id"]))
                list_text.append(msg.text)
            except:
                pass
    return list_text

async def check_spambot_status(client):
    """Fungsi Pinter buat ngecek SpamBot Realtime tanpa Cache"""
    try:
        await client.unblock_user("SpamBot")
        xin = await client.resolve_peer("SpamBot")
        
        try:
            await client.invoke(raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True))
        except:
            pass
        await asyncio.sleep(0.5)

        await client.send_message("SpamBot", "/start")
        await asyncio.sleep(2) 
        
        result = None
        async for status in client.get_chat_history("SpamBot", limit=1):
            if status.text:
                result = status.text
            break
            
        if not result:
            return False, "Aman"
            
        try:
            await client.invoke(raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True))
        except:
            pass
        
        aman_words = ["Good news", "Kabar baik", "tidak dibatasi", "free as a bird"]
        if any(word in result for word in aman_words):
            return False, "Aman"
        else:
            return True, result 
    except Exception:
        return False, "Gagal Cek"


# --- FUNGSI INTI AUTO BC ---
async def run_autobc(client, msg_obj=None):
    done = 0
    while client.me.id in AG:
        # Pengecekan Database (Biar singkron kalau di-off lewat perintah)
        is_active = await dB.get_var(client.me.id, "AUTOBC_ACTIVE")
        if not is_active:
            if client.me.id in AG:
                AG.remove(client.me.id)
            break

        # 1. CEK SPAMBOT (AUTO-PAUSE JIKA KENA LIMIT)
        is_limited, reason = await check_spambot_status(client)
        if is_limited:
            await dB.set_var(client.me.id, "AUTOBC_ACTIVE", False)
            if client.me.id in AG:
                AG.remove(client.me.id)
            try:
                alert_text = f"⚠️ **AUTO-BC DIJEDA OTOMATIS!**\nAkun kamu terdeteksi limit SpamBot.\n\n`{reason[:100]}...`\n\n*Fitur dimatikan sementara untuk mengamankan akun.*"
                await client.send_message("me", alert_text)
                if msg_obj:
                    await msg_obj.reply(f"<blockquote>{alert_text}</blockquote>")
            except: pass
            break 

        # 2. AMBIL DATA DARI DATABASE
        delay = await dB.get_var(client.me.id, "DELAY_GCAST") or 1
        blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST") or []
        auto_text_vars = await dB.get_var(client.me.id, "AUTO_GCAST")
        
        if not auto_text_vars:
            await dB.set_var(client.me.id, "AUTOBC_ACTIVE", False)
            if client.me.id in AG:
                AG.remove(client.me.id)
            break
            
        send_msg = [int(ax["message_id"]) for ax in auto_text_vars]
        txt = random.choice(send_msg)
        
        try:
            msg_id = await client.get_messages("me", txt)
        except:
            await asyncio.sleep(60)
            continue

        group = 0
        failed = 0
        
        # 3. KIRIM PESAN KE GROUP
        async for dialog in client.get_dialogs():
            if dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP) and dialog.chat.id not in blacklist and dialog.chat.id not in BLACKLIST_GCAST:
                try:
                    await asyncio.sleep(1.5)
                    await msg_id.copy(dialog.chat.id)
                    group += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    try:
                        await msg_id.copy(dialog.chat.id)
                        group += 1
                    except:
                        failed += 1
                except:
                    failed += 1

        if client.me.id not in AG:
            break

        done += 1
        
        # 4. LAPORAN LOG VPS (LEBIH SINGKAT)
        nama_akun = f"{client.me.first_name} {client.me.last_name or ''}".strip()
        logger.info(f"[AUTO-BC] {nama_akun} ({client.me.id}) | Sukses: {group} | Gagal: {failed} | Putaran: {done} | Delay: {delay}m")
        
        # Laporan ke Telegram (Hanya jika dijalankan manual)
        if msg_obj:
            wib = pytz.timezone("Asia/Jakarta")
            next_schedule = datetime.now(wib) + timedelta(minutes=int(delay))
            next_schedule_str = next_schedule.strftime('%H:%M:%S WIB')
            report_text = (
                f"<emoji id=5352712960982654265>📢</emoji> **Auto-BC Report**\n\n"
                f"<emoji id=5971867376130461576>👤</emoji> **Akun:** {nama_akun}\n"
                f"<emoji id=5231200819986047254>📊</emoji> **Berhasil:** `{group}` | **Gagal:** `{failed}`\n"
                f"<emoji id=5017470156276761427>🔄</emoji> **Putaran:** `{done}`\n"
                f"<emoji id=5382194935057372936>🔛</emoji> **Jadwal Berikutnya:** `{next_schedule_str}`"
            )
            try:
                await msg_obj.reply(f"<blockquote>{report_text}</blockquote>")
            except: pass
            
        # 5. PEMBERSIHAN CACHE (PENTING)
        del msg_id
        gc.collect() 
        
        await asyncio.sleep(int(60 * int(delay)))


@CMD.UBOT("autobc")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    proses_ = await em.get_costum_text()
    msg = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    type, value = extract_type_and_text(message)
    reply = message.reply_to_message
    
    if type == "on":
        auto_text_vars = await dB.get_var(client.me.id, "AUTO_GCAST")
        if not auto_text_vars:
            return await msg.edit(f"<blockquote>{em.gagal}**Please add custom text before setting it on!!**</blockquote>")
        
        if client.me.id not in AG:
            await dB.set_var(client.me.id, "AUTOBC_ACTIVE", True)
            AG.append(client.me.id)
            await msg.edit(f"<blockquote>{em.sukses}<b>Autobc online brok!</b></blockquote>")
            asyncio.create_task(run_autobc(client, msg))
        else:
            return await msg.edit(f"<blockquote>{em.gagal}<b>Autobc is already running!</b></blockquote>")

    elif type == "off":
        await dB.set_var(client.me.id, "AUTOBC_ACTIVE", False)
        if client.me.id in AG:
            AG.remove(client.me.id)
            return await msg.edit(f"<blockquote>{em.sukses}<b>Autobc has been stopped.</b></blockquote>")
        else:
            return await msg.delete()

    elif type == "add":
        if not reply:
            return await msg.edit(f"<blockquote>{em.gagal}<b>At least reply to a text to create the message.</b></blockquote>")
        await add_auto_text(message)
        return await msg.edit(f"<blockquote>{em.sukses}<b>Saved for Autobc message.</b></blockquote>")

    elif type == "delay":
        if not value or not value.isdigit():
            return await msg.edit(f"<blockquote>{em.gagal}<b>Please input valid number for delay.</b></blockquote>")
        await dB.set_var(client.me.id, "DELAY_GCAST", int(value))
        return await msg.edit(f"<blockquote>{em.sukses}<b>Autobc delay set to: <code>{value}</code> menit</b></blockquote>")

    elif type == "del":
        if not value:
            return await msg.edit(f"<blockquote>{em.gagal}<b>Provide a number or 'all' to delete.</b></blockquote>")
        auto_text_vars = await dB.get_var(client.me.id, "AUTO_GCAST")
        if value == "all":
            await dB.set_var(client.me.id, "AUTO_GCAST", [])
            return await msg.edit(f"<blockquote>{em.sukses}<b>All texts have been deleted.</b></blockquote>")
        try:
            value = int(value) - 1
            auto_text_vars.pop(value)
            await dB.set_var(client.me.id, "AUTO_GCAST", auto_text_vars)
            return await msg.edit(f"<blockquote>{em.sukses}<b>Text number: <code>{value+1}</code> deleted.</b></blockquote>")
        except Exception as error:
            return await msg.edit(str(error))

    elif type == "get":
        auto_text_vars = await dB.get_var(client.me.id, "AUTO_GCAST")
        if not auto_text_vars:
            return await msg.edit(f"<blockquote>{em.gagal}<b>Your Autobc text is empty.</b></blockquote>")
        txt = "<blockquote><b>Your Autobc Texts</b>\n\n</blockquote>"
        data = await text_autogcast(client)
        for num, x in enumerate(data, 1):
            txt += f"<blockquote>{num}: {x[:50]}...\n\n</blockquote>"
        return await msg.edit(txt)

    elif type == "limit":
        if value == "off":
            if client.me.id in LT:
                LT.remove(client.me.id)
                return await msg.edit(f"<blockquote>{em.gagal}<b>Auto Limit turned off.</b></blockquote>")
            else:
                return await msg.delete()

        elif value == "on":
            if client.me.id not in LT:
                LT.append(client.me.id)
                await msg.edit(f"<blockquote>{em.sukses}<b>Auto Limit turned on.</b></blockquote>")
                while client.me.id in LT:
                    for x in range(2):
                        await spam_bot(client, message)
                        await asyncio.sleep(5)
                    await asyncio.sleep(1200)
            else:
                return await msg.delete()
        else:
            return await msg.edit(f"<blockquote>{em.gagal}<b>Wrong query! Use on/off.</b></blockquote>")
    else:
        return await msg.edit(f"<blockquote>{em.gagal}<b>Wrong query! Use on/off/add/del/get/delay.</b></blockquote>")


async def add_auto_text(message):
    client = message._client
    auto_text = await dB.get_var(client.me.id, "AUTO_GCAST") or []
    rep = message.reply_to_message
    value = None
    type_mapping = {
        "text": rep.text, "photo": rep.photo, "voice": rep.voice,
        "audio": rep.audio, "video": rep.video, "video_note": rep.video_note,
        "animation": rep.animation, "sticker": rep.sticker, "document": rep.document,
        "contact": rep.contact,
    }
    for media_type, media in type_mapping.items():
        if media:
            send = await rep.copy("me")
            value = {"type": media_type, "message_id": send.id}
            break
    if value:
        auto_text.append(value)
        await dB.set_var(client.me.id, "AUTO_GCAST", auto_text)


# =========================================================
# DAEMON PENJAGA AUTOBC (Berjalan otomatis di background)
# =========================================================
async def daemon_autobc():
    """Fungsi ini akan terus berjalan di background buat nge-cek database"""
    await asyncio.sleep(20) # Tunggu Ubot selesai login setelah VPS direstart
    while True:
        try:
            for client in kelra._ubot:
                if client.me.id not in AG:
                    # Ambil status dari Database
                    is_active = await dB.get_var(client.me.id, "AUTOBC_ACTIVE")
                    if is_active:
                        AG.append(client.me.id)
                        asyncio.create_task(run_autobc(client))
                        logger.info(f"[DAEMON] Menghidupkan ulang Auto-BC untuk {client.me.id}")
        except Exception as e:
            logger.error(f"[DAEMON] Error: {e}")
        await asyncio.sleep(60)

# Langsung jalankan daemon saat file plugin ini dibaca
asyncio.get_event_loop().create_task(daemon_autobc())
