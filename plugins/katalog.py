from kelra.helpers import CMD, Emoji
from kelra.database import dB

__MODULES__ = "Katalog"
__HELP__ = """<blockquote>Command Help **Katalog**</blockquote>
<blockquote expandable>
**Manajemen Katalog:**
• <code>{0}addkatalog</code> [Kategori] | [Isi]: Tambah daftar harga.
• <code>{0}delkatalog</code> [Kategori]: Hapus kategori.
• <code>{0}katalog</code>: Tampilkan seluruh katalog.
</blockquote>"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

# 1. TAMBAH KATALOG
@CMD.UBOT("addkatalog")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    # Deteksi teks dari pesan langsung atau dari reply
    text = client.get_text(message)
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption

    # Cek apakah format pemisahnya benar
    if not text or "|" not in text:
        return await message.reply(
            f"{emo.gagal} **Format salah ngab!**\n\n"
            f"Gunakan tanda `|` untuk memisahkan Judul dan Isi.\n"
            f"**Contoh:**\n`.addkatalog Server | - Fix Error 404: 50k\n- Setup Bot: 100k`"
        )
    
    # Pecah teks jadi 2 bagian: Kategori dan Isi
    kategori, isi = text.split("|", 1)
    kategori = kategori.strip()
    isi = isi.strip()
    
    # Ambil data lama, update, lalu simpan lagi
    katalog_data = await dB.get_var(client.me.id, "KATALOG_DATA") or {}
    katalog_data[kategori] = isi
    await dB.set_var(client.me.id, "KATALOG_DATA", katalog_data)
    
    await message.reply(f"{emo.sukses} **Kategori '{kategori}' berhasil ditambahkan ke Katalog!**")

# 2. HAPUS KATALOG
@CMD.UBOT("delkatalog")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    text = client.get_text(message)
    if not text:
        return await message.reply(f"{emo.gagal} **Masukkan nama kategori yang mau dihapus!**")
        
    katalog_data = await dB.get_var(client.me.id, "KATALOG_DATA") or {}
    
    # Cek apakah kategorinya ada di database
    if text in katalog_data:
        del katalog_data[text]
        await dB.set_var(client.me.id, "KATALOG_DATA", katalog_data)
        await message.reply(f"{emo.sukses} **Kategori '{text}' berhasil dihapus dari Katalog.**")
    else:
        await message.reply(f"{emo.gagal} **Kategori '{text}' tidak ditemukan!**")

# 3. TAMPILKAN KATALOG (DESAIN RAPIH)
@CMD.UBOT("katalog")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    pros = await message.reply(f"{emo.proses} **Memuat Katalog...**")
    katalog_data = await dB.get_var(client.me.id, "KATALOG_DATA") or {}
    
    if not katalog_data:
        return await pros.edit(f"{emo.gagal} **Katalog masih kosong! Tambahin dulu pakai `.addkatalog`**")
        
    # Bikin Header / Judul Utama
    msg = "<blockquote><b>🛒 KATALOG PRODUK & LAYANAN</b></blockquote>\n\n"
    
    # Looping semua data dan bungkus pakai blockquote expandable
    for kategori, isi in katalog_data.items():
        msg += f"<blockquote expandable><b>📦 {kategori}</b>\n{isi}</blockquote>\n"
        
    try:
        await client.send_message(message.chat.id, msg, disable_web_page_preview=True)
        await pros.delete()
        await message.delete()
    except Exception as error:
        await pros.edit(f"{emo.gagal} **Error memuat katalog:**\n<code>{str(error)}</code>")
