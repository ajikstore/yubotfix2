from kelra import *
from pyrogram.raw.functions.contacts import AddContact
from kelra.helpers import CMD, Emoji, Tools


__MODULES__ = "Save kontak"
__HELP__ = """<blockquote>Command Help **Save kontak**</blockquote> 

<blockquote expandable><u>**To save Telegram account contacts**</u>
    <u>**You can save contacts easily**</u>
        `{0}savekon` (reply/id/username) (name) 

    <u>**To delete Telegram account contacts**</u>
    <u>**Youcand delete contacts easily**</u>
        `{0}delkon` (reply)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴜsᴇʀ <emoji id=5253539825360843975>👥</emoji>"

@CMD.UBOT("savekon")
async def save_contact(client, message):
    user_id = None
    custom_name = ""

    reply_message = message.reply_to_message
    if reply_message and reply_message.from_user:
        user_id = reply_message.from_user.id
        custom_name = message.text.split(maxsplit=1)[1] if len(message.text.split(maxsplit=1)) > 1 else ""
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply_text("<blockquote>❎ Mohon reply ke pengguna atau masukkan nama custom untuk menyimpan kontak.</blockquote>")

        custom_name = args[1]
        args = message.command
        if len(args) < 3:
            return await message.reply_text("<blockquote>❎ Mohon reply ke pengguna atau masukkan ID pengguna/username dan nama custom untuk menyimpan kontak.</blockquote>")

        user_id_or_username = args[1]

        try:
            user = await client.get_users(user_id_or_username)
            user_id = user.id
        except Exception as e:
            return await message.reply_text(f"<blockquote>❎ Terjadi kesalahan: {e}</blockquote>")

    if not custom_name.strip():
        return await message.reply_text("<blockquote>❎ Nama custom tidak boleh kosong.</blockquote>")

    first_name = custom_name.strip()
    chat_id = await client.resolve_peer(user_id)

    try:
        response = await client.invoke(
            AddContact(
                id=chat_id,
                first_name=first_name,
                last_name="",
                phone=""
            )
        )
        if response.users and response.users[0].contact:
            await message.reply_text(f"<blockquote>✅ Berhasil menyimpan kontak dengan nama <code>{first_name}</code></blockquote>")
        else:
            await message.reply_text("<blockquote>❎ Terjadi kesalahan saat menyimpan kontak.</blockquote>")
    except RPCError as e:
        await message.reply_text(f"<blockquote>❎ Terjadi kesalahan: {e}</blockquote>")

@CMD.UBOT("delkon")
async def delete_contact(client, message):
    user_id = None

    reply_message = message.reply_to_message
    if reply_message and reply_message.from_user:
        user_id = reply_message.from_user.id
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply_text("<blockquote>❎ Mohon reply ke pengguna atau masukkan ID pengguna/username untuk menghapus kontak.</blockquote>")

        user_id_or_username = args[1]

        try:
            user = await client.get_users(user_id_or_username)
            user_id = user.id
        except Exception as e:
            return await message.reply_text(f"<blockquote>❎ Terjadi kesalahan: {e}</blockquote>")

    try:
        response = await client.delete_contacts([user_id])
        if response:
            await message.reply_text(f"<blockquote>✅ Berhasil menghapus kontak dengan ID {user_id}</blockquote>")
        else:
            await message.reply_text("<blockquote>❎ Terjadi kesalahan saat menghapus kontak.</blockquote>")
    except RPCError as e:
        await message.reply_text(f"<blockquote>❎ Terjadi kesalahan: {e}</blockquote>")
