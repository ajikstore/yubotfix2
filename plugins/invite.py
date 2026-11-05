import asyncio

from pyrogram.errors import FloodWait, UserNotMutualContact, UserPrivacyRestricted

from kelra.helpers import CMD, Emoji

__MODULES__ = "Invite"
__HELP__ = """<blockquote>Command Help **Invite**</blockquote>

<blockquote expandable>    <u>**Adding user to chat**</u>
        `{0}invite` (username) or (username1, username2)</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

@CMD.UBOT("invite")
async def invite(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<b>{em.proses}{proses_}</b>")
    users = message.text.split()[1:]
    if not users:
        await proses.edit(f"{em.gagal}<b>Please provide a list of users to invite.</b>")
        return
    chat_id = message.chat.id
    for user in users:
        try:
            await client.add_chat_members(chat_id, user)
            await proses.edit(f"{em.sukses}<b>Succesfully adding {user}</b>")
        except UserNotMutualContact:
            await proses.edit(f"{em.gagal}<b>Failed to invite {user}: User not mutual contact.</b>")
        except UserPrivacyRestricted:
            await proses.edit(f"{em.gagal}<b>Failed to invite {user}: User privacy restricted.</b>")
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await proses.edit(f"{em.uptime}<b>Flood wait for {e.value} seconds.</b>")
            await client.add_chat_members(chat_id, user)
        except Exception as e:
            await proses.edit(f"{em.gagal}<b>Failed to invite {user}: {str(e)}</b>")
    return
