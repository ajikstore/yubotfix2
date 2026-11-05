import asyncio
import random

from kelra import *
from kelra.helpers import CMD, Emoji


__MODULES__ = "Cek ganteng"
__HELP__ = """<blockquote>Command Help **Cek ganteng**</blockquote>

<blockquote><u>**Get cek ganteng orang**</u>
    <u>**Get cek ganteng orang command**</u>
        `{0}cekganteng` (name)</blockquote>
    
<b>   {1}</b>
"""
__CATEGORY__ = "ʀᴇʟɪɢɪᴏɴ <emoji id=5436262556064817413>📚</emoji>"

@CMD.UBOT("cekganteng")
async def cekkhodam(client, message):
    try:
        nama = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if not nama:
            await message.edit("ɴᴀᴍᴀɴʏᴀ ᴍᴀɴᴀ")
            return

        def pick_random(options):
            return random.choice(options)

        hasil = f"""
 <blockquote><b>𖤐 ʜᴀsɪʟ ᴄᴇᴋ ɢᴀɴᴛᴇɴɢ:</b>
╭───────────────────────
├ •ɴᴀᴍᴀ : {nama}
├ •ɢᴀɴᴛᴇɴɢ : {pick_random(['ᴋᴀʏᴀ ᴋᴛʟ', 'ᴅɪᴋɪᴛ', 'ʙᴀɴʏᴀᴋ', 'sᴇᴛᴇɴɢᴀʜ', 'sᴇᴘᴇʀᴀᴘᴀᴛ', 'sᴇ ᴛᴇᴛᴇ'])}
├ •ɴɢᴇʀɪ ʙᴇᴛ ᴊɪʀ
╰────────────────────────
  **ɴᴇxᴛ ᴄᴇᴋ ɢᴀɴᴛᴇɴɢ sɪᴀᴘᴀ ʟᴀɢɪ.**</blockquote>       
      """
        await message.edit(hasil)
    except BaseException:
        pass
