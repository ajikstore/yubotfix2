import random
from pyrogram import *
from pyrogram import Client, filters
from kelra import *
from kelra.helpers import CMD, Emoji

__MODULES__ = "Cek cantik"
__HELP__ = """<blockquote>Command Help **Cek cantik**</blockquote>

<blockquote><u>**Get cek cantikorang**</u>
    <u>**Get cek cantik orang command**</u>
        `{0}cekcantik` (name)</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"

KHODAM_LIST = [
    "1% (JELEK BINGIT)🤮", "55% (MAYAN)🙂", "30% (DEMPUL)🙃", "70% (CANTIK TAPI AGAK IRENG)😉",
    "90% (CANTIKNYA PAS)😎", "100% (CANTIK+TOBRUT)🤯", "4% (IRENG)🤢", "10% (IRENG+TEPOS)😖", "1000% (CANTIK+TOBRUT+MANIS)😱"
]

@CMD.UBOT("cekcantik")
async def cek_khodam(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("<blockquote>{em.gagal} Gunakan format: cekkctkn [nama]</blockquote>")

    nama = args[1]
    khodam = random.choice(KHODAM_LIST)
    hasil = f"<blockquote><b>🤭HASIL KECANTIKAN🤭\n\n=👩 Nama: `{nama}`\n Persen: `{khodam}`</blockquote></b>"
    await message.reply_text(hasil)
