import asyncio
import random
from pyrogram import enums
from kelra.helpers import CMD, Emoji

__MODULES__ = "Maki"
__HELP__ = """<blockquote>Command Help **Maki**</blockquote>
    
<blockquote expandable><u>**Maki Orang**</u>
    <u>**Fitur untuk nge-roast atau maki target**</u>
        `{0}maki` (reply pesan target)</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"

# Daftar kata-kata maki/roasting (Silakan tambahin sendiri sesuka lu)
KATA_MAKI = [
    "Muka lu kayak gorengan sisa kemarin, lembek!",
    "Bocil kematian gausah caper di mari deh.",
    "Otak lu kalau dijual laku mahal nih, soalnya jarang dipakai alias masih mulus.",
    "Mandi dulu sana ngab, bau daki lu nembus sampai layar hp gua.",
    "Lu kalau lahir di zaman purba, dinosaurus juga males mangsa lu.",
    "Ketik aja masih typo, gaya-gayaan mau debat.",
    "Sadar diri dong, lu tuh ibarat ampas tahu, dibuang sayang dimakan ga enak.",
    "Napas lu bau asbak warteg, minggir lu dari mari!",
    "Jembut lu noh ubanan mending lu warnain dlu!!",
    "bisa ae napas kopling, gigi lu noh kuning",
    "Atur ajee dek lo kan panitianya, gua ngikut ajaa!!",
    "lu kan cuman babu, gausah banyak tingkah!!",
    "jangan so keras dek!! di rumah lo masi pake gas lpg ijo (untuk rakyat miskin)",
    "anak mamih jangan sok keras, lu gua guyur aeer langsung ayan ngtd!!",
    "muka kek kanebo lecek so-soan ngehina orang!!"
    "gaya lo ga sesuai duit lo, kalo punya utang di bayar",
    "so pentantang petenteng, di tatang udah kaya ayam sayur!!",
    "Muka lu mah boro-boro cinematic, disaring pakai filter cyberpunk aja masih burik.",
    "Otak lu kayak server error 404, pantesan loading-nya lama banget kalau diajak ngobrol.",
    "Daripada lu caper di sini, mending lu bantu nguras kolam ikan koi. Lebih berfaedah.",
    "Banyak tingkah lu, gue setelin breakbeat 150 BPM langsung kesurupan lu entar.",
    "Sok-sokan mau jadi hacker ala-ala, nge-restart modem aja lu masih nanya emak.",
    "Bacot lu bising banget, ngalah-ngalahin speaker hajatan pas lagi muter musik jedag-jedug.",
    "Gue kick juga lu lama-lama. Mental masih tempe aja berani caper di grup sekelas Hyperion.",
    "Chat lu nggak ada isinya, persis kayak dompet lu pas akhir bulan.",
    "Lu ngetik pakai dengkul ya? Hurufnya berantakan kayak jalanan belum diaspal.",
    "Gue bot canggih, lu manusia purba. Jauh beda kasta kita, ngab.",
    "Coba cek kaca deh, muka lu butuh di-render ulang tuh, resolusinya pecah 144p.",
    "Dih, caper amat lu. Ngarep banget dibikinin animasi profil Telegram VIP ya?",
    "Nggak usah sok asik, lu bukan artis yang dateng-dateng minta disambut meriah.",
    "Mending lu ikut adu JJ battle aja sana, biar ketahuan editing lu sekelas anak TK.",
    "Kalau miskin kuota jangan nyepam, mending lu nyari job ngelonte gih biar ada pemasukan.",
    "Sadar diri kek, lu di sini cuma badut grup yang bahkan nggak dapet saweran.",
    "Gaya lu neon-neon cyberpunk, tapi kelakuan masih kayak bocah warnet kehabisan billing.",
    "Tombol spasi lu jebol ya? Ngomong nyerocos mulu nggak ada titik komanya.",
    "Nggak usah bawa-bawa backingan, di mata bot lu cuma sebaris kode yang siap di-banned.",
    "Lu kalau mau ngelawak yang lucu dikit ngapa, garing banget kayak kerupuk masuk angin.",
    "Gue rasa IQ lu setara sama suhu ruangan, pantesan gampang banget dipancing emosinya.",
    "Mending lu diam deh, makin lu ngetik makin kelihatan kalau otak lu jarang dipakai.",
    "Gaya lu minta dilayanin ala luxury, padahal nge-chat aja masih suka typo malu-maluin.",
    "Napas lu kedengeran ngos-ngosan sampai sini, saking kerasnya usaha lu buat caper.",
    "Lu kalau nggak ada kerjaan mending typing di gc lo noh sepi bat kek kuburan, daripada menu-menuhin history chat doang."
    "petinggi petinggi tai anjing, lo kan gapunya nama anjg!!"
]

@CMD.UBOT("maki|roast")
async def maki_orang(client, message):
    em = Emoji(client)
    await em.get()
    
    # Cek apakah lu nge-reply pesan orangnya
    if not message.reply_to_message:
        return await message.reply(f"<blockquote>{em.gagal} <b>Reply dulu pesan orang yang mau dimaki ngab!</b></blockquote>")
        
    korban = message.reply_to_message.from_user
    nama_korban = f"<a href=tg://user?id={korban.id}>{korban.first_name}</a>" if korban else "Woi"
    
    # Milih kata maki secara acak
    kata = random.choice(KATA_MAKI)
    
    # Efek pura-pura ngetik biar keliatan manual
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await asyncio.sleep(1.5)
    
    teks_maki = f"{nama_korban}, {kata}"
    
    # Ngirim pesan makian
    await client.send_message(
        message.chat.id,
        teks_maki,
        reply_to_message_id=message.reply_to_message.id
    )
    
    # Hapus pesan trigger lu (.maki) biar elegan dan kelihatannya bot lu yang marah
    try:
        await message.delete()
    except:
        pass
