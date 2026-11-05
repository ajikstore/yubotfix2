from kelra import bot
from kelra.database import state
from kelra.helpers import CMD, ButtonUtils, Emoji
from pyrogram import types

__MODULES__ = "Fonts"
__HELP__ = """<blockquote>Command Help **Fonts**</blockquote>

<blockquote expandable>    <u>**Generate costum font**</u>
        `{0}font` (text/reply text)
        
    <u>**Fonts Bahasa Luar (Button)**</u>
        `{0}fontbs` [text/reply]</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

# --- FITUR FONT BAWAAN ---
@CMD.UBOT("font")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    text = client.get_text(message)
    if not text:
        return await message.reply(f"{emo.gagal}<b>Please give text or reply to text:\n\nExample: <code>{x}font</code> [text or reply to text]</b>")
    proses_ = await emo.get_costum_text()
    pros = await message.reply(f"{emo.proses}<b>{proses_[4]}</b>")
    query = f"inline_font"
    state.set(client.me.id, "FONT", text)
    try:
        inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, query)
        if inline:
            await pros.delete()
            return await message.delete()
    except Exception as error:
        return await pros.edit(f"{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code>")

# --- FITUR FONT BS (Dengan Pagination) ---
@CMD.UBOT("fontbs")
async def fontbs(client, message):
    text = client.get_text(message)
    if not text:
        return await message.reply("<b>Kasih teksnya dulu ngab!</b>")
    
    short_text = text[:15]
    # Halaman 1
    buttons = [
        [types.InlineKeyboardButton("🇯🇵 Jepang", callback_data=f"f_jepang_{short_text}"),
         types.InlineKeyboardButton("🇷🇺 Rusia", callback_data=f"f_rusia_{short_text}")],
        [types.InlineKeyboardButton("🇹🇭 Thai", callback_data=f"f_thai_{short_text}"),
         types.InlineKeyboardButton("🇸🇦 Arab", callback_data=f"f_arab_{short_text}")],
        [types.InlineKeyboardButton("➡️ Halaman 2", callback_data=f"fnxt_2_{short_text}")]
    ]
    await message.reply(f"<b>Pilih gaya font (Hal 1):</b> <code>{short_text}</code>", reply_markup=types.InlineKeyboardMarkup(buttons))

# Callback untuk Pindah Halaman
@bot.on_callback_query(lambda _, q: q.data.startswith("fnxt_"))
async def callback_next_page(client, query):
    data = query.data.split("_")
    page, text = data[1], data[2]
    
    if page == "2":
        buttons = [
            [types.InlineKeyboardButton("🔤 Bubble", callback_data=f"f_bubble_{text}"),
             types.InlineKeyboardButton("🔳 Square", callback_data=f"f_square_{text}")],
            [types.InlineKeyboardButton("⬅️ Kembali", callback_data=f"fnxt_1_{text}")]
        ]
        await query.message.edit(f"<b>Pilih gaya font (Hal 2):</b> <code>{text}</code>", reply_markup=types.InlineKeyboardMarkup(buttons))
    else:
        buttons = [
            [types.InlineKeyboardButton("🇯🇵 Jepang", callback_data=f"f_jepang_{text}"),
             types.InlineKeyboardButton("🇷🇺 Rusia", callback_data=f"f_rusia_{text}")],
            [types.InlineKeyboardButton("🇹🇭 Thai", callback_data=f"f_thai_{text}"),
             types.InlineKeyboardButton("🇸🇦 Arab", callback_data=f"f_arab_{text}")],
            [types.InlineKeyboardButton("➡️ Halaman 2", callback_data=f"fnxt_2_{text}")]
        ]
        await query.message.edit(f"<b>Pilih gaya font (Hal 1):</b> <code>{text}</code>", reply_markup=types.InlineKeyboardMarkup(buttons))

# Callback untuk Eksekusi Font
@bot.on_callback_query(lambda _, q: q.data.startswith("f_"))
async def callback_font_luar(client, query):
    data = query.data.split("_")
    style, text = data[1], data[2]
    
    mapping = {
        "jepang": str.maketrans("abcdefghijklmnopqrstuvwxyz", "卂乃匚刀乇下厶卄丨丁长乚爪𠘨口尸 সুবিধ丂丅凵リ山乂丫乙"),
        "rusia": str.maketrans("abcdefghijklmnopqrstuvwxyz", "αвc∂єƒgнιנкℓмησρqяѕтυνωкуz"),
        "thai": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ค๒ς๔єŦﻮђเןкɭ๓ภ๏קợгรՇยשฬאץz"),
        "arab": str.maketrans("abcdefghijklmnopqrstuvwxyz", "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙"),
        "bubble": str.maketrans("abcdefghijklmnopqrstuvwxyz", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"),
        "square": str.maketrans("abcdefghijklmnopqrstuvwxyz", "🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉")
    }
    
    translated = text.translate(mapping.get(style, str.maketrans("", "")))
    await query.message.edit(f"<b>Hasil {style.upper()}:</b>\n\n<code>{translated}</code>")
