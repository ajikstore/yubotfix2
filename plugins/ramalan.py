import random
from pyrogram import enums
from kelra.helpers import CMD, Emoji

__MODULES__ = "Ramalan"
__HELP__ = """<blockquote>Command Help **Ramalan**</blockquote>

<blockquote expandable><u>**Ramalan Cyber**</u>
    <u>**Ramal nasib diri sendiri atau orang lain**</u>
        `{0}ramal` (reply/username)</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "Fun <emoji id=5316832430529722441>🕹</emoji>"

# Definisi List Langsung
RAMALAN_LIST = [
    "Sistem mendeteksi hari ini kamu bakal dapet notif, tapi isinya cuma promo pinjol yang nanyain kabar cicilan.",
    "Wajah lo hari ini lagi versi 'belum mandi tiga hari', mending tutup kamera sebelum bikin server error.",
    "Jangan sok-sokan minta ramalan, rezeki lo aja masih nyangkut di dompet orang lain.",
    "Hari ini lo bakal dapet kejutan: Ternyata mantan lo udah bahagia, dan lo masih aja jomblo sambil mantau story dia.",
    "Sistem mendeteksi bau amis di sekitar lo, ternyata itu bau kegagalan yang lo simpen rapat-rapat.",
    "Jangan terlalu banyak gaya, hidup lo itu ibarat kuota 1GB: Cepet banget abisnya, terus abis itu cuma bisa bengong.",
    "Tingkat ketampanan lo hari ini lagi diskon besar-besaran, alias lagi anjlok parah.",
    "Besok lo bakal dapet hidayah, tapi sayang lo-nya keburu asik main game sampe lupa waktu.",
    "Ada energi negatif di sekeliling lo, itu bukan hantu, itu cuma rasa iri lo liat temen lo sukses.",
    "Ramalan gue buat lo: Masih hidup sampe hari ini aja udah sebuah keajaiban, syukurilah jangan malah minta yang aneh-aneh.",
    "Sistem mendeteksi lo lagi boker ya? Mending fokus boker daripada fokus nanya ramalan ga jelas.",
    "Jangan sok keras jadi jagoan di grup, padahal di rumah lo cuma babu yang disuruh cuci piring.",
    "Tampang lo hari ini 11-12 sama kardus bekas di gudang, buruan cuci muka sana!",
    "Lo itu definisi dari kata 'sia-sia', udah usaha tapi tetep aja nggak ada hasilnya.",
    "Sistem mendeteksi lo lagi stalking mantan, sadar bos, dia udah punya yang lebih kaya dan ganteng.",
    "Jangan tanya kapan nikah/punya pacar, tanyain kenapa orang se-tengil lo bisa bertahan hidup sampai sekarang.",
    "Jangan sok keras jadi jagoan di grup, padahal di rumah lo cuma babu yang disuruh cuci piring.",
    "Ramalan gue: Lo bakal dapet uang, tapi buat bayar utang yang lo lupa sejak zaman majapahit.",
    "Tampang lo hari ini 11-12 sama kardus bekas di gudang, buruan cuci muka sana!",
    "Hari ini keberuntungan lo lagi simulasi, alias nggak ada sama sekali.",
    "Ramalan buat lo: Berhenti berharap sama dia, dia aja bahkan nggak tau lo hidup di dunia ini.",
    "Jangan banyak gaya, kuota aja minta hotspot orang lain, mending diem di pojokan.",
    "Sistem mendeteksi adanya kebodohan akut pada diri lo, mending jangan keluar rumah hari ini.",
    "Nasib lo ibarat sinyal provider murah: Kadang ilang, kadang lelet, nggak bisa diandelin.",
    "Lo nanya ramalan buat nyari jawaban? Padahal jawaban dari hidup lo cuma 'gagal'.",
    "Peringatan: Jangan pernah nyalain api di dekat lo, bisa-bisa rambut lo yang awut-awutan langsung ludes.",
    "Ramalan sistem: Lo bakal dapet pesan dari seseorang, tapi isinya cuma 'lu siapa ya?'.",
    "Jangan ngerasa paling ganteng/cantik, itu cuma pantulan kaca yang lagi rusak.",
    "Hari ini lo bakal ngerasa pinter, padahal itu cuma efek kebanyakan halu.",
    "Sistem merekomendasikan lo buat uninstall hidup lo aja, bercanda ding, tapi emang iya.",
    "Lo tuh kayak iklan di YouTube: Suka muncul nggak diundang, dan bikin orang pengen nge-skip.",
    "Ramalan buat lo: Segera beli cermin, terus sadar diri sebelum lo makin dihujat orang.",
    "Jangan tanya kapan nikah/punya pacar, tanyain kenapa orang se-tengil lo bisa bertahan hidup sampai sekarang.",
    "Keberuntungan lo hari ini lagi diculik alien, jangan harap bisa balik lagi.",
    "Lo itu definisi dari kata 'sia-sia', udah usaha tapi tetep aja nggak ada hasilnya.",
    "Sistem mendeteksi lo lagi stalking mantan, sadar bos, dia udah punya yang lebih kaya dan ganteng.",
    "Jangan berharap hidup lo bakal berubah, karena kelakuan lo aja masih tetep sampah kayak dulu.",
    "Ramalan gue: Hari ini lo bakal kena sial yang luar biasa, tapi tenang, itu udah biasa buat lo.",
    "Mending tidur daripada nanya ramalan, seenggaknya pas tidur lo nggak bikin orang lain emosi."
    "Lo tuh kayak iklan di YouTube: Suka muncul nggak diundang, dan bikin orang pengen nge-skip."
]

@CMD.UBOT("ramal")
async def ramalan_cyber(client, message):
    em = Emoji(client)
    await em.get()
    
    target = message.from_user
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except:
            target = message.from_user
            
    nama_target = f"<a href=tg://user?id={target.id}>{target.first_name}</a>"
    teks = random.choice(RAMALAN_LIST)
    
    caption = (
        f"<blockquote><b>╭──「 <emoji id=6089144627833611433>🔮</emoji> RAMALAN CYBER </b>\n"
        f"<b>│</b>\n"
        f"<b>│ Status:</b> <code>System Online</code>\n"
        f"<b>│ Target:</b> {nama_target}\n"
        f"<b>│</b>\n"
        f"<b>│ Prediksi:</b> <i>{teks}</i>\n"
        f"<b>╰──</b></blockquote>"
    )
    
    await message.delete()
    await client.send_message(message.chat.id, caption, parse_mode=enums.ParseMode.HTML)
