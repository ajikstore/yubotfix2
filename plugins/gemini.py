import asyncio
import os

from google import genai
from google.genai import types
from pyrogram.enums import ChatAction
from pyrogram.errors import ChatWriteForbidden

from config import API_GEMINI
from kelra.helpers import CMD, Emoji

__MODULES__ = "Gemini"
__HELP__ = """<blockquote expandable><u>Command Help **Gemini**</u>

    <u>**Chat to gemini**</u>
        `{0}gemini` (prompt)</blockquote>

<b>   {1}</b>
"""
__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

# Inisialisasi Client Gemini Baru
client_gemini = genai.Client(api_key=API_GEMINI)

# Diubah menjadi async agar userbot tidak freeze saat menunggu respon server Google
async def gemini(text):
    try:
        # Menggunakan .aio.models untuk request asynchronous & model terbaru
        response = await client_gemini.aio.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=text,
            config=types.GenerateContentConfig(
                temperature=0.6,
                top_p=1.0,
                top_k=1,
                max_output_tokens=2048,
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    ),
                ]
            )
        )
        if response and response.text:
            return f"{response.text}"
        return "Maaf, tidak ada respon dari AI."
    except Exception as e:
        return f"Error generating text: {str(e)}"


async def mari_kirim(client, message, query):
    em = Emoji(client)
    await em.get()
    try:
        chat_id = message.chat.id
        
        # Eksekusi fungsi gemini secara asynchronous dengan await
        respon = await gemini(query)
        await message._client.send_chat_action(chat_id, ChatAction.TYPING)
        
        # Validasi panjang karakter untuk mencegah limit API Telegram (max 4096)
        if len(respon) > 4096:
            with open("gemini.txt", "wb") as file:
                file.write(respon.encode("utf-8"))
            await message._client.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            await message._client.send_document(chat_id, "gemini.txt", reply_to_message_id=message.id)
            os.remove("gemini.txt")
            return await message._client.send_chat_action(chat_id, ChatAction.CANCEL)
        else:
            # Format bold dihapus dari {respon} agar markdown bawaan Gemini tidak rusak
            await message.reply_text(f"{em.sukses} {respon}", reply_to_message_id=message.id)
            
        return await message._client.send_chat_action(chat_id, ChatAction.CANCEL)
    except ChatWriteForbidden:
        return


@CMD.UBOT("gemini|ai")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(f"{em.gagal} **Please reply to message text or give message!**")
        
    reply_text = client.get_text(message)
    proses_ = await em.get_costum_text()
    
    pros = await message.reply(f"{em.proses}**{proses_[4]}**")
    await mari_kirim(client, message, reply_text)
    
    return await pros.delete()
