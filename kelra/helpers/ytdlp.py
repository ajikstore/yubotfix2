import asyncio
import functools
import glob
import json
import multiprocessing
import os
import random
import time
import traceback
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from math import floor
from typing import Union
from urllib.parse import parse_qs, urlparse

import httpx
import yt_dlp
from pyrogram.errors import FloodWait
from pyrogram.types import Voice
from pytgcalls.types import AudioQuality, MediaStream, VideoQuality

from config import BOT_ID, BOT_NAME
from kelra.logger import logger

from .tools import Tools

max_workers = multiprocessing.cpu_count() * 2
exc_ = ThreadPoolExecutor(max_workers=max_workers)
lyrical = {}
downloader = {}

lyrical = {}
queues = {}
demus_data = {}
streaming_data = {}
downloader = {}


cookies_yt = "storage/cookies/cookies.txt"


def clean_youtube_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def cookies():
    folder_path = f"{os.getcwd()}/storage/cookies"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return f"""storage/cookies/{str(cookie_txt_file).split("/")[-1]}"""


class StreamingTools:
    play_text = """ 
<blockquote expandable>╭──「<u><b><emoji id=5260268501515377807>🎼</emoji>{} Now Playing {} <emoji id={}>🎶</emoji></b></u>」

<b>│ • <emoji id=5260348422266822411>🎵</emoji> Title: {}</b>
<b>│ • <emoji id=5260652149469094137>🎤</emoji> Uploader: <u>{}</u></b>
<b>│ • <emoji id=5258258882022612173>⏲️️</emoji> Duration: <code>{}</code></b>
<b>╰ • <emoji id=5316727448644103237>📩</emoji> Request: {}</b></blockquote>"""

    def __init__(self):
        self.active_calls = {}
        self.queue = {}

    async def run_stream(self, link, media_type):
        url = clean_youtube_url(link)
        ydl_params = f"--cookies {cookies_yt} -f {url} --extractor-args 'youtubetab:skip=authcheck'"
        stream_kwargs = {
            "media_path": url,
            "audio_parameters": AudioQuality.MEDIUM,
            "ytdlp_parameters": ydl_params,
        }

        if media_type == "Video":
            stream_kwargs["video_parameters"] = VideoQuality.SD_480p
        else:
            stream_kwargs["video_flags"] = MediaStream.Flags.IGNORE

        return MediaStream(**stream_kwargs)

    def get_active_call(self, chat_id, user_id):
        return self.active_calls.get((chat_id, user_id))

    def add_active_call(self, chat_id, user_id, group_call, message):
        self.active_calls[(chat_id, user_id)] = (group_call, message)

    def is_active_call(self, chat_id, user_id):
        return (chat_id, user_id) in self.active_calls

    def remove_active_call(self, chat_id, user_id):
        self.active_calls.pop((chat_id, user_id), None)

    def get_queue(self, chat_id, user_id):
        return self.queue.get((chat_id, user_id), [])

    def add_to_queue(self, chat_id, user_id, media_info):
        self.queue.setdefault((chat_id, user_id), []).append(media_info)

    def clear_queue(self, chat_id, user_id):
        queue = self.queue.pop((chat_id, user_id), [])
        for item in queue:
            self._delete_file_if_exists(item.get("file_path"))

    def skip(self, chat_id, user_id):
        queue = self.get_queue(chat_id, user_id)
        if queue:
            current = queue.pop(0)
            self._delete_file_if_exists(current.get("file_path"))
            return queue[0] if queue else None
        return None

    def endm(self, chat_id, user_id):
        self.clear_queue(chat_id, user_id)
        self.remove_active_call(chat_id, user_id)

    def get_current_and_next_media(self, chat_id, user_id):
        queue = self.get_queue(chat_id, user_id)
        return (queue[0], queue[1:]) if queue else (None, [])

    def _delete_file_if_exists(self, path):
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Failed to delete {path}: {e}")

    @staticmethod
    def seconds_to_min(seconds):
        if seconds is None:
            return "-"
        seconds = int(seconds)
        d, h, m, s = (
            seconds // 86400,
            (seconds // 3600) % 24,
            (seconds % 3600) // 60,
            seconds % 60,
        )
        if d > 0:
            return f"{d:02}:{h:02}:{m:02}:{s:02}"
        elif h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"


stream = StreamingTools()


class YoutubeAPI:
    bar_characters = ["𖢨", "𖤊", "𖦹", "𖥞", "𖥕", "𖥚", "𖤞", "𖣵", "𖣠", "𖣨"]

    def __init__(self):
        self.last_percent = 0

    async def download(self, url: str, as_video: bool = False):
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "ignore_no_formats_error": False,
            "extract_flat": False,
            "cachedir": False,
            "noprogress": True,
            "cookiefile": cookies(),
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "extractor_args": {"youtubetab": ["skip=authcheck", "flat=1"]},
        }

        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]" if as_video else "bestaudio[ext=m4a]"

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        link = clean_youtube_url(url)
        ytdl_data = await self.run_sync(ydl.extract_info, link, download=True)

        file_name = ydl.prepare_filename(ytdl_data)
        inpoh = "Video" if as_video else "Audio"
        videoid = ytdl_data.get("id")
        title = ytdl_data.get("title")
        url = f"https://youtu.be/{videoid}"
        duration = int(ytdl_data.get("duration", 0))
        channel = ytdl_data.get("uploader", "Unknown")
        views = f"{ytdl_data.get('view_count', 0):,}".replace(",", ".")
        thumb = f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg"

        caption = f"""
<blockquote expandable><b>╝──「💡 Information {inpoh}」</b>
│ • 🏇 Title: <code>{title}</code>
│ • 🛍 Duration: <code>{Tools.get_readable_time(duration)}</code>
│ • 👀 Views: <code>{views}</code> views
│ • 📢 Channel: <code>{channel}</code>
│ • 🔗 Link: <a href='{link}'>Youtube</a>
╚ • ⚡ Downloaded By: <a href="tg://openmessage?user_id={BOT_ID}">{BOT_NAME}</a></blockquote>"""

        return file_name, inpoh, title, duration, views, channel, link, thumb, caption

    def run_sync(self, func, *args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, functools.partial(func, *args, **kwargs))

    async def progress(self, current, total, pros, mulai, operasi, nama_file):
        percent = current * 100 / total
        if floor(percent) >= self.last_percent + random.randint(17, 25) or floor(percent) == 100:
            now = time.time()
            self.last_percent = floor(percent)
            kecepatan = current / max(1, now - mulai)
            sisa_waktu = (total - current) / max(1, kecepatan)
            progress_bar = self.generate_progress_bar(floor(percent))

            teks_progress = f"""
<blockquote expandable><b> • {operasi}</b>
│ • 📂 <code>{nama_file}</code>
│ • 📊 <b>Progress</b>: {progress_bar} <code>{floor(percent)}%</code>
│ • 🚀 <b>Speed</b>: <code>{self.humanbytes(kecepatan)}/s</code>
│ • ⏳ <b>Remaining</b>: <code>{self.human_time(sisa_waktu)}</code>
╚ • 📀 <b>Downloaded</b>: <code>{self.humanbytes(current)}</code> / <code>{self.humanbytes(total)}</code></blockquote>"""
            try:
                await pros.edit(teks_progress)
                await asyncio.sleep(2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await self.progress(current, total, pros, mulai, operasi, nama_file)

    def generate_progress_bar(self, percent):
        bar_length = 10
        filled_length = floor(bar_length * percent / 100)
        bar = "".join(random.choices(self.bar_characters, k=filled_length))
        empty_space = "•" * (bar_length - filled_length)
        return f"[{bar}{empty_space}]"

    def humanbytes(self, size):
        if not size:
            return "0 B"
        power = 2**10
        n = 0
        while size > power:
            size /= power
            n += 1
        units = ["B", "KB", "MB", "GB", "TB"]
        return f"{round(size, 2)} {units[n]}"

    def human_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        parts = [
            f"{d}d" if d else "",
            f"{h}h" if h else "",
            f"{m}m" if m else "",
            f"{s}s" if s else "",
        ]
        return ", ".join(filter(None, parts))


youtube = YoutubeAPI()


class TelegramAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = 5

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x, disable_web_page_preview=True)
        return True

    async def get_link(self, message):
        return message.link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            file_name = file.file_name
            if file_name is None:
                file_name = "Audio Telegram" if audio else "Video Telegram"
        except Exception:
            file_name = "Audio Telegram" if audio else "Video Telegram"
        return file_name

    async def get_duration(self, filex, file_path):
        try:
            dur = Tools.seconds_to_min(filex.duration)
        except Exception:
            try:
                dur = youtube.run_sync(None, Tools.check_duration, file_path)
                dur = Tools.seconds_to_min(dur)
            except Exception:
                return "Unknown"
        return dur

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        if audio:
            try:
                file_name = audio.file_unique_id + "." + ((audio.file_name.split(".")[-1]) if (not isinstance(audio, Voice)) else "ogg")
            except Exception as e:
                logger.error(f"Error Get File Path Audio: {e}")
                file_name = audio.file_unique_id + "." + ".ogg"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        if video:
            try:
                file_name = video.file_unique_id + "." + (video.file_name.split(".")[-1])
            except Exception as e:
                logger.error(f"Error Get File Path Video: {e}")
                file_name = video.file_unique_id + "." + "mp4"
            file_name = os.path.join(os.path.realpath("downloads"), file_name)
        return file_name

    async def download(self, client, message, pros, fname):
        try:
            left_time = {}
            speed_counter = {}
            if os.path.exists(fname):
                return True

            async def down_load():
                async def progress(current, total):
                    if current == total:
                        return
                    current_time = time.time()
                    start_time = speed_counter.get(message.id)
                    check_time = current_time - start_time
                    if datetime.now() > left_time.get(message.id):
                        percentage = current * 100 / total
                        percentage = str(round(percentage, 2))
                        speed = current / check_time
                        eta = int((total - current) / speed)
                        downloader[message.id] = eta
                        eta = Tools.get_readable_time(eta)
                        if not eta:
                            eta = "0 sec"
                        total_size = Tools.convert_bytes(total)
                        completed_size = Tools.convert_bytes(current)
                        speed = Tools.convert_bytes(speed)
                        text = f"""
    **{client.me.mention} Telegram Media Downloader**

    **Size:** {total_size}
    **Complete:** {completed_size} 
    **percentage:** {percentage[:5]}%

    **Speed:** {speed}/s
    **Elapsed Time:** {eta}"""
                        try:
                            await pros.edit_text(text)
                        except Exception as e:
                            logger.error(f"Error Proggres Download: {e}")
                        left_time[message.id] = datetime.now() + timedelta(seconds=self.sleep)

                speed_counter[message.id] = time.time()
                left_time[message.id] = datetime.now()

                try:
                    await client.download_media(
                        message.reply_to_message,
                        file_name=fname,
                        progress=progress,
                    )
                    await pros.edit_text("Succesfully Downloaded...")
                    downloader.pop(message.id)
                except Exception:
                    await pros.edit_text("Failed to download the media from the telegram.")

            if len(downloader) > 10:
                timers = []
                for x in downloader:
                    timers.append(downloader[x])
                try:
                    low = min(timers)
                    eta = Tools.get_readable_time(low)
                except Exception as e:
                    logger.error(f"Error Get Readable Time: {e}")
                    eta = "Unknown"
                await pros.edit_text("**overload ** with downloads now. \n\n ** try after: ** {} (__ The expected time__)".format(eta))
                return False

            task = asyncio.create_task(down_load())
            lyrical[pros.id] = task
            await task
            downloaded = downloader.get(message.id)
            if downloaded:
                downloader.pop(message.id)
                return False
            verify = lyrical.get(pros.id)
            if not verify:
                return False
            lyrical.pop(pros.id)
            return True
        except Exception as er:
            logger.error(f"Error: {er} \n {traceback.format_exc()}")


telegram = TelegramAPI()


class YoutubeSearch:
    def __init__(self, search_terms: str, max_results=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = []

    async def _fetch(self, client, url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    async def _search(self):
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        BASE_URL = "https://www.youtube.com"
        url = f"{BASE_URL}/results?search_query={encoded_search}"

        async with httpx.AsyncClient(http2=True) as client:
            response = await self._fetch(client, url)
            while "ytInitialData" not in response:
                response = await self._fetch(client, url)
            results = self._parse_html(response)
            if self.max_results is not None and len(results) > self.max_results:
                self.videos = results[: self.max_results]
            else:
                self.videos = results

    def _parse_html(self, response):
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        for contents in data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]:
            for video in contents["itemSectionRenderer"]["contents"]:
                res = {}
                if "videoRenderer" in video.keys():
                    video_data = video.get("videoRenderer", {})
                    res["id"] = video_data.get("videoId", None)
                    res["thumbnails"] = [thumb.get("url", None) for thumb in video_data.get("thumbnail", {}).get("thumbnails", [{}])]
                    res["title"] = video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
                    res["long_desc"] = video_data.get("descriptionSnippet", {}).get("runs", [{}])[0].get("text", None)
                    res["channel"] = video_data.get("longBylineText", {}).get("runs", [[{}]])[0].get("text", None)
                    res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                    res["views"] = video_data.get("viewCountText", {}).get("simpleText", 0)
                    res["publish_time"] = video_data.get("publishedTimeText", {}).get("simpleText", 0)
                    res["url_suffix"] = video_data.get("navigationEndpoint", {}).get("commandMetadata", {}).get("webCommandMetadata", {}).get("url", None)
                    results.append(res)

            if results:
                return results
        return results

    async def fetch_results(self):
        await self._search()

    def to_dict(self, clear_cache=True):
        result = self.videos
        if clear_cache:
            self.videos = []
        return result

    def to_json(self, clear_cache=True):
        result = json.dumps({"videos": self.videos})
        if clear_cache:
            self.videos = []
        return result

    def get_id(self, index=0):
        return self.videos[index]["id"] if self.videos else None

    def get_link(self, index=0):
        if self.videos:
            video = self.videos[index]
            return f"https://www.youtube.com{video['url_suffix']}"
        return None

    def get_title(self, index=0):
        return self.videos[index]["title"] if self.videos else None

    def get_thumbnail(self, index=0):
        return self.videos[index]["thumbnails"][0] if self.videos else None

    def get_channel(self, index=0):
        return self.videos[index]["channel"] if self.videos else None

    def get_duration(self, index=0):
        return self.videos[index]["duration"] if self.videos else None

    def get_views(self, index=0):
        return self.videos[index]["views"] if self.videos else None

    def get_publish_time(self, index=0):
        return self.videos[index]["publish_time"] if self.videos else None
