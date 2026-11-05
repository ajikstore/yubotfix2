"""
 𝘐𝘕𝘐 𝘊𝘖𝘋𝘌 𝘎𝘜𝘌 𝘚𝘌𝘕𝘋𝘐𝘙𝘐 𝘔𝘌𝘒!! 𝘕𝘎𝘈𝘒𝘜 𝘕𝘎𝘈𝘒𝘜? 𝘙𝘌𝘡𝘌𝘒𝘐 𝘒𝘌𝘛𝘜𝘙𝘜𝘕𝘈𝘕 𝘓𝘖 𝘎𝘈 𝘉𝘌𝘙𝘍𝘈𝘌𝘋𝘈𝘏 1000 𝘛𝘈𝘏𝘜𝘕!!
 𝘊𝘙𝘌𝘋𝘐𝘛𝘚 𝘉𝘠 : @ahMakan
"""

import aiohttp
from pyrogram import filters
from pyrogram.enums import ChatType, ChatAction
from kelra import kelra
from kelra.helpers import CMD, Emoji, Tools
from config import API_BOTCHAX

__MODULES__ = "Chatbot"
__HELP__ = """<blockquote>Command Help <b>Chatbot</b></blockquote>

<blockquote expandable>      <u><b>Turn on chatbot</b></u>
        <code>{0}chatbot on</code>

    <u><b>Turn off chatbot</b></u>
        <code>{0}chatbot off</code>

    <u><b>You can set role chatbot</b></u>
        <code>{0}chatbot role</code> (tipe)

    <u><b>You can see the chatbot status</b></u>
        <code>{0}chatbot status</code></blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

CONVERSATIONS = {}
CHATBOT_GROUPS = {}
CHATBOT_PRIVATE = {}
CHATBOT_ROLE = {}

DEFAULT_ROLE = """
Kamu adalah kelra, anggota grup Telegram yang menyamar sebagai manusia.
Gunakan bahasa gaul, santai, cuek, kadang sedikit toxic.
Selalu pakai 'gw' dan 'lu'. Jangan pernah ngaku AI.
Balaslah pesan menggunakan huruf kecil disemua teks dan balaslah pesan sesingkat mungkin."
"""

ROLES = {
    "default": DEFAULT_ROLE,

    "formal": """
bicara sopan tapi tetap singkat,
tanpa huruf kapital, tanpa nanya balik, jawab seperlunya aja
""",

    "santai": """
bahasa gaul tongkrongan, cuek, to the point,
jawaban pendek, tanpa kapital, tanpa nanya balik
""",

    "humoris": """
gaya bercanda ringan, ogah ribet,
jawaban pendek, tanpa kapital, tanpa nanya balik
""",

    "romantis": """
lembut tapi natural, bukan robotik,
jawaban singkat, tanpa kapital, tanpa nanya balik
""",

    "galak": """
nyolot dikit, ketus, kayak lagi kesel,
jawaban maksimal dua kalimat, pakai sedikit kata kasar ringan,
tanpa kapital, tanpa nanya balik
""",

    "nyolot": """
sinis, sarkas, males nanggepin,
jawaban super pendek 1–2 kalimat, tanpa kapital, tanpa nanya balik
"""
}

__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"


# ---------- AI REPLY DENGAN HISTORY ----------
async def ai_reply(client_id: int, text: str, user_id: int):
    if client_id not in CONVERSATIONS:
        CONVERSATIONS[client_id] = {}

    if user_id not in CONVERSATIONS[client_id]:
        role_text = CHATBOT_ROLE.get(client_id, DEFAULT_ROLE)
        CONVERSATIONS[client_id][user_id] = [
            {"role": "system", "content": role_text}
        ]

    # simpan user message
    CONVERSATIONS[client_id][user_id].append({"role": "user", "content": text})

    # batasi history
    if len(CONVERSATIONS[client_id][user_id]) > 20:
        base = CONVERSATIONS[client_id][user_id][:1]
        tail = CONVERSATIONS[client_id][user_id][-19:]
        CONVERSATIONS[client_id][user_id] = base + tail

    url = "https://api.botcahx.eu.org/api/search/openai-custom"
    payload = {"message": CONVERSATIONS[client_id][user_id], "apikey": API_BOTCHAX}

    try:
        data = await Tools.post_json(url, payload)
        if not data or "result" not in data:
            return None
        result = data["result"]
    except Exception as e:
        print(f"[Chatbot] ⚠️ Gagal request API: {e}")
        return None

    # simpan reply AI
    CONVERSATIONS[client_id][user_id].append({"role": "assistant", "content": result})
    return result


# ---------- COMMAND CHATBOT ----------
@CMD.UBOT("chatbot")
async def chatbot_command(client, message):
    em = Emoji(client)
    await em.get()
    chat = message.chat
    chat_id = chat.id
    client_id = client.me.id

    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        text_roles = ", ".join(ROLES.keys())
        return await message.reply(
            f"""
<blockquote expandable>{em.gagal} Please use format:\n
• `{args[0]} on/off`\n
• `{args[0]} role [tipe]`\n
• `{args[0]} status`\n
{em.owner} Roles available: `{text_roles}`</blockquote>
"""
        )

    subcmd = args[1].lower()
    CHATBOT_GROUPS.setdefault(client_id, {})
    CHATBOT_PRIVATE.setdefault(client_id, False)
    CHATBOT_ROLE.setdefault(client_id, DEFAULT_ROLE)

    # ---------- GROUP CHAT ----------
    if chat.type in (ChatType.SUPERGROUP, ChatType.GROUP):
        if subcmd == "on":
            CHATBOT_GROUPS[client_id][chat_id] = True
            return await message.reply(f"{em.sukses} Chatbot activated for this group")
        elif subcmd == "off":
            CHATBOT_GROUPS[client_id][chat_id] = False
            return await message.reply(f"{em.gagal} Chatbot turned off for this group")
        elif subcmd == "status":
            is_on = CHATBOT_GROUPS.get(client_id, {}).get(chat_id, False)
            role_text = next(
                (k for k, v in ROLES.items() if v == CHATBOT_ROLE.get(client_id, DEFAULT_ROLE)),
                "custom",
            )
            return await message.reply(
                f"""
{em.sukses} **Chatbot status in this group:** {'Active' if is_on else 'Deactive'}
{em.proses} **Role:** {role_text}
"""
            )

    # ---------- PRIVATE CHAT ----------
    elif chat.type == ChatType.PRIVATE:
        if subcmd == "on":
            CHATBOT_PRIVATE[client_id] = True
            return await message.reply(f"{em.sukses} Chatbot activated for private chat")
        elif subcmd == "off":
            CHATBOT_PRIVATE[client_id] = False
            return await message.reply(f"{em.gagal} Chatbot turned off for private chat")
        elif subcmd == "status":
            is_on = CHATBOT_PRIVATE.get(client_id, False)
            role_text = next(
                (k for k, v in ROLES.items() if v == CHATBOT_ROLE.get(client_id, DEFAULT_ROLE)),
                "custom",
            )
            return await message.reply(
                f"""
{em.sukses} **Chatbot status in private:** {'Active' if is_on else 'Deactive'}
{em.proses} **Role:** {role_text}
"""
            )

    # ---------- SET ROLE ----------
    if subcmd == "role":
        if len(args) < 3:
            text_roles = ", ".join(ROLES.keys())
            return await message.reply(
                f"""
<blockquote expandable>{em.gagal} Please choose role with format:\n
`chatbot role [tipe]`\n
{em.owner} Roles available: `{text_roles}`</blockquote>
"""
            )

        role_name = args[2].lower()
        if role_name not in ROLES:
            return await message.reply(f"{em.gagal} Unknown Role `{role_name}`.")

        CHATBOT_ROLE[client_id] = ROLES[role_name]
        CONVERSATIONS.pop(client_id, None)
        return await message.reply(f"{em.sukses} Chatbot role changed to **{role_name}**")

    else:
        return await message.reply(f"{em.gagal} Unknown argument. use `on/off/role/status`.")


# ---------- HANDLER GROUP ----------
@kelra.on_message(filters.group & ~filters.me & ~filters.bot, group=10)
async def chatbot_handler(client, message):
    em = Emoji(client)
    await em.get()

    chat_id = message.chat.id
    client_id = client.me.id

    if not CHATBOT_GROUPS.get(client_id, {}).get(chat_id, False):
        return

    if message.from_user and message.from_user.is_bot:
        return

    try:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        pass

    user_id = message.from_user.id if message.from_user else message.chat.id
    reply_text = await ai_reply(client_id, message.text, user_id)

    if not reply_text:
        return

    try:
        await message.reply_text(reply_text, quote=True)
    except Exception as e:
        print(f"[Chatbot] ⚠️ Gagal balas pesan: {e}")


# ---------- HANDLER PRIVATE ----------
@kelra.on_message(filters.private & ~filters.me & ~filters.bot, group=11)
async def chatbot_private_handler(client, message):
    em = Emoji(client)
    await em.get()

    client_id = client.me.id

    if not CHATBOT_PRIVATE.get(client_id, False):
        return

    if message.from_user and message.from_user.is_bot:
        return

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    user_id = message.from_user.id if message.from_user else message.chat.id
    reply_text = await ai_reply(client_id, message.text, user_id)

    if not reply_text:
        return

    try:
        await message.reply_text(reply_text, quote=True)
    except Exception as e:
        print(f"[Chatbot] ⚠️ Gagal balas pesan private: {e}")
