import os
from kelra.helpers import CMD, Emoji
from kelra.database import dB
from pyrogram.types import Message

__MODULES__ = "Payment"
__HELP__ = """<blockquote>Command Help **Payment**</blockquote>
<blockquote expandable>
**Atur Metode Pembayaran:**
• <code>{0}getqr</code> [reply foto]: Menyimpan gambar QR Code.
• <code>{0}delqr</code>: Menghapus gambar QR Code.
• <code>{0}getdana</code> [text/reply]: Set DANA utama.
• <code>{0}deldana</code>: Hapus data DANA.
• <code>{0}getbank</code> [text/reply]: Tambah Bank/E-Wallet (Bisa banyak).
• <code>{0}delbank</code>: Hapus semua data Bank.

**Tampilkan Pembayaran:**
• <code>{0}payment</code>: Memunculkan seluruh info pembayaran & QR.
</blockquote>"""

__CATEGORY__ = "Payment <emoji id=5287231198098117669>💳</emoji>"

# 1. SETUP QR CODE
@CMD.UBOT("getqr")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    if message.reply_to_message and message.reply_to_message.photo:
        file_id = message.reply_to_message.photo.file_id
        await dB.set_var(client.me.id, "QR_PAYMENT", file_id)
        return await message.reply(f"{emo.sukses} **QR Code pembayaran berhasil disimpan!**")
    else:
        return await message.reply(f"{emo.gagal} **Silakan reply ke sebuah foto QR Code!**")

# 2. HAPUS QR CODE
@CMD.UBOT("delqr")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    await dB.set_var(client.me.id, "QR_PAYMENT", None)
    return await message.reply(f"{emo.sukses} **QR Code berhasil dihapus.**")

# 3. SETUP DANA
@CMD.UBOT("getdana")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    # Ambil teks dari command atau reply
    text = client.get_text(message)
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption

    if text:
        await dB.set_var(client.me.id, "DANA_PAYMENT", text)
        return await message.reply(f"{emo.sukses} **Data DANA berhasil diatur menjadi:**\n<code>{text}</code>")
    else:
        return await message.reply(f"{emo.gagal} **Kirim teksnya atau reply pesan!**\nContoh: `.getdana 081219623569 a/n rifkyxx`")

# 4. HAPUS DANA
@CMD.UBOT("deldana")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    await dB.set_var(client.me.id, "DANA_PAYMENT", None)
    return await message.reply(f"{emo.sukses} **Data DANA berhasil dihapus.**")

# 5. SETUP BANK / E-WALLET (BISA BANYAK)
@CMD.UBOT("getbank")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    text = client.get_text(message)
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption

    if text:
        # Ambil list bank lama, atau buat list baru kalau kosong
        banks = await dB.get_var(client.me.id, "BANK_PAYMENT") or []
        if not isinstance(banks, list):
            banks = []
            
        banks.append(text)
        await dB.set_var(client.me.id, "BANK_PAYMENT", banks)
        return await message.reply(f"{emo.sukses} **Berhasil menambahkan Rekening/Bank:**\n<code>{text}</code>")
    else:
        return await message.reply(f"{emo.gagal} **Kirim teksnya atau reply pesan!**\nContoh: `.getbank Shopeepay 081219623569 a/n rifkyxx`")

# 6. HAPUS SEMUA BANK
@CMD.UBOT("delbank")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    await dB.set_var(client.me.id, "BANK_PAYMENT", [])
    return await message.reply(f"{emo.sukses} **Seluruh data Bank & E-Wallet berhasil dikosongkan.**")

# 7. TAMPILKAN PAYMENT
@CMD.UBOT("payment")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"{emo.proses} **Memuat data pembayaran...**")
    
    qr = await dB.get_var(client.me.id, "QR_PAYMENT")
    dana = await dB.get_var(client.me.id, "DANA_PAYMENT")
    banks = await dB.get_var(client.me.id, "BANK_PAYMENT") or []
    
    if not qr and not dana and not banks:
        return await pros.edit(f"{emo.gagal} **Kamu belum mengatur metode pembayaran apapun!**")

    # Bikin tampilan caption estetik dan premium
    msg = "<blockquote><b>💳 INFORMASI PEMBAYARAN</b></blockquote>\n\n"
    
    if dana:
        msg += "<b>🟣 DANA:</b>\n"
        msg += f"├ <code>{dana}</code>\n\n"
        
    if banks:
        msg += "<b>🏦 BANK & E-WALLET LAINNYA:</b>\n"
        for idx, b in enumerate(banks):
            if idx == len(banks) - 1:
                msg += f"└ <code>{b}</code>\n"
            else:
                msg += f"├ <code>{b}</code>\n"
                
    msg += "\n<i>*(Silakan klik nomor di atas untuk menyalin/copy otomatis)*</i>"

    # Kirim hasil
    try:
        if qr:
            await client.send_photo(message.chat.id, photo=qr, caption=msg, reply_to_message_id=message.reply_to_message_id)
        else:
            await client.send_message(message.chat.id, text=msg, reply_to_message_id=message.reply_to_message_id)
            
        await pros.delete()
        await message.delete()
    except Exception as error:
        await pros.edit(f"{emo.gagal} **Gagal memuat pembayaran:**\n<code>{str(error)}</code>")
