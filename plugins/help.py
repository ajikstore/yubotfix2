from config import BOT_NAME, HELPABLE
from kelra import bot
from kelra.helpers import CMD, ButtonUtils, Emoji


@CMD.UBOT("help")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if not client.get_arg(message):
        query = "help"
        chat_id = message.chat.id if len(message.command) < 2 else message.text.split()[1]
        try:
            inline = await ButtonUtils.send_inline_bot_result(
                message,
                chat_id,
                bot.me.username,
                query,
            )
            if inline:
                return await message.delete()
        except Exception as error:
            return await message.reply(f"<blockquote>{em.gagal}Error: {str(error)}</blockquote>")
    else:
        nama = f"{client.get_arg(message)}"
        pref = client.get_prefix(client.me.id)
        x = next(iter(pref))
        text_help2 = f"<blockquote>***🤖 {BOT_NAME}***</blockquote>"
        if nama in HELPABLE:
            return await message.reply(
                f"{HELPABLE[nama].__HELP__.format(x, text_help2)}",
            )
        else:
            return await message.reply(f"<blockquote>{em.gagal}<b>Tidak ada modul bernama <code>{nama}</code></b></blockquote>")
