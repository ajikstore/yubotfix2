import asyncio

from pyrogram.errors import FloodWait, SlowmodeWait

from config import BLACKLIST_GCAST
from kelra.database import dB
from kelra.helpers import CMD, Emoji, task

__MODULES__ = "Spam"
__HELP__ = """<blockquote>Command Help **Spam**</blockquote>

<blockquote expandable>        <u>**Spam message with delay**</u>
    <u>**Send spam with delay**</u>
        `{0}dspam` (reply message) (amount) (delay)
        
        <u>**Spam message without delay**</u>
    <u>**Send spam without delay**</u>
        `{0}spam` (reply message) (amount)

        <u>**Spam broadcast** </u>
    <u>**Send spam broadcast with count**</u>
        `{0}spamg` (count) (text/reply message)

        <u>**Stop spam**</u>
    <u>**Cancel task spam**</u>
        `{0}cancel` (taskid)</blockquote>

<b>   {1}</b>
"""


@CMD.UBOT("spam|dspam")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    command = message.command[0]
    reply = message.reply_to_message
    proses = await message.reply(f"<blockquote>{emo.proses}<b>{'Delay ' if command == 'dspam' else ''}Spam process is running ..</b></blockquote>")
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    try:
        if len(message.command) < 2:
            return await proses.edit(f"<blockquote>{emo.gagal}<b>Usage `{prefix[0]}{command}`[amount] {'[delay] ' if command == 'dspam' else ''}[text/reply text].</b></blockquote>")
        jumlah = int(message.command[1])
        count_delay = int(message.command[2]) if command == "dspam" and len(message.command) > 2 else 0
    except Exception as error:
        return await proses.edit(f"<blockquote>{emo.gagal}<b>Error:</b>\n<code>{str(error)}</code></blockquote>")
    await proses.edit(
        f"<blockquote>{emo.proses}<i>{'Delay ' if command == 'dspam' else ''}Spam task running #<code>{task_id}</code>. </blockquote>"
        f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel {'delay ' if command == 'dspam' else ''}spam!</i>"
    )
    if reply:
        text = reply.text
    else:
        if len(message.command) < (3 if command == "dspam" else 2):
            return await proses.edit(f"<blockquote>{emo.gagal}<b>Usage `{prefix[0]}{command}`[amount] {'[delay] ' if command == 'dspam' else ''}[text/reply text].</b></blockquote>")
        text = message.text.split(None, 3 if command == "dspam" else 2)[-1]
    for i in range(jumlah):
        if not task.is_active(task_id):
            return await proses.edit(f"<blockquote>{emo.gagal}{'Delay ' if command == 'dspam' else ''}Spam cancelled.</blockquote>")
        else:
            try:
                await (reply.copy(message.chat.id) if reply else message.reply(text))
                await asyncio.sleep(count_delay if command == "dspam" else 0.1)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await (reply.copy(message.chat.id) if reply else message.reply(text))
            except SlowmodeWait as e:
                await asyncio.sleep(e.value)
                await (reply.copy(message.chat.id) if reply else message.reply(text))

            except Exception as error:
                return await proses.edit(str(error))
    task.end_task(task_id)
    await proses.delete()
    return await message.delete()


@CMD.UBOT("spamg")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    proses = await message.reply(f"<blockquote>{emo.proses}<b>Spam broadcast process ..</b></blockquote>")
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await proses.edit(f"<blockquote>{emo.gagal}<b>Please use command: `{message.text.split()[0]} 5` (text or reply text)</b></blockquote>")

    jumlah = int(message.command[1])
    send = client.get_message(message)
    if not send:
        return await proses.edit(f"<blockquote>{emo.gagal}<b>Provide me with text or reply to a message ..</b></blockquote>")
    task_id = task.start_task()
    prefix = client.get_prefix(client.me.id)
    await proses.edit(f"<blockquote>{emo.proses}<i>Spam broadcast task running #<code>{task_id}</code>. " f"Type <code>{prefix[0]}cancel {task_id}</code> to cancel Spam broadcast!</i></blockquote>")
    chats = await client.get_chat_id("group")
    blacklist = await dB.get_list_from_var(client.me.id, "BLACKLIST_GCAST")
    done = 0
    failed = 0
    for chat_id in chats:
        if chat_id in blacklist or chat_id in BLACKLIST_GCAST:
            continue
        if not task.is_active(task_id):
            return await proses.edit(f"<blockquote>{emo.gagal}Spam broadcast cancelled.</blockquote>")
        else:
            try:
                for i in range(jumlah):
                    (await send.copy(chat_id) if message.reply_to_message else await client.send_message(chat_id, send))
                done += 1
            except FloodWait as e:
                wait = int(e.value)
                if wait > 200:
                    failed += 1
                    continue
                await asyncio.sleep(wait)
                try:
                    for i in range(jumlah):
                        (await send.copy(chat_id) if message.reply_to_message else await client.send_message(chat_id, send))
                    done += 1
                except Exception:
                    failed += 1
                    continue
            except Exception:
                failed += 1
                continue
    task.end_task(task_id)

    await message.reply(
        f"""<blockquote>
{emo.profil}<b>Spam Broadcast Report:
{emo.sukses} Success: <code>{done}</code> Groups
{emo.gagal} Failed: <code>{failed}</code> Groups
</b></blockquote>"""
    )
    return await proses.delete()
