import asyncio
import io
import os
import random

import cv2
import requests
from pyrogram import raw, types

from kelra.helpers import CMD, ApiImage, Emoji

__MODULES__ = "Image"
__HELP__ = """<blockquote>Command Help **Image**</blockquote>

<blockquote expandable>        <u>**Remove background**</u>
        `{0}rbg` (reply image)
        
        <u>**Blur image**</u>
        `{0}blur` (reply image)

        <u>**Mirror image**</u>
        `{0}mirror` (reply image)

        <u>**Negative image**</u>
        `{0}negative` (reply image)

        <u>**Search image**</u>
        `{0}wall`

        <u>**Get beautiful anime image**</u>
        `{0}waifu`

        <u>**Get image with your command**</u>
        `{0}pic` (prompt)
        
        <u>**Get gif with your command**</u>
        `{0}gif` (prompt)</blockquote>
    
<b>   {1}</b>
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

async def ReTrieveFile(input_file_name):
    headers = {
        "X-API-Key": "HgrmjXeGacBNXHnUGuw4msC1",
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    return requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers=headers,
        files=files,
        allow_redirects=True,
        stream=True,
    )


@CMD.UBOT("rbg")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if message.reply_to_message:
        reply_message = message.reply_to_message

        try:
            if isinstance(reply_message.media, raw.types.MessageMediaPhoto) or reply_message.media:
                downloaded_file_name = await client.download_media(reply_message, "./downloads/")
                await proses.edit(f"<b>{em.gagal}Try removing background...</b>")
                output_file_name = await ReTrieveFile(downloaded_file_name)
                os.remove(downloaded_file_name)
            else:
                return await proses.edit(f"<b>{em.gagal}Please reply to photo!!</b>")
        except Exception as e:
            await proses.edit(f"{em.gagal}**ERROR:** {(str(e))}")
            return
        contentType = output_file_name.headers.get("content-type")
        if "image" in contentType:
            with io.BytesIO(output_file_name.content) as remove_bg_image:
                remove_bg_image.name = "rbg.png"
                await client.send_document(
                    message.chat.id,
                    document=remove_bg_image,
                    force_document=True,
                    reply_to_message_id=message.id,
                )
                return await proses.delete()
        else:
            return await proses.edit("{}<b>ERROR</b>\n<i>{}</i>".format(em.gagal, output_file_name.content.decode("UTF-8")))
    else:
        return await message.reply(f"<b>{em.gagal}Please reply to photo</b>")


@CMD.UBOT("blur")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    reply = message.reply_to_message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo</b>")
    yinsxd = await client.download_media(reply, "./downloads/")
    if yinsxd.endswith(".tgs"):
        cmd = ["lottie_convert.py", yinsxd, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(yinsxd)
        heh, lol = img.read()
        cv2.imwrite("yin.png", lol)
        file = "yin.png"
    yin = cv2.imread(file)
    ayiinxd = cv2.GaussianBlur(yin, (35, 35), 0)
    cv2.imwrite("yin.jpg", ayiinxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(yinsxd)
    return await proses.delete()


@CMD.UBOT("negative")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    reply = message.reply_to_message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo</b>")
    ayiinxd = await client.download_media(reply, "./downloads/")
    if ayiinxd.endswith(".tgs"):
        cmd = ["lottie_convert.py", ayiinxd, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(ayiinxd)
        heh, lol = img.read()
        cv2.imwrite("yin.png", lol)
        file = "yin.png"
    yinsex = cv2.imread(file)
    kntlxd = cv2.bitwise_not(yinsex)
    cv2.imwrite("yin.jpg", kntlxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(ayiinxd)
    return await proses.delete()


@CMD.UBOT("miror")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    reply = message.reply_to_message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if not reply:
        return await proses.edit(f"<b>{em.gagal}Please reply to photo.</b>")
    xnproses = await client.download_media(reply, "./downloads/")
    if xnproses.endswith(".tgs"):
        cmd = ["lottie_convert.py", xnproses, "yin.png"]
        file = "yin.png"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        stderr.decode().strip()
        stdout.decode().strip()
    else:
        img = cv2.VideoCapture(xnproses)
        kont, tol = img.read()
        cv2.imwrite("yin.png", tol)
        file = "yin.png"
    yin = cv2.imread(file)
    mmk = cv2.flip(yin, 1)
    ayiinxd = cv2.hconcat([yin, mmk])
    cv2.imwrite("yin.jpg", ayiinxd)
    await client.send_photo(
        message.chat.id,
        "yin.jpg",
        reply_to_message_id=message.id,
    )
    os.remove("yin.png")
    os.remove("yin.jpg")
    os.remove(xnproses)
    return await proses.delete()


@CMD.UBOT("wall|waifu")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    message.reply_to_message
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    if message.command[0] == "wall":
        photo = await ApiImage.wall(client)
        try:
            await photo.copy(message.chat.id, reply_to_message_id=message.id)
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**{str(error)}**")
    elif message.command[0] == "waifu":
        photo = ApiImage.waifu()
        try:
            await message.reply_photo(photo)
            return await proses.delete()
        except Exception as error:
            return await proses.edit(f"{em.gagal}**{str(error)}**")


@CMD.UBOT("pic")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prompt = client.get_text(message)
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    await asyncio.sleep(2)
    if not prompt:
        return await proses.edit(f"{em.gagal}**Please use command:** <code>{message.text.split()[0]} dino kuning</code>")
    x = await client.get_inline_bot_results(message.command[0], prompt)
    await proses.delete()
    get_media = []
    for X in range(5):
        try:
            saved = await client.send_inline_bot_result(client.me.id, x.query_id, x.results[random.randrange(30)].id)
            saved = await client.get_messages(client.me.id, int(saved.updates[1].message.id), replies=0)
            get_media.append(types.InputMediaPhoto(saved.photo.file_id))
        except Exception as er:
            return await proses.edit(f"{em.gagal}<b>Image nothing found</b> {str(er)}")
    await saved.delete()
    return await client.send_media_group(
        message.chat.id,
        get_media,
        reply_to_message_id=message.id,
    )


@CMD.UBOT("gif")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prompt = client.get_text(message)
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")
    await asyncio.sleep(2)
    if not prompt:
        return await proses.edit(f"{em.gagal}**Please use command: <code>{message.text.split()[0]} dino kuning</code>")
    x = await client.get_inline_bot_results(message.command[0], prompt)
    await proses.delete()
    try:
        saved = await client.send_inline_bot_result(client.me.id, x.query_id, x.results[random.randrange(30)].id)
    except Exception as er:
        await proses.edit(f"{em.gagal}<b>Media nothing found</b> {str(er)}")
    saved = await client.get_messages(client.me.id, int(saved.updates[1].message.id), replies=0)
    await saved.delete()
    return await client.send_animation(message.chat.id, saved.animation.file_id, reply_to_message_id=message.id)
