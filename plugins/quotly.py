import base64
import io
import json
import os
import random
import traceback
from io import BytesIO

from config import SUDO_OWNERS
from kelra.helpers import CMD, Emoji, Tools, Quotly

__MODULES__ = "Quote"
__HELP__ = """<blockquote>Command Help **Quote**</blockquote>

<blockquote expandable>        <u>**Make quote text with color**</u>
    <u>**You can make quote the message with random color or custom color just give name color after command**</u>
        `{0}q pink` (reply message)

        <u>**Make fake quote text** </u>
    <u>**You can make fake quote user the message with this message**</u>
        `{0}q @kelraubot` (reply message)

        <u>**View quote color** </u>
    <u>**Get supported color for quote**</u>
        `{0}qcolor`</blockquote>

<b>   {1}</b>
"""

# =======================================================
# FIX: Tambahkan fungsi get_emoji dan parse_reply_info
# =======================================================

# Emoji list default
emoji_list = "😀😃😄😁😆😅😂🤣😊🙂🙃😉😍😘😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😢😭😤😡🤬🤯"

async def get_emoji(message):
    """Mengambil emoji dari sticker / text."""
    try:
        if not message:
            return None

        # Jika sticker punya emoji
        if message.sticker and message.sticker.emoji:
            return message.sticker.emoji

        # Jika text mengandung emoji
        text = message.text or message.caption or ""
        for char in text:
            if char in emoji_list:
                return char

        return None
    except:
        return None

Quotly.get_emoji = get_emoji  # Patch fix inject fungsi


async def parse_reply_info(msg):
    """Fallback reply parser."""
    if not msg:
        return {}

    user = msg.from_user
    name = "Unknown"
    if user:
        name = user.first_name or "Unknown"
        if user.last_name:
            name += " " + user.last_name

    return {
        "name": name,
        "text": await Quotly.t_or_c(msg),
    }

Quotly.parse_reply_info = parse_reply_info  # Patch fix inject fungsi


# ========================================
# FIX: Tambahkan fungsi forward_info lokal
# ========================================
async def forward_info(msg):
    """Gantikan Quotly.forward_info yang hilang."""
    user = msg.from_user

    if not user:
        return 0, "Unknown", "Unknown"

    title = user.first_name or "Unknown"
    if user.last_name:
        title += f" {user.last_name}"

    name = title
    return user.id, title, name


# ==========================
# Command: qcolor
# ==========================
@CMD.UBOT("qcolor")
async def _(client, message):
    em = Emoji(client)
    await em.get()

    iymek = f"\n•".join(Quotly.colors)
    jadi = f"{em.sukses}Color for quotly\n•"

    if len(iymek) > 4096:
        with open("qcolor.txt", "w") as file:
            file.write(iymek)
        await message.reply_document("qcolor.txt", caption=f"{em.sukses}Color for quotly")
        os.remove("qcolor.txt")
    else:
        await message.reply(jadi + iymek)


# ==========================
# Command: q / qr
# ==========================
@CMD.UBOT("q|qr")
async def qoutly_cmd(client, message):
    em = Emoji(client)
    await em.get()
    acak = None
    messages = None
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()

    if not message.reply_to_message:
        return await message.reply(f"{em.gagal}**Please reply to a message!**")

    pros = await message.reply(f"<blockquote>{em.proses}</blockquote>")

    reply_msg = message.reply_to_message
    cmd = message.command[1:]
    print(f"Cmd: {cmd}")

    def get_color(index=0):
        return cmd[index] if len(cmd) > index else random.choice(Quotly.colors)

    try:
        # ========================
        # Default random color
        # ========================
        if not cmd:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(),
                "messages": [],
            }

            sid, title, name = await forward_info(reply_msg)
            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            }
            payload["messages"].append(messages_json)

        # ========================
        # Fake User: q @username
        # ========================
        elif cmd[0].startswith("@"):
            color = get_color(1)
            include_reply = len(cmd) > 2 and cmd[2] == "-r"

            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": color,
                "messages": [],
            }

            username = cmd[0][1:]
            user = await client.get_users(username)

            if user.id in SUDO_OWNERS:
                return await pros.edit(f"{em.gagal}**You can't quote this user**")

            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"

            emoji_status = (
                getattr(getattr(user, "emoji_status", None), "custom_emoji_id", None)
            )

            reply_message = (
                await Quotly.parse_reply_info(reply_msg.reply_to_message)
                if include_reply else {}
            )

            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": user.id,
                    "title": name,
                    "name": name,
                    "emoji_status": emoji_status,
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }

            payload["messages"].append(messages_json)

        # ========================
        # q -r → include reply
        # ========================
        elif cmd[0].startswith("-r"):
            replied = reply_msg.reply_to_message
            reply_message = await Quotly.parse_reply_info(replied)

            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "messages": [],
            }

            sid, title, name = await forward_info(reply_msg)

            messages_json = {
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": reply_message,
            }

            payload["messages"].append(messages_json)

        # ========================
        # q 5 → multi message
        # ========================
        elif cmd[0].isdigit():
            count = int(cmd[0])
            if count > 10:
                return await pros.edit(f"{em.gagal}**Max 10 messages**")

            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": get_color(1),
                "scale": 2,
                "messages": [],
            }

            sid, title, name = await forward_info(reply_msg)
            payload["messages"].append({
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
                "replyMessage": {},
            })

            async for msg in client.get_chat_history(reply_msg.chat.id, limit=count, offset_id=reply_msg.id):
                sid, title, name = await forward_info(msg)
                payload["messages"].append({
                    "entities": Tools.get_msg_entities(msg),
                    "avatar": True,
                    "from": {
                        "id": sid,
                        "title": title,
                        "name": name,
                        "emoji_status": await Quotly.get_emoji(msg),
                    },
                    "text": await Quotly.t_or_c(msg),
                    "replyMessage": {},
                })

            payload["messages"].reverse()

        # ========================
        # q red / q pink / q green
        # ========================
        else:
            payload = {
                "type": "quote",
                "format": "png",
                "backgroundColor": cmd[0],
                "messages": [],
            }

            sid, title, name = await forward_info(reply_msg)
            payload["messages"].append({
                "entities": Tools.get_msg_entities(reply_msg),
                "avatar": True,
                "from": {
                    "id": sid,
                    "title": title,
                    "name": name,
                    "emoji_status": await Quotly.get_emoji(reply_msg),
                },
                "text": await Quotly.t_or_c(reply_msg),
            })

        # PRODUKSI QUOTLY
        hasil = await Quotly.quotly(payload)

        bio_sticker = BytesIO(hasil)
        bio_sticker.name = "biosticker.webp"

        await message.reply_sticker(bio_sticker)
        await pros.delete()

    except Exception as e:
        print(traceback.format_exc())
        return await pros.edit(f"{em.gagal}{e}")
