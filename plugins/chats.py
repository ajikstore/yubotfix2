import asyncio

from pyrogram import raw
from pyrogram.errors import FloodWait, PeerIdInvalid

from kelra.helpers import CMD, Emoji

__MODULES__ = "Chats"
__HELP__ = """<blockquote>Command Help **Chats**</blockquote>

<blockquote expandable>    <u>**Clear chat user in group**</u>
        `{0}cc` (username/reply user)

    <u>**Endchat all bot**</u>
        `{0}endchat bot`

    <u>**Endchat all users**</u>
        `{0}endchat private`

    <u>**Endchat all bot and users**</u>
        `{0}endchat all`

    <u>**Endchat user**</u>
        `{0}endchat` (username/reply user)

    <u>**Create a channel**</u>
        `{0}create ch`

    <u>**Create a group**</u>
        `{0}create gc`

    <u>**Create invite chat link**</u>
        `{0}getlink`

    <u>**Get total member chat**</u>
        `{0}cekmember`

    <u>**Get online member chat**</u>
        `{0}cekonline`

    <u>**Check message count user**</u>
        `{0}cekmsg` (username/reply user)</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

@CMD.UBOT("cc")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        aan = await message.reply_text(f"<blockquote>{em.gagal}**Please reply to valid user_id!**</blockquote>")
        await asyncio.sleep(0.5)
        return await aan.delete()
    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        aa = await message.reply_text(f"<blockquote>{em.gagal}**Please reply to user or give username!**</blockquote>")
        await asyncio.sleep(0.5)
        return await aa.delete()
    await message.delete()
    try:
        return await client.delete_user_history(message.chat.id, user)
    except Exception:
        pass


@CMD.UBOT("endchat")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    query = ["bot", "private", "all"]
    if len(message.command) < 2 and not reply:
        return await proses.edit(f"<blockquote>{em.gagal}**Please give query or username!**</blockquote>")
    if len(message.command) == 1 and reply:
        who = reply.from_user.id
        try:
            info = await client.resolve_peer(who)
            await client.invoke(raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True))
        except PeerIdInvalid:
            pass
        await message.reply(f"<blockquote>{em.sukses}<b>Succesfully endchat: {who}</b></blockquote>")
    elif message.command[1] in query:
        target = await client.get_chat_id(message.command[1])
        for ids in target:
            try:
                info = await client.resolve_peer(ids)
                await client.invoke(raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True))
            except PeerIdInvalid:
                continue
            except FloodWait as e:
                await asyncio.sleep(e.value)
                info = await client.resolve_peer(ids)
                await client.invoke(raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True))
        await message.reply(f"<blockquote>{em.sukses}**Succesfully endchat: `{message.command[1]}`, total: `{len(target)}`**</blockquote>")
    else:
        who = message.text.split()[1]
        try:
            info = await client.resolve_peer(who)
            await client.invoke(raw.functions.messages.DeleteHistory(peer=info, max_id=0, revoke=True))
        except PeerIdInvalid:
            pass
        await message.reply(f"<blockquote>{em.sukses}<b>Succesfully endchat: {who}</b></blockquote>")
    return await proses.delete()


@CMD.UBOT("create")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    if len(message.command) < 3:
        return await message.reply(f"<blockquote>{em.gagal}<b>Please `{message.text.split()[0]}` `gc` to create a group, or `ch` to create a channel.</b></blockquote>")
    group_type = message.command[1]
    split = message.command[2:]
    group_name = " ".join(split)
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    args = ["gc", "ch"]
    if message.command[1] not in args:
        return await proses.edit(f"<blockquote>{em.gagal}<b>Please `{message.text.split()[0]}` `gc` to create a group, or `ch` to create a channel.</b></blockquote>")
    try:
        desc = "Welcome To My " + ("Group" if group_type == "gc" else "Channel")
        if group_type == "gc":
            _id = await client.create_supergroup(group_name, desc)
            link = await client.get_chat(_id.id)
            return await proses.edit(
                f"<blockquote>{em.sukses}<b>Succesfully created group: [{group_name}]({link.invite_link})</b></blockquote>",
                disable_web_page_preview=True,
            )
        elif group_type == "ch":
            _id = await client.create_channel(group_name, desc)
            link = await client.get_chat(_id.id)
            return await proses.edit(
                f"<blockquote>{em.sukses}<b>Succesfully created channel: [{group_name}]({link.invite_link})</b></blockquote>",
                disable_web_page_preview=True,
            )
    except Exception as err:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(err)}</blockquote>")


@CMD.UBOT("getlink")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    try:
        link = await client.export_chat_invite_link(chat_id)
        return await proses.edit(
            f"<blockquote>{em.sukses}**This is invite link: {chat_id}\n\n{link}</blockquote>",
            disable_web_page_preview=True,
        )
    except Exception as er:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** `{str(er)}`</blockquote>")


@CMD.UBOT("cekmember")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    try:
        member_count = await client.get_chat_members_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(f"<blockquote>{em.sukses}**Total members in group: {chat_id} is `{member_count}` members.**</blockquote>")
    except Exception as e:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(e)}</blockquote>")


@CMD.UBOT("cekonline")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")
    try:
        member_online = await client.get_chat_online_count(chat_id)
        await asyncio.sleep(1)
        return await proses.edit(f"<blockquote>{em.sukses}**Total members online in group: {chat_id} is `{member_online}` members.**</blockquote>")
    except Exception as e:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(e)}</blockquote>")


@CMD.UBOT("cekmsg")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    chat_id = message.chat.id
    user_id = None

    if len(message.command) > 1:
        chat_id = message.command[1] if message.command[1].isdigit() else chat_id
        user_id = message.command[2] if len(message.command) > 2 else message.command[1]
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    if not user_id:
        return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to a user or provide a username/ID!**</blockquote>")

    try:
        user = await client.get_users(user_id)
        umention = user.mention
    except (PeerIdInvalid, KeyError):
        return await message.reply_text(f"<blockquote>{em.gagal}**Error: PeerIdInvalid or invalid user ID/username.**</blockquote>")

    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")

    try:

        total_msg = await client.search_messages_count(chat_id, from_user=user.id)
        await asyncio.sleep(1)
        await proses.edit(f"<blockquote>{em.sukses}**Total messages by {umention} in chat `{chat_id}`: `{total_msg}` messages.**</blockquote>")
    except Exception as e:
        await proses.edit(f"<blockquote>{em.gagal}**Error:** `{str(e)}`</blockquote>")
