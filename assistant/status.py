from time import time
from pyrogram.raw.functions import Ping
from pyrogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from pytz import timezone

from config import BOT_NAME, SUDO_OWNERS
from kelra import kelra
from kelra.database import dB
from kelra.helpers import CMD, get_time, start_time

@CMD.BOT("close")
async def _(client, message):
    return await message.reply_text("<b>Keyboard Ditutup</b>", reply_markup=ReplyKeyboardRemove())

async def cek_status_akun(client, message):
    is_cb = hasattr(message, "data")
    user_id = message.from_user.id
    seles = await dB.get_list_from_var(client.me.id, "SELLER")
    
    status2 = "aktif" if user_id in kelra._get_my_id else "tidak aktif"
        
    if user_id in SUDO_OWNERS: status = "<b>[Admins]</b>"
    elif user_id in seles: status = "<b>[Seller]</b>"
    else: status = "<b>[Costumer]</b>"
        
    uptime = await get_time((time() - start_time))
    await client.invoke(Ping(ping_id=0))
    exp = await dB.get_expired_date(user_id)
    habis = exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M") if exp else "None"
    prefix = client.get_prefix(user_id)
    
    keyboard_inline = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="back_home")]])
    
    text_status = f"""
<blockquote>
<b><emoji id=5420120668807123670>👑</emoji> {BOT_NAME}</b>
    <b><emoji id=6030400221232501136>👑</emoji>Status Ubot:</b> <code>{status2}</code>
    <b><emoji id=6032994772321309200>👑</emoji>Status Pengguna:</b> <i>{status}</i>
    <b><emoji id=5445128296276718145>👑</emoji>Prefixes :</b> <code>{' '.join(prefix)}</code>
    <b><emoji id=5775896410780079073>👑</emoji>Tanggal Kedaluwarsa:</b> <code>{habis}</code>
    <b><emoji id=5775896410780079073>👑</emoji>Uptime Ubot:</b> <code>{uptime}</code>
</blockquote>
"""
    if is_cb:
        msg_obj = message.message
        if msg_obj.media:
            return await msg_obj.edit_caption(text_status, reply_markup=keyboard_inline)
        else:
            return await msg_obj.edit_text(text_status, reply_markup=keyboard_inline)
    else:
        return await message.reply(text_status, reply_markup=keyboard_inline)
