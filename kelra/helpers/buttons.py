import re
from math import ceil
from typing import List, Optional, Tuple

from pyrogram.helpers import ikb, kb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from kelra.database import state
from kelra.logger import logger

COLUMN_SIZE = 4
NUM_COLUMNS = 2

class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text
    def __lt__(self, other):
        return self.text < other.text
    def __gt__(self, other):
        return self.text > other.text

def paginate_modules(page_n, module_dict, prefix, chat=None):
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULES__,
                    callback_data="{}_module({},{})".format(prefix, x.__MODULES__.lower(), page_n),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULES__,
                    callback_data="{}_module({},{},{})".format(prefix, chat, x.__MODULES__.lower(), page_n),
                )
                for x in module_dict.values()
            ]
        )
    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton("❮", callback_data="{}_prev({})".format(prefix, modulo_page - 1 if modulo_page > 0 else max_num_pages - 1)),
                EqInlineKeyboardButton("🔙 Kembali", callback_data="back_home"),
                EqInlineKeyboardButton("❯", callback_data="{}_next({})".format(prefix, modulo_page + 1)),
            )
        ]
    else:
        pairs.append([EqInlineKeyboardButton("🔙 Kembali", callback_data="back_home")])

    return pairs


class ButtonUtils:
    URL_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:[/?]\S+)?|tg://\S+")
    BUTTON_PATTERN = re.compile(r"\[(.*?)\|(.*?)\]")
    FORMAT_TAGS = {"<b>": "**", "<i>": "__", "<strike>": "~~", "<spoiler>": "||", "<u>": "--"}

    @staticmethod
    def is_url(text: str) -> bool:
        return bool(ButtonUtils.URL_PATTERN.match(text))

    @staticmethod
    def is_number(text: str) -> bool:
        return text.isdigit()

    @staticmethod
    def is_copy(text: str) -> bool:
        pattern = r"copy:"
        return bool(re.search(pattern, text))

    @staticmethod
    def is_web(text: str) -> bool:
        pattern = r"web:"
        return bool(re.search(pattern, text))

    @staticmethod
    def cek_tg(text):
        tg_pattern = r"https?:\/\/files\.catbox\.moe\/\S+"
        match = re.search(tg_pattern, text)
        if match:
            tg_link = match.group(0)
            non_tg_text = text.replace(tg_link, "").strip()
            return tg_link, non_tg_text
        else:
            return (None, text)

    @staticmethod
    def parse_msg_buttons(texts: str) -> Tuple[str, List[List]]:
        btn = []
        for z in ButtonUtils.BUTTON_PATTERN.findall(texts):
            text, url = z
            urls = url.split("|")
            url = urls[0]
            if len(urls) > 1:
                btn[-1].append([text, url])
            else:
                btn.append([[text, url]])
        txt = texts
        for z in re.findall(r"\[.+?\|.+?\]", texts):
            txt = txt.replace(z, "")
        return txt.strip(), btn

    @staticmethod
    def create_button(text: str, data: str, with_suffix: str = "") -> InlineKeyboardButton:
        data = data.strip()
        if ButtonUtils.is_url(data):
            return InlineKeyboardButton(text=text, url=data)
        elif ButtonUtils.is_number(data):
            return InlineKeyboardButton(text=text, user_id=int(data))
        elif ButtonUtils.is_copy(data):
            return InlineKeyboardButton(text=text, copy_text=data.replace("copy:", ""))
        elif ButtonUtils.is_web(data):
            url = data.replace("web:", "")
            return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))
        return InlineKeyboardButton(text=text, callback_data=f"{data}_{with_suffix}" if with_suffix else data)

    @staticmethod
    def create_inline_keyboard(buttons: List[List], suffix: str = "") -> InlineKeyboardMarkup:
        keyboard = []
        for row in buttons:
            if len(row) > 1:
                keyboard.append([ButtonUtils.create_button(text, data, suffix) for text, data in row])
            else:
                text, data = row[0]
                keyboard.append([ButtonUtils.create_button(text, data, suffix)])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def start_menu(is_admin: bool = False):
        """Menu Utama (Aesthetic & Rapi)"""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        buttons = [
            [InlineKeyboardButton("✨ ᴍᴜʟᴀɪ ʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ ✨", callback_data="buat_ubot")],
            [InlineKeyboardButton("❓ ꜱᴛᴀᴛᴜs ᴀᴋᴜɴ", callback_data="status_akun"),
             InlineKeyboardButton("🛠️ ᴄᴇᴋ ꜰɪᴛᴜʀ", callback_data="cek_fitur")],
            [InlineKeyboardButton("⚙️ ᴘᴇɴɢᴀᴛᴜʀᴀɴ", callback_data="pengaturan"),
             InlineKeyboardButton("🎟️ ᴄʟᴀɪᴍ ɢᴀʀᴀɴsɪ", callback_data="claim_garansi")],
            [InlineKeyboardButton("💬 ʜᴜʙᴜɴɢɪ ᴀᴅᴍɪɴs 💬", callback_data="hubungi_admin")]
        ]
        
        if is_admin:
            buttons.append([
                InlineKeyboardButton("🚀 ᴜᴘᴅᴀᴛᴇ ꜱʏsᴛᴇᴍ 🚀", callback_data="update_bot")
            ])
            
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def settings_menu():
        """Menu Pengaturan"""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴇᴍᴏᴊɪ", callback_data="reset_emoji"),
             InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴘʀᴇꜰɪx", callback_data="reset_prefix")],
            [InlineKeyboardButton("🔄 ʀᴇsᴇᴛ ᴛᴇxᴛ", callback_data="reset_text"),
             InlineKeyboardButton("🔄 ʀᴇsᴛᴀʀᴛ ᴜʙᴏᴛ", callback_data="restart_ubot")],
            [InlineKeyboardButton("🔙 ᴋᴇᴍʙᴀʟɪ 🔙", callback_data="back_home")]
        ])

    @staticmethod
    def userbot(user_id, count):
        return ikb([
            [("Delete User", f"del_ubot {int(user_id)}"), ("Check Phone", f"get_phone {int(count)}")],
            [("Check Expired", f"cek_masa_aktif {int(user_id)}")],
            [("Get Otp", f"get_otp {int(count)}"), ("Get V2L", f"get_faktor {int(count)}")],
            [("❮", f"prev_ub {int(count)}"), ("Close", f"close get_users"), ("❯", f"next_ub {int(count)}")]
        ])

    @staticmethod
    def deak(user_id, count):
        return ikb([[("⬅️", f"prev_ub {int(count)}"), ("Approve", f"deak_akun {int(count)}")]])

    @staticmethod
    async def generate_inline_query(message, chat_id, bot_username, query):
        try:
            client = message._client
            results = await client.get_inline_bot_results(bot_username, query)
            if results and results.results:
                return {"query_id": results.query_id, "result_id": results.results[0].id, "results": results.results, "query": query}
            return None
        except Exception as e:
            return None

    @staticmethod
    async def send_inline_bot_result(message, chat_id, bot_username, query, reply_to_message_id: Optional[int] = None) -> bool:
        client = message._client
        try:
            query_results = await ButtonUtils.generate_inline_query(message, chat_id, bot_username, query)
            if not query_results: return False
            data = await client.send_inline_bot_result(chat_id, query_results["query_id"], query_results["result_id"], reply_to_message_id=reply_to_message_id)
            inline_id = {"chat": chat_id, "_id": data.updates[0].id, "me": client.me.id, "idm": id(message)}
            state.set(client.me.id, query, inline_id)
            return True
        except Exception as e:
            return False

    @staticmethod
    def plus_minus(query, amount):
        return ikb([
            [("⁻1 bulan", f"kurang {query}"), ("⁺1 bulan", f"tambah {query}")],
            [("Konfirmasi", f"confirm {amount} {query}")],
            [("Batal", "closed")]
        ])

    @staticmethod
    def create_font_keyboard(font_list, get_id, current_batch):
        keyboard = []
        for font_dict in font_list:
            for key, value in font_dict.items():
                keyboard.append(InlineKeyboardButton(key, callback_data=f"get_font {get_id} {value}"))
        rows = [keyboard[i : i + 2] for i in range(0, len(keyboard), 2)]
        while len(rows) < 3: rows.append([])
        rows.append([InlineKeyboardButton("⬅️", callback_data=f"prev_font {get_id} {current_batch - 1}"), InlineKeyboardButton("❌", callback_data=f"close inline_font"), InlineKeyboardButton("➡️", callback_data=f"next_font {get_id} {current_batch + 1}")])
        return rows

    @staticmethod
    def create_buttons_textpro(font_list, get_id, current_batch):
        keyboard = []
        for font_dict in font_list:
            for key, value in font_dict.items():
                keyboard.append(InlineKeyboardButton(key, callback_data=f"genpro {get_id} {value}"))
        rows = [keyboard[i : i + 2] for i in range(0, len(keyboard), 2)]
        while len(rows) < 3: rows.append([])
        rows.append([InlineKeyboardButton("⬅️", callback_data=f"prev_textpro {get_id} {current_batch - 1}"), InlineKeyboardButton("❌", callback_data=f"close inline_textpro"), InlineKeyboardButton("➡️", callback_data=f"next_textpro {get_id} {current_batch + 1}")])
        return rows
