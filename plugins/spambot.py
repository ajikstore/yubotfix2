from asyncio import sleep

from pyrogram import raw
from pyrogram.errors import FloodWait

from kelra.helpers import CMD, Emoji

__MODULES__ = "Spambot"
__HELP__ = """<blockquote>Command Help **Spambot**</blockquote> 

<blockquote expandable>        <u>**Check spambot**<u>
    <u>**Check your status account from limit @spambot**</u>
        `{0}limit`</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴛᴏᴏʟs <emoji id=5435961551871813164>🛠</emoji>"

@CMD.UBOT("limit")
@CMD.FAKEDEV("limit")
async def _(client, message):
    return await spam_bot(client, message)


async def spam_bot(client, message):
    em = Emoji(client)
    await em.get()
    await client.unblock_user("SpamBot")
    xin = await client.resolve_peer("SpamBot")
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    msg = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    
    # Hapus pesan lama biar bersih
    try:
        await client.invoke(raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True))
    except:
        pass
    await sleep(0.5)

    await client.send_message("SpamBot", "/start")
    await sleep(2) # Beri waktu spambot membalas
    
    # Menggunakan get_chat_history agar realtime dan tidak cache
    isdone = None
    async for status in client.get_chat_history("SpamBot", limit=1):
        if status.text:
            isdone = status.text
        break
        
    if isdone:
        emoji = em.warn
        aman_words = ["Good news", "Kabar baik", "tidak dibatasi", "free as a bird"]
        if any(word in isdone for word in aman_words):
            emoji = em.sukses
            
        await client.send_message(
            message.chat.id,
            f"<blockquote>{emoji} **{isdone}**\n\n ~ {em.owner} **{client.me.first_name}**</blockquote>",
        )
        try:
            await client.invoke(raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True))
        except FloodWait as e:
            await sleep(e.value)
            await client.invoke(raw.functions.messages.DeleteHistory(peer=xin, max_id=0, revoke=True))
            
    return await msg.delete()
