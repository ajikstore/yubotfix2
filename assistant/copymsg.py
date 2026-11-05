from kelra.helpers import CMD, Tools
from kelra.logger import logger


@CMD.BOT("kontol")
async def _(client, message):
    proses = await message.reply("<b>Please wait a minute...</b>")
    try:
        link = message.text.split()[1]
        if len(message.command) < 2:
            return await message.reply(f"<b><code>{message.text.split()[0]}</code> [link]</b>")
        if link.startswith(("https", "t.me")):
            msg_id = int(link.split("/")[-1])
            if "t.me/c/" in link:
                chat = int("-100" + str(link.split("/")[-2]))
            else:
                chat = str(link.split("/")[-2])
            try:
                get_msg = await client.get_messages(chat, msg_id)
                try:
                    await get_msg.copy(message.chat.id)
                except Exception:
                    return await Tools.download_media(get_msg, client, proses, message)
            except Exception as er:
                return await message.reply(str(er))
        else:
            return await message.reply("Link tidak valid.")
    except Exception as er:
        logger.error(f"copy eror {str(er)}")
