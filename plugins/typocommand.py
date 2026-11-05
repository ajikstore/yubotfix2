import random
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import MessageIdInvalid

__MODULES__ = "Typo Command"
__HELP__ = "Fitur otomatis maki owner kalau ngetik command typo untuk prefix simbol."

PREFIXES = [".", "/", "!", "?", "-", "_", "+", "$", "#", "*", "~", "="]

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

# Daftar makian SUPER SAVAGE (Udah di-upgrade jadi lebih pedas & brutal)
MAKI_TYPO = [
    # --- Roasting Skill & Kerjaan ---
    "Woi bos! Command apaan tuh? Ngarang lu ya? Mending lu ngurusin SUPERKOI aja sana daripada main bot.",
    "Sok-sokan ngetik command, mending dengerin breakbeat 150 BPM dulu sana biar melek matanya.",
    "Command lu nyangkut kayak server error 404 Garfield Store, benerin dulu woi jari lu.",
    "Muka lu kurang cyberpunk buat ngetik command rahasia begini, balek aja dah.",
    "Typo parah, skill ngetik lu gak secinematic dan semewah bacot lu bos.",
    "Gaya lu sok hacker neon ungu biru, ngetik command basic aja tremor.",
    "Malu-maluin HYPERION aja lu. Ngetik command typo, nanti abis lu dihujat di Menfess.",
    "Mending lu siap-siap buat Adu JJ Battle sana, daripada maksain ngetik command abal-abal.",
    "Sok-sokan pamer animasi Telegram Gift, ngetik awalan prefix aja masih typo.",
    "Beli VPS sanggup, ngetik command yang bener kagak sanggup. Miris.",
    "Bot lu ini udah canggih, jangan dirusak sama jari lu yang asal neken keyboard itu.",
    
    # --- Roasting Fisik & Kelakuan ---
    "Mandi dulu sana ngab, bau daki lu nembus sampai layar hp.",
    "Otak lu kalau dijual laku mahal nih, soalnya jarang dipakai alias masih mulus.",
    "Sadar diri dong, lu tuh ibarat ampas tahu, dibuang sayang dimakan ga enak.",
    "Napas lu bau asbak warteg, gausah sok-sokan ngetik cepet dah.",
    "Udah miskin, typo pula. Beban bumi lu bos.",
    "Jari lu segede jempol kaki ya? Ngetik ginian aja kepeleset mulu.",
    "Lu ngetik pakai dengkul apa gimana? Berantakan bener.",
    "Kalau IQ lu setara suhu ruangan, mending gausah maksain main HP dah.",
    "Tarik napas panjang, minum air putih, terus sadar diri kalau lu tuh beban server.",
    "Coba jempolnya di-ruqyah dulu sebelum pegang HP biar lurus.",
    "Typo lu mendarah daging, persis kayak utang lu ke warung sebelah.",
    "Ikan koi aja bisa berenang lurus, masa lu ngetik command belok-belok.",
    "Mending rebahan aja dah, ngurang-ngurangin dosa daripada ngetik gajelas.",
    "Tolong donasikan jari lu ke orang yang lebih membutuhkan.",
    "Lu kalau lahir di zaman purba, dinosaurus juga males mangsa lu gara-gara typo terus.",
    "Lu ngetik apaan dah? Kalo ngantuk tidur aja, gausah maksain ngetik.",
    "Mending lu ngaca dulu dah sebelum ngetik. Command sama obrolan biasa aja nggak bisa bedain.",
    "Kocak lu bos, ngetik pendek aja typo apalagi ngetik paragraf. Mending diam aja dah.",
    "Tangan lu abis megang apaan dah? Licin bener ngetik aja typo mulu.",
    "Prefix doang bener, belakangnya ngawur. Malu dong sama bot sendiri."
]

# Pake group=-1 biar nyolong start jalan duluan sebelum diblokir mesin utama
@Client.on_message(filters.me & filters.text, group=-1)
async def cek_semua_typo(client, message):
    # Lempar ke background biar gak bikin bot lag
    asyncio.create_task(proses_typo(client, message))

async def proses_typo(client, message):
    teks = message.text
    if not teks:
        return
        
    karakter_pertama = teks[0]
    
    if karakter_pertama in PREFIXES:
        parts = teks.split()
        if len(parts[0]) > 1: 
            
            # Tunggu 0.5 detik buat nungguin command asli kelar
            await asyncio.sleep(0.5)
            
            try:
                # Ngecek ke server Telegram, pesannya masih ada nggak?
                cek_pesan = await client.get_messages(message.chat.id, message.id)
                
                # Kalau command beneran, pasti teksnya udah berubah atau kehapus
                if cek_pesan.empty or cek_pesan.text != teks:
                    return
                    
                # Kalau masih utuh, HABISI!
                makian = random.choice(MAKI_TYPO)
                pesan_error = f"<blockquote>❌ {makian}\n(Lu ngetik: {teks})</blockquote>"
                
                await message.edit(pesan_error)
                
                await asyncio.sleep(4)
                await message.delete()
                
            except Exception:
                pass
