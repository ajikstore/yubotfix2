import re
from pyrogram import enums
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.helpers import ikb
from pyrogram.types import InlineKeyboardMarkup
from config import BOT_NAME, HELPABLE
from kelra import kelra
from kelra.database import dB, state
from kelra.helpers import CMD, paginate_modules
from kelra.logger import logger

text_markdown = "**Untuk melihat format markdown silakan klik tombol di bawah ini.**"
text_formatting = """
> **Markdown Formatting**
> Anda dapat memformat pesan menggunakan **tebal**, _miring_, --garis bawah--, ~~coret~~, dll.
> `<code>code</code>` : monospace.
> `[hyperlink](link)` : hyperlink.
> `Halo Disini [Tombol 1|https://link.com]` : tombol URL.
> Awali `cb_` untuk callback data. Awali `alert:` untuk popup alert.
"""

text_fillings = "<blockquote><b>Fillings</b>\nIsian yang didukung:\n<code>{first}</code> <code>{last}</code> <code>{fullname}</code> <code>{username}</code> <code>{mention}</code> <code>{id}</code> <code>{date}</code> <code>{day}</code> <code>{month}</code> <code>{year}</code> <code>{hour}</code> <code>{minute}</code>.</blockquote>"

async def cek_plugins(client, message):
    is_cb = hasattr(message, "data")
    user = message.from_user
    msg_obj = getattr(message, "message", None)

    prefix = kelra.get_prefix(user.id)
    text_help = await dB.get_var(user.id, "text_help") or f"**🤖 {BOT_NAME}**"
    full = f"<a href=tg://user?id={user.id}>{user.first_name} {user.last_name or '' }</a>"

    msg = f"""
<blockquote><b>
 📚 Inline Help Menu
 🤖 Prefixes: <code>{' '.join(prefix)}</code>
 🧩 Plugins: <code>{len(HELPABLE)}</code>
 👤 {full} </b></blockquote>
<blockquote>{text_help}</blockquote>"""

    buttons = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

    if is_cb:
        if hasattr(message, "inline_message_id") and message.inline_message_id:
            await client.edit_inline_text(message.inline_message_id, msg, reply_markup=buttons, disable_web_page_preview=True)
        elif msg_obj:
            if msg_obj.media:
                await msg_obj.delete()
                await client.send_message(msg_obj.chat.id, msg, reply_markup=buttons, disable_web_page_preview=True)
            else:
                await msg_obj.edit_text(msg, reply_markup=buttons, disable_web_page_preview=True)
    else:
        await message.reply_text(msg, reply_markup=buttons, disable_web_page_preview=True)


@CMD.CALLBACK("^markdown")
async def cb_markdown(client, callback_query):
    await callback_query.answer()
    data = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    prev_page_num = state.get(user_id, "prev_page_num", 0)
    
    msg_obj = getattr(callback_query, "message", None)
    
    button = ikb([
        [("Formatting", "markdown_format", "callback_data"), ("Fillings", "markdown_fillings", "callback_data")],
        [("🔙 Kembali", f"help_back({prev_page_num})")],
    ])
    
    text = text_formatting if data == "format" else text_fillings

    try:
        if callback_query.inline_message_id:
            await client.edit_inline_text(callback_query.inline_message_id, text, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)
        elif msg_obj:
            if msg_obj.media:
                await msg_obj.delete()
                await client.send_message(msg_obj.chat.id, text, reply_markup=button, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)
            else:
                await msg_obj.edit_text(text, reply_markup=button, disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN)
    except MessageNotModified:
        pass


@CMD.CALLBACK("help_(.*?)")
async def _(client, callback_query):
    await callback_query.answer()
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", callback_query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", callback_query.data)
    next_match = re.match(r"help_next\((.+?)\)", callback_query.data)
    back_match = re.match(r"help_back\((\d+)\)", callback_query.data)
    
    user_id = callback_query.from_user.id
    prefix = kelra.get_prefix(user_id)
    x_ = next(iter(prefix))
    full = f"<a href=tg://user?id={callback_query.from_user.id}>{callback_query.from_user.first_name} {callback_query.from_user.last_name or ''}</a>"
    text_help = await dB.get_var(user_id, "text_help") or f"**🤖 {BOT_NAME}**"
    text_help2 = f"<blockquote>**🤖 {BOT_NAME}**</blockquote>"
    
    msg_obj = getattr(callback_query, "message", None)

    top_text = f"""
    <blockquote><b>
    📚 Inline Help Menu
    🤖 Prefixes: <code>{' '.join(prefix)}</code>
    🧩 Plugins: <code>{len(HELPABLE)}</code>
    👤 {full} </b></blockquote>
    <blockquote>{text_help}</blockquote>"""

    async def edit_content(text, reply_markup):
        try:
            if callback_query.inline_message_id:
                await client.edit_inline_text(callback_query.inline_message_id, text, reply_markup=reply_markup, disable_web_page_preview=True)
            elif msg_obj:
                if msg_obj.media:
                    await msg_obj.delete()
                    await client.send_message(msg_obj.chat.id, text, reply_markup=reply_markup, disable_web_page_preview=True)
                else:
                    await msg_obj.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
        except MessageNotModified:
            pass

    if mod_match:
        module = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        state.set(user_id, "prev_page_num", prev_page_num)
        bot_text = f"{HELPABLE[module].__HELP__}".format(x_, text_help2)
        
        if "markdown" in bot_text:
            button_ = ikb([[("Formatting", "markdown_format", "callback_data"), ("Fillings", "markdown_fillings", "callback_data")], [("🔙 Kembali", f"help_back({prev_page_num})")]])
            await edit_content(text_markdown, button_)
        else:
            button = ikb([[("🔙 Kembali", f"help_back({prev_page_num})", "callback_data")]])
            await edit_content(bot_text, button)

    elif prev_match or next_match or back_match:
        page = int(prev_match.group(1)) if prev_match else int(next_match.group(1)) if next_match else int(back_match.group(1))
        await edit_content(top_text, InlineKeyboardMarkup(paginate_modules(page, HELPABLE, "help")))
