import asyncio
import os
import re
from uuid import uuid4

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Chat, InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls.exceptions import NotInCallError

from config import URL_LOGO, OWNER_ID, SUDO_OWNERS
from kelra import dB, kelra, bot
from kelra.database import state
from kelra.helpers import CMD, Emoji, Tools, YoutubeSearch, gen_qthumb, stream, telegram
from kelra.logger import logger
from pytgcalls.types import AudioQuality, MediaStream, VideoQuality


async def send_music_inline(client, chat_id, thumb_media, caption):
    try:
        if str(thumb_media).startswith("http"):
            photo_url = thumb_media
        else:
            try:
                photo_url = await Tools.upload_thumb(thumb_media)
            except Exception:
                photo_url = URL_LOGO  
            
        state.set(client.me.id, "NOW_PLAYING", {
            "chat_id": chat_id,
            "user_id": client.me.id, 
            "caption": caption,
            "photo_url": photo_url
        })
        
        query_results = await client.get_inline_bot_results(bot.me.username, "inline_music")
        if query_results and query_results.results:
            await client.send_inline_bot_result(
                chat_id, 
                query_results.query_id, 
                query_results.results[0].id
            )
            return True
    except Exception as e:
        logger.error(f"Inline Music Error: {e}")
    
    await client.send_photo(chat_id, photo=thumb_media, caption=caption)


@bot.on_callback_query(filters.regex(r"^(mresume|mpause|mskip|mstop|mplaylist)\|"))
async def music_callback(client, callback):
    data = callback.data.split("|")
    action = data[0]
    chat_id = int(data[1])
    owner_id = int(data[2])

    if callback.from_user.id != owner_id and callback.from_user.id not in SUDO_OWNERS:
        return await callback.answer(f"Gass beli ke ID: {OWNER_ID} 👑", show_alert=True)

    ubot = next((x for x in kelra._ubot if x.me.id == owner_id), None)
    if not ubot:
        return await callback.answer("⚠️ Userbot sedang offline.", show_alert=True)

    try:
        if action == "mpause":
            await ubot.group_call.pause_stream(chat_id)
            await callback.answer("⏸ Paused")
        elif action == "mresume":
            await ubot.group_call.resume_stream(chat_id)
            await callback.answer("▶️ Resumed")
        elif action == "mskip":
            await callback.answer("⏭ Skipping...")
            await skip_songs(ubot, chat_id)
        elif action == "mstop":
            await ubot.group_call.leave_call(chat_id)
            stream.clear_queue(chat_id, ubot.me.id)
            stream.remove_active_call(chat_id, ubot.me.id)
            await callback.answer("⏹ Stopped")
            await callback.message.delete()
        elif action == "mplaylist":
            queue = stream.get_queue(chat_id, ubot.me.id)
            if not queue:
                return await callback.answer("Playlist kosong.", show_alert=True)
            text = "📜 Daftar Putar:\n"
            for i, track in enumerate(queue):
                text += f"{i+1}. {track['song_name']}\n"
            await callback.answer(text[:190], show_alert=True)
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)


@bot.on_callback_query(filters.regex(r"^pselect\|"))
async def play_select_cb(client, callback):
    _, client_id, uniq, index = callback.data.split("|")
    client_id, index = int(client_id), int(index)

    if callback.from_user.id != client_id and callback.from_user.id not in SUDO_OWNERS:
        return await callback.answer(f"Gass beli ke ID: {OWNER_ID} 👑", show_alert=True)

    search_results = state.get(client_id, f"SEARCH_{uniq}")
    song = search_results[index]

    buttons = [
        [
            InlineKeyboardButton("🎧 Audio", callback_data=f"pformat|{client_id}|{uniq}|{index}|Audio"),
            InlineKeyboardButton("🎬 Video", callback_data=f"pformat|{client_id}|{uniq}|{index}|Video")
        ],
        [InlineKeyboardButton("🔙 Kembali", callback_data=f"pback|{client_id}|{uniq}")]
    ]

    await callback.edit_message_text(
        f"🎵 **Lagu Terpilih:** `{song.get('title')}`\n\n🎬 **Silakan pilih format pemutaran:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@bot.on_callback_query(filters.regex(r"^pback\|"))
async def play_back_cb(client, callback):
    _, client_id, uniq = callback.data.split("|")
    client_id = int(client_id)
    
    if callback.from_user.id != client_id and callback.from_user.id not in SUDO_OWNERS:
        return await callback.answer(f"Gass beli ke ID: {OWNER_ID} 👑", show_alert=True)

    search_results = state.get(client_id, f"SEARCH_{uniq}")
    buttons = []
    for i, res in enumerate(search_results):
        title = res.get("title", "Unknown")[:30]
        duration = res.get("duration", "-")
        channel = res.get("channel", "Unknown")[:15]
        button_text = f"{i+1}. {title} | {duration} | {channel}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"pselect|{client_id}|{uniq}|{i}")])
    buttons.append([InlineKeyboardButton("❌ Batal", callback_data=f"close_playsearch|{client_id}")])

    await callback.edit_message_text("🔍 **Silakan pilih lagu yang ingin diputar:**", reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex(r"^close_playsearch"))
async def close_playsearch_cb(client, callback):
    _, client_id = callback.data.split("|")
    if callback.from_user.id != int(client_id) and callback.from_user.id not in SUDO_OWNERS:
        return await callback.answer(f"Gass beli ke ID: {OWNER_ID} 👑", show_alert=True)
    try: await callback.message.delete()
    except: pass


@bot.on_callback_query(filters.regex(r"^pformat\|"))
async def play_format_cb(client, callback):
    _, client_id, uniq, index, fmt = callback.data.split("|")
    client_id, index = int(client_id), int(index)

    if callback.from_user.id != client_id and callback.from_user.id not in SUDO_OWNERS:
        return await callback.answer(f"Gass beli ke ID: {OWNER_ID} 👑", show_alert=True)

    search_results = state.get(client_id, f"SEARCH_{uniq}")
    info = state.get(client_id, f"SINFO_{uniq}")

    if not search_results or not info:
        return await callback.answer("Sesi telah berakhir, silakan cari ulang.", show_alert=True)

    song = search_results[index]
    pros = await callback.edit_message_text(f"⏳ **Memproses {fmt} untuk:** `{song.get('title')}`...")

    ubot = next((x for x in kelra._ubot if x.me.id == client_id), None)
    if not ubot:
        return await pros.edit_message_text("❌ Userbot sedang offline.")

    chat_id = info["chat_id"]
    mode = info["mode"]
    user_mention = info["user_mention"]
    
    media_link = f"https://www.youtube.com{song['url_suffix']}"
    audio_original = media_link
    media_title = song["title"]
    uploade_r = song["channel"]
    dur = song["duration"]
    thumbs = song["thumbnails"][0]
    views = song["views"]
    vidid = song["id"]

    await _process_play(
        ubot=ubot, message=callback.message, pros=pros,
        chat_id=chat_id, mode=mode, user_mention=user_mention, type_media=fmt,
        media_link=media_link, audio_original=audio_original, media_title=media_title,
        uploade_r=uploade_r, dur=dur, thumbs=thumbs, views=views, vidid=vidid,
        callback=callback
    )


__MODULES__ = "Music"
__HELP__ = """<blockquote>Command Help **Music**</blockquote>

<blockquote expandable>        <u>**Basic command**</u>
    <u>**Use `v` for play video**</u>
        `{0}play` (title)
        `{0}vplay` (title)
    <u>**Resume playing**</u>
        `{0}resume`
    <u>**Pause playing**</u>
        `{0}pause`
    <u>**Skip playing**</u>
        `{0}skip`
    <u>**End playing**</u>
        `{0}end`</blockquote>
        
<blockquote expandable>        <u>**Channelplay command**</u>
    <u>**Playing to channel, use `v` for playing video**</u>
        `{0}cplay` (title) 
        `{0}cvplay` title
    <u>**Resume playing channel**</u>
        `{0}cresume`
    <u>**Pause playing channel**</u>
        `{0}cpause`
    <u>**Skip playing channel**</u>
        `{0}cskip`
    <u>**End playing channel**</u>
        `{0}cend`
    <u>**Linked channel to chat**</u>
        `{0}channelplay linked`
    <u>**Disable linked channel**</u>
        `{0}channelplay disable`
    <u>**Check linked playback channel**</u>
        `{0}channelplay status`</blockquote>
    
<blockquote expandable>        <u>**Other command**</u>
    <u>**Set volume playing, then try leave voice chat and join again**</u>
        `{0}volume` (1-200)
    <u>**Get playlist playing now**</u>
        `{0}playlist`</blockquote>
    
<b>   {1}</b>"""


async def format_play_caption(mode, type_media, title, singer, dur, req_id):
    """Format Custom Emoji saat Media berhasil diputar (Sesuai Request)"""
    media_icon = "<emoji id=6089144627833611433>🎬</emoji>" if type_media == "Video" else "<emoji id=6089144627833611433>🎧</emoji>"
    return (
        f"<blockquote expandable>╭──「<u><b><emoji id=6089144627833611433>👑</emoji> {mode} Now Playing {type_media} {media_icon}</b></u>」\n"
        f"│ • <emoji id=5064672027248427816>🎵</emoji> Title: {title}\n"
        f"│ • <emoji id=5199885118214255386>🎤</emoji> Uploader: <u>{singer}</u>\n"
        f"│ • <emoji id=5382194935057372936>⏲️</emoji> Duration: <code>{dur}</code>\n"
        f"╰ • <emoji id=5323788950404346894>👤</emoji> Request: {req_id}</blockquote>"
    )


async def skip_songs(client, chat_id):
    emo = Emoji(client)
    await emo.get()
    
    logo = await Tools.get_logo()
    group_calls = stream.get_active_call(chat_id, client.me.id)
    queue = stream.get_queue(chat_id, client.me.id)

    if not group_calls:
        return await client.send_message(chat_id, f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")

    if not queue or len(queue) <= 1:
        return await client.send_message(chat_id, f"<blockquote>{emo.gagal} <b>Tidak ada track selanjutnya.</b></blockquote>")
        
    pros = await client.send_message(chat_id, f"<blockquote>{emo.proses} <b>Memproses media selanjutnya...</b></blockquote>")
    
    try:
        next_song = stream.skip(chat_id, client.me.id)
        
        mode_ = next_song["mode"]
        type_ = next_song["media_type"]
        name_ = next_song["song_name"]
        singer_ = next_song["singer"]
        dur = next_song["dur"]
        media_link = next_song["url"]
        thumb_ = next_song["thumb"]
        file_path = next_song["file_name"]
        title_song = f'<a href="{media_link}">{name_}</a>'
        req_id = f"<a href='tg://user?id={client.me.id}'>{client.me.first_name} {client.me.last_name or ''}</a>"

        try:
            streaming = await stream.run_stream(file_path, type_)
            await client.group_call.play(chat_id, streaming)
        except Exception as e:
            return await pros.edit(f"<blockquote>{emo.gagal} <b>Gagal memutar track selanjutnya: {str(e)}</b></blockquote>")
            
        try:
            teks_caption = await format_play_caption(mode_, type_, title_song, singer_, dur, req_id)
            await send_music_inline(client, chat_id, thumb_ if thumb_ else logo, teks_caption)
            await pros.delete()
        except Exception as e:
            await pros.edit(f"<blockquote>{emo.gagal} <b>Gagal mengirim info:</b>\n<code>{str(e)}</code></blockquote>")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(thumb_):
                os.remove(thumb_)
                
    except Exception as e:
        await pros.edit(f"<blockquote>{emo.gagal} <b>Gagal melompati lagu:</b>\n<code>{str(e)}</code></blockquote>")

def build_header(icon: str, title: str) -> str:
    return "<blockquote>┏━━━━━━━━━━━━━━━━━━━━━\n" f"  {icon} {title}\n" "┗━━━━━━━━━━━━━━━━━━━━━</blockquote>\n"

@kelra.group_call_logs()
async def _(client, update):
    return await group_call_ends(client, update)

async def group_call_ends(client, update):
    clientbot = client.mtproto_client
    user_id = clientbot.me.id
    update_chat_id = update.chat_id
    try:
        group_calls_data = stream.get_active_call(update_chat_id, user_id)
        if not isinstance(group_calls_data, tuple) or len(group_calls_data) != 2:
            raise ValueError("Invalid group_calls_data format")
    except Exception as e:
        return

    c, m = group_calls_data
    play_list = stream.get_queue(m.chat.id, c.me.id)

    if not play_list or len(play_list) <= 1:
        emo = Emoji(c)
        await emo.get()
        stream.clear_queue(m.chat.id, c.me.id)
        stream.remove_active_call(m.chat.id, c.me.id)
        await client.leave_call(update_chat_id)
        try:
            text = build_header(
                f"{emo.block}",
                f"<b>Stream Ended on {m.chat.title or m.chat.id}</b>\n<b>The playlist has ended.</b>\n<i>Leaving the call quietly..</i>",
            )
            sent = await c.send_message(m.chat.id, text)
            await asyncio.sleep(5)
            return await sent.delete()
        except Exception as e:
            return

    try:
        return await skip_songs(c, m.chat.id)
    except Exception as e:
        logger.error(f"[VC] Error while skipping: {e}")
        return


async def _process_play(ubot, message, pros, chat_id, mode, user_mention, type_media, media_link, audio_original, media_title, uploade_r, dur, thumbs, views, vidid, callback=None):
    emo = Emoji(ubot)
    await emo.get()

    data = {
        "title": media_title,
        "duration": dur,
        "thumbnail": thumbs,
        "views": views,
        "channel": uploade_r,
    }
    state.set(ubot.me.id, "GEN_THUMB", data)
    thumb_media = await gen_qthumb(ubot, vidid)

    jadul = f"<a href='{media_link}'>{media_title}</a>"
    f_info = {
        "song_name": media_title,
        "file_name": audio_original,
        "singer": uploade_r,
        "dur": dur,
        "url": media_link,
        "thumb": thumb_media,
        "mode": mode,
        "media_type": type_media,
    }
    
    group_calls = stream.get_active_call(chat_id, ubot.me.id)
    
    if not group_calls:
        streaming = await stream.run_stream(audio_original, type_media)
        await ubot.group_call.play(chat_id, streaming)
        stream.add_active_call(chat_id, ubot.me.id, ubot, message)
        stream.add_to_queue(chat_id, ubot.me.id, f_info)
        durations_to_min = dur
        
        try:
            teks_caption = await format_play_caption(mode, type_media, jadul, uploade_r, durations_to_min, user_mention)
            await send_music_inline(ubot, chat_id, thumb_media, teks_caption)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
            teks_caption = await format_play_caption(mode, type_media, jadul, uploade_r, durations_to_min, user_mention)
            await send_music_inline(ubot, chat_id, thumb_media, teks_caption)
        except Exception as e:
            logger.error(f"Error Thumb: {str(e)}")
            await pros.reply(
                await format_play_caption(mode, type_media, jadul, uploade_r, durations_to_min, user_mention),
                disable_web_page_preview=True,
            )
            
        try: 
            if hasattr(pros, "delete") and not isinstance(pros, bool):
                await pros.delete()
            elif callback:
                anu = await callback.edit_message_text(
                    f"<blockquote><b>🎧 Now Playing:</b> {jadul}</blockquote>",
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.3)
                pass
        except Exception as e:
            logger.error(f"[Cleanup Error] {e}")
            
    else:
        stream.add_to_queue(chat_id, ubot.me.id, f_info)
        data_q = stream.get_queue(chat_id, ubot.me.id)
        try:
            if hasattr(pros, "edit") and not isinstance(pros, bool):
                await pros.edit(
                    f"<blockquote expandable>{emo.sukses} <b>Added to queue #{len(data_q)}:</b> {jadul} | {type_media}</blockquote>",
                    disable_web_page_preview=True,
                )
            elif callback:
                await callback.edit_message_text(
                    f"<blockquote expandable>{emo.sukses} <b>Added to queue #{len(data_q)}:</b> {jadul} | {type_media}</blockquote>",
                    disable_web_page_preview=True,
                )
        except: 
            pass


@CMD.UBOT("play|vplay|cplay|cvplay")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()
    
    pref = client.get_prefix(client.me.id)
    x = next(iter(pref), None)
    rep = message.reply_to_message
    
    if len(message.command) < 2 and not rep:
        return await message.reply(f"<blockquote expandable>{emo.gagal} <b>Gunakan perintah ini dengan membalas Musik, Video, atau masukkan judul/link Youtube.</b></blockquote>")

    pros = await message.reply(f"<blockquote expandable>{emo.proses} <b>Memproses media..</b></blockquote>")

    user_mention = message.sender_chat.title if message.sender_chat else message.from_user.mention
    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c") or cmd.startswith("cv")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    as_video = cmd.startswith("v") or cmd.startswith("cv")
    type_media = "Video" if as_video else "Audio"
    
    if is_channel_mode:
        chat = await dB.get_var(client.me.id, "CHANNEL")
        if not chat:
            return await pros.edit(f"<blockquote expandable>{emo.gagal} <b>Channel belum dihubungkan!\nGunakan: <code>{x}channelplay linked</code></b></blockquote>")

    mode = "Channel" if is_channel_mode or message.sender_chat else "Group"
    duration_limit = 5500000000
    size_limit = 2147483648
    
    audio_telegram = (rep.audio or rep.voice) if rep else None
    video_telegram = (rep.video or rep.document) if rep else None
    
    if audio_telegram or video_telegram:
        try:
            await pros.edit(f"<blockquote expandable>{emo.proses} <b>Mendownload media Telegram ..</b></blockquote>")
            if audio_telegram:
                type_media = "Audio"
                if audio_telegram.file_size > size_limit: 
                    return await pros.edit(f"{emo.gagal} Audio terlalu besar!")
                file_path = await telegram.get_filepath(audio=audio_telegram)
                await telegram.download(client, message, pros, file_path)
                media_title = await telegram.get_filename(audio_telegram, audio=True)
                dur = await telegram.get_duration(audio_telegram, file_path)
                file = await client.download_media(rep.audio.thumbs[-1].file_id) if getattr(rep.audio, "thumbs", None) else None
            else:
                type_media = "Video"
                if video_telegram.file_size > size_limit: 
                    return await pros.edit(f"{emo.gagal} Video terlalu besar!")
                file_path = await telegram.get_filepath(video=video_telegram)
                await telegram.download(client, message, pros, file_path)
                media_title = await telegram.get_filename(video_telegram)
                dur = await telegram.get_duration(video_telegram, file_path)
                file = await client.download_media(rep.video.thumbs[-1].file_id) if getattr(rep.video, "thumbs", None) else None

            thumbs = await Tools.upload_thumb(file) if file else URL_LOGO
            vidid = int(uuid4())
            views = Tools.gen_views()
            
            await _process_play(
                ubot=client, message=message, pros=pros, chat_id=chat_id, mode=mode,
                user_mention=user_mention, type_media=type_media, media_link=f"[Here]({rep.link})",
                audio_original=file_path, media_title=media_title, uploade_r="Telegram User",
                dur=dur, thumbs=thumbs, views=views, vidid=vidid
            )
        except Exception as e:
            return await pros.edit(f"<blockquote>{emo.gagal} <b>Gagal memproses media Telegram:</b>\n<code>{str(e)}</code></blockquote>")

    else:
        gt_txt = client.get_text(message)
        if re.match(r"^https?://", gt_txt):
            try:
                await pros.edit(f"<blockquote expandable>{emo.proses} <b>Menganalisis Link YouTube..</b></blockquote>")
                yt_search = YoutubeSearch(gt_txt, max_results=1)
                await yt_search.fetch_results()
                
                media_link = yt_search.get_link()
                audio_original = media_link
                media_title = yt_search.get_title()
                uploade_r = yt_search.get_channel()
                dur = yt_search.get_duration()
                thumbs = yt_search.get_thumbnail()
                views = yt_search.get_views()
                vidid = yt_search.get_id()
                
                await _process_play(
                    ubot=client, message=message, pros=pros, chat_id=chat_id, mode=mode,
                    user_mention=user_mention, type_media=type_media, media_link=media_link,
                    audio_original=audio_original, media_title=media_title, uploade_r=uploade_r,
                    dur=dur, thumbs=thumbs, views=views, vidid=vidid
                )
            except Exception as e:
                return await pros.edit(f"<blockquote>{emo.gagal} <b>Gagal memproses YouTube Link:</b>\n<code>{str(e)}</code></blockquote>")
        else:
            try:
                await pros.edit(f"<blockquote>{emo.proses} <b>Mencari hasil untuk:</b> <code>{gt_txt}</code>...</blockquote>")
                yt_search = YoutubeSearch(gt_txt, max_results=5)
                await yt_search.fetch_results()
                results = yt_search.to_dict(clear_cache=False)

                if not results:
                    return await pros.edit(f"<blockquote>{emo.gagal} <b>Pencarian tidak ditemukan!</b></blockquote>")

                uniq = str(uuid4())[:8]
                
                state.set(client.me.id, f"SEARCH_{uniq}", results)
                state.set(client.me.id, f"SINFO_{uniq}", {
                    "chat_id": chat_id,
                    "mode": mode,
                    "user_mention": user_mention
                })

                from kelra.helpers import ButtonUtils
                query = f"inline_playsearch {client.me.id} {uniq}"
                inline = await ButtonUtils.send_inline_bot_result(message, chat_id, bot.me.username, query)
                
                if inline:
                    await pros.delete()
                else:
                    await pros.edit(f"{emo.gagal} Gagal memuat menu pencarian (Inline Bot Error).")

            except Exception as e:
                return await pros.edit(f"<blockquote>{emo.gagal} <b>Pencarian Gagal:</b>\n<code>{str(e)}</code></blockquote>")


@CMD.UBOT("resume|cresume")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    group_calls = stream.get_active_call(chat_id, client.me.id)
    
    if not group_calls:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar. </b></blockquote>")
        
    queue = stream.get_queue(chat_id, client.me.id)
    current_media = queue[0]
    
    resumed = "<blockquote expandable><b>   「 ▶️ Melanjutkan pemutaran:」</b>\n"
    resumed += f" 🎵 Judul: <code>{current_media['song_name']}</code>\n"
    resumed += f" 🎤 Penyanyi: <code>{current_media['singer']}</code>\n"
    resumed += f"╰ • ⏲️ Durasi: <code>{current_media['dur']}</code></b>\n</blockquote>"
    
    try:
        await client.group_call.resume_stream(chat_id)
        return await message.reply(resumed)
    except Exception as e:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Gagal melanjutkan media:</b>\n<code>{str(e)}</code></blockquote>")


@CMD.UBOT("end|cend")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    group_calls = stream.get_active_call(chat_id, client.me.id)
    
    if not group_calls:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")
        
    try:
        await client.group_call.leave_call(chat_id)
        stream.clear_queue(chat_id, client.me.id)
        stream.remove_active_call(chat_id, client.me.id)
        return await message.reply(f"<blockquote>{emo.sukses} <b>Pemutaran dihentikan.</b></blockquote>")
    except NotInCallError:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")
    except Exception as e:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Gagal menghentikan media:\n<code>{str(e)}</code></b></blockquote>")


@CMD.UBOT("pause|cpause")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    group_calls = stream.get_active_call(chat_id, client.me.id)
    
    if not group_calls:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")
        
    queue = stream.get_queue(chat_id, client.me.id)
    current_media = queue[0]
    
    paused = "<blockquote expandable><b>   「 ⏸ Jeda pemutaran:」</b>\n"
    paused += f" 🎵 Judul: <code>{current_media['song_name']}</code>\n"
    paused += f" 🎤 Penyanyi: <code>{current_media['singer']}</code>\n"
    paused += f"╰ • ⏲️ Durasi: <code>{current_media['dur']}</code></b>\n</blockquote>"
    
    try:
        await client.group_call.pause_stream(chat_id)
        return await message.reply(paused)
    except Exception as e:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Gagal menjeda media:</b>\n<code>{e}</code></blockquote>")


@CMD.UBOT("skip|cskip")
async def _(client, message):
    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    
    await skip_songs(client, chat_id)


@CMD.UBOT("playlist|cplaylist")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    logo = await Tools.get_logo()
    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    group_calls = stream.get_active_call(chat_id, client.me.id)
    
    if not group_calls:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")

    pros = await message.reply(f"<blockquote>{emo.proses} <b>Mengambil playlist...</b></blockquote>")

    current_media, next_media_list = stream.get_current_and_next_media(chat_id, client.me.id)
    if not current_media:
        return await pros.edit(f"<blockquote>{emo.gagal} <b>Antrean kosong.</b></blockquote>")

    playlist = "<blockquote expandable><b>   「 🎧 Sedang Diputar:」</b>\n"
    playlist += f" 🎵 Judul: <code>{current_media['song_name']}</code>\n"
    playlist += f" 🎤 Penyanyi: <code>{current_media['singer']}</code>\n"
    playlist += f"╰ • ⏲️ Durasi: <code>{current_media['dur']}</code>\n\n"

    if next_media_list:
        playlist += "<b>   「 📜 Daftar Putar Berikutnya:」</b>\n"
        for count, track in enumerate(next_media_list, start=1):
            if count == len(next_media_list):
                playlist += f"╰ • <code>{track['song_name']}</code>\n"
            else:
                playlist += f" ├ <code>{track['song_name']}</code>\n"
    playlist += "</blockquote>"
    
    try:
        await message.reply_photo(
            photo=current_media.get("thumb", logo),
            caption=playlist,
        )
        return await pros.delete()
    except Exception as e:
        return await pros.edit(playlist)


@CMD.UBOT("volume|cvolume")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    cmd = message.command[0].lower()
    is_channel_mode = cmd.startswith("c")
    chat_id = await dB.get_var(client.me.id, "CHANNEL") if is_channel_mode else message.chat.id
    nilai = client.get_text(message)
    
    if not nilai:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Masukkan angka 1 - 200 untuk mengubah volume.</b></blockquote>")
        
    group_calls = stream.get_active_call(chat_id, client.me.id)
    if not group_calls:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada media yang diputar.</b></blockquote>")
        
    try:
        await client.group_call.change_volume_call(chat_id, int(nilai))
        return await message.reply(f"<blockquote>{emo.sukses} <b>Volume diubah menjadi: <code>{nilai}%</code></b></blockquote>")
    except Exception as e:
        if "USER_VOLUME_INVALID" in str(e):
            return await message.reply(f"<blockquote>{emo.gagal} <b>Masukkan angka 1 - 200 untuk mengubah volume.</b></blockquote>")
        return await message.reply(f"<blockquote>{emo.gagal} <b>Gagal mengatur volume:\n<code>{str(e)}</code></b></blockquote>")


@CMD.UBOT("channelplay")
async def _(client, message):
    emo = Emoji(client)
    await emo.get()

    pref = client.get_prefix(client.me.id)
    x = next(iter(pref))
    
    if len(message.command) not in [2, 3]:
        return await message.reply(
            f"<blockquote expandable>{emo.warn} <b>Tautkan channel dengan obrolan ini.\n\nGunakan: <code>{x}channelplay linked</code></b></blockquote>"
        )
        
    query = message.text.split(None, 2)[1].lower().strip()
    
    if str(query) == "disable":
        await dB.remove_var(client.me.id, "CHANNEL")
        return await message.reply(f"<blockquote>{emo.sukses} <b>Pemutaran melalui channel dinonaktifkan.</b></blockquote>")

    elif str(query) == "linked":
        try:
            chat = await client.get_chat(message.chat.id)
        except Exception as e:
            return await message.reply(f"<blockquote>{emo.gagal} <b>Error:\n<code>{str(e)}</code></b></blockquote>")

        if chat and chat.linked_chat:
            channel_id = chat.linked_chat.id
            try:
                members = await client.get_chat_member(channel_id, client.me.id)
                if not members.privileges.can_manage_video_chats:
                    return await message.reply(f"<blockquote>{emo.gagal} <b>Jadikan saya admin dengan hak Voice Chat di Channel tersebut.</b></blockquote>")
                await dB.set_var(client.me.id, "CHANNEL", channel_id)
                return await message.reply(f"<blockquote>{emo.sukses} <b>Berhasil mengatur {chat.linked_chat.title} sebagai channel pemutaran.</b></blockquote>")
            except Exception as e:
                return await message.reply(f"<blockquote>{emo.gagal} <b>Error:\n<code>{e}</code></b></blockquote>")
        else:
            if len(message.command) < 3:
                return await message.reply(f"<blockquote>{emo.gagal} **Channel tidak terhubung, gunakan: `{message.text.split()[0]} linked` (username channel)**</blockquote>")
            chat_id = message.text.split()[2]
            try:
                if "/+" in str(chat_id) or "t.me/" in str(chat_id) or "@" in str(chat_id):
                    chat_id = chat_id.replace("https://t.me/", "")
                    gid = await client.get_chat(str(chat_id))
                    chat_id = int(gid.id)
                else:
                    chat_id = int(chat_id)
                await dB.set_var(client.me.id, "CHANNEL", chat_id)
                return await message.reply(f"<blockquote>{emo.sukses} <b>Berhasil mengatur channel sebagai media pemutaran.</b></blockquote>")
            except Exception as err:
                return await message.reply(f"<blockquote>{emo.gagal} <b>Gagal menghubungkan channel\nError: `{str(err)}`</b></blockquote>")

    elif str(query) == "status":
        mode = await dB.get_var(client.me.id, "CHANNEL")
        if not mode:
            return await message.reply(f"<blockquote>{emo.gagal} <b>Tidak ada channel yang terhubung.</b></blockquote>")
        else:
            try:
                chat = await client.get_chat(int(mode))
                return await message.reply(f"<blockquote>{emo.sukses} <b>Grup {message.chat.title} terhubung ke:</b> {chat.title}</blockquote>")
            except Exception as e:
                return await message.reply(f"<blockquote>{emo.gagal} <b>Error:\n<code>{str(e)}</code></b></blockquote>")

    else:
        return await message.reply(f"<blockquote>{emo.gagal} <b>Query tidak valid!</b></blockquote>")
    
