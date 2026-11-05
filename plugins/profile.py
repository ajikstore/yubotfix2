import asyncio
import os
from datetime import datetime
from io import BytesIO

from pyrogram import enums
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import (
    ChannelPrivate,
    FloodWait,
    PeerIdInvalid,
    UsernameOccupied,
    UserNotParticipant,
)
from pyrogram.raw import functions

from kelra.helpers import CMD, Emoji

__MODULES__ = "Profile"
__HELP__ = """<blockquote>Command Help **Profile** </blockquote>

<blockquote expandable>        <u>**Check stats account**</u>
    <u>**This command for check list your admins group**</u>
        `{0}adminlist`
    <u>**Get stats your account, like group counts, channel, bot, private messages**</u>
        `{0}me`

        <u>**Set delete username**</u>
    <u>**You can set new username to your account**</u>
        `{0}setuname` (text/reply text)
    <u>**You delete the username from your account**</u>
        `{0}remuname`

        <u>**Set profile bio**</u>
    <u>**You can change bio from your account**</u>
        `{0}setbio` (text/reply text)

        <u>**Set profile name**</u>
    <u>**You can set new name to your account**</u>
        `{0}setname` (text/reply text)

        <u>**Set profile photo**</u>
    <u>**You can set new profile photo to your account**</u>
        `{0}setpp` (reply media)

        <u>**Block unblock user**</u>
    <u>**You can block the user if you want**</u>
        `{0}block` (username/reply user)
    <u>**Unblock the user**</u>
        `{0}unblock` (username/reply user)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

@CMD.UBOT("setonline")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Use the command like this:</b>\n<code>{x}setonline</code> on/off.</blockquote>")
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to set online status ..</b></blockquote>")
    handle = message.text.split(None, 1)[1]
    try:
        if handle.lower() == "off":
            await client.invoke(functions.account.UpdateStatus(offline=False))
            return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed online status to: <code>{handle}</code></b></blockquote>")
        elif handle.lower() == "on":
            await client.invoke(functions.account.UpdateStatus(offline=True))
            return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed online status to: <code>{handle}</code></b></blockquote>")
        else:
            return await pros.edit(f"<blockquote>{emo.gagal}<b>Use the command like this:</b>\n<code>{x}setonline</code> on/off.</blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{e}</code></blockquote>")


@CMD.UBOT("unblock")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Provide username/user_id/reply to user's message.</b></blockquote>")
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to unblock user ..</b></blockquote>")
    try:
        user = await client.get_users(user_id)
    except PeerIdInvalid:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>I have never interacted with <code>{user_id}</code></b></blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{str(e)}</code></blockquote>")
    if user.id == client.me.id:
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Ok!</b></blockquote>")
    await client.unblock_user(user.id)
    return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully unblocked {user.mention}.</b></blockquote>")


@CMD.UBOT("block")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    user_id = await client.extract_user(message)
    if not user_id:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Provide username/user_id or reply to user's message.</b></blockquote>")
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to block user ..</b></blockquote>")
    try:
        user = await client.get_users(user_id)
    except PeerIdInvalid:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>I have never interacted with <code>{user_id}</code></b></blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{str(e)}</code></blockquote>")
    if user.id == client.me.id:
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Ok!</b></blockquote>")
    await client.block_user(user_id)
    return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully blocked {user.mention}.</b></blockquote>")


@CMD.UBOT("setname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to change name ..</b></blockquote>")
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Provide text or reply to a message to set as your name.</b></blockquote>")
    elif len(message.command) > 1:
        nama = message.text.split(None, 2)
        name = nama[1]
        namee = nama[2] if len(nama) > 2 else ""

        try:
            await client.update_profile(first_name=name)
            await client.update_profile(last_name=namee)
            return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed name to: <code>{name} {namee}</code></b></blockquote>")
        except Exception as e:
            return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{e}</code></blockquote>")


@CMD.UBOT("setuname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await message.reply(f"<blockquote>{emo.gagal}<b>Provide text or reply to a message to set as your username.</b></blockquote>")
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to change username ..</b></blockquote>")
    if rep:
        uname = rep.text or rep.caption
    elif len(message.command) > 1:
        nama = message.text.split(None, 1)
        uname = nama[1]
    else:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Provide text or reply to a message to set as your username.</b></blockquote>")

    try:
        await client.set_username(username=uname)
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed username to: <code>{uname}</code></b></blockquote>")
    except FloodWait as e:
        wait = int(e.value)
        await asyncio.sleep(wait)
        await client.set_username(username=uname)
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed username to: <code>{uname}</code></b></blockquote>")
    except UsernameOccupied:
        return await pros.edit(f"<blockquote>{emo.gagal}<b><code>{uname}</code> is already taken by another user.</b></blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{e}</code></blockquote>")


@CMD.UBOT("remuname")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to remove username ..</b></blockquote>")

    try:
        await client.set_username(username="")
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Username successfully removed.</b></blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{e}</code></blockquote>")


@CMD.UBOT("setbio")
@CMD.FAKEDEV("setbio")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to change bio ..</b></blockquote>")
    rep = message.reply_to_message
    if len(message.command) == 1 and not rep:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Provide text or reply to a message.</b></blockquote>")
    if rep:
        bio = rep.text or rep.caption
    elif len(message.command) > 1:
        bio = message.text.split(None, 1)[1]
    try:
        await client.update_profile(bio=bio)
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully changed bio to: <code>{bio}</b></blockquote>")
    except Exception as e:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Error:</b> <code>{e}</code></blockquote>")


@CMD.UBOT("adminlist")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to check the list of groups where you are an admin ..</b></blockquote>")
    a_chats = []
    me = await client.get_me()
    async for dialog in client.get_dialogs():
        try:
            tipe = dialog.chat.type
            if tipe in (enums.ChatType.SUPERGROUP, enums.ChatType.GROUP):
                try:
                    gua = await dialog.chat.get_member(int(me.id))
                    if gua.status in (
                        enums.ChatMemberStatus.OWNER,
                        enums.ChatMemberStatus.ADMINISTRATOR,
                    ):
                        a_chats.append(dialog.chat)
                except Exception:
                    continue
        except Exception:
            continue

    text = "<blockquote expandable><b>❒ LIST OF GROUPS WHERE YOU ARE AN ADMIN:</b>\n┃\n"
    if len(a_chats) == 0:
        text += "<b>You are not an admin anywhere.</b>"
        return await pros.edit(f"{text}")
    for count, chat in enumerate(a_chats, 1):
        try:
            title = chat.title
        except Exception:
            title = "Private Group"
        if count == len(a_chats):
            text += f"<b>┖ {title}</b>\n"
        else:
            text += f"<b>┣ {title}</b>\n<blockquote>"

    if len(text) > 4096:
        with BytesIO(str.encode(text)) as out_file:
            out_file.name = "adminlist.txt"
            await message.reply_document(
                document=out_file,
                caption=f"<blockquote>{emo.sukses}<b>Admin List {client.me.mention}.</b></blockquote>",
            )
            os.remove(out_file)
            return await pros.delete()
    else:
        return await pros.edit(f"{text}")


@CMD.UBOT("setpp")
@CMD.FAKEDEV("setpp")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    po = "storage/TM_BLACK.png"
    replied = message.reply_to_message
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to change profile picture ..</b></blockquote>")
    if replied and replied.media and (replied.photo or (replied.document and "image" in replied.document.mime_type)):
        prop = await client.download_media(message=replied, file_name=po)
        await client.set_profile_photo(photo=prop)
        await client.send_photo(
            message.chat.id,
            prop,
            caption=f"<blockquote>{emo.sukses}<b>Successfully changed your profile picture.</b></blockquote>",
        )
        if os.path.exists(prop):
            os.remove(prop)
        return await pros.delete()
    else:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>Reply to a photo/image, or a document that is a photo/image to set as your profile picture.</b></blockquote>")


@CMD.UBOT("me")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing to gather statistics ..</b></blockquote>")
    start = datetime.now()
    pc = 0
    groups = 0
    super_groups = 0
    channels = 0
    bots = 0
    adminchats = 0
    banned = 0
    here = set()
    gue = await client.get_me()

    try:
        async for dialog in client.get_dialogs():
            try:
                if dialog.chat.type == ChatType.PRIVATE:
                    pc += 1
                elif dialog.chat.type == ChatType.BOT:
                    bots += 1
                elif dialog.chat.type == ChatType.GROUP:
                    groups += 1
                    ucel = await dialog.chat.get_member(int(gue.id))
                    if ucel.status in (
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ):
                        adminchats += 1
                elif dialog.chat.type == ChatType.SUPERGROUP:
                    super_groups += 1
                    user_s = await dialog.chat.get_member(int(gue.id))
                    if user_s.status in (
                        ChatMemberStatus.OWNER,
                        ChatMemberStatus.ADMINISTRATOR,
                    ):
                        adminchats += 1
                elif dialog.chat.type == ChatType.CHANNEL:
                    channels += 1
            except ChannelPrivate:
                banned += 1
                here.add(dialog.chat.id)
                continue
            except UserNotParticipant:
                await client.leave_chat(dialog.chat.id)
                print(f"Bot is not a member of this chat, leaving: {dialog.chat.id}")
                continue
    except ChannelPrivate:
        banned += 1
        here.add(dialog.chat.id)
    except Exception as e:
        print(f"An error occurred: {str(e)} {dialog.chat.id}")

    end = datetime.now()
    waktu = (end - start).seconds

    if not here:
        here = 0

    return await pros.edit(
        f"""
<blockquote expandable>{emo.sukses}<b>Successfully extracted your data in <code>{waktu}</code> seconds:

• <code>{pc}</code> Private Messages.
• <code>{groups}</code> Groups.
• <code>{super_groups}</code> Super Groups.
• <code>{channels}</code> Channels.
• <code>{adminchats}</code> Admin Chats.
• <code>{bots}</code> Bots.
• <code>{banned}</code> Problematic Groups.

I encountered issues with these chats: 
• <code>{here}</code></b></blockquote>
"""
    )
