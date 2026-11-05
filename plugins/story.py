__MODULES__ = "Story"
__HELP__ = """<blockquote>Command Help **Story**</blockquote>

<blockquote expandable>        <u>**Post story**</u>
    <u>**You can post media to telegram story**</u>
        `{0}story post` (reply media)
    
        <u>**Check story**</u>
    <u>**Get all stories on your account**</u>
        `{0}story cek`

        <u>**Delete story**</u>
    <u>**You can delete story with this command**</u>
        `{0}story del` (strory id)

        <u>**Get or steal story**</u>
    <u>**You can steal story from user**</u>
        `{0}story get` (url)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴍᴇᴅɪᴀ <emoji id=5472315641123851828>🗂</emoji>"

import traceback

from pyrogram.enums import StoriesPrivacyRules

from kelra.helpers import CMD, Emoji, Tools
from kelra.logger import logger


@CMD.UBOT("story")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    args = ["cek", "del", "get", "post"]
    query = message.command[1]
    if len(message.command) < 2 and query not in args:
        return await proses.edit(f"<blockquote>{em.gagal}<b>Please give query [post, cek, get, or del]</b></blockquote>")
    prefix = client.get_prefix(client.me.id)
    if query == "cek":
        text = f"<blockquote expandable>{em.owner}<b>Your stories:</b>\n\n"
        async for story in client.get_all_stories():
            if story.from_user.id == client.me.id:
                story_link = await client.export_story_link("me", story.id)
                text += f"{em.sukses}<b>• Story ID: `{story.id}` | Story Link: [Click Here]({story_link})</b>\n</blockquote>"
        await message.reply(text, disable_web_page_preview=True)
        return await proses.delete()

    elif query == "del":
        if len(message.command) < 3:
            return await proses.edit(
                f"<blockquote expandable><b>{em.gagal} That's not how it works!! Provide your story ID.\nExample: `{prefix[0]}story del` 5\n\nOr you can type `{prefix[0]}story cek` to see your story IDs!! </b></blockquote>"
            )
        story_id = message.text.split()[2]
        if not story_id.isnumeric():
            return await proses.edit(f"<blockquote>{em.gagal}<b>ID should be a number, not letters or symbols.</b></blockquote>")
        await client.delete_stories(story_ids=int(story_id))
        return await proses.edit(f"<blockquote>{em.sukses}<b>Successfully deleted Story ID: `{story_id}`!!</b></blockquote>")

    elif query == "get":
        if len(message.command) < 3:
            return await proses.edit(f"<blockquote>{em.gagal}**Please give link story!**</blockquote>")
        link = message.text.split()[2]
        if "/s/" not in link:
            return await proses.edit(f"<blockquote>{em.gagal}<b>Please provide a valid Telegram stories link!!</b></blockquote>")
        user, story_id = Tools.extract_story_link(link)
        story = await client.get_stories(user, story_id)
        await Tools.download_media(story, client, proses, message, True)
        return await proses.delete()

    elif query == "post":
        reply = message.reply_to_message
        if not reply or reply and not reply.media:
            return await proses.edit(f"<blockquote>{em.gagal}**Please reply to photo or video**</blockquote>")
        kwargs = reply.photo.file_id or reply.video.file_id
        text = reply.caption or ""
        try:
            target = "me" if len(message.command) < 3 else message.text.split()[2]
            story = await client.send_story(target, kwargs, caption=text, privacy=StoriesPrivacyRules.PUBLIC)
            this = await client.export_story_link("me", story.id)
            return await proses.edit(
                f"<blockquote>{em.sukses}<b>Succesfully upload to [Story]({this})!</b></blockquote>",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Error: {traceback.format_exc()}")
            return await proses.edit(f"<blockquote>{em.gagal}**ERROR:** {str(e)}</blockquote>")
    else:
        return await proses.edit(f"<blockquote>{em.gagal}<b>Please give query [post, cek, get, or del]</b></blockquote>")
