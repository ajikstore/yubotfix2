import random
from typing import Optional

from pytz import timezone

from config import BOT_ID, BOT_NAME
from kelra import kelra
from kelra.database import dB


class Message:
    """Enhanced message templates with modern formatting"""

    JAKARTA_TZ = timezone("Asia/Jakarta")

    # --- 4 STIKER ANIMASI TRANSPARAN (DARI ID KAMU) ---
    DAFTAR_GIFT = [
        "CAACAgUAAxkBAAOTajnaMiVNL15eoYqhd284djz0BywAAhAOAAKnDfhVzL_QoUH4vkYeBA",
        "CAACAgEAAxkBAAOXajnagvQ5NJn5YOtRC1lEfxeZzG8AAtYDAAIsIVhGgQbZe3L1W08eBA",
        "CAACAgEAAxkBAAOWajnabGtVEfFtllWx1JWYKgO3AAGWAAL5AwACSXFhRUhL8Yij1MSlHgQ",
        "CAACAgUAAxkBAAOVajnaUD60zBsjE6nB5tB_-ncKMcAAApIKAAII1gFWqcBGCpiIOrIeBA"
    ]

    @classmethod
    def get_random_gift(cls):
        """Mengambil satu stiker secara acak untuk dikirim"""
        return random.choice(cls.DAFTAR_GIFT)
    # --------------------------------------------------

    # HTML formatting templates
    USER_MENTION = "<a href=tg://user?id={id}>{name}</a>"
    CODE_BLOCK = "<code>{text}</code>"
    SECTION_START = "<b>❏ {title}</b>"
    SECTION_ITEM = "<b>├ {label}:</b> {value}"
    SECTION_END = "<b>╰ {label}</b> {value}"

    @staticmethod
    def ReplyCheck(message):
        reply_id = None
        if message.reply_to_message:
            reply_id = message.reply_to_message.id
        elif not message.from_user:
            reply_id = message.id
        return reply_id

    @staticmethod
    async def _ads() -> str:
        txt = await dB.get_var(BOT_ID, "Ads")
        if txt:
            msg = txt
        else:
            msg = "Masih kosong bang"
        return msg

    @classmethod
    def _format_user_mention(cls, user_id: int, first_name: str, last_name: Optional[str] = None) -> str:
        """Format user mention with full name"""
        full_name = f"{first_name} {last_name or ''}".strip()
        return cls.USER_MENTION.format(id=user_id, name=full_name)

    @classmethod
    def expired_message(cls, client) -> str:
        """Generate expired account notification"""
        return f"""
{cls.SECTION_START.format(title="Notifikasi")}
{cls.SECTION_ITEM.format(
    label="Akun",
    value=cls._format_user_mention(client.me.id, client.me.first_name, client.me.last_name)
)}
{cls.SECTION_ITEM.format(label="ID", value=cls.CODE_BLOCK.format(text=client.me.id))}
{cls.SECTION_END.format(label="Status", value="Masa Aktif Telah Habis")}
"""

    @classmethod
    def welcome_message(cls, client, message) -> str:
        """Generate personalized welcome message"""
        return f"""
<blockquote><b><emoji id=6088918540755148137>✨</emoji> Selamat datang, {cls._format_user_mention(
    message.from_user.id,
    message.from_user.first_name,
    message.from_user.last_name
)}!</b>

<b><emoji id=6046636374432420480>🤖</emoji> Saya adalah <u>[garfield bot](https://t.me/maongqw)</u>, asisten pintar yang akan membantu Anda membuat userbot dengan mudah dan cepat.</b></blockquote>
"""


    @staticmethod
    async def userbot(count):
        expired_date = await dB.get_expired_date(kelra._ubot[int(count)].me.id)
        expir = expired_date.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
        return f"""
<b>❏ Userbot ke </b> <code>{int(count) + 1}/{len(kelra._ubot)}</code>
<b>├ Akun:</b> <a href=tg://user?id={kelra._ubot[int(count)].me.id}>{kelra._ubot[int(count)].me.first_name} {kelra._ubot[int(count)].me.last_name or ''}</a> 
<b>├ ID:</b> <code>{kelra._ubot[int(count)].me.id}</code>
<b>╰ Expired</b> <code>{expir}</code>
"""

    @staticmethod
    def deak(X):
        return f"""
<b>Attention !!</b>
<b>Akun:</b> <a href=tg://user?id={X.me.id}>{X.me.first_name} {X.me.last_name or ''}</a>
<b>ID:</b> <code>{X.me.id}</code>
<b>Reason:</b> <code>ᴅɪ ʜᴀᴘᴜs ᴅᴀʀɪ ᴛᴇʟᴇɢʀᴀᴍ</code>
"""

    @staticmethod
    async def policy_message() -> str:
        """Generate enhanced policy and terms message"""
        return f"""
<b>🤖 {BOT_NAME} - Kebijakan & Ketentuan</b>

<b>💫 Kebijakan Pengembalian Dana</b>
• Anda memiliki hak pengembalian dana dalam 48 jam setelah pembelian
• Pengembalian hanya berlaku jika Anda belum menggunakan layanan
• Penggunaan fitur apapun menghilangkan hak pengembalian dana

<b>🛟 Dukungan Pelanggan</b>
• Panduan lengkap tersedia di bot ini
• Informasi risiko userbot: [Baca Di Sini](https://telegra.ph/RESIKO-USERBOT-11-05)
• Pembelian = Persetujuan terhadap semua risiko

<b>✅ Selanjutnya</b>
• Tekan 📃 <b>Saya Setuju</b> untuk melanjutkan pembelian
• Tekan 🏠 <b>Menu Utama</b> untuk kembali

<b>📢 {await Message._ads()}</b>
"""

    @staticmethod
    def TEXT_PAYMENT(harga, total, bulan):
        return f"""
<blockquote><b>Please make a payment first. </b>

<b> Monthly Price: <code>{harga}</code></b>


<b> 🔖 Total Price: Rp.<code>{total}</code> </b>
<b> 🗓️ Total Months: <code> {bulan} </code> </b> 

<b> ✅ Click the button below if you have made your choice.</b></blockquote>
"""
