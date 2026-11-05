import asyncio
import os
import traceback
from datetime import datetime

import croniter
from aiorun import run
from pyrogram.errors import (
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    SessionRevoked,
    UserAlreadyParticipant,
    UserDeactivated,
    UserDeactivatedBan,
)
from pytz import timezone

from config import LOG_SELLER, OWNER_ID, WAJIB_JOIN
from kelra import UserBot, bot, logger, kelra
from kelra.database import dB
from kelra.helpers import (
    CheckUsers,
    CleanAcces,
    ExpiredUser,
    Tools,
    check_payment,
    installPeer,
)

list_error = []


async def cleanup_total(ubot_id):
    """Clean up database records for a specific userbot."""
    try:
        await dB.rem_expired_date(ubot_id)
        await dB.rem_pref(ubot_id)
        await dB.rm_all(ubot_id)
        await dB.remove_ubot(ubot_id)
        logger.info(f"Deleted user {ubot_id}")
    except Exception as e:
        logger.error(f"Failed to cleanup userbot {ubot_id}: {e}")


async def auto_restart():
    tz = timezone("Asia/Jakarta")
    cron = croniter.croniter("00 00 * * *", datetime.now(tz))
    while True:
        now = datetime.now(tz)
        next_run = cron.get_next(datetime)

        wait_time = (next_run - now).total_seconds()
        await asyncio.sleep(wait_time)
        try:
            await bot.send_message(
                OWNER_ID,
                "<blockquote><b>Restart Daily..\n\nTunggu beberapa menit bot sedang di Restart!!</b></blockquote>",
            )
        except Exception:
            pass
        os.execl("/bin/bash", "bash", "start.sh")


async def handle_start_error():
    if list_error:
        for data in list_error:
            ubot = data["user"]
            reason = data["error_msg"]
            await bot.send_message(
                LOG_SELLER,
                f"<b>Userbot {ubot} failed to start due to {reason}, deleted user on database</b>",
            )
            await cleanup_total(ubot)


async def start_ubot(ubot):
    """Start a userbot instance and handle setup."""
    userbot = UserBot(**ubot)
    try:
        await userbot.start()
        sudo_users = await dB.get_list_from_var(userbot.me.id, "SUDOERS")
        for user in sudo_users:
            userbot.add_sudoers(userbot.me.id, user)
            userbot.add_sudoers(userbot.me.id, userbot.me.id)
        for chat in [WAJIB_JOIN]:
            try:
                await userbot.join_chat(chat)
            except UserAlreadyParticipant:
                pass
            except Exception:
                continue
    except (AuthKeyUnregistered, AuthKeyDuplicated, SessionRevoked):
        reason = "Session Ended"
        data = {"user": int(ubot["name"]), "error_msg": reason}
        list_error.append(data)
    except (UserDeactivated, UserDeactivatedBan):
        reason = "Account Banned by Telegram"
        data = {"user": int(ubot["name"]), "error_msg": reason}
        list_error.append(data)


async def start_main_bot():
    """Start the main bot after userbots."""
    logger.info("🤖 Starting main bot...")
    await bot.start()
    await bot.add_reseller()
    total_bots = len(kelra._ubot)
    message = "<emoji id=5332336747072208845>🔥</emoji>**Userbot berhasil diaktifkan**<emoji id=5332336747072208845>🔥</emoji>\n" f"<emoji id=5206607081334906820>✅</emoji> **Total User: {total_bots}**"
    await dB.set_var(bot.id, "total_users", total_bots)
    logger.info("✅ Main bot started successfully.")
    try:
        await bot.send_message(OWNER_ID, f"<blockquote>{message}</blockquote>")
    except Exception:
        pass


async def start_userbots():
    await dB.initialize()
    logger.info("🔄 Starting userbots...")
    userbots = await dB.get_userbots()
    tasks = [asyncio.create_task(start_ubot(ubot)) for ubot in userbots]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"❌ Error starting userbot {userbots[idx]['name']}: {result}")
            await bot.send_message(
                LOG_SELLER,
                f"❌ Error starting userbot {userbots[idx]['name']}: {result}",
            )

    logger.info("✅ All userbots started successfully.")


async def end_main():
    background_tasks = [
        ExpiredUser(),
        installPeer(),
        CheckUsers(),
        CleanAcces(),
        check_payment(),
        auto_restart(),
    ]
    for task in background_tasks:
        asyncio.create_task(task)
    logger.info(f"Started {len(background_tasks)} background tasks")


async def stop_main():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logger.info(f"📌 Total task yang akan dihentikan: {len(tasks)}")

    if not tasks:
        logger.info("✅ Tidak ada task yang berjalan.")
        return

    for task in tasks:
        if not task.done():
            task.cancel()

    await asyncio.sleep(1)

    results = []
    for task in tasks:
        try:
            result = await asyncio.wait_for(asyncio.shield(task), timeout=5)
            results.append(result)
        except asyncio.TimeoutError:
            logger.error(f"⏳ Timeout saat menghentikan task: {task.get_name() or task}")
            results.append(None)
        except asyncio.CancelledError:
            continue
        except Exception as e:
            logger.error(f"⚠️ Task {task.get_name() or task} mengalami error: {e}")

    logger.info("⚠️ Menutup database...")
    await Tools.close_fetch()
    await dB.close()
    logger.info("✅ Semua task dihentikan dan database telah ditutup.")


async def main():
    try:
        await start_userbots()
        await start_main_bot()
        await end_main()
        await handle_start_error()

    except asyncio.CancelledError:
        logger.warning("Stopped All.")
    except Exception:
        logger.error(f"{traceback.format_exc()}")


if __name__ == "__main__":
    run(
        main(),
        loop=bot.loop,
        shutdown_callback=stop_main(),
    )
