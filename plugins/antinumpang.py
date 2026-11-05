import random
import asyncio
from pyrogram import Client, filters, enums

__MODULES__ = "Anti Numpang"
__HELP__ = """<blockquote>Fitur ini otomatis jalan di background! 
Bot akan memaki siapa saja yang mencoba mengetik command di Private Chat lu.</blockquote>"""

# Daftar makian buat orang yang numpang command
KATA_MAKI_NUMPANG = [
    "Woi {nama}, lu siapa anjir merintah-merintah bot gua? Muka lu kek gorengan dingin!",
    "Dih caper, ngapain lu ngetik command? Ini userbot eksklusif, gausah numpang {nama}.",
    "Sadar diri dong {nama}, lu tuh babu, ngapain nyoba make bot majikan?",
    "Command ditolak! Beli VPS sendiri sana {nama}, gausah sok make bot orang.",
    "Kasian banget pengen punya bot ya {nama}? Mending lu cuci piring aja sana.",
    "Ngetik apaan lu {nama}? Jari lu keriting ya? Udah miskin, gatau diri mau make bot orang."
]

# Aktif untuk pesan masuk (incoming), di Private Chat, yang mirip command
@Client.on_message(filters.incoming & filters.private & filters.text & filters.regex(r"^[.!/?][a-zA-Z]+"), group=10)
async def tolak_numpang(client, message):
    # Memastikan pesannya benar-benar dari orang lain
    if message.from_user and message.from_user.id != client.me.id:
        nama = message.from_user.first_name or "Bocil"
        makian = random.choice(KATA_MAKI_NUMPANG).format(nama=nama)
        
        # Pura-pura ngetik biar panik
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        await asyncio.sleep(1.5)
        
        # Balas pesannya
        await message.reply(f"<blockquote>{makian}</blockquote>")
