import asyncio
import traceback

from pyrogram.enums import UserStatus

from kelra import bot
from kelra.helpers import CMD
from kelra.logger import logger


async def send_to_user(chat_id, text):
    try:
        await bot.send_message(chat_id, text)
    except Exception:
        logger.error(f"Error saat mengirim pesan: {traceback.format_exc()}")


@CMD.USER_STATUS()
async def _(client, user):
    if user.id == client.me.id:
        status = (await client.get_users(client.me.id)).status
        if status == UserStatus.LAST_WEEK:
            logger.info(f"Try to stopping {client.me.id}\nStatus {user.status}.")
            if client.is_connected:
                asyncio.create_task(stop_client(client))
            else:
                logger.info(f"{user.id} User already stopped.")
        """
        elif user.status == UserStatus.ONLINE:
            logger.info(f"Try to starting {client.me.id}\nStatus {user.status}.")
            if not client.is_connected:
                asyncio.create_task(start_client(client))
            else:
                logger.info(f"{user.id} User already started.")"
        """


async def stop_client(client):
    logger.info(f"{client.me.id} Stopping Ubot.")
    await asyncio.sleep(1)
    await client.stop()
