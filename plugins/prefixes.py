from kelra.database import dB
from kelra.helpers import CMD, Emoji

__MODULES__ = "Prefix"
__HELP__ = """<blockquote>Command Help **Prefix**</blockquote>

<blockquote expandable>        <u>**Set handler userbot**</u>
    <u>**You can set handler or trigger to your userbot**</u>
        `{0}setprefix` (trigger/symbol)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

@CMD.UBOT("setprefix")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = await emo.get_costum_text()
    pros = await message.reply(f"<blockquote>{emo.proses}**{proses_}**</blockquote>")
    if len(message.command) < 2:
        m = message.text.split()[0]
        return await pros.edit(
            f"<blockquote>{emo.gagal}<b>Please provide the Prefix/Handler you want to use.</b>\n\n</blockquote>"
            f"Example:\n<code>{m}setprefix , . ? : ;</code>\n\n"
            f"Or use <code>none</code> if you want to use commands without a Prefix/Handler."
        )
    ub_prefix = []
    for prefix in message.command[1:]:
        if prefix.lower() == "none":
            ub_prefix.append("")
        else:
            ub_prefix.append(prefix)
    try:
        client.set_prefix(client.me.id, ub_prefix)
        await dB.set_pref(client.me.id, ub_prefix)
        parsed_prefix = " ".join(f"<code>{prefix}</code>" for prefix in ub_prefix if prefix) or "none"
        return await pros.edit(f"<blockquote>{emo.sukses}<b>Successfully set the Prefix to: {parsed_prefix}</b></blockquote>")
    except Exception as error:
        return await pros.edit(f"<blockquote>{emo.gagal}<b>ERROR: <code>{error}</code></b></blockquote>")
