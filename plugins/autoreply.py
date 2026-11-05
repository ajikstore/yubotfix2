import asyncio
import random
import time
from openai import AsyncOpenAI
from pyrogram import filters
from pyrogram.enums import ChatType, ChatAction, ChatMemberStatus
from pyrogram.errors import FloodWait

# Import library Gemini versi terbaru
from google import genai
from google.genai import types

from kelra import kelra
from kelra.helpers import CMD, Emoji, Tools

# Pastikan variabel ini sudah ada di config.py kamu
from config import API_BOTCHAX, API_GROQ, GOOGLE_API_KEY

__MODULES__ = "Autoreply"
__HELP__ = """<blockquote>Command Help **Autoreply**</blockquote>
<blockquote expandable>
<u>**Autoreply pengaturan & status**</u>
`{0}autoreply on`
`{0}autoreply off`
`{0}autoreply global on`
`{0}autoreply global off`
`{0}autoreply global status`
`{0}autoreply status`
`{0}autoreply role [tipe]`
</blockquote>
<b>{1}</b>
"""
__CATEGORY__ = "ᴄʜᴀᴛ <emoji id=5215538577496090960>💬</emoji>"

# ================= API SETUP ================
gemini_client = None
if GOOGLE_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Gagal load Gemini Client: {e}")

if API_GROQ:
    groq_client = AsyncOpenAI(api_key=API_GROQ, base_url="https://api.groq.com/openai/v1")

# ================= STORAGE ================
CONVERSATIONS = {}      
AUTOREPLY_GROUPS = {}   
AUTOREPLY_GLOBAL = {}   
AUTOREPLY_IGNORE = {}   
AUTOREPLY_ROLE = {}

# ================= ROLES ==================
DEFAULT_ROLE = """
lu anak tongkrongan yang jutek males tapi kadang ketawa tipis
jawab super pendek satu kalimat aja
semua teks huruf kecil
jangan pake titik koma tanda seru tanda tanya
jangan basa basi jangan nanya balik
kalo orang ngelucu kasih respon 'wkwk' atau 'haha' biar ga kaku
jawaban harus kayak orang yang lagi diganggu dan males bales
PENTING: Jangan selalu pake emoji di setiap balasan! 80% balasan lu harus TEKS POLOS tanpa emoji.
Kalau terpaksa mau pake emoji, variasikan (misal: 💀, 🗿, 🥱, 😭, 🙏), JANGAN PERNAH cuma pakai emoji 😳.
"""

ROLES = {
    "default": DEFAULT_ROLE,
    "formal": "jawab pendek banget dan sopan seadanya, huruf kecil semua tanpa tanda baca, TANPA emoji.",
    "santai": "jawab pendek gaya santai cuek dan ga peduli. 90% teks polos, sesekali aja pake emoji 🗿 atau 🥱.",
    "humoris": "jawab pendek ada selipan candaan tipis. jangan keseringan pake emoji, variasiin pake 😭 atau 💀.",
    "galak": "jawab pendek pedes jutek toxic halus. jangan pake emoji 😳. pake 👎 atau 🗿 aja sesekali.",
    "nyolot": "jawab super pendek ketus sinis males. teks polos aja mending."
}

# ================= AI FUNCTION ==================
async def ai_reply(client_id: int, text: str, user_id: int):
    if client_id not in CONVERSATIONS:
        CONVERSATIONS[client_id] = {}
    if user_id not in CONVERSATIONS[client_id]:
        role_text = AUTOREPLY_ROLE.get(client_id, DEFAULT_ROLE)
        CONVERSATIONS[client_id][user_id] = [{"role": "system", "content": role_text}]
    
    CONVERSATIONS[client_id][user_id].append({"role": "user", "content": text})
    
    if len(CONVERSATIONS[client_id][user_id]) > 6:
        base = CONVERSATIONS[client_id][user_id][:1]
        tail = CONVERSATIONS[client_id][user_id][-5:]
        CONVERSATIONS[client_id][user_id] = base + tail
        
    history_data = CONVERSATIONS[client_id][user_id]

    # 1. COBA GEMINI 
    if gemini_client:
        try:
            gemini_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_data])
            response = await gemini_client.aio.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=gemini_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                    safety_settings=[
                        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
                        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
                        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
                        types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
                    ]
                )
            )
            if response and response.text:
                CONVERSATIONS[client_id][user_id].append({"role": "assistant", "content": response.text})
                return response.text
        except Exception:
            pass 

    # 2. COBA GROQ
    if API_GROQ:
        try:
            completion = await groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=history_data
            )
            result = completion.choices[0].message.content
            if result:
                CONVERSATIONS[client_id][user_id].append({"role": "assistant", "content": result})
                return result
        except Exception:
            pass 

    # 3. COBA BOTCAHX 
    if API_BOTCHAX:
        url = "https://api.botcahx.eu.org/api/search/openai-custom"
        payload = {"message": history_data, "apikey": API_BOTCHAX}
        try:
            data = await Tools.post_json(url, payload)
            if data and "result" in data:
                result = data["result"]
                CONVERSATIONS[client_id][user_id].append({"role": "assistant", "content": result})
                return result
        except Exception:
            pass
            
    return None

# ================= ADMIN CHECK ==================
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# ================= COMMAND ==================
@CMD.UBOT("autoreply")
async def autoreply_cmd(client, message):
    em = Emoji(client)
    await em.get()
    chat = message.chat
    chat_id = chat.id
    client_id = client.me.id
    
    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply(f"{em.gagal} Autoreply hanya untuk grup!")
        
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        return await message.reply(f"{em.gagal} Format salah!\nGunakan: autoreply on/off/status")
        
    subcmd = args[1].lower()
    AUTOREPLY_GROUPS.setdefault(client_id, {})
    AUTOREPLY_GLOBAL.setdefault(client_id, False)
    AUTOREPLY_IGNORE.setdefault(client_id, {})
    AUTOREPLY_ROLE.setdefault(client_id, DEFAULT_ROLE)
    
    if subcmd == "global":
        if len(args) < 3: return await message.reply(f"{em.gagal} Format salah!\nGunakan: autoreply global on/off/status")
        mode = args[2].lower()
        if mode == "on":
            AUTOREPLY_GLOBAL[client_id] = True
            return await message.reply(f"{em.sukses} Autoreply GLOBAL aktif!")
        elif mode == "off":
            AUTOREPLY_GLOBAL[client_id] = False
            return await message.reply(f"{em.gagal} Autoreply GLOBAL dimatikan!")
        elif mode == "status":
            status = AUTOREPLY_GLOBAL.get(client_id, False)
            return await message.reply(f"{em.proses} Global Autoreply: {'Aktif' if status else 'Nonaktif'}")
    elif subcmd == "on":
        AUTOREPLY_GROUPS[client_id][chat_id] = True
        AUTOREPLY_IGNORE[client_id][chat_id] = False
        return await message.reply(f"{em.sukses} Autoreply aktif di grup ini!")
    elif subcmd == "off":
        AUTOREPLY_GROUPS[client_id][chat_id] = False
        AUTOREPLY_IGNORE[client_id][chat_id] = True
        return await message.reply(f"{em.gagal} Autoreply dimatikan di grup ini!")
    elif subcmd == "role":
        if len(args) < 3: return await message.reply(f"{em.gagal} Pilih role!\nAvailable: {', '.join(ROLES.keys())}")        
        role_name = args[2].lower()
        if role_name not in ROLES: return await message.reply(f"{em.gagal} Role tidak dikenal `{role_name}`")
        AUTOREPLY_ROLE[client_id] = ROLES[role_name]
        CONVERSATIONS.pop(client_id, None)
        return await message.reply(f"{em.sukses} Role autoreply diubah menjadi **{role_name}**")
    elif subcmd == "status":
        gr = AUTOREPLY_GROUPS.get(client_id, {}).get(chat_id, False)
        gl = AUTOREPLY_GLOBAL.get(client_id, False)
        return await message.reply(f"{em.sukses} Status Grup: {'Aktif' if gr else 'Nonaktif'}\n{em.proses} Global: {'Aktif' if gl else 'Nonaktif'}")

# ================= HANDLER ==================
@kelra.on_message(filters.group & ~filters.me, group=10)
async def autoreply_handler(client, message):
    if not message.from_user or message.from_user.is_bot: 
        return
    if not message.text: 
        return

    teks = message.text.lower()
    chat_id = message.chat.id
    client_id = client.me.id
    user_id = message.from_user.id
    
    # SYSTEM CHECK
    is_global = AUTOREPLY_GLOBAL.get(client_id, False)
    is_group_on = AUTOREPLY_GROUPS.get(client_id, {}).get(chat_id, False)
    is_ignored = AUTOREPLY_IGNORE.get(client_id, {}).get(chat_id, False)
    
    if is_global and is_ignored: return
    if not is_global and not is_group_on: return
    if message.text.startswith(("/", "!", "#", ".")): return
    if len(teks) < 5 or teks in ["p", "oi", "halo", "test", "wkwk", "haha", "hehe", "hi"]: return
    if await is_admin(client, chat_id, user_id): return

    # FITUR IKLAN & NSFW (Ditambah kosa kata dari screenshot lu)
    keyword_jualan = ["jajan tele", "jualan", "ubot", "jual ubot", "bot", "nokos", "premium", "jual bot"]
    kata_kotor = ["calksex", "sang3", "kuda goyang", "tetek", "vcs", "open bo", "coli", "ngentot", "sange", "bokep", "bugil", "crt", "gede", "toket", "crot", "ngewe", "desah"]
    
    is_promosi = any(kw in teks for kw in keyword_jualan)
    is_kotor = any(kw in teks for kw in kata_kotor)

    # DELAY ACAK INDEPENDEN (Ga pake sistem antrean numpuk lagi. Langsung jeda 2-5 detik per pesan biar ga bikin bot koma)
    await asyncio.sleep(random.uniform(2.0, 5.0))

    # FITUR IKLAN OTOMATIS
    if is_promosi:
        try:
            await message.react(random.choice(["🔥", "🛍", "😎", "👀"]))
            teks_promosi = "mending beli di store keren gua 🛍️ [Gᴀʀғɪᴇʟᴅ Sᴛᴏʀᴇ](https://t.me/storegarf)"
            return await message.reply_text(teks_promosi, quote=True, disable_web_page_preview=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await message.reply_text(teks_promosi, quote=True, disable_web_page_preview=True)
        except Exception:
            return 

    # FITUR ANTI-NSFW
    if is_kotor:
        try:
            await message.react("👎")
            return await message.reply_text("najis lu, tobat woy", quote=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await message.reply_text("najis lu, tobat woy", quote=True)
        except Exception:
            return

    # REACTION ACAK NATURAL 
    if random.random() < 0.25:
        try:
            await message.react(random.choice(["🤔", "👀", "😂", "👍", "🔥", "🗿", "💀", "😭", "🥱", "👎"]))
        except Exception:
            pass

    try: 
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(random.uniform(0.5, 1.5))
    except Exception: 
        pass
        
    # EKSEKUSI AI BACA & BALES
    result = await ai_reply(client_id, message.text, user_id)
    
    # ANTI BISU: Kalau AI nolak jawab gara-gara chatnya aneh/agak nsfw, bot bakal fallback ngasih teks ini daripada diem doang.
    if not result:
        result = random.choice(["au ah gelap", "males mikir gua", "gajelas lu", "skip dlu ngantuk", "pusing gua baca chat lu"])

    # EKSEKUSI KIRIM (Dengan tameng sakti anti FloodWait Telegram)
    try:
        await message.reply_text(result, quote=True)
    except FloodWait as e:
        # Kalau Telegram ngelimit karena terlalu gacor, dia bakal nunggu sesuai waktu limit, terus hajar kirim lagi!
        await asyncio.sleep(e.value + 1)
        try:
            await message.reply_text(result, quote=True)
        except Exception:
            pass
    except Exception:
        pass
