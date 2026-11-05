import asyncio
import sys
from datetime import datetime

from pyrogram import enums, raw
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    PeerIdInvalid,
    UsernameInvalid,
)

from kelra import bot
from kelra.database import dB, state
from kelra.helpers import CMD, ButtonUtils, Emoji
from kelra.logger import logger

__MODULES__ = "Info"
__HELP__ = """<blockquote>Command Help **Info**</blockquote>

<blockquote expandable>    <u>**Get information user**</u>
        `{0}info` (username/reply user)
        
    <u>**Get information chat**</u>
        `{0}cinfo` (chatid)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

interact_with_to_delete = []


async def interact_with(message):
    """
    Check history with bot and return bot's response

    Example:
    .. code-block:: python
        bot_msg = await interact_with(await bot.send_message("@BotFather", "/start"))
    :param message: already sent message to bot
    :return: bot's response
    """

    await asyncio.sleep(1)
    response = [msg async for msg in message._client.get_chat_history(message.chat.id, limit=1)]
    seconds_waiting = 0

    while response[0].from_user.is_self:
        seconds_waiting += 1
        if seconds_waiting >= 5:
            raise RuntimeError("bot didn't answer in 5 seconds")

        await asyncio.sleep(1)
        response = [msg async for msg in message._client.get_chat_history(message.chat.id, limit=1)]

    interact_with_to_delete.append(message.id)
    interact_with_to_delete.append(response[0].id)

    return response[0]


async def get_info_chat(client, chat):
    try:
        administrator = []
        async for admin in client.get_chat_members(chat_id=chat, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            administrator.append(admin)
        total_admin = administrator
        bot = []
        async for tbot in client.get_chat_members(chat_id=chat, filter=enums.ChatMembersFilter.BOTS):
            bot.append(tbot)

        total_bot = bot
        bot_admin = 0
        ban = []
        async for banned in client.get_chat_members(chat, filter=enums.ChatMembersFilter.BANNED):
            ban.append(banned)

        total_banned = ban
        for x in total_admin:
            for y in total_bot:
                if x == y:
                    bot_admin += 1
        total_admin = len(total_admin)
        total_bot = len(total_bot)
        total_banned = len(total_banned)
        return total_bot, total_admin, bot_admin, total_banned
    except Exception:
        return total_bot, total_admin, bot_admin, total_banned


@CMD.UBOT("info|cinfo")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    await client.unblock_user("creationdatebot")
    crbot = await client.resolve_peer("creationdatebot")

    if message.command[0] == "cinfo":
        try:
            if message.reply_to_message and message.reply_to_message.sender_chat:
                chat = message.reply_to_message.sender_chat.id
            elif len(message.command) > 1:
                chat = message.text.split()[1]
            else:
                return await message.reply_text(f"{em.gagal}**Please provide a chat username or reply to a channel/group message**")

            if isinstance(chat, str) and chat.startswith("https://t.me"):
                chat = "@" + chat.split("/")[-1]

            try:
                gc = await client.get_chat(chat)
                type = "channel" if gc.type == enums.ChatType.CHANNEL else "group"
            except (UsernameInvalid, KeyError, ChannelInvalid, PeerIdInvalid):
                return await message.reply_text(f"{em.gagal}**You need meet before interact**")

            dict_gcinfo = {
                "name": gc.title,
                "id": gc.id,
                "type": type,
                "username": gc.username,
                "member": gc.members_count,
                "protect": gc.has_protected_content,
                "is_creator": gc.is_creator,
                "is_admin": gc.is_admin,
                "is_restricted": gc.is_restricted,
                "dc_id": gc.dc_id,
                "desc": gc.description,
            }
            state.set(client.me.id, "gc_info", dict_gcinfo)

            try:
                inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, "gc_info")
                if inline:
                    return await message.delete()
            except Exception as er:
                return await message.reply_text(f"{em.gagal}**ERROR:** {str(er)}")

        except Exception as er:
            logger.error(f"Error in info command at line {sys.exc_info()[-1].tb_lineno}: {str(er)}")
            return await message.reply_text(f"{em.gagal}**An error occurred**")

    elif message.command[0] == "info":
        try:
            if message.reply_to_message and message.reply_to_message.sender_chat:
                return await message.reply_text(f"{em.gagal}**Please reply to a user or provide a username**")

            if message.reply_to_message and message.reply_to_message.from_user:
                sus = message.reply_to_message.from_user.id
            elif len(message.command) > 1:
                sus = message.text.split()[1]
            else:
                return await message.reply_text(f"{em.gagal}**Please provide a username or reply to a user's message**")

            try:
                user = await client.get_users(sus)
            except (UsernameInvalid, KeyError, ChannelInvalid, PeerIdInvalid):
                return await message.reply_text(f"{em.gagal}**You need meet before interact**")

            full = f"<a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a>"

            try:
                response = await interact_with(await client.send_message("creationdatebot", f"/id {user.id}"))
                creation_date = response.text
            except:
                creation_date = "None"

            interact_with_to_delete.clear()

            gbanned = user.id in await dB.get_list_from_var(client.me.id, "GBANNED")

            dict_userinfo = {
                "name": full,
                "id": user.id,
                "create": creation_date,
                "contact": user.is_contact,
                "premium": user.is_premium,
                "deleted": user.is_deleted,
                "isbot": user.is_bot,
                "dc_id": user.dc_id,
                "gbanned": gbanned,
            }
            state.set(client.me.id, "user_info", dict_userinfo)

            try:
                await client.invoke(raw.functions.messages.DeleteHistory(peer=crbot, max_id=0, revoke=True))
                inline = await ButtonUtils.send_inline_bot_result(message, message.chat.id, bot.me.username, "user_info")
                if inline:
                    return await message.delete()
            except Exception as er:
                return await message.reply_text(f"{em.gagal}**ERROR:** {str(er)}")

        except Exception as er:
            logger.error(f"Error in info command at line {sys.exc_info()[-1].tb_lineno}: {str(er)}")
            return await message.reply_text(f"{em.gagal}**An error occurred**")


@CMD.UBOT("mestats")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply_text(f"{em.proses}**{proses_}**")
    start = datetime.now()
    zz = 0
    nanki = 0
    luci = 0
    tgr = 0
    ceger = 0
    kntl = 0
    benet = 0
    dimari = set()
    try:
        async for dialog in client.get_dialogs():
            try:
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    zz += 1
                elif dialog.chat.type == enums.ChatType.BOT:
                    ceger += 1
                elif dialog.chat.type == enums.ChatType.GROUP:
                    nanki += 1
                elif dialog.chat.type == enums.ChatType.SUPERGROUP:
                    luci += 1
                    user_s = await dialog.chat.get_member(client.me.id)
                    if user_s.status in (
                        enums.ChatMemberStatus.OWNER,
                        enums.ChatMemberStatus.ADMINISTRATOR,
                    ):
                        kntl += 1
                elif dialog.chat.type == enums.ChatType.CHANNEL:
                    tgr += 1
            except ChannelPrivate:
                benet += 1
                dimari.add(dialog.chat.id)
                await client.leave_chat(dialog.chat.id)
                logger.info(f"Left chat: {dialog.chat.id}")
                continue
    except ChannelPrivate:
        benet += 1
        dimari.add(dialog.chat.id)

    end = datetime.now()
    ms = (end - start).seconds
    if not dimari:
        dimari = None
    await proses.delete()
    return await message.reply_text(
        """
<blockquote expandable>{} **Succesfully extract your data in `{}` seconds
>`{}` Private Messages.
>`{}` Groups.
>`{}` Super Groups.
>`{}` Channels.
>`{}` Admin in Chats.
>`{}` Bots.
>`{}` Group With Trouble
>
>I've trouble with this chat : 
>- `{}`**</blockquote>""".format(
            em.sukses,
            ms,
            zz,
            nanki,
            luci,
            tgr,
            kntl,
            ceger,
            benet,
            dimari,
        )
    )
