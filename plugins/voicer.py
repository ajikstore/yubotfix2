import os
import subprocess
import gtts
import speech_recognition as sr
from config import API_BOTCHAX
from kelra.helpers import CMD, Emoji, Tools
from pyrogram import enums

__MODULES__ = "Voice"
__HELP__ = """<blockquote>Command Help **Voice**</blockquote>

<blockquote expandable>        <u>**Send text to voice**</u>
    <u>**You can convert text to voice**</u>
        `{0}tts` (text/reply text)

        <u>**Get text from voice**</u>
    <u>**You can convert text from voice**</u>
        `{0}stt` (reply audio)

        <u>**Extract instruments**</u>
    <u>**You can extract instruments from media**</u>
        `{0}vremover` (reply audio)</blockquote>

<b>   {1}</b>
"""

__CATEGORY__ = "ᴛᴏᴏʟs <emoji id=5435961551871813164>🛠</emoji>"

@CMD.UBOT("vremover")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    prs = await message.reply_text(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    rep = message.reply_to_message or message
    if not rep or not (rep.audio or rep.video):
        return await prs.edit(f"<blockquote>{em.gagal}**Please reply to audio or video!!**</blockquote>")
    arg = await Tools.upload_media(message)
    url = f"https://api.botcahx.eu.org/api/tools/voiceremover?url={arg}&apikey={API_BOTCHAX}"
    respon = await Tools.fetch.get(url)
    ex = await message.reply(f"<blockquote>{em.proses}**Try to extract of instruments...**</blockquote>")

    if respon.status_code == 200:
        data = respon.json()["result"]
        try:
            await prs.delete()
            voice = data["vocal_path"]
            audio = data["instrumental_path"]
            send_voice = await client.send_audio(message.chat.id, voice, caption=f"<b>Vocal</b>")
            send_audio = await client.send_audio(message.chat.id, audio, caption=f"<b>Instruments</b>")
            await ex.delete()
            caption_text = (
                f"{em.sukses}<blockquote>**Status error:** {data['error']}\n"
                f"**Status message:** {data['message']}\n"
                f"**Vocal of the <a href='{rep.link}'>media</a>:** <a href='{send_voice.link}'>here</a>\n"
                f"**Instruments of the <a href='{rep.link}'>media</a>:** <a href='{send_audio.link}'>here</a></blockquote>"
            )
            return await message.reply(caption_text, disable_web_page_preview=True)
        except Exception as er:
            await ex.delete()
            return await message.reply(f"<blockquote>{em.gagal}**ERROR:** {str(er)}</blockquote>")
    else:
        return await message.reply(f"<blockquote>**{em.gagal}Please try again: {respon.status_code}!**</blockquote>")


@CMD.UBOT("tts")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()

    pros = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    bhs = await client.get_translate()
    if message.reply_to_message:
        kata = message.reply_to_message.text or message.reply_to_message.caption
    else:
        if len(message.command) < 2:
            return await pros.edit(f"<blockquote>{em.gagal}**Please reply to message text or give text!**</blockquote>")
        else:
            kata = message.text.split(None, 1)[1]
    gts = gtts.gTTS(kata, lang=bhs)
    gts.save("trs.oog")
    rep = message.reply_to_message or message
    try:
        await client.send_voice(
            chat_id=message.chat.id,
            voice="trs.oog",
            reply_to_message_id=rep.id,
        )
        await pros.delete()
        os.remove("trs.oog")
        return
    except Exception as er:
        return await pros.edit(f"<blockquote>{em.gagal}**Error: {str(er)}</blockquote>**")


@CMD.UBOT("stt")
async def _(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"<blockquote>{em.proses}**{proses_[4]}**</blockquote>")
    reply = message.reply_to_message
    
    if not reply or not (reply.voice or reply.audio):
        return await proses.edit(f"<blockquote>{em.gagal}**Please reply to a voice message or audio!**</blockquote>")

    try:
        file_path = await reply.download()
        wav_path = file_path + ".wav"
        
        proc = subprocess.run(
            ["ffmpeg", "-i", file_path, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav_path, "-y"],
            capture_output=True, text=True
        )
        
        if proc.returncode != 0:
            return await proses.edit(f"<blockquote>{em.gagal}**FFmpeg Error:** <code>{proc.stderr[:50]}</code></blockquote>")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="id-ID")
            
            result_text = (
                f"<blockquote><b>╭──「 <emoji id=5317374828695628623>🔊</emoji> HASIL KONVERSI </b>\n"
                f"<b>│</b>\n"
                f"<b>│ Teks:</b> <i>{text}</i>\n"
                f"<b>╰──</b></blockquote>"
            )
            await client.send_message(message.chat.id, result_text, parse_mode=enums.ParseMode.HTML)
            await proses.delete()

    except sr.UnknownValueError:
        await proses.edit(f"<blockquote><emoji id=5382194935057372936>❌</emoji> <b>Suara tidak jelas (UnknownValue)!</b></blockquote>")
    except Exception as e:
        await proses.edit(f"<blockquote><emoji id=5382194935057372936>❌</emoji> <b>Error:</b> <code>{str(e)}</code></blockquote>")
    finally:
        if os.path.exists(wav_path): os.remove(wav_path)
        if os.path.exists(file_path): os.remove(file_path)
