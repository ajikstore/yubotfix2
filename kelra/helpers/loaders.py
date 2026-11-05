import asyncio
import os
import sys
import traceback
import zipfile
from datetime import datetime

from dateutil.relativedelta import relativedelta
from pyrogram import enums
from pyrogram.helpers import kb
from pytz import timezone

from config import (
    AKSES_DEPLOY,
    BOT_ID,
    BOT_NAME,
    LOG_SELLER,
    OWNER_ID,
    DATABASE,
    SAWERIA_USERID,
)
from kelra import bot, kelra
from kelra.logger import logger

from ..database import DB_PATH, dB, state
from .message import Message
from .tools import Tools

waktu_jkt = timezone("Asia/Jakarta")


def find_env_file():
    for file in os.listdir():
        if file.endswith(".env"):
            return os.path.abspath(file)
    return None


async def add_transaction(user_id, month):
    expired = await dB.get_expired_date(user_id)
    if not expired:
        now = datetime.now(waktu_jkt)
        expired = now + relativedelta(months=month)
        await dB.set_expired_date(user_id, expired)


async def get_receive(payment_id):
    receipt_url = f"https://api.maelyn.sbs/api/saweria/check/payment/{SAWERIA_USERID}/{payment_id}"
    try:
        response = await Tools.fetch.get(receipt_url)
        if response.status_code == 200:
            resp = response.json()
            teks = resp["msg"]
            if teks == "BERHASIL":
                return "Berhasil"
            return "Pending"

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


async def get_user_progres(ids):
    data = state.get(ids, "USER_PAYMENT")
    logger.info(f"cek data: {data}")
    if not data:
        return None, None, None

    idpay = data.get("idpay")
    userid = data.get("userid")
    month = data.get("month")

    if not all([idpay, userid, month]):
        return None, None, None

    return idpay, int(userid), int(month)


async def check_payment():
    logger.info("Menjalankan auto cek payment")
    while True:
        await asyncio.sleep(10)
        try:
            data_id = await dB.get_var(BOT_ID, "PAYMENT") or []
            if not data_id:
                continue

            for ids in data_id:
                try:
                    teks = await get_receive(ids)
                    idpay, target, month = await get_user_progres(ids)

                    if None in (idpay, target, month):
                        logger.error(f"Invalid payment data for ID: {ids}")
                        data_id.remove(ids)
                        await dB.set_var(BOT_ID, "PAYMENT", data_id)
                        continue

                    if ids == idpay:
                        user = await bot.get_users(target)
                        mention = user.mention
                        userid = user.id
                        if teks == "Berhasil":
                            await add_transaction(userid, month)
                            expired = await dB.get_expired_date(userid)
                            data_id.remove(ids)
                            await dB.set_var(BOT_ID, "PAYMENT", data_id)
                            state.delete(ids, "USER_PAYMENT")
                            msg = f"""
<b><blockquote>#New Order User Added To Access!!

User: {mention}
User ID: `{userid}`

Payment ID: `{ids}`
Month: {month}

Expired at: `{expired.astimezone(waktu_jkt).strftime("%Y-%m-%d %H:%M")}`
Payment status: <u>Succesed</u>

Message: Payment has been successful, [Click here](https://saweria.co/receipt/{ids})</blockquote></b>"""
                            if userid not in AKSES_DEPLOY:
                                AKSES_DEPLOY.append(userid)
                                try:
                                    await bot.send_message(
                                        userid,
                                        f"Selamat ! Akun anda sudah memiliki akses untuk pembuatan Userbot",
                                        reply_markup=kb(
                                            [["✅ Lanjutkan Buat Userbot"]],
                                            resize_keyboard=True,
                                            one_time_keyboard=True,
                                        ),
                                    )
                                except Exception:
                                    pass
                            await bot.send_message(LOG_SELLER, msg)
                    else:
                        await bot.send_message(LOG_SELLER, f"**ERROR:** {teks}")
                except Exception as er:
                    logger.error(f"Error processing payment ID {ids}: {str(er)}")
                    data_id.remove(ids)
                    await dB.set_var(BOT_ID, "PAYMENT", data_id)
                    logger.error(f"Check_Payment error: {traceback.format_exc()}")
        except Exception as e:
            await bot.send_message(LOG_SELLER, f"Check_Payment error: {traceback.format_exc()}")
            await bot.send_message(LOG_SELLER, f"Check_Payment error: {str(e)}")
        await asyncio.sleep(10)


async def load_user_allchats(client):
    private = []
    group = []
    globall = []
    all = []
    bots = []
    try:
        async for dialog in client.get_dialogs():
            try:
                if dialog.chat.type == enums.ChatType.PRIVATE:
                    private.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                ):
                    group.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                    enums.ChatType.CHANNEL,
                ):
                    globall.append(dialog.chat.id)
                elif dialog.chat.type in (
                    enums.ChatType.GROUP,
                    enums.ChatType.SUPERGROUP,
                    enums.ChatType.PRIVATE,
                ):
                    all.append(dialog.chat.id)
                if dialog.chat.type == enums.ChatType.BOT:
                    bots.append(dialog.chat.id)
            except Exception:
                continue
    except Exception:
        pass
    return private, group, globall, all, bots


async def installing_user(client):
    private, group, globall, all, bots = await load_user_allchats(client)
    client_id = client.me.id
    client._get_my_peer[client_id] = {
        "private": private,
        "group": group,
        "global": globall,
        "all": all,
        "bot": bots,
    }


async def installPeer():
    try:
        for client in kelra._ubot:
            await installing_user(client)
    except Exception as er:
        await bot.send_message(OWNER_ID, f"Error installPeer {str(er)}, {sys.exc_info()[-1].tb_lineno}")
    await bot.send_message(OWNER_ID, "<emoji id=6089144627833611433>✅</emoji> Sukses Install Data Pengguna.")


async def sending_user(user_id):
    try:
        return await bot.send_message(
            user_id,
            f"<blockquote><b>Akun anda tidak dapat memberikan Respon!!\n\nHarap Hentikan Sesi Perangkat dengan nama <code>{BOT_NAME}</code>. Lalu, lakukan Re-Deploy atau klik Lanjut Pembuatan Ulang Userbot di bawah (JIKA MERASA ANDA MASIH MEMILIKI SISA WAKTU EXPIRED USERBOT).</b></blockquote>",
            reply_markup=kb(
                [["✨ Pembuatan Ulang Userbot"]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except Exception:
        return


async def CheckUsers():
    while True:
        await asyncio.sleep(15)
        total = await dB.get_var(BOT_ID, "total_users")
        try:
            if len(kelra._ubot) != total:
                now = datetime.now(timezone("Asia/Jakarta"))
                timestamp = now.strftime("%Y-%m-%d_%H:%M")
                zip_filename = f"{BOT_NAME}_{timestamp}.zip"
                with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
                    if os.path.exists(".env"):
                        env_path = os.path.abspath(".env")
                        zipf.write(env_path, os.path.basename(env_path))
                        zipf.write(DB_PATH, os.path.basename(DB_PATH))
                    else:
                        zipf.write(DB_PATH, os.path.basename(DB_PATH))
                caption = now.strftime("%d %B %Y %H:%M")
                await bot.send_document(DATABASE, zip_filename, caption=caption)
                os.remove(zip_filename)
                return
        except Exception as e:
            return await bot.send_message(LOG_SELLER, f"CheckUsers error: {str(e)}")


async def ExpiredUser():
    while True:
        for X in kelra._ubot:
            try:
                wkt = datetime.now(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                exp = await dB.get_expired_date(X.me.id)
                expir = exp.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expir == wkt:
                    msg = Message.expired_message(X)
                    await bot.send_message(LOG_SELLER, msg)
                    await X.unblock_user(bot.me.username)
                    await bot.send_message(X.me.id, msg)
                    await dB.remove_ubot(X.me.id)
                    await dB.rem_pref(X.me.id)
                    await dB.rem_expired_date(X.me.id)
                    kelra._get_my_id.remove(X.me.id)
                    kelra._ubot.remove(X)
            except Exception as e:
                await bot.send_message(LOG_SELLER, f"Delete user {X.me.mention}: {str(e)}")
                await dB.remove_ubot(X.me.id)
                await dB.rem_pref(X.me.id)

                os.execl("/bin/bash", "bash", "start.sh")
        await asyncio.sleep(1)


async def CleanAcces():
    while True:
        for org in AKSES_DEPLOY:
            try:
                seles = await dB.get_list_from_var(BOT_ID, "SELLER")
                if org not in seles:
                    AKSES_DEPLOY.remove(org)
            except Exception as e:
                await bot.send_message(LOG_SELLER, f"Clean_Accses error: {str(e)}")
        await asyncio.sleep(3600)
