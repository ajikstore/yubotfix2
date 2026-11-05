import asyncio
import os
import sys
import traceback
from gc import get_objects
from uuid import uuid4

import requests
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.helpers import ikb
from pyrogram.types import InlineKeyboardButton as Ikb
from pyrogram.types import (
    InlineKeyboardMarkup,
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)
from pyrogram.utils import unpack_inline_message_id

from config import COPY_ID, SUDO_OWNERS, AKSES_DEPLOY
from kelra import bot, kelra
from kelra.database import dB, state
from kelra.helpers import CMD, ButtonUtils, Tools, gens_font, query_fonts, trigger
from kelra.logger import logger
from plugins.pmpermit import LIMIT

from .create_users import mari_buat_userbot
from .eval import eval_tasks, update_kode
from .help import cek_plugins
from .restart import reset_costum_text, reset_emoji, reset_prefix, restart_userbot
from .start import start_home
from .status import cek_status_akun
from .support import pengguna_nanya

MESSAGE_DICT = {}

@CMD.CALLBACK("^(buat_ubot|status_akun|cek_fitur|hubungi_admin|update_bot|claim_garansi|input_token|pengaturan|back_home|batal_garansi|reset_emoji|reset_prefix|reset_text|restart_ubot)$")
async def start_menu_callbacks(client, callback_query):
    data = callback_query.data
    message = callback_query.message
    message.from_user = callback_query.from_user 
    
    try:
        if data == "buat_ubot":
            await callback_query.answer()
            return await mari_buat_userbot(client, message)
        elif data == "status_akun":
            await callback_query.answer()
            return await cek_status_akun(client, callback_query)
        elif data == "cek_fitur":
            await callback_query.answer()
            return await cek_plugins(client, callback_query)
        elif data == "hubungi_admin":
            await callback_query.answer()
            return await contact_admins(client, message)
        elif data == "update_bot":
            await callback_query.answer("Checking updates...", show_alert=True)
            return await update_kode(client, message)
            
        # --- MENU SISTEM TOKEN ---
        elif data == "claim_garansi":
            await callback_query.answer()
            return await info_claim_garansi(client, callback_query)
        elif data == "input_token":
            await callback_query.answer()
            return await proses_claim_garansi(client, message)
        # -------------------------
            
        elif data == "pengaturan":
            await callback_query.answer()
            return await callback_query.edit_message_reply_markup(reply_markup=ButtonUtils.settings_menu())
        elif data == "back_home":
            await callback_query.answer()
            return await start_home(client, callback_query)
        elif data == "batal_garansi":
            await callback_query.answer("Dibatalkan", show_alert=True)
            await callback_query.message.delete()
            
        elif data == "reset_emoji":
            await callback_query.answer()
            return await reset_emoji(client, callback_query)
        elif data == "reset_prefix":
            await callback_query.answer()
            return await reset_prefix(client, callback_query)
        elif data == "reset_text":
            await callback_query.answer()
            return await reset_costum_text(client, callback_query)
        elif data == "restart_ubot":
            await callback_query.answer("Restarting Userbot...", show_alert=True)
            return await restart_userbot(client, callback_query)
            
    except Exception as er:
        logger.error(f"Terjadi error Callback Start: {str(er)}")

async def info_claim_garansi(client, callback_query):
    teks_info = """<b>🔑 SISTEM TOKEN</b>

<b>Apa itu Token?</b>
Token kamu berfungsi untuk mengklaim garansi ubot dalam kondisi:
• Jika kamu ingin berpindah akun Telegram
• Jika akunmu dibanned oleh pihak Telegram
• Jika kamu perlu menginstall ulang userbot

<b>Perhatian:</b>
• Setiap token memiliki batas penggunaan maksimal 3 kali
• Token hanya bisa digunakan oleh pemiliknya
• Simpan token kamu dengan aman, jangan dibagikan

<b>Cara Kerja:</b>
Token berperan sebagai kunci akses untuk memindahkan layanan userbot dari satu akun ke akun lainnya tanpa harus membayar ulang.

<b>PENTING:</b> Mohon simpan Token kamu dengan aman!"""

    buttons = ikb([
        [("📝 Input Token", "input_token", "callback_data")],
        [("🔙 Kembali", "back_home", "callback_data")]
    ])

    await callback_query.edit_message_text(teks_info, reply_markup=buttons, disable_web_page_preview=True)


async def proses_claim_garansi(client, message):
    user_id = message.chat.id
    try:
        ask = await client.ask(
            user_id,
            "🛡 **Silakan kirimkan Token Garansi Anda.**\n\n*Ketik 'batal' atau klik tombol di bawah untuk membatalkan.*",
            reply_markup=ikb([[("❌ Batal", "batal_garansi", "callback_data")]]),
            timeout=60
        )
        if ask.text and ask.text.lower() == "batal":
            return await ask.reply("❌ Claim garansi dibatalkan.")
            
        token = ask.text.strip().upper()
        data_garansi = await dB.get_var(bot.id, f"GARANSI_{token}")
        
        if not data_garansi:
            return await ask.reply("❌ **Token Garansi tidak valid atau tidak ditemukan!**")
            
        usage_count = data_garansi.get("usage_count", 0)
        max_usage = data_garansi.get("max_usage", 3)
        
        if usage_count >= max_usage:
            return await ask.reply(f"⚠️ **Batas penggunaan Token ini sudah habis! ({max_usage}/{max_usage})**")
            
        # ========================================================
        # KILL SWITCH: HANCURKAN UBOT LAMA & LOGOUT SESI TELEGRAM
        # ========================================================
        old_ubot_id = data_garansi.get("ubot_id")
        if old_ubot_id:
            # 1. Cari bot yang lama di memory, lalu Log Out (Sesi Telegram terhapus)
            for X in kelra._ubot:
                if X.me.id == old_ubot_id:
                    try:
                        await X.log_out() # Ini bikin "Devices" di pengaturan Telegram lama otomatis keluar
                    except Exception:
                        pass
                    kelra._ubot.remove(X)
                    break
            
            # 2. Hapus data bot lama dari Database
            try:
                await dB.remove_ubot(old_ubot_id)
                await dB.rem_expired_date(old_ubot_id)
                if old_ubot_id in kelra._get_my_id:
                    kelra._get_my_id.remove(old_ubot_id)
            except Exception:
                pass
        # ========================================================
            
        # Update hitungan penggunaan
        data_garansi["usage_count"] = usage_count + 1
        # Hapus ubot_id lama agar siap diisi ubot_id baru
        data_garansi["ubot_id"] = None 
        await dB.set_var(bot.id, f"GARANSI_{token}", data_garansi)
        
        # Pindahkan masa aktif (expired date) lama ke peminta garansi
        exp_date_str = data_garansi.get("expired_date")
        if exp_date_str:
            await dB.set_expired_date(user_id, exp_date_str)
        
        # Berikan Akses Deploy ke Nomor Baru
        from config import AKSES_DEPLOY
        if user_id not in AKSES_DEPLOY:
            AKSES_DEPLOY.append(user_id)
            
        sisa_claim = max_usage - (usage_count + 1)
        await ask.reply(f"✅ **Garansi Berhasil Di-Claim!**\nSisa penggunaan token: {sisa_claim} kali.\n\nSesi pada akun lama otomatis diputuskan 📴.\nSekarang akun ini mewarisi masa aktif sebelumnya. Silakan klik tombol 'Mulai Buat Userbot' pada menu utama.")
        
    except asyncio.TimeoutError:
        await client.send_message(user_id, "⏳ Waktu habis. Silakan coba lagi.")
    except Exception as e:
        logger.error(f"Error claim garansi: {e}")

@CMD.REGEX(trigger)
async def _(client, message):
    try:
        text = message.text
        if text in [
            "✨ Mulai Buat Userbot",
            "✨ Pembuatan Ulang Userbot",
            "✅ Lanjutkan Buat Userbot",
        ]:
            return await mari_buat_userbot(client, message)
        elif text == "❓ Status Akun":
            return await cek_status_akun(client, message)
        elif text.startswith("🔄 Reset"):
            data = text.split(" ")[2]
            if data == "Emoji":
                return await reset_emoji(client, message)
            elif data == "Prefix":
                return await reset_prefix(client, message)
            elif data == "Text":
                return await reset_costum_text(client, message)
        elif text == "🔄 Restart Userbot":
            return await restart_userbot(client, message)
        elif text == "🚀 Updates":
            return await update_kode(client, message)
        elif text == "🛠️ Cek Fitur":
            return await cek_plugins(client, message)
        elif text == "🤔 Pertanyaan":
            return await pengguna_nanya(client, message)
        elif text == "💬 Hubungi Admins":
            return await contact_admins(client, message)
        elif text == "↩️ Beranda":
            return await start_home(client, message)
    except Exception as er:
        logger.error(f"Terjadi error: {str(er)}")

@CMD.CALLBACK("^Canceleval")
async def _(_, callback_query):
    await callback_query.answer()
    reply_message_id = callback_query.message.reply_to_message_id
    if not reply_message_id:
        return
    def cancel_task(task_id) -> bool:
        task = eval_tasks.get(task_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False
    canceled = cancel_task(reply_message_id)
    if not canceled:
        return

async def contact_admins(client, message):
    new_msg = "<b><emoji id=5447183459602669338>👑</emoji>Dibawah ini adalah Admins Saya. Kamu dapat menghubungi salah satu dari mereka.</b>"
    tombol = []
    row = []
    for admin in SUDO_OWNERS:
        try:
            user = await client.get_users(admin)
            owner_name = user.first_name
            row.append(Ikb(owner_name, user_id=f"{user.id}"))
            if len(row) == 2:
                tombol.append(row)
                row = []
        except Exception:
            continue
    if row:
        tombol.append(row)
    tombol.append([Ikb(text="❌ Tutup", callback_data="closed")])
    markup = InlineKeyboardMarkup(tombol)
    
    is_cb = hasattr(message, "data")
    if is_cb:
        msg_obj = message.message
        if msg_obj.media:
            return await msg_obj.edit_caption(new_msg, reply_markup=markup)
        else:
            return await msg_obj.edit_text(new_msg, reply_markup=markup)
    return await message.reply(new_msg, reply_markup=markup)

@CMD.CALLBACK("^close")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        user = callback_query.from_user
        split = callback_query.data.split(maxsplit=1)[1]
        data = state.get(user.id, split)
        if not data:
            return await callback_query.answer("This button not for you fvck!!", True)
        message = next((obj for obj in get_objects() if id(obj) == int(data["idm"])), None)
        c = message._client
        state.clear_client(c.me.id)
        return await c.delete_messages(int(data["chat"]), int(data["_id"]))
    except Exception as er:
        logger.error(f"{str(er)}")

@CMD.CALLBACK("^cb_pm")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        data = callback_query.data.split()
        user = callback_query.from_user.id
        maling = int(data[3])
        polisi = int(data[2])
        pm_ok = await dB.get_list_from_var(polisi, "PM_OKE")
        if data[1] == "ok":
            if user != polisi:
                return await callback_query.answer("This button not for you fvck!!", True)
            if maling not in pm_ok:
                await dB.add_to_var(polisi, "PM_OKE", maling)
                return await callback_query.edit_message_text("<b>User has been approved to send message.</b>")
            else:
                return await callback_query.edit_message_text("<b>This user is already approved</b>")
        elif data[1] == "no":
            if user != polisi:
                return await callback_query.answer("This button not for you fvck!!", True)
            if maling in pm_ok:
                await dB.remove_from_var(polisi, "PM_OKE", maling)
                return await callback_query.edit_message_text("<b>User has been disapproved to send message.</b>")
            else:
                return await callback_query.edit_message_text("<b>This user is already disapproved</b>")
        elif data[1] == "warn":
            Flood = state.get(polisi, maling)
            pm_warns = await dB.get_var(polisi, "PMLIMIT") or LIMIT
            return await callback_query.answer(
                f"⚠️ You have a chance {Flood}/{pm_warns} ❗\n\nIf you insist on sending messages continuously then you will be ⛔ blocked automatically and we will 📢 report your account as spam",
                True,
            )
    except Exception as er:
        logger.error(f"ERROR: {str(er)}, line: {sys.exc_info()[-1].tb_lineno}")

@CMD.CALLBACK("^cb_gc_info")
async def _(client, callback_query):
    await callback_query.answer()
    cek = state.get(client.me.id, "gc_info")
    state.set(client.me.id, "desc_gc", cek)
    usr = cek["username"]
    if usr is None:
        keyb = ikb([[("Desc", f"cb_desc {cek['id']}", "callback_data")]])
    else:
        keyb = ikb([[("Chat", f"https://t.me/{usr}", "url"), ("Desc", f"cb_desc {cek['id']}", "callback_data")]])
    msg = f"""
<b>ChatInfo:</b>
   <b>name:</b> <b>{cek['name']}</b>
      <b>id:</b> <code>{cek['id']}</code>
      <b>type:</b> <b>{cek['type']}</b>
      <b>dc_id:</b> <b>{cek['dc_id']}</b>
      <b>username:</b> <b>@{cek['username']}</b>
      <b>member:</b> <b>{cek['member']}</b>
      <b>protect:</b> <b>{cek['protect']}</b>
"""
    return await callback_query.edit_message_text(msg, reply_markup=keyb)

@CMD.CALLBACK("^cb_desc")
async def _(client, callback_query):
    await callback_query.answer()
    query = callback_query.data.split(None, 1)
    id_gc = query[1]
    data = state.get(client.me.id, "gc_info")
    if int(id_gc) == int(data["id"]):
        return await callback_query.answer(f"{data['desc']}", True)
    else:
        return await callback_query.answer("Tidak ada perasaan ini", True)

@CMD.CALLBACK("^copymsg")
async def _(client, callback_query):
    await callback_query.answer()
    try:
        get_id = int(callback_query.data.split("_", 1)[1])
        message = [obj for obj in get_objects() if id(obj) == get_id][0]
        await message._client.unblock_user(bot.me.username)
        await callback_query.edit_message_text("<b>Proses Upload...</b>")
        copy = await message._client.send_message(bot.me.username, f"/kontol {message.text.split()[1]}")
        msg = message.reply_to_message or message
        await asyncio.sleep(1.5)
        await copy.delete()
        async for get in message._client.search_messages(bot.me.username, limit=1):
            await message._client.copy_message(message.chat.id, bot.me.username, get.id, reply_to_message_id=msg.id)
            await message._client.delete_messages(message.chat.id, COPY_ID[message._client.me.id])
            await get.delete()
    except Exception as error:
        await callback_query.edit_message_text(f"**ERROR:** <code>{error}</code>")

@CMD.CALLBACK("^cb")
async def _(client, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")
    btn_close = state.get("close_notes", "get_note")
    dia = callback_query.from_user
    type_mapping = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "animation": InputMediaAnimation,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    try:
        notetag = data[-2].replace("cb_", "")
        gw = data[-1]
        item = [x for x in mmk._ubot if int(gw) == x.me.id]
        noteval = await dB.get_var(int(gw), notetag, "notes")

        if not noteval:
            await callback_query.answer("Catatan tidak ditemukan.", True)
            return

        full = f"<a href=tg://user?id={dia.id}>{dia.first_name} {dia.last_name or ''}</a>"
        await dB.add_userdata(dia.id, dia.first_name, dia.last_name, dia.username, dia.mention, full, dia.id)

        for me in item:
            tks = noteval["result"].get("text")
            note_type = noteval["type"]
            file_id = noteval.get("file_id")
            note, button = ButtonUtils.parse_msg_buttons(tks)
            teks = await Tools.escape_tag(bot, dia.id, note, Tools.parse_words)
            button = ButtonUtils.create_inline_keyboard(button, int(gw))
            for row in btn_close.inline_keyboard:
                button.inline_keyboard.append(row)
            try:
                if note_type == "text":
                    await callback_query.edit_message_text(text=teks, reply_markup=button)
                elif note_type in type_mapping and file_id:
                    InputMediaType = type_mapping[note_type]
                    media = InputMediaType(media=file_id, caption=teks)
                    await callback_query.edit_message_media(media=media, reply_markup=button)
                else:
                    await callback_query.edit_message_caption(caption=teks, reply_markup=button)
            except FloodWait as e:
                return await callback_query.answer(f"FloodWait {e}, Please Waiting!!", True)
            except MessageNotModified:
                pass
    except Exception as e:
        return await callback_query.answer("Terjadi kesalahan saat memproses catatan.", True)

from kelra.database import state

@CMD.CALLBACK("^(get_font|next_font|prev_font)")
async def handle_font_buttons(client, callback_query):
    try:
        data = callback_query.data.split()
        aksi = data[0]
        user_id = int(data[1])

        if callback_query.from_user.id != user_id:
            return await callback_query.answer("❌ Ini bukan sesi font milikmu!", show_alert=True)

        if aksi == "get_font":
            tipe_font = data[2]
            text_asli = state.get(user_id, "FONT")
            
            if not text_asli:
                return await callback_query.answer("⚠️ Sesi teks sudah habis. Silakan ketik perintah .font lagi.", show_alert=True)

            current_batch = 0
            try:
                if callback_query.message.reply_markup:
                    last_row = callback_query.message.reply_markup.inline_keyboard[-1]
                    for btn in last_row:
                        if btn.callback_data and "prev_font" in btn.callback_data:
                            current_batch = int(btn.callback_data.split()[-1])
                            break
            except Exception:
                pass

            teks_baru = gens_font(tipe_font, text_asli)
            from pyrogram.types import InlineKeyboardMarkup
            keyboard = ButtonUtils.create_font_keyboard(query_fonts[current_batch], user_id, current_batch=current_batch)
            markup = InlineKeyboardMarkup(keyboard)
            await callback_query.edit_message_text(
                f"**Hasil:**\n\n<code>{teks_baru}</code>\n\n<i>*(Klik teks di atas untuk copy)*</i>", 
                reply_markup=markup
            )
            
        elif aksi in ("next_font", "prev_font"):
            current_batch = int(data[2])
            num_batches = len(query_fonts)
            
            if aksi == "next_font":
                new_batch = (current_batch + 1) % num_batches
            else:
                new_batch = (current_batch - 1) % num_batches
                
            keyboard = ButtonUtils.create_font_keyboard(query_fonts[new_batch], user_id, current_batch=new_batch)
            from pyrogram.types import InlineKeyboardMarkup
            markup = InlineKeyboardMarkup(keyboard)
            
            await callback_query.edit_message_reply_markup(reply_markup=markup)
            await callback_query.answer()
            
    except Exception as e:
        logger.error(f"Error di handle_font_buttons: {str(e)}")
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

# ==========================================
# CALLBACK HANDLER FONT BAHASA (FONTBS)
# ==========================================
@CMD.CALLBACK("^fb_")
async def fontbs_callback(client, callback_query):
    try:
        # Pecah data dari tombol (misal: fb_🇯🇵 Jepang_teks)
        data = callback_query.data.split("_", 2)
        if len(data) < 2:
            return await callback_query.answer("Data error!", True)
            
        style = data[1]
        
        # Ambil full text dari database state
        user_id = callback_query.from_user.id
        text = state.get(user_id, "FONTBS")
        
        if not text:
            return await callback_query.answer("Teks tidak ditemukan atau sesi habis!", show_alert=True)
            
        maps = {
            "🇯🇵 Jepang": "卂乃匚刀乇下厶卄丨丁长乚爪𠘨口尸",
            "🇨🇳 China": "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩",
            "🇷🇺 Rusia": "αвc∂єƒgнιנкℓмησρqяѕтυνωку",
            "🇹🇭 Thai": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇸🇦 Arab": "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩ",
            "🇰🇷 Korea": "闩乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩ",
            "🇮🇳 India": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇻🇳 Vietnam": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇬🇷 Yunani": "αвcdєfghijкlмиσpqrѕтuvwхy",
            "🇮🇩 Jawa": "ꦄꦧꦕꦢꦌꦥꦖꦲꦶꦙꦏꦊꦩꦤꦴꦥꦥꦴꦫꦱ",
            "🇧🇩 Bengali": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇬🇪 Georgia": "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩ",
            "🇦🇲 Armenia": "卂乃匚刀乇下厶卄丨丁长乚爪𠘨口尸 সুবিধ",
            "🇮🇱 Israel": "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩ",
            "🇱🇦 Laos": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇰🇭 Kamboja": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇲🇲 Myanmar": "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬא",
            "🇧🇹 Tibet": "卂乃匚刀乇下厶卄丨丁长乚爪𠘨口尸 সুবিধ",
            "🇲🇳 Mongolia": "αвc∂єƒgнιנкℓмησρqяѕтυνωку",
            "🇪🇹 Ethiopia": "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩ"
        }
        
        # Bypass error maketrans wajib 26 huruf
        abc = "abcdefghijklmnopqrstuvwxyz"
        trans = maps.get(style, abc)
        trans_padded = (trans + abc)[:26]
        
        # Terjemahkan
        hasil = text.lower().translate(str.maketrans(abc, trans_padded))
        
        # Ganti isi pesan dengan hasil teks
        await callback_query.edit_message_text(f"<b>Hasil {style}:</b>\n\n<code>{hasil}</code>")
        
    except Exception as e:
        logger.error(f"Error di fontbs callback: {str(e)}")
        await callback_query.answer(f"Terjadi kesalahan saat proses.", show_alert=True)

import asyncio
from plugins.jaseb import JASEB_RUNNING, JASEB_TASKS, run_jaseb_loop
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_callback_query(filters.regex(r"^jsb_start_"))
async def on_jaseb_start(client, callback_query):
    data = callback_query.data.split("_")
    user_id = int(data[2])
    interval = int(data[3]) 
    
    if JASEB_RUNNING.get(user_id, False):
        return await callback_query.answer("⚠️ Jaseb sudah berjalan! Matikan dulu dengan .jaseb off", show_alert=True)

    JASEB_RUNNING[user_id] = True
    
    # PERHATIKAN: ganti 'client' dengan variable ubot mu jika diperlukan oleh base Kelra
    task = asyncio.create_task(run_jaseb_loop(client, user_id, interval))
    JASEB_TASKS[user_id] = task
    
    menit = interval // 60
    await callback_query.edit_message_text(
        f"<blockquote>✅ **JASEB BERHASIL DIAKTIFKAN!**\n\n"
        f"Pesan dikirim setiap **{menit} Menit**.\n"
        f"Cek `Saved Messages` untuk log auto-broadcast.</blockquote>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Matikan Jaseb", callback_data=f"jsb_cancel_{user_id}")]])
    )

@Client.on_callback_query(filters.regex(r"^jsb_cancel_"))
async def on_jaseb_cancel(client, callback_query):
    data = callback_query.data.split("_")
    user_id = int(data[2])

    if user_id in JASEB_RUNNING and JASEB_RUNNING[user_id]:
        JASEB_RUNNING[user_id] = False
        
        if user_id in JASEB_TASKS and JASEB_TASKS[user_id]:
            JASEB_TASKS[user_id].cancel()
            del JASEB_TASKS[user_id]

        await callback_query.edit_message_text("<blockquote>🛑 **Jaseb berhasil DIMATIKAN.**</blockquote>")
    else:
        await callback_query.answer("⚠️ Jaseb sedang tidak aktif.", show_alert=True)
