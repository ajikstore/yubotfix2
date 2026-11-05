import asyncio
import importlib

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME
from kelra import UserBot, bot, kelra
from kelra.database import dB
from kelra.helpers import CMD, Emoji
from plugins import PLUGINS

# Menggunakan Inline Keyboard untuk kembali ke Pengaturan
keyboard_inline = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="pengaturan")]])

async def reset_costum_text(client, message):
    user_id = message.from_user.id
    
    # Jika dipanggil dari inline (memiliki atribut callback_query_message)
    if hasattr(message, "message") and hasattr(message, "data"):
        proses = message.message
    else:
        proses = await message.reply("<b>Processing...</b>")
        
    if user_id not in kelra._get_my_id:
        return await proses.edit(f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard_inline)
        
    try:
        await dB.set_var(user_id, "text_ping", "Ping")
        await dB.set_var(user_id, "text_uptime", "Uptime")
        owner_name = f"<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a>"
        await dB.set_var(user_id, "text_owner", f"Owner: {owner_name}")
        await dB.set_var(user_id, "text_ubot", f"{BOT_NAME}")
        await dB.set_var(user_id, "text_gcast", "Proses")
        await dB.set_var(user_id, "text_sukses", "Gcast Sukses")
        await asyncio.sleep(1)
        return await proses.edit("<b>Your costum text has been reset</b>", reply_markup=keyboard_inline)
    except Exception as er:
        return await proses.edit(f"<b>ERROR: `{str(er)}`</b>", reply_markup=keyboard_inline)


async def reset_emoji(client, message):
    user_id = message.from_user.id
    
    if hasattr(message, "message") and hasattr(message, "data"):
        proses = message.message
    else:
        proses = await message.reply("<b>Processing...</b>")
        
    if user_id not in kelra._get_my_id:
        return await proses.edit(f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard_inline)
        
    for User in kelra._ubot:
        if user_id == User.me.id:
            try:
                em = Emoji(User)
                await em.reset_emoji()
                await asyncio.sleep(1)
                return await proses.edit("<b>Your costum emoji has been reset.!!</b>", reply_markup=keyboard_inline)
            except Exception as er:
                return await proses.edit(f"<b>ERROR: `{str(er)}`</b>", reply_markup=keyboard_inline)


async def reset_prefix(client, message):
    mepref = [".", ",", "?", "+", "!"]
    user_id = message.from_user.id
    
    if hasattr(message, "message") and hasattr(message, "data"):
        proses = message.message
    else:
        proses = await message.reply("<b>Processing...</b>")
        
    if user_id not in kelra._get_my_id:
        return await proses.edit(f"<b><emoji id=5206607081334906820>👑</emoji>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard_inline)
        
    for x in kelra._ubot:
        if x.me.id == user_id:
            x.set_prefix(x.me.id, mepref)
            await dB.set_pref(x.me.id, mepref)
            return await proses.edit(
                f"<b>Your prefix has been reset to: `{' '.join(mepref)}` .</b>",
                reply_markup=keyboard_inline,
            )


async def restart_userbot(client, message):
    user_id = message.from_user.id
    
    if hasattr(message, "message") and hasattr(message, "data"):
        proses = message.message
    else:
        proses = await message.reply("<b>Processing...</b>")
        
    if user_id not in kelra._get_my_id:
        return await proses.edit(f"<b>You are not user @{bot.me.username}!!</b>", reply_markup=keyboard_inline)
        
    for X in await dB.get_userbots():
        if user_id == int(X["name"]):
            try:
                ubot = UserBot(**X)
                await ubot.start()
                for modul in PLUGINS:
                    importlib.reload(importlib.import_module(f"plugins.{modul}"))
                return await proses.edit(
                    f"<b><emoji id=5206607081334906820>✅</emoji> Userbot has been restarted {ubot.me.first_name} {ubot.me.last_name or ''} | {ubot.me.id}.</b>",
                    reply_markup=keyboard_inline,
                )
            except Exception as error:
                return await proses.edit(f"<b>{error}</b>", reply_markup=keyboard_inline)


@CMD.BOT("restart")
async def _(client, message):
    return await restart_userbot(client, message)
