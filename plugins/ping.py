import random
from datetime import datetime
from time import time

from pyrogram.raw.functions import Ping

from kelra import dB
from kelra.helpers import CMD, Emoji, get_time, start_time
from kelra.helpers.emoji_logs import get_auto_effect

__MODULES__ = "Settings"
__HELP__ = """<blockquote>Command Help **Settings**</blockquote>

<blockquote expandable>    <u>**Set text ping message**</u>
        `{0}set_text ping` (text/reply text)

    <u>**Set text uptime message**</u>
        `{0}set_text uptime` (text/reply text)

    <u>**Set text owner message**</u>
        `{0}set_text owner` (text/reply text)

    <u>**Set text ubot message**</u>
        `{0}set_text ubot` (text/reply text)

    <u>**Set text sukses message**</u>
        `{0}set_text sukses` (text/reply text)

    <u>**Set text proses message**</u>
        `{0}set_text proses` (text/reply text)

    <u>**Set text help message**</u>
        `{0}set_text help` (text/reply text)

<u>**Note:** Use `{0}ping` to check the changes and `{0}help`</u></blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

async def set_pong_message(user_id, new_message):
    await dB.set_var(user_id, "text_ping", new_message)
    return


async def set_utime_message(user_id, new_message):
    await dB.set_var(user_id, "text_uptime", new_message)
    return


async def set_owner_message(user_id, new_message):
    await dB.set_var(user_id, "text_owner", new_message)
    return


async def set_ubot_message(user_id, new_message):
    await dB.set_var(user_id, "text_ubot", new_message)
    return


async def set_gcast_message(user_id, new_message):
    await dB.set_var(user_id, "text_gcast", new_message)
    return


async def set_sukses_message(user_id, new_message):
    await dB.set_var(user_id, "text_sukses", new_message)
    return


async def set_help_message(user_id, new_message):
    await dB.set_var(user_id, "text_help", new_message)
    return


costumtext_query = {
    "ping": set_pong_message,
    "uptime": set_utime_message,
    "owner": set_owner_message,
    "ubot": set_ubot_message,
    "proses": set_gcast_message,
    "sukses": set_sukses_message,
    "help": set_help_message,
}


# ─── Command: ping ──────────────────────────────
@CMD.UBOT("ping|p")
@CMD.DEV_CMD("cping|kp")
@CMD.FAKEDEV("cping|kp")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()

    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    end = datetime.now()

    upnya = await get_time((time() - start_time))
    duration = round((end - start).microseconds / 100000, 2)

    _ping = (
        f"<blockquote>"
        f"<b>{em.ping} {pong_}:</b> <u>{duration}ms</u>\n"
        f"<b>{em.uptime} {uptime_}:</b> <u>{upnya}</u>\n"
        f"<b>{em.owner} {owner_}</b>"
        f"</blockquote>"
    )
    # 🔹 Pilih efek otomatis berdasarkan premium/bukan
    effect_id = get_auto_effect(client)
    try:
        return await message.reply(
            _ping,
            effect_id=effect_id,
            disable_web_page_preview=True,
        )
    except Exception:
        return await message.reply(
            _ping,
            disable_web_page_preview=True,
        )


@CMD.UBOT("set_text")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await em.get_costum_text()
    pros = await message.reply(f"<blockquote>{em.proses}**{proses_}**</blockquote>")

    args = message.text.split(maxsplit=2)
    variable = args[1]
    # if len(args) >= 3:
    new_message = client.new_arg(message)
    if variable in costumtext_query:
        await costumtext_query[variable](client.me.id, new_message)
        return await pros.edit(f"{em.sukses}**Successfully updated custom text: <u>{variable}</u>**")
    else:
        return await pros.edit(f"<blockquote>{em.gagal}**Please given text for this query: {variable}!**</blockquote>")
    # else:
    # return await pros.edit(
    #    f"<blockquote>{em.gagal}**No query: <code>{variable}</code>. Please provide the correct query!**</blockquote>"
    # )


@CMD.FAKEDEV("absen")
@CMD.DEV_CMD("absen")
async def _(client, message):
    txt = await dB.get_var(client.me.id, "TEXT_ABSEN")
    if len(message.command) == 1:
        if not txt:
            return
        try:
            psn = random.choice(txt)
            return await message.reply(psn)
        except:
            pass
    else:
        command, variable = message.command[:2]
        if variable.lower() == "text":
            for x in client._ubot:
                value = " ".join(message.command[2:])
                await add_absen(x, value)

        else:
            return
