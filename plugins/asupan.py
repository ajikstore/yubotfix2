import asyncio
import aiohttp
from pyrogram import enums, types
from config import API_BOTCHAX
from kelra.helpers import CMD, Emoji

__MODULES__ = "Asupan"
__HELP__ = """<blockquote>Command Help **Asupan**</blockquote>

<blockquote expandable>        <u>**Get photos**</u>
    <u>**You can get girl photo**</u>
        `{0}cewek`
    <u>**You can get boy photo**</u>
        `{0}cowok`
    <u>**You can get pap random**</u>
        `{0}pap`
    <u>**You can get couple photo**</u>
        `{0}ppcp`
        
        <u>Get videos</u>
    <u>**Get random asupan video**</u>
        `{0}asupan`</blockquote>
    
<b>   {1}</b>
"""

# FUNGSI AJAIB BUAT NGECEK API BOTCAHX
async def get_api_media(endpoint):
    url = f"https://api.botcahx.eu.org{endpoint}?apikey={API_BOTCHAX}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                try:
                    data = await resp.json()
                    # Kalau API ngebales pakai JSON, kita ambil link-nya
                    if "result" in data:
                        return data["result"]
                except:
                    # Kalau API langsung ngasih gambar/video, kita pakai URL aslinya
                    return url
    raise Exception("API lagi sibuk atau limit lu habis ngab!")


@CMD.UBOT("asupan")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    y = await message.reply(f"<blockquote><b>{em.proses}{proses_[4]}...</b></blockquote>")
    
    try:
        # Nembak ke endpoint /api/asupan/asupan
        media_url = await get_api_media("/api/asupan/asupan")
        
        await client.send_video(
            message.chat.id,
            video=media_url,
            caption=f"<blockquote>{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b></blockquote>",
            reply_to_message_id=message.id,
        )
        await y.delete()
    except Exception as e:
        await y.edit(f"<blockquote>{em.gagal}<b>Error asupan: {str(e)}</b></blockquote>")


@CMD.UBOT("cewek")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    y = await message.reply(f"<blockquote><b>{em.proses}{proses_[4]}...</b></blockquote>")
    
    try:
        # Nembak ke endpoint cewek (cecan)
        media_url = await get_api_media("/api/asupan/cecan")
        
        await client.send_photo(
            message.chat.id,
            photo=media_url,
            caption=f"<blockquote>{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b></blockquote>",
            reply_to_message_id=message.id,
        )
        await y.delete()
    except Exception as e:
        await y.edit(f"<blockquote>{em.gagal}<b>Error cewek: {str(e)}</b></blockquote>")


@CMD.UBOT("cowok")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    y = await message.reply(f"<blockquote><b>{em.proses}{proses_[4]}...</b></blockquote>")
    
    try:
        # Nembak ke endpoint cowok (cogan)
        media_url = await get_api_media("/api/asupan/cogan")
        
        await client.send_photo(
            message.chat.id,
            photo=media_url,
            caption=f"<blockquote>{em.sukses}<b>Upload by: <a href=tg://user?id={client.me.id}>{client.me.first_name} {client.me.last_name or ''}</a></b></blockquote>",
            reply_to_message_id=message.id,
        )
        await y.delete()
    except Exception as e:
        await y.edit(f"<blockquote>{em.gagal}<b>Error cowok: {str(e)}</b></blockquote>")


@CMD.UBOT("pap")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    y = await message.reply(f"<blockquote><b>{em.proses}{proses_[4]}...</b></blockquote>")
    
    try:
        # Pakai endpoint random buat pap (misal pakai ukhty)
        media_url = await get_api_media("/api/asupan/ukhty")
        
        await client.send_photo(
            message.chat.id,
            photo=media_url,
            caption=f"<blockquote>{em.sukses}<b>Ange ga kamu???</b></blockquote>",
            reply_to_message_id=message.id,
        )
        await y.delete()
    except Exception as e:
        await y.edit(f"<blockquote>{em.gagal}<b>Error pap: {str(e)}</b></blockquote>")


@CMD.UBOT("ppcp")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Proses mengunduh Foto Profil berpasangan ..</b></blockquote>")

    try:
        # Nembak ke endpoint PPCP dari BOTCAHX
        url = f"https://api.botcahx.eu.org/api/randomgambar/ppcouple?apikey={API_BOTCHAX}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception("Server error")
                
                data = await resp.json()
                if "result" not in data or "male" not in data["result"]:
                    raise Exception("Format JSON berubah")
                
                foto_cowok = data["result"]["male"]
                foto_cewek = data["result"]["female"]

        media_group = [
            types.InputMediaPhoto(foto_cowok),
            types.InputMediaPhoto(foto_cewek)
        ]

        await client.send_media_group(
            message.chat.id,
            media=media_group,
            reply_to_message_id=message.id,
        )
        await pros.delete()

    except Exception as error:
        await pros.edit(f"<blockquote>{emo.gagal}<b>Error ppcp:</b>\n<code>{error}</code></blockquote>")
