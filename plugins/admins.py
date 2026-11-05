import asyncio
import os

from pyrogram import enums
from pyrogram.errors import (
    FloodWait,
    PeerIdInvalid,
    UsernameInvalid,
    UsernameNotOccupied,
)
from pyrogram.types import ChatPermissions, ChatPrivileges

from config import DEVS
from kelra.helpers import CMD, Emoji

__MODULES__ = "Admins"
__HELP__ = """<blockquote>Command Help **Admins**</blockquote>

<blockquote expandable>    <u>**Kick user from chat**</u>
        `{0}kick` (username/reply user)
    <u>**Kick user with delete the messages**</u>
        `{0}delkick` (username/reply user)
        
    <u>**Ban user from chat**</u>    
        `{0}ban` (username/reply user)
    <u>**Ban user with delete th messages**</u>
        `{0}delban` (username/reply user)
    <u>**Unban user from chat**</u>
        `{0}unban` (username/reply user)
        
    <u>**Mute user from chat**</u>
        `{0}mute` (username/reply user)
    <u>**Mute user with delete message**</u>
        `{0}delmute` (username/reply user)
    <u>**Unmute user from chat**</u>
        `{0}unmute` (username/reply user)
        
    <u>**Banned deleted account from chat**</u>
        `{0}zombies`
        
    <u>**Pin the message from chat**</u>    
        `{0}pin` (reply message) 
    <u>**Unpin the message from chat**</u>    
        `{0}unpin` (reply message)
        
    <u>**Delete the message from chat**</u>    
        `{0}del` (reply message) 
    <u>**Delete your message from chat**</u>    
        `{0}purgeme` (number)
    <u>**Delete all message from chat**</u>    
        `{0}purge` (reply message)
        
    <u>**Add user to admins**</u>    
        `{0}promote` (username/reply user)
    <u>**Add user to admins with full acces**</u>    
        `{0}fullpromote` (username/reply user)
    <u>**Delete user from admins**</u>    
        `{0}demote` (username/reply user)
        
    <u>**Get admins from chat**</u>
        `{0}staff` 
    <u>**Change user admin title from chat**</u>
        `{0}title` (username/reply user) (title)
    <u>**Change description group**</u>
        `{0}group desc` (text/reply text)
    <u>**Change title group**</u>
        `{0}group title` (text/reply text)
    <u>**Change media photo group**</u>
        `{0}group media` (text/reply text)</blockquote>
 
<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

@CMD.UBOT("staff")
@CMD.ONLY_GROUP
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    chat = message.chat
    if chat.username:
        uname = chat.username
    else:
        uname = chat.id
    owner = []
    co_founder = []
    admin = []
    bot = []
    pros = await message.reply(f"<blockquote>{emo.proses}<b>Processing staff data in <code>{message.chat.title or 'this group'}</code> ..</b></blockquote>")
    await asyncio.sleep(1)
    if uname:
        chat_link = f"<a href='t.me/{uname}'>{chat.title}</a>"
    else:
        chat_link = f"<a href='{message.link}'>{chat.title}</a>"
    async for dia in client.get_chat_members(chat.id):
        user = dia.user
        ijin = dia.privileges
        status = dia.status
        title = dia.custom_title
        botol = user.is_bot
        mention = f"<blockquote><a href=tg://user?id={user.id}>{user.first_name or ''} {user.last_name or ''}</a></blockquote>"
        if (
            status == enums.ChatMemberStatus.ADMINISTRATOR
            and ijin.can_promote_members
            and ijin.can_manage_chat
            and ijin.can_delete_messages
            and ijin.can_manage_video_chats
            and ijin.can_restrict_members
            and ijin.can_change_info
            and ijin.can_invite_users
            and ijin.can_pin_messages
            and not botol
        ):
            if title:
                co_founder.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                co_founder.append(f" ┣ {mention} <u>as</u> <i>Co-Founder</i>")
        elif status == enums.ChatMemberStatus.ADMINISTRATOR and not botol:
            if title:
                admin.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                admin.append(f" ┣ {mention} <u>as</u> <i>Admin</i>")
        elif status == enums.ChatMemberStatus.OWNER:
            if title:
                owner.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                owner.append(f" ┣ {mention} <u>as</u> <i>Founder</i>")
        elif botol:
            if title:
                bot.append(f" ┣ {mention} <u>as</u> <i>{title}</i>")
            else:
                bot.append(f" ┣ {mention} <u>as</u> <i>Bot Admin</i>")

    result = "<b>Administrator Structure in {}</b>\n\n\n".format(chat_link)
    if owner:
        on = owner[-1].replace(" ┣", "┗")
        owner.pop(-1)
        owner.append(on)
        result += "<b>👑 Founder : </b>\n ┃\n {}\n\n".format(owner[0])
    if co_founder:
        cof = co_founder[-1].replace(" ┣", " ┗")
        co_founder.pop(-1)
        co_founder.append(cof)
        result += "<b>👨🏻‍💻 Co-Founder : </b>\n ┃\n" + "\n".join(co_founder) + "\n\n"
    if admin:
        adm = admin[-1].replace(" ┣", " ┗")
        admin.pop(-1)
        admin.append(adm)
        result += "<b>🧑🏻‍💻 Admin : </b>\n ┃\n" + "\n".join(admin) + "\n\n"
    if bot:
        botak = bot[-1].replace(" ┣", " ┗")
        bot.pop(-1)
        bot.append(botak)
        result += "<b>🤖 Bots : </b>\n ┃\n" + "\n".join(bot) + "\n"

    photo_path = None
    if message.chat.photo:
        try:
            photo_path = await client.download_media(message.chat.photo.big_file_id)
            await client.send_photo(
                message.chat.id,
                photo=photo_path,
                caption=f"{result}",
            )
        except Exception as e:
            print(f"Error sending media: {str(e)}")
            await message.reply(f"{result}", disable_web_page_preview=True)
    else:
        await message.reply(f"{result}", disable_web_page_preview=True)

    if photo_path and os.path.exists(photo_path):
        os.remove(photo_path)

    return await pros.delete()


async def admin_check(message, user_id):
    c = message._client
    status = (await c.get_chat_member(message.chat.id, user_id)).status
    admins = [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    if status not in admins:
        return False
    return True


async def member_check(message, user_id):
    client = message._client
    check_user = (await client.get_chat_member(message.chat.id, user_id)).privileges
    user_type = check_user.status
    if user_type == enums.ChatMemberStatus.MEMBER:
        return False
    if user_type == enums.ChatMemberStatus.ADMINISTRATORS:
        add_adminperm = check_user.can_promote_members
        return bool(add_adminperm)
    return True


@CMD.UBOT("purgeme")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if len(message.command) != 2:
        return await message.delete()
    n = message.reply_to_message if message.reply_to_message else message.text.split(None, 1)[1].strip()
    if not n.isnumeric():
        return await message.delete()
    n = int(n)
    if n < 1:
        return await message.delete()
    chat_id = message.chat.id
    message_ids = [
        message.id
        async for message in client.search_messages(
            chat_id,
            from_user=int(message.from_user.id),
            limit=n,
        )
    ]
    if not message_ids:
        return
    to_delete = [message_ids[i : i + 999] for i in range(0, len(message_ids), 999)]
    for hundred_messages_or_less in to_delete:
        return await client.delete_messages(
            chat_id=chat_id,
            message_ids=hundred_messages_or_less,
            revoke=True,
        )


@CMD.UBOT("purge")
async def _(client, message):
    if not message.reply_to_message:
        return await message.delete()

    await message.delete()
    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
        message.reply_to_message.id,
        message.id,
    ):
        message_ids.append(message_id)
        if len(message_ids) == 100:
            await client.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,
            )
            message_ids = []

    if len(message_ids) > 0:
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )
    return


@CMD.UBOT("kick|delkick")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need to specify a user (either by reply or username/ID)!</b></blockquote>")
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need meet before interact!!</b></blockquote>")

    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in DEVS:
        return await message.reply_text(f"<blockquote>{em.gagal}<b>Go to the heal now!!</b></blockquote>")

    msg = f"<blockquote>{em.warn}<b>Kicked user {mention}</b></blockquote>"
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
        await message.delete()
    try:
        await message.chat.ban_member(user_id)
    except Exception as er:
        return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
    teks = await message.reply_text(msg)
    await asyncio.sleep(1)
    await teks.delete()
    return await message.chat.unban_member(user_id)


@CMD.UBOT("ban|delban|unban")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need to specify a user (either by reply or username/ID)!</b></blockquote>")
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need meet before interact!!</b></blockquote>")
    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in DEVS:
        return await message.reply_text(f"<blockquote>{em.gagal}<b>Go to the heal now!!</b></blockquote>")

    if message.command[0] == "unban":
        try:
            await message.chat.unban_member(user_id)
        except Exception as er:
            return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
        teks = await message.reply_text(f"<blockquote>{em.sukses}<b>Unbanned: {mention}!</b></blockquote>")
        await asyncio.sleep(1)
        return await teks.delete()
    else:
        msg = f"<blockquote>{em.block}<b>Banned user {mention}</b></blockquote>"
        if message.command[0][0] == "d":
            await message.reply_to_message.delete()
            await message.delete()
        try:
            await message.chat.ban_member(user_id)
        except Exception as er:
            return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
        teks = await message.reply_text(msg)
        await asyncio.sleep(1)
        return await teks.delete()


@CMD.UBOT("del")
async def _(client, message):
    await message.delete()
    try:
        return await message.reply_to_message.delete()
    except Exception:
        return


@CMD.UBOT("pin|unpin")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if not message.reply_to_message:
        return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message!**</blockquote>")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await message.reply_text(
            f"<blockquote>{em.sukses}<b>Unpinned [this]({r.link}) message!</b></blockquote>",
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=False)
    return await message.reply(
        f"<blockquote>{em.sukses}<b>Pinned [this]({r.link}) message!</b></blockquote>",
        disable_web_page_preview=True,
    )


@CMD.UBOT("mute|delmute|unmute")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need to specify a user (either by reply or username/ID)!</b></blockquote>")
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need meet before interact!!</b></blockquote>")
    mention = user.mention
    user_id = user.id
    if user_id == client.me.id or user_id in DEVS:
        return await message.reply_text(f"<blockquote>{em.gagal}<b>Go to the heal now!!</b></blockquote>")

    if message.command[0] == "unmute":
        try:
            await message.chat.unban_member(user_id)
            teks = await message.reply_text(f"<blockquote>{em.block}<b>Unmuted user {mention}</b></blockquote>")
            await asyncio.sleep(1)
            return await teks.delete()
        except Exception as er:
            return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
    else:
        msg = f"<blockquote>{em.block}<b>Muted user {mention}</b></blockquote>"
        if message.command[0][0] == "d":
            await message.reply_to_message.delete()
            await message.delete()
        try:
            await message.chat.restrict_member(user_id, permissions=ChatPermissions())
            teks = await message.reply_text(msg)
            await asyncio.sleep(1)
            return await teks.delete()
        except Exception as er:
            return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")


@CMD.UBOT("zombies")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    failed = 0
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    mt = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")

    async for i in client.get_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
                banned_users += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await mt.edit(f"<blockquote>**FloodWait waiting for `{e.value}` seconds!**</blockquote>")
            except Exception:
                failed += 1
        return await mt.edit(f"<blockquote>{em.sukses}**Succesfuly banned deleted account: `{banned_users}`, failed: `{failed}`</blockquote>")
    else:
        return await mt.edit(f"<blockquote>{em.gagal}**No deleted accounts here!**</blockquote>")


@CMD.UBOT("report")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if not message.reply_to_message:
        return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message!**</blockquote>")

    reply = message.reply_to_message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if reply_id == user_id:
        return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message to member!**</blockquote>")

    list_of_admins = await admin_check(message, user_id)
    linked_chat = (await client.get_chat(message.chat.id)).linked_chat
    if linked_chat is not None:
        if list_of_admins is True and reply_id == message.chat.id or reply_id == linked_chat.id:
            return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message to member!**</blockquote>")
    else:
        if list_of_admins is True and reply_id == message.chat.id:
            return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message to member!**</blockquote>")

    user_mention = reply.from_user.mention if reply.from_user else reply.sender_chat.title
    text = f"<blockquote>{em.warn}<b>Reported to admins, user: {user_mention}!</b></blockquote>"
    admin_data = [i async for i in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)]
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"
    return await message.reply_to_message.reply_text(text)


@CMD.UBOT("fullpromote|promote|demote")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    command = message.command[0]

    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need to specify a user (either by reply or username/ID)!</b></blockquote>")
    try:
        user = await client.get_users(target)
    except (PeerIdInvalid, KeyError, UsernameInvalid, UsernameNotOccupied):
        return await message.reply(f"<blockquote>{em.gagal}<b>You need meet before interact!!</b></blockquote>")
    user.mention
    user_id = user.id

    if user_id == client.me.id:
        return await message.reply_text(f"<blockquote>{em.gagal}**Please reply to message to member!**</blockquote>")

    # Check admin rights
    if command != "demote":
        is_right = await client.get_chat_member(message.chat.id, client.me.id)
        if not is_right.privileges.can_promote_members:
            return await message.reply_text(f"<blockquote>{em.gagal}**You don't have the right to promote members in this group!**</blockquote>")
    else:
        botol = await admin_check(message, client.me.id)
        if not botol:
            return await message.reply_text(f"<blockquote>{em.gagal}**You are not an admin in this group!**</blockquote>")
        is_admin = await admin_check(message, user_id)
        if not is_admin:
            return await message.reply_text(f"<blockquote>{em.gagal}**Yes they are still member!**</blockquote>")

    try:
        if message.chat.type in [enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
            if len(message.text.split()) >= 3 and not message.reply_to_message:
                title = " ".join(message.text.split()[2:16])
            elif len(message.text.split()) >= 2 and message.reply_to_message:
                title = " ".join(message.text.split()[1:16])
            else:
                title = f"{user.first_name}"
            if command in ["promote", "fullpromote"]:

                privileges = ChatPrivileges(
                    can_change_info=command == "fullpromote",
                    can_invite_users=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_promote_members=command == "fullpromote",
                    can_manage_chat=True,
                    can_manage_video_chats=True,
                )

                await client.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    privileges=privileges,
                )
                await client.set_administrator_title(message.chat.id, user_id, title)

                return await message.reply_text(f"<blockquote>{em.sukses}<b>Successfully promoted user {user.mention} to admin!</b></blockquote>")

            else:  # demote
                await client.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id,
                    privileges=ChatPrivileges(
                        can_change_info=False,
                        can_invite_users=False,
                        can_delete_messages=False,
                        can_restrict_members=False,
                        can_pin_messages=False,
                        can_promote_members=False,
                        can_manage_chat=False,
                        can_manage_video_chats=False,
                    ),
                )
                return await message.reply_text(f"<blockquote>{em.sukses}<b>Successfully demoted user {user.mention} from admin!</b></blockquote>")
    except Exception as er:
        return await message.reply_text(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")


@CMD.UBOT("title|group")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    prefix = next(iter(client.get_prefix(client.me.id)))

    if len(message.text.split()) == 1 and not message.reply_to_message:
        return await message.reply(f"<blockquote>{em.gagal}**Please provide command specifications!**</blockquote>")

    command = message.command[0]

    try:
        if command == "group":
            return await handle_group_command(client, message, em, prefix)
        elif command == "title":
            return await handle_title_command(client, message, em, prefix)
        else:
            await message.reply(f"<blockquote>{em.gagal}**Please provide command specifications!**</blockquote>")
    except Exception as e:
        await message.reply(f"<blockquote>{em.gagal}**ERROR: `{str(e)}`**</blockquote>")


async def handle_group_command(client, message, em, prefix):
    if len(message.command) < 2:
        return await message.reply(f"<blockquote>{em.gagal}**Please provide command specifications! Example: `{prefix}group [desc or title]` [text here or reply to text]!**</blockquote>")

    query = message.command[1]
    valid_queries = ["desc", "title", "media"]

    if query not in valid_queries:
        return await message.reply(f"<blockquote>{em.gagal}**Please provide command specifications! Example: `{prefix}group [desc or title]` [text here or reply to text]!**</blockquote>")

    reply = message.reply_to_message
    content = None

    if query in ["desc", "title"]:
        if reply:
            content = reply.text or reply.caption
        elif len(message.command) > 2:
            content = message.text.split(None, 2)[2]

        if not content:
            return await message.reply(f"<blockquote>{em.gagal}**Please give me description to set. Example: `{prefix}group [desc or title]` [text here or reply to text]!**</blockquote>")

        chat = await client.get_chat(message.chat.id)

        if query == "desc":
            await message.chat.set_description(content)
            return await message.reply(f"<blockquote>{em.sukses}**Successfully set description group: `{chat.description}` to: `{content}`**</blockquote>")
        else:  # title
            await message.chat.set_title(content)
            return await message.reply(f"<blockquote>{em.sukses}**Successfully set title group: `{chat.title}` to: `{content}`**</blockquote>")

    else:  # media
        if not reply or not (reply.photo or reply.video):
            return await message.reply(f"<blockquote>{em.gagal}**Please reply to photo or video**</blockquote>")

        media = reply.photo or reply.video
        kwargs = {"photo": media.file_id} if reply.photo else {"video": media.file_id}
        await client.set_chat_photo(message.chat.id, **kwargs)
        return await message.reply(
            f"<blockquote>{em.sukses}<b>Successfully changed [media]({reply.link}) to profile group!</b></blockquote>",
            disable_web_page_preview=True,
        )


async def handle_title_command(client, message, em, prefix):
    reply = message.reply_to_message
    user_id = None
    title = None
    if reply:
        user_id = reply.from_user.id
        if len(message.command) > 1:
            title = message.text.split(None, 1)[1]
    elif len(message.command) > 2:
        user_id = message.text.split()[1]
        title = message.text.split(None, 2)[2]

    if not all([user_id, title]):
        return await message.reply(f"<blockquote>{em.gagal}**Please give me title to set. Example: `{prefix}title [user_id] [title]` or reply to user with title!**</blockquote>")

    try:
        user = await client.get_users(user_id)
        current_title = (await client.get_chat_member(message.chat.id, user.id)).custom_title
        mention = user.mention
        await client.set_administrator_title(message.chat.id, user.id, title)
        return await message.reply(f"<blockquote>{em.sukses}<b>Successfully set title user: {mention} `{current_title}` to: `{title}`</b></blockquote>")
    except Exception as e:
        return await message.reply(f"<blockquote>{em.gagal}**ERROR: `{str(e)}`**</blockquote>")
