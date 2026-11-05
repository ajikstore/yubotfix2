__MODULES__ = "History"
__HELP__ = """<blockquote>Command Help **History** </blockquote>

<blockquote expandable>        <u>**Get history name**</u>
    <u>**Get history name from user you want**</u>
        `{0}sg` (userid/username)</blockquote>

<b>   {1}</b>
"""

import asyncio

from pyrogram import raw

from kelra.helpers import CMD, Emoji


@CMD.UBOT("sg")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    try:
        if len(message.command) < 2 and not reply:
            return await message.reply(f"<blockquote>**{em.gagal}Please reply to a message or provide a username/id**</blockquote>")
        if reply:
            user = reply.from_user.id
        else:
            target = message.text.split()[1]
            user = (await client.get_users(target)).id
        proses_ = await em.get_costum_text()
        proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
        sg = "@SangMata_BOT"
        try:
            a = await client.send_message(sg, user)
            await asyncio.sleep(1)
            await a.delete()
        except Exception as e:
            return await proses.edit(f"<blockquote>**{em.gagal}{str(e)}**</blockquote>")
        async for respon in client.search_messages(a.chat.id):
            if respon.text == None:
                continue
            if not respon:
                return await message.reply(f"<blockquote>**{em.gagal}No response from Sangmata**</blockquote>")
            elif respon:
                await message.reply(f"<blockquote>{em.sukses} {respon.text}</blockquote>")
                break
        await proses.delete()
        try:
            user_info = await client.resolve_peer(sg)
            return await client.invoke(raw.functions.messages.DeleteHistory(peer=user_info, max_id=0, revoke=True))
        except Exception:
            pass
    except Exception as er:
        return await message.reply(f"<blockquote>**ERROR**: {str(er)}</blockquote>")
