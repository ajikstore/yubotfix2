import base64
import io
import os
import random
from io import BytesIO

import aiofiles
import aiohttp

from config import BOT_NAME
from .tools import Tools

emoji_list = (
    "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥸🤩🥳"
    "😏😒😞😔😟😕🙁☹️😭🤬🤯😤😡😢"
)


class QuotlyException(Exception):
    pass


class Quotly:
    # ----------------------------------------
    #  ASCII (jangan diubah)
    # ----------------------------------------
    GAMBAR_KONTOL = """
⣠⡶⠚⠛⠲⢄⡀
⣼⠁ ⠀⠀⠀ ⠳⢤⣄
⢿⠀⢧⡀⠀⠀⠀⠀⠀⢈⡇
⠈⠳⣼⡙⠒⠶⠶⠖⠚⠉⠳⣄
⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄
⠀⠀⠀⠘⣆ ⠀⠀⠀⠀ ⠀⠈⠓⢦⣀
⠀⠀⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠲⢤
⠀⠀⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧
⠀⠀⠀⠀⠀⠀⠀⡴⠋⠓⠦⣤⡀⠀⠀⠀⠀⠀⠀⠀⠈⣇
⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄
⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇
⠀⠀⠀⠀⠀⠀⢹⡄⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃
⠀⠀⠀⠀⠀⠀⠀⠙⢦⣀⣳⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⢦⣀⣀⣀⣀⣠⡴⠚⠉
"""

    GAMBAR_TITIT = """
😋😋
😋😋😋
  😋😋😋
    😋😋😋
     😋😋😋
       😋😋😋
        😋😋😋
         😋😋😋
          😋😋😋
          😋😋😋
      😋😋😋😋
 😋😋😋😋😋😋
 😋😋😋  😋😋😋
    😋😋       😋😋
"""

    # ----------------------------------------
    #  LIST WARNA
    # ----------------------------------------
    colors = [
        "White", "Navy", "DarkBlue", "MediumBlue", "Blue", "DarkGreen",
        "Green", "Teal", "DarkCyan", "DeepSkyBlue", "DarkTurquoise",
        "Lime", "SpringGreen", "Aqua", "Cyan", "MidnightBlue", "DodgerBlue",
        "LightSeaGreen", "ForestGreen", "SeaGreen", "DarkSlateGray",
        "LimeGreen", "Turquoise", "RoyalBlue", "SteelBlue", "Indigo",
        "Purple", "Gray", "Silver", "Pink", "Red", "Yellow", "Orange",
        "Cyan", "Lime", "Black"
    ]

    # ----------------------------------------
    #  FIX: SERIALISASI ENTITY PYROGRAM → JSON AMAN
    # ----------------------------------------
    @staticmethod
    async def serialize_entities(msg):
        if not msg or not msg.entities:
            return []

        fixed = []
        for e in msg.entities:
            fixed.append({
                "offset": e.offset,
                "length": e.length,
                "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                "url": getattr(e, "url", None),
                "user": getattr(e, "user", None),
                "language": getattr(e, "language", None),
            })
        return fixed

    # ----------------------------------------
    # Ambil teks/caption
    # ----------------------------------------
    @staticmethod
    async def t_or_c(msg):
        if not msg:
            return ""
        return msg.text or msg.caption or ""

    # ----------------------------------------
    # Ambil emoji dari pesan
    # ----------------------------------------
    @staticmethod
    async def get_emoji(msg):
        try:
            if msg.sticker and msg.sticker.emoji:
                return msg.sticker.emoji

            text = msg.text or msg.caption or ""
            for c in text:
                if c in emoji_list:
                    return c
            return None
        except:
            return None

    # ----------------------------------------
    # Parse reply
    # ----------------------------------------
    @staticmethod
    async def parse_reply_info(msg):
        if not msg:
            return {}

        user = msg.from_user
        name = "Unknown"

        if user:
            name = user.first_name or "Unknown"
            if user.last_name:
                name += f" {user.last_name}"

        return {
            "name": name,
            "text": msg.text or msg.caption or "",
        }

    # ----------------------------------------
    # Pengganti fungsi forward_info
    # ----------------------------------------
    @staticmethod
    async def forward_info(msg):
        user = msg.from_user
        if not user:
            return 0, "Unknown", "Unknown"

        title = user.first_name or "Unknown"
        if user.last_name:
            title += f" {user.last_name}"

        return user.id, title, title

    # ----------------------------------------
    #  API Utama + Fallback
    # ----------------------------------------
    @staticmethod
    async def quotly_api(payload):
        url_main = "https://bot.lyo.su/quote/generate.png"
        url_fallback = "https://api.quotly.io/generate"

        # API utama
        try:
            r = await Tools.fetch.post(url_main, json=payload)
            if r.status_code == 200:
                return r.read()
        except:
            pass

        # API fallback
        async with aiohttp.ClientSession() as ses:
            async with ses.post(url_fallback, json=payload) as resp:
                if resp.status != 200:
                    raise QuotlyException(f"API Quotly Error: {resp.status}")
                return await resp.read()

    # ----------------------------------------
    #  COMPAT: method lama `quotly()`
    # ----------------------------------------
    @staticmethod
    async def quotly(payload):
        return await Quotly.quotly_api(payload)

    # ----------------------------------------
    #  Ambil isi pesan text/dokumen
    # ----------------------------------------
    @staticmethod
    async def get_message_content(message):
        if message.text:
            return message.text, "text"

        if message.document:
            file_path = await message.download()
            async with aiofiles.open(file_path, "r") as f:
                text = await f.read()
            os.remove(file_path)
            return text, "document"

        return None, None
