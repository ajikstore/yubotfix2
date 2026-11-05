import asyncio
import random

from kelra import kelra
from kelra.helpers import CMD, Emoji, task

__MODULES__ = "Reaction"
__HELP__ = """<blockquote>Command Help **Reaction** </blockquote>

<blockquote expandable>        <u>**Reaction 1**</u>
    <u>**Give reactions to chat with costum emoji or random**</u>
        `{0}react` (chatid) (emoji/random)

        <u>**Reaction 2**</u>
    <u>**Give many reactions to 1 message with active userbot**</u>
        `{0}react2` (reply message) (emoji/random)

        <u>**Stop Reaction**</u>
    <u>**Stop task reaction with taskid**</u>
        `{0}cancel` (taskid)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

RANDOM_EMOJIS = [
    "😀",
    "😂",
    "😍",
    "😎",
    "😢",
    "😡",
    "👍",
    "👎",
    "🙏",
    "👏",
    "❤️",
    "🗿",
    "😭",
    "🔥",
]


@CMD.UBOT("react")
@CMD.FAKEDEV("Creact")
@CMD.DEV_CMD("Creact")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    sukses = 0
    failed = 0

    if len(message.command) not in [2, 3]:
        return await proses.edit(f"<blockquote>{em.gagal}**Please use format `{message.text.split()[0]}` [@username/chat_id] [emoji/random]**</blockquote>")

    task_id = task.start_task()
    try:
        if len(message.command) == 3:
            chat_id = message.text.split()[1]
            emoji = message.text.split()[2]
        else:
            chat_id = message.chat.id
            emoji = message.text.split()[1]

        if emoji.lower() == "random":
            emoji = random.choice(RANDOM_EMOJIS)

        prefix = client.get_prefix(client.me.id)

        await proses.edit(f"<blockquote>{em.proses}<i>Task reaction running #<code>{task_id}</code>. Type <code>{prefix[0]}cancel {task_id}</code> to stop reaction!</i></blockquote>")
        async for m in client.get_chat_history(chat_id):
            if not task.is_active(task_id):
                return await proses.edit(f"<blockquote>{em.gagal}**Task #{task_id} has been cancelled!**</blockquote>")
            await asyncio.sleep(0.5)
            message_id = m.id
            try:
                for c in mmk._ubot:
                    await asyncio.sleep(0.5)
                    await c.send_reaction(chat_id=chat_id, message_id=message_id, emoji=emoji)
                    sukses += 1
            except Exception:
                failed += 1
    except Exception as er:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
    finally:
        task.end_task(task_id)
    return await proses.edit(f"<blockquote><b>{em.sukses}Succesfully send reaction to chat: {chat_id}, emoji: {emoji}.\n\nSucces: {sukses}, Failed: {failed}.</b></blockquote>")


@CMD.UBOT("react2")
@CMD.FAKEDEV("Creact2")
@CMD.DEV_CMD("Creact2")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    reply = message.reply_to_message or message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    sukses = 0
    failed = 0

    if len(message.command) < 2:
        return await proses.edit(f"<blockquote>{em.gagal}**Please use format `{message.text.split()[0]}` [emoji/random]**</blockquote>")

    task_id = task.start_task()
    try:
        chat_id = message.chat.id
        emoji = message.text.split()[1]

        if emoji.lower() == "random":
            emoji = random.choice(RANDOM_EMOJIS)

        prefix = client.get_prefix(client.me.id)

        await proses.edit(f"<blockquote>{em.proses}<i>Task reaction running #<code>{task_id}</code>. Type <code>{prefix[0]}cancel {task_id}</code> to stop reaction!</i></blockquote>")
        try:
            for c in mmk._ubot:
                message_id = reply.id
                await asyncio.sleep(0.5)
                await c.send_reaction(chat_id=chat_id, message_id=message_id, emoji=emoji)
                sukses += 1
        except Exception:
            failed += 1
    except Exception as er:
        return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
    finally:
        task.end_task(task_id)
    return await proses.edit(f"<blockquote><b>{em.sukses}Succesfully send reaction to chat: {chat_id}\nEmoji: {emoji}\nSucces: {sukses}, Failed: {failed}.</b></blockquote>")
