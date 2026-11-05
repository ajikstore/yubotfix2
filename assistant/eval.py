import asyncio
import contextlib
import html
import io
import os
import subprocess
import zipfile
from datetime import datetime
from time import perf_counter
from typing import Any, Dict
from uuid import uuid4

import pyrogram
import pyrogram.enums
import pyrogram.errors
import pyrogram.helpers
import pyrogram.raw
import pyrogram.types
import pyrogram.utils
from meval import meval
from pyrogram.helpers import ikb
from pytz import timezone

import config
from kelra import bot, kelra
from kelra.database import DB_PATH, dB, state
from kelra.helpers import (
    CMD,
    ButtonUtils,
    Emoji,
    Message,
    Quotly,
    Sticker,
    Tools,
    YoutubeSearch,
    cookies,
    stream,
    task,
    telegram,
    youtube,
)

eval_tasks: Dict[int, Any] = {}


@CMD.BOT("getubot")
@CMD.NLX
async def _(client, message):
    return await bot.send_message(
        message.from_user.id,
        await Message.userbot(0),
        reply_markup=ButtonUtils.userbot(kelra._ubot[0].me.id, 0),
    )


@CMD.BOT("restore")
@CMD.NLX
async def restore(client, message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("**Please reply to a .db or .zip file**")

    document = reply.document
    file_path = await client.download_media(document, "./")

    if file_path.endswith(".zip"):
        extract_path = "./extracted_db"
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        db_files = [f for f in os.listdir(extract_path) if f.endswith(".db")]
        if not db_files:
            return await message.reply("**No .db file found in the ZIP archive**")

        extracted_db = os.path.join(extract_path, db_files[0])
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        os.rename(extracted_db, DB_PATH)

        os.remove(file_path)
    else:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        file_path = await client.download_media(document, "./")

    await message.reply(
        "<blockquote><b>Sukses melakukan restore database, tunggu sebentar bot akan me-restart.</b></blockquote>"
    )
    await client.bash("pkill -f uvicorn")
    os.execl("/bin/bash", "bash", "start.sh")


@CMD.BOT("backup")
@CMD.NLX
async def backup(client, message):
    now = datetime.now(timezone("Asia/Jakarta"))
    timestamp = now.strftime("%Y-%m-%d_%H:%M")
    zip_filename = f"{config.BOT_NAME}_{timestamp}.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(".env"):
            env_path = os.path.abspath(".env")
            zipf.write(env_path, os.path.basename(env_path))
        zipf.write(DB_PATH, os.path.basename(DB_PATH))

    caption = now.strftime("%d %B %Y %H:%M")
    return await message.reply_document(zip_filename, caption=caption)


@CMD.BOT("shell")
@CMD.BOT("sh")
@CMD.NLX
async def _(client: bot, message):
    return await cb_shell(client, message)


async def cb_shell(client, message):
    if len(message.command) < 2:
        return await message.reply("Noob!!")

    cmd_text = message.text.split(maxsplit=1)[1]
    text = f"<code>{cmd_text}</code>\n\n"
    start_time = perf_counter()

    try:
        stdout, stderr = await client.bash(cmd_text)
    except asyncio.TimeoutError:
        text += "<b>Timeout expired!!</b>"
        return await message.reply(text)
    finally:
        duration = perf_counter() - start_time

    if len(stdout) > 4096:
        anuk = await message.reply("<b>Oversize, sending file...</b>")

        output_filename = "output.txt"
        if cmd_text.startswith("cat "):
            filepath = cmd_text.split("cat ", 1)[1].strip()
            output_filename = os.path.basename(filepath)

        with open(output_filename, "w") as file:
            file.write(stdout)

        await message.reply_document(
            output_filename,
            caption=f"<b>Command completed in `{duration:.2f}` seconds.</b>",
        )
        os.remove(output_filename)
        return await anuk.delete()
    else:
        text += f"<pre><code>{stdout}</code></pre>"

    if stderr:
        text += f"<blockquote>{stderr}</blockquote>"

    text += f"\n<b>Completed in `{duration:.2f}` seconds.</b>"
    return await message.reply(text, parse_mode=pyrogram.enums.ParseMode.HTML)


@CMD.BOT("eval")
@CMD.BOT("e")
@CMD.NLX
async def _(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text("<b>No Code!</b>", quote=True)
        return

    reply_text = await message.reply_text(
        "...",
        quote=True,
        reply_markup=ikb([[("Cancel", "Canceleval")]]),
    )

    async def eval_func() -> None:
        eval_code = message.text.split(maxsplit=1)[1]
        eval_vars = {
            "c": client,
            "m": message,
            "u": (message.reply_to_message or message).from_user,
            "r": message.reply_to_message,
            "chat": message.chat,
            "asyncio": asyncio,
            "pyrogram": pyrogram,
            "raw": pyrogram.raw,
            "enums": pyrogram.enums,
            "types": pyrogram.types,
            "errors": pyrogram.errors,
            "utils": pyrogram.utils,
            "helpers": pyrogram.helpers,
            "bot": bot,
            "dB": dB,
            "Emoji": Emoji,
            "config": config,
            "Message": Message,
            "Tools": Tools,
            "Sticker": Sticker,
            "Quotly": Quotly,
            "YoutubeSearch": YoutubeSearch,
            "cookies": cookies,
            "stream": stream,
            "telegram": telegram,
            "youtube": youtube,
            "task": task,
            "button": ButtonUtils,
            "state": state,
            "DB_PATH": DB_PATH,
        }

        start_time = client.loop.time()

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                meval_out = await meval(eval_code, globals(), **eval_vars)
                print_out = buf.getvalue().strip() or str(meval_out) or "None"
            except Exception as exception:
                print_out = repr(exception)

        elapsed_time = client.loop.time() - start_time
        converted_time = Tools.convert_seconds(elapsed_time)

        final_output = (
            f"<pre>{html.escape(print_out)}</pre>\n"
            f"<b>Elapsed:</b> {converted_time}"
        )

        if len(final_output) > 4096:
            paste_url = await Tools.paste(html.escape(print_out))
            await reply_text.edit_text(
                f"<b>Elapsed:</b> {converted_time}",
                reply_markup=ikb([[("Output", f"{paste_url}", "url")]]),
                disable_web_page_preview=True,
            )
        else:
            await reply_text.edit_text(final_output)

    task_id = message.id
    _e_task = asyncio.create_task(eval_func())
    eval_tasks[task_id] = _e_task

    try:
        await _e_task
    except asyncio.CancelledError:
        await reply_text.edit_text("<b>Process Cancelled!</b>")
    finally:
        if task_id in eval_tasks:
            del eval_tasks[task_id]


async def cb_evalusi(client, message):
    if len(message.text.split()) == 1:
        await message.reply_text("<b>No Code!</b>", quote=True)
        return

    reply_text = await message.reply_text("...", quote=True)
    uniq = str(uuid4())

    async def eval_func() -> None:
        eval_code = message.text.split(maxsplit=1)[1]
        eval_vars = {
            "c": client,
            "m": message,
            "u": (message.reply_to_message or message).from_user,
            "r": message.reply_to_message,
            "chat": message.chat,
            "asyncio": asyncio,
            "pyrogram": pyrogram,
            "raw": pyrogram.raw,
            "enums": pyrogram.enums,
            "types": pyrogram.types,
            "errors": pyrogram.errors,
            "utils": pyrogram.utils,
            "helpers": pyrogram.helpers,
            "bot": bot,
            "dB": dB,
            "Emoji": Emoji,
            "config": config,
            "Message": Message,
            "Tools": Tools,
            "Sticker": Sticker,
            "Quotly": Quotly,
            "YoutubeSearch": YoutubeSearch,
            "cookies": cookies,
            "stream": stream,
            "telegram": telegram,
            "youtube": youtube,
            "task": task,
            "button": ButtonUtils,
            "state": state,
            "DB_PATH": DB_PATH,
        }

        start_time = client.loop.time()

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                meval_out = await meval(eval_code, globals(), **eval_vars)
                print_out = buf.getvalue().strip() or str(meval_out) or "None"
            except Exception as exception:
                print_out = repr(exception)

        elapsed_time = client.loop.time() - start_time
        converted_time = Tools.convert_seconds(elapsed_time)

        final_output = (
            f"<pre>{html.escape(print_out)}</pre>\n"
            f"<b>Elapsed:</b> {converted_time}"
        )

        uniq_key = uniq.split("-")[0]

        if len(final_output) > 4096:
            paste_url = await Tools.paste(html.escape(print_out))
            datas = {"time": f"<b>Elapsed:</b> {converted_time}", "url": paste_url}
            state.set(config.BOT_ID, uniq_key, datas)

            if paste_url is None:
                output_filename = f"{uniq_key}.txt"
                with open(output_filename, "w") as f:
                    data = html.escape(print_out).replace("&quot;", "'")
                    f.write(data)
                await message.reply_document(
                    output_filename,
                    caption=f"<b>Elapsed: `{converted_time}.`</b>",
                )
                os.remove(output_filename)
                await reply_text.delete()
            else:
                inline = await ButtonUtils.send_inline_bot_result(
                    message,
                    message.chat.id,
                    bot.me.username,
                    f"inline_eval {uniq_key}",
                )
                if inline:
                    await reply_text.delete()
        else:
            datas = {"time": final_output}
            state.set(config.BOT_ID, uniq_key, datas)
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                message.chat.id,
                bot.me.username,
                f"inline_eval {uniq_key}",
            )
            if inline:
                await reply_text.delete()

    task_id = message.id
    _e_task = asyncio.create_task(eval_func())
    eval_tasks[task_id] = _e_task

    try:
        await _e_task
    except asyncio.CancelledError:
        await reply_text.edit_text("<b>Process Cancelled!</b>")
    finally:
        if task_id in eval_tasks:
            del eval_tasks[task_id]


async def send_large_output(message, output):
    with io.BytesIO(str.encode(str(output))) as out_file:
        out_file.name = "update.txt"
        await message.reply_document(document=out_file)


@CMD.BOT("reboot")
@CMD.BOT("update")
@CMD.FAKE_NLX
async def _(client: bot, message):
    return await cb_gitpull2(client, message)


async def update_kode(client, message):
    out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if "Already up to date." in out:
        return await message.reply(f"<pre>{out}</pre>")
    if len(out) > 4096:
        await send_large_output(message, out)
    else:
        await message.reply(f"<pre>{out}</pre>")
    await client.bash("pkill -f uvicorn")
    os.execl("/bin/bash", "bash", "start.sh")


async def cb_gitpull2(client, message):
    if message.command[0] == "update":
        return await update_kode(client, message)
    elif message.command[0] == "reboot":
        await client.bash("pkill -f uvicorn")
        await message.reply("<b>✅ Gunicorn stopped successfully. Trying to restart Userbot!!</b>")
        os.execl("/bin/bash", "bash", "start.sh")
