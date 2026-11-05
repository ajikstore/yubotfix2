import asyncio 
import io 
import random
from uuid import uuid4 
 
from pyrogram import * 
from pyrogram.errors import ImageProcessFailed, MessageTooLong, RPCError
 
from config import API_BOTCHAX 
from kelra.helpers import CMD, Emoji, Message, Tools 
from kelra.logger import logger 
 
MODULES = "Khodam" 
HELP = """<blockquote>Command Help Khodam</blockquote> 
 
<blockquote expandable><u>Cek Khodam Seseorang</u> 
    <u>Gunakan perintah ini untuk cek khodam</u> 
        {0}khodam (reply atau tag user)</blockquote> 
 
<b>   {1}</b>""" 

__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"
 
MAX_CAPTION_LENGTH = 1024 
MAX_TEXT_LENGTH = 4000 
 
async def gen_kdm(text): 
    bahan = [ 
        { 
            "role": "system", 
            "content": "Anda adalah seorang paranormal paranormal sakti. Tugas Anda adalah mendeskripsikan khodam seseorang berdasarkan namanya. Deskripsikan wujud binatangnya, sifatnya, dan energinya dengan bahasa Indonesia yang mistis namun menghibur. Jangan terlalu panjang, maksimal 500 karakter.", 
        }, 
        {"role": "user", "content": f"Cek khodam untuk nama: {text}"}, 
    ] 
    # URL UDAH DIGANTI KE V2 DI BAWAH INI
    url = "https://api.botcahx.eu.org/api/search/openai-custom-v2" 
    payload = {"message": bahan, "apikey": f"{API_BOTCHAX}"} 
    try:
        res = await Tools.fetch.post(url, json=payload) 
        if res.status_code == 200: 
            data = res.json() 
            return data["result"].replace("\n", " ").strip() 
        else: 
            return "Khodam sepertinya sedang bersembunyi (API Error)."
    except:
        return "Gagal terhubung ke alam gaib (Connection Error)."
 
async def get_name(client, message): 
    full_name = None
    if message.reply_to_message: 
        user = message.reply_to_message.from_user
        if user:
            first_name = user.first_name 
            last_name = user.last_name or "" 
            full_name = f"{first_name} {last_name}".strip() 
    else: 
        input_text = await client.extract_user(message) 
        if input_text:
            try:
                user = await client.get_users(input_text)
                first_name = user.first_name 
                last_name = user.last_name or "" 
                full_name = f"{first_name} {last_name}".strip()
            except:
                full_name = input_text
        else:
            user = message.from_user
            full_name = f"{user.first_name} {user.last_name or ''}".strip()
    return full_name 
 
async def gen_img(text): 
    url = f"https://api.botcahx.eu.org/api/maker/text2img?text={text}&apikey={API_BOTCHAX}" 
    try:
        res = await Tools.fetch.get(url) 
        if res.status_code == 200:
            image_data = io.BytesIO(res.read())
            image_data.name = "khodam.jpg"
            return image_data
        return None
    except:
        return None
 
@CMD.UBOT("khodam|kodam") 
async def ckdm_cmd(client, message): 
    em = Emoji(client) 
    await em.get() 
    
    nama = await get_name(client, message) 
    proses_ = await em.get_costum_text() 
    pros = await message.reply(f"{em.proses}{proses_[4]}") 
    
    try: 
        deskripsi_khodam = await gen_kdm(nama) 
        
        caption = (
            f"{em.sukses}<b>Hasil Terawang Khodam <code>{nama}</code>:</b>\n\n"
            f"<blockquote>{deskripsi_khodam}</blockquote>\n\n"
            f"{em.profil} <b>Oleh: {client.me.mention}</b>"
        )
        
        short_desc = deskripsi_khodam[:50].replace(" ", ",")
        photo = await gen_img(short_desc) 
        
        if photo:
            try:
                final_caption = caption[:MAX_CAPTION_LENGTH-5] + "..." if len(caption) > MAX_CAPTION_LENGTH else caption
                
                await client.send_photo( 
                    message.chat.id, 
                    photo=photo, 
                    caption=final_caption, 
                    reply_to_message_id=message.id, 
                )
                return await pros.delete()
            except Exception as e:
                logger.error(f"Gagal kirim foto: {e}")
        
        final_text = caption[:MAX_TEXT_LENGTH-5] + "..." if len(caption) > MAX_TEXT_LENGTH else caption
        await message.reply(final_text)
        await pros.delete()
 
    except Exception as e: 
        try:
            await pros.edit(f"{em.gagal} Error: {str(e)[:100]}")
        except:
            await message.reply(f"{em.gagal} Error: {str(e)[:100]}")
