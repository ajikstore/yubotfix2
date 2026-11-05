import asyncio

import uvloop

uvloop.install()
asyncio.set_event_loop(asyncio.new_event_loop())

import importlib
import inspect
import os
import re

from pyrogram import filters
from pyrogram.handlers import (
    CallbackQueryHandler,
    DisconnectHandler,
    EditedMessageHandler,
    MessageHandler,
    UserStatusHandler,
)
from pyrogram.types import BotCommand
from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import ChatUpdate
from pytz import timezone

from config import (
    AKSES_DEPLOY,
    API_HASH,
    API_ID,
    BOT_ID,
    BOT_NAME,
    BOT_TOKEN,
    DEVS,
    FAKE_DEVS,
    HELPABLE,
    OWNER_ID,
    SUDO_OWNERS,
)
from kelra.clients import BaseClient
from kelra.database import dB
from kelra.logger import logger
from plugins import PLUGINS

if not os.path.exists("downloads"):
    os.makedirs("downloads")


list_error = []


class UserBot(BaseClient):
    __module__ = "pyrogram.client"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_id = API_ID
        self.api_hash = API_HASH
        self.device_model = BOT_NAME
        self.group_call = PyTgCalls(self)

    def on_message(self, filters=None, group=-1):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(MessageHandler(func, filters), group)
            return func

        return decorator

    def on_edited_message(self, filters=None, group=-1):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(EditedMessageHandler(func, filters), group)
            return func

        return decorator

    def on_user_status(self, filters=None, group=-1):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(UserStatusHandler(func, filters), group)
            return func

        return decorator

    def on_disconnect(self):
        def decorator(func):
            for ub in self._ubot:
                ub.add_handler(DisconnectHandler(func))
            return func

        return decorator

    def group_call_logs(self):
        def decorator(func):
            for ub in self._ubot:
                ub.group_call.on_update(fl.stream_end)(func)
            return func

        return decorator

    def user_prefix(self, cmd):
        command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

        async def func(_, client, message):
            if message.text:
                text = message.text.strip().encode("utf-8").decode("utf-8")
                username = client.me.username or ""
                prefixes = self.get_prefix(client.me.id)

                if not text:
                    return False

                for prefix in prefixes:
                    if not text.startswith(prefix):
                        continue

                    without_prefix = text[len(prefix) :]

                    for command in cmd.split("|"):
                        if not re.match(
                            rf"^(?:{command}(?:@?{username})?)(?:\s|$)",
                            without_prefix,
                            flags=re.IGNORECASE | re.UNICODE,
                        ):
                            continue

                        without_command = re.sub(
                            rf"{command}(?:@?{username})?\s?",
                            "",
                            without_prefix,
                            count=1,
                            flags=re.IGNORECASE | re.UNICODE,
                        )
                        message.command = [command] + [re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "") for m in command_re.finditer(without_command)]

                        return True

                return False

        return filters.create(func)

    async def start(self):
        await super().start()
        await self.group_call.start()
        prefixes = await dB.get_pref(self.me.id)
        if prefixes:
            self._prefix[self.me.id] = prefixes
        else:
            self._prefix[self.me.id] = [".", ",", "?", "+", "!"]
        self._ubot.append(self)
        self._get_my_id.append(self.me.id)
        logger.info(f"Starting Userbot {self.me.id}|@{self.me.username}")


class Bot(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            device_model=BOT_NAME,
            plugins=dict(root="assistant"),
            **kwargs,
        )

    def on_message(self, filters=None, group=-1):
        def decorator(function):
            self.add_handler(MessageHandler(function, filters), group)
            return function

        return decorator

    def on_callback_query(self, filters=None, group=-1):
        def decorator(function):
            self.add_handler(CallbackQueryHandler(function, filters), group)
            return function

        return decorator

    async def add_reseller(self):
        for user in SUDO_OWNERS:
            if user not in await dB.get_list_from_var(BOT_ID, "SELLER"):
                await dB.add_to_var(BOT_ID, "SELLER", user)
        if OWNER_ID not in await dB.get_list_from_var(BOT_ID, "SELLER"):
            await dB.add_to_var(BOT_ID, "SELLER", OWNER_ID)
        for user in await dB.get_list_from_var(BOT_ID, "SELLER"):
            if user not in AKSES_DEPLOY:
                AKSES_DEPLOY.append(user)

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.fullname = f"{self.me.first_name} {self.me.last_name or ''}"
        self.username = self.me.username
        self.mention = self.me.mention

        await self.set_bot_commands(
            [
                BotCommand("start", "Start the bot."),
                BotCommand("restart", "Restart userbots."),
            ]
        )
        logger.info("🔄 Importing Modules")
        for modul in PLUGINS:
            imported_module = importlib.import_module(f"plugins.{modul}")
            module_name = getattr(imported_module, "__MODULES__", "").lower()
            # logger.info(f"Module name: {module_name}")
            if module_name:
                HELPABLE[module_name] = imported_module
        logger.info("✅ Successed Import All Modules")
        logger.info(f"🔥 {self.username} Bot Started 🔥")


kelra = UserBot(name="Clients")
bot = Bot()
