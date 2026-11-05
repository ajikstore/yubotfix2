import re
import asyncio
from pyrogram import enums
from pyrogram.errors import (
    RPCError,
    UserAlreadyParticipant,
    UsernameInvalid,
    UsernameNotOccupied, 
    InviteHashInvalid,
    ChannelInvalid,
    ChannelPrivate,
    ChannelIdInvalid,
    FloodWait,
    FloodPremiumWait
)
from pyrogram.raw.functions.messages import ImportChatInvite

from config import BLACKLIST_GCAST
from kelra.database import dB
from kelra.helpers import CMD, Emoji

__MODULES__ = "Extras"
__HELP__ = """<blockquote>Command Help **Extras**</blockquote>

<blockquote expandable>    <u>**Leave all channel**</u>
        `{0}leave channel`

    <u>**Leave all channel and group**</u>
        `{0}leave global`

    <u>**Leave all mute**</u>
        `{0}leave mute`

    <u>**Leave all group**</u> 
        `{0}leave group`

    <u>**Join chat**</u>
        `{0}join` (chatid)

    <u>**Leave chat** </u>
        `{0}kickme`

    <u>**Blacklist leave**</u> 
    **Add chat to blacklist leave if you want**
        `{0}bl-leave` (chatid)

    <u>**Remove blacklist leave**</u>
        `{0}unbl-leave` (chatid)

    <u>**Get blacklist leave** </u>
        `{0}getbl-leave`

    <u>**Clear all blacklist leave**</u> 
    `{0}cleardb-leave`

    <u>**Get mute group**</u> 
        `{0}getmute`

<u>**Note**: For the blacklist leave, when you use the leave command then you will not leave from db leave blacklist.</u></blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

async def try_join_chat(client, link: str):
    """
    Join grup/channel via link (username atau invite link)
    Return:
        status (bool), info (str), chat (Chat object | None)
    """
    try:
        # Bersihkan link
        if "t.me/" in link:
            clean = link.split("t.me/")[1].strip()
            link = clean

        # Cek apakah link invite (private)
        if link.startswith("+") or link.startswith("joinchat/"):
            # Private group via invite hash
            chat = await client.invoke(
                ImportChatInvite(hash=link.replace("+", ""))
            )
        else:
            # Public group via username
            chat = await client.join_chat(link)

        return True, "Joined successfully", chat

    except UserAlreadyParticipant:
        return True, "Already a member", None

    except (UsernameInvalid, UsernameNotOccupied):
        return False, "Invalid username or not occupied", None

    except InviteHashInvalid:
        return False, "Invite link invalid or expired", None

    except (ChannelIdInvalid, ChannelInvalid, ChannelPrivate) as e:
        return False, f"Cannot join: {e}", None

    except FloodWait as e:
        return False, f"Flood wait: wait {e.value} seconds", None

    except RPCError as e:
        return False, f"RPC Error: {e}", None

    except Exception as e:
        return False, f"Unknown error: {e}", None
        
@CMD.UBOT("getmute")
@CMD.FAKEDEV("getmute")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    output = ""
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")

    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(dialog.chat.id, client.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    chat = await client.get_chat(dialog.chat.id)
                    output += f"{chat.title} | [`{chat.id}`]\n"
            except Exception:
                continue

    if output:
        text = f"<blockquote><b>The list of groups that mute you are:</b>\n{output}</blockquote>"
    else:
        text = "<blockquote>List of groups that mute you are empty</blockquote>"

    return await msg.edit(text)
    

@CMD.UBOT("join") 
@CMD.FAKEDEV("join")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**sabar hama proses**")
    replied = message.reply_to_message
    if replied:
        links = client.extract_links(replied.text or replied.caption or "")
        if not links:
            return await proses.edit(f"{em.gagal}**No links found!**")

        total = len(links)
        success = 0
        failed = 0
        results = []

        await proses.edit(f"{em.proses}**Processing {total} link...**")

        progress_msg = await message.reply(
            f"{em.proses}**Progress Join Grup**\n"
            f"{em.sukses}Succeed: 0/{total}\n"
            f"{em.gagal}Failed: 0/{total}\n"
            f"{em.msg}Progress: 0%"
        )

        for idx, link in enumerate(links, 1):

            status, info, ok = await try_join_chat(client, link)

            if ok:
                success += 1
            else:
                failed += 1

            results.append(f"{status} {link.strip()} - {info}")

            if idx % 3 == 0 or idx == total:
                percent = (idx / total) * 100
                await progress_msg.edit(
                    f"{em.proses}**Progress Join Grup**\n"
                    f"{em.sukses}Succeed: {success}/{total}\n"
                    f"{em.gagal}Failed: {failed}/{total}\n"
                    f"{em.msg}Progress: {percent:.1f}% ({idx}/{total})"
                )

        report = [
            f"{em.msg}**GROUP JOIN REPORT**",
            f"{em.klip}Total Link: {total}",
            f"{em.sukses}Succeed: {success}",
            f"{em.gagal}Failed: {failed}",
            f"{em.profil}Success Rate: {(success/total)*100:.1f}%",
            "",
            "**Detail:**",
            *results,
        ]

        report_text = "\n".join(report)

        if len(report_text) > 4096:
            chunk = []
            size = 0
            for line in report:
                if size + len(line) + 1 > 4096:
                    await message.reply("\n".join(chunk))
                    chunk = [line]
                    size = len(line)
                else:
                    chunk.append(line)
                    size += len(line) + 1
            if chunk:
                await message.reply("\n".join(chunk))
        else:
            await progress_msg.edit(report_text)

        return await proses.edit(f"{em.sukses}**All groups processed!**")

    else:
        if len(message.command) < 2:
            return await proses.edit(
                f"{em.gagal}**Please give me a link or username to join!**"
            )

        link = message.command[1]
        status, info, ok = await try_join_chat(client, link)

        if ok:
            return await proses.edit(
                f"{status}**{info}: {link}**", disable_web_page_preview=True
            )
        else:
            return await proses.edit(f"{status}**Error:** {info}")


@CMD.UBOT("kickme")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    status = None
    if chat_id in BLACKLIST_GCAST:
        return await proses.edit(f"<blockquote>{em.gagal}**Sorry, you cant leave this group!**</blockquote>")
    try:
        chat_id = int(chat_id)
    except ValueError:
        chat_id = str(chat_id)
    try:
        chat_member = await client.get_chat_member(chat_id, "me")
        if chat_member.status == enums.ChatMemberStatus.ADMINISTRATOR:
            status = "admin"
        elif chat_member.status == enums.ChatMemberStatus.OWNER:
            status = "owner"
        elif chat_member.status == enums.ChatMemberStatus.MEMBER:
            status = "member"
    except Exception as er:
        return await proses.edit(f"<blockquote>{em.gagal}**Error:** {str(er)}</blockquote>")
    if status in ["admin", "owner"]:
        return await proses.edit(f"<blockquote>{em.gagal}**Sorry you cant leave this chat because you as: {status} in this chat.!**</blockquote>")
    else:
        return await client.leave_chat(chat_id)
        return await proses.edit(f"<blockquote>{em.sukses}**Succesfully leave chat: {chat_id}**!</blockquote>")


@CMD.UBOT("leave")
@CMD.FAKEDEV("leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    no_leave = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    no_leave.append(-1001818398503)
    no_leave.append(-1001537280879)
    if len(message.command) < 2 and message.command not in [
        "group",
        "channel",
        "global",
        "mute",
    ]:
        return await proses.edit(f"<blockquote>{em.gagal}**Please specify command!**\n**Example: `{message.text.split()[0]}` [group, channel, mute or global].**</blockquote>")
    command = message.text.split()[1]
    if command == "mute":
        sukses = await leave_mute(client)
        await proses.delete()
        return await message.reply(f"<blockquote>{em.sukses}**Succesfully leaved muted group, succesed: {sukses}**</blockquote>")
    sukses = 0
    arg = 0
    chats = await client.get_chat_id(command)
    for chat in chats:
        if chat in no_leave:
            continue
        try:
            chat_info = await client.get_chat_member(chat, "me")
            user_status = chat_info.status
            if user_status not in (
                enums.ChatMemberStatus.OWNER,
                enums.ChatMemberStatus.ADMINISTRATOR,
            ):
                sukses += 1
                await client.leave_chat(chat)
        except FloodWait as e:
            await asyncio.sleep(e)
            await client.leave_chat(chat)
            sukses += 1
        except Exception:
            arg += 1
    await proses.delete()
    return await message.reply(f"<blockquote>{em.sukses}**Succesfully leave {command}, succesed: {sukses} failed: {arg}.**</blockquote>")


@CMD.UBOT("bl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    chat_id = message.command[1] if len(message.command) > 1 else message.chat.id
    blacklist = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await proses.edit("<blockquote>{}<b>KONTOL KONTOL KALO PAKE NONE PREFIX JANGAN ASAL KETIK GOBLOK\n\n BOT GW YANG EROR ANJ!!!</b></blockquote>".format(em.gagal))
    if chat_id in blacklist:
        return await proses.edit(f"<blockquote>{em.sukses}**{chat_id} Already in database blacklist leave!**</blockquote>")
    await dB.add_to_var(client.me.id, "NO_LEAVE", chat_id)
    return await proses.edit(f"<blockquote>{em.sukses}**Added {chat_id} to database blacklist leave.**</blockquote>")


@CMD.UBOT("unbl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    blacklist = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    try:
        chat_id = int(message.command[1]) if len(message.command) > 1 else message.chat.id
        if chat_id not in blacklist:
            return await proses.edit(f"<blockquote>{em.gagal}**{chat_id} Not in database blacklist leave!**</blockquote>")
        await dB.remove_from_var(client.me.id, "NO_LEAVE", chat_id)
        return await proses.edit(f"<blockquote>{em.sukses}**Removed {chat_id} from database blacklist leave.**</blockquote>")
    except Exception as error:
        return await proses.edit(str(error))


@CMD.UBOT("getbl-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    msg = f"<blockquote>{em.sukses} List blacklist leave:\n\n</blockquote>"
    listbc = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    for num, x in enumerate(listbc, 1):
        try:
            get = await client.get_chat(x)
            msg += f"{num}. {get.title} - {get.id}\n"
        except Exception:
            msg += f"{num}. {x}\n"
    await proses.delete()
    return await message.reply(msg)


@CMD.UBOT("cleardb-leave")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    get_bls = await dB.get_list_from_var(client.me.id, "NO_LEAVE")
    if not get_bls:
        return await proses.edit(f"<blockquote>{em.gagal}**You dont have blacklist leave!**</blockquote>")
    for x in get_bls:
        await dB.remove_from_var(client.me.id, "NO_LEAVE", x)
    return await proses.edit(f"<blockquote>{em.sukses}**Succesfully removed all group in blacklist leave!**</blockquote>")


async def leave_mute(client):
    sukses = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(dialog.chat.id, client.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    sukses += 1
                    await client.leave_chat(dialog.chat.id)
            except FloodWait as e:
                await asyncio.sleep(e)
                await client.leave_chat(dialog.chat.id)
                sukses += 1
            except Exception:
                continue
    return sukses
