from pyrogram.errors import ChatAdminRequired, ChatNotModified, RPCError
from pyrogram.types import ChatPermissions

from kelra.helpers import CMD, Emoji

__MODULES__ = "Locks"
__HELP__ = """<blockquote>Command Help **Locks**</blockquote>

<blockquote expandable>        <u>**Basic command**</u>
    <u>**To view lock type**</u>
        `{0}locktypes`
    <u>**View permisson from chat**</u>
        `{0}locks`
    
        <u>**Lock unlock**</u>
    <u>**You can lock some permission from chat**</u>
        `{0}lock` (type)
    <u>**You can unlock some permission from chat**</u>
        `{0}unlock` (type)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴛᴏᴏʟs <emoji id=5435961551871813164>🛠</emoji>"

l_t = """
**Lock Types:**
- `all` = Everything
- `msg` = Messages
- `media` = Media, such as Photo and Video.
- `polls` = Polls
- `invite` = Add users to Group
- `pin` = Pin Messages
- `info` = Change Group Info
- `webprev` = Web Page Previews
- `inline` = Inline bots
- `animations` = Animations
- `games` = Game Bots
- `stickers` = Stickers
- `url` = Lock links"""

data = {
    "msg": "can_send_messages",
    "stickers": "can_send_other_messages",
    "gifs": "can_send_other_messages",
    "media": "can_send_media_messages",
    "games": "can_send_other_messages",
    "inline": "can_send_other_messages",
    "url": "can_add_web_page_previews",
    "polls": "can_send_polls",
    "info": "can_change_info",
    "invite": "can_invite_users",
    "pin": "can_pin_messages",
}


async def current_chat_permissions(client, chat_id):
    perms = []
    perm = (await client.get_chat(chat_id)).permissions
    if perm.can_send_messages:
        perms.append("can_send_messages")
    if perm.can_send_media_messages:
        perms.append("can_send_media_messages")
    if perm.can_send_other_messages:
        perms.append("can_send_other_messages")
    if perm.can_add_web_page_previews:
        perms.append("can_add_web_page_previews")
    if perm.can_send_polls:
        perms.append("can_send_polls")
    if perm.can_change_info:
        perms.append("can_change_info")
    if perm.can_invite_users:
        perms.append("can_invite_users")
    if perm.can_pin_messages:
        perms.append("can_pin_messages")
    return perms


@CMD.UBOT("locktypes")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    await message.reply_text(l_t)
    return


async def tg_lock(client, message, permissions: list, perm: str, lock: bool):
    em = Emoji(client)
    await em.get()
    if lock:
        if perm not in permissions:
            return await message.reply(f"{em.sukses}**Successfully locked.**")
        permissions.remove(perm)
    elif perm in permissions:
        return await message.reply(f"{em.sukses}**Already unlocked.**")
    else:
        permissions.append(perm)

    permissions = {perm: True for perm in list(set(permissions))}

    try:
        await client.set_chat_permissions(message.chat.id, ChatPermissions(**permissions))
    except ChatNotModified:
        return await message.reply(f"{em.gagal}**To unlock this, you have to unlock 'messages' first.**")

    return await message.reply((f"{em.sukses}**Successfully locked.**") if lock else (f"{em.sukses}**Successfully unlocked.**"))


@CMD.UBOT("lock|unlock")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    if len(message.command) != 2:
        return await message.reply(f"{em.gagal}**Invalid command format.**")

    chat_id = message.chat.id
    parameter = message.text.strip().split(None, 1)[1].lower()
    state = message.command[0].lower()

    if parameter not in data and parameter != "all":
        return await message.reply(f"{em.gagal}**Invalid lock type.**")

    permissions = await current_chat_permissions(client, chat_id)

    if parameter in data:
        return await tg_lock(client, message, permissions, data[parameter], state == "lock")
    elif parameter == "all" and state == "lock":
        try:
            await client.set_chat_permissions(chat_id, ChatPermissions())
            return await message.reply(f"{em.sukses}**All permissions locked.**")
        except ChatAdminRequired:
            return await message.reply(f"{em.gagal}**Admin privileges required.**")

    elif parameter == "all" and state == "unlock":
        try:
            await client.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False,
                ),
            )
            return await message.reply(f"{em.sukses}**All permissions unlocked.**")
        except ChatAdminRequired:
            return await message.replyf(f"{em.gagal}**Admin privileges required.**")


@CMD.UBOT("locks")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    chkmsg = await message.reply_text(f"{em.proses}**{proses_[4]}**")
    v_perm = message.chat.permissions

    def convert_to_emoji(val: bool):
        if val:
            return f"{em.sukses}"
        return f"{em.gagal}"

    vmsg = convert_to_emoji(v_perm.can_send_messages)
    vmedia = convert_to_emoji(v_perm.can_send_media_messages)
    vwebprev = convert_to_emoji(v_perm.can_add_web_page_previews)
    stickers = convert_to_emoji(v_perm.can_send_other_messages)
    vpolls = convert_to_emoji(v_perm.can_send_polls)
    vinfo = convert_to_emoji(v_perm.can_change_info)
    vinvite = convert_to_emoji(v_perm.can_invite_users)
    vpin = convert_to_emoji(v_perm.can_pin_messages)
    if v_perm is not None:
        try:
            permission_view_str = f"""
<b>{em.warn}Chat Permissions:</b>

      <b>Send Messages:</b> {vmsg}
      <b>Send Media:</b> {vmedia}
      <b>Send Stickers:</b> {stickers}
      <b>Webpage Preview:</b> {vwebprev}
      <b>Send Polls:</b> {vpolls}
      <b>Change Info:</b> {vinfo}
      <b>Invite Users:</b> {vinvite}
      <b>Pin Messages:</b> {vpin}
      """
            return await chkmsg.edit_text(permission_view_str)

        except RPCError as e_f:
            return await message.reply_text(f"{em.gagal}Error: {str(e_f)}")
