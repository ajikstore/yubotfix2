import base64
import io
import sys
import time
import traceback
from datetime import datetime

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from config import LOG_SELLER, SAWERIA_EMAIL, SAWERIA_USERID, OWNER_ID, API_MAELYN
from kelra.database import dB, state
from kelra.helpers import CMD, ButtonUtils, Message, Tools
from kelra.logger import logger

last_generated_time = {}


@CMD.CALLBACK("^go_payment")
async def user_aggre(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    await callback_query.message.delete()
    buttons = ButtonUtils.plus_minus(0, user_id)
    return await client.send_message(
        user_id,
        Message.TEXT_PAYMENT(0, 0, 0),
        disable_web_page_preview=True,
        reply_markup=buttons,
    )


@CMD.CALLBACK("^(kurang|tambah)")
async def update_payment(client, callback_query):
    await callback_query.answer()
    BULAN = int(callback_query.data.split()[1])
    HARGA = 20000
    QUERY = callback_query.data.split()[0]
    try:
        if QUERY == "kurang" and BULAN > 1:
            BULAN -= 1
        elif QUERY == "tambah" and BULAN < 12:
            BULAN += 1
        TOTAL_HARGA = HARGA * BULAN
        buttons = ButtonUtils.plus_minus(BULAN, TOTAL_HARGA)
        await callback_query.edit_message_text(
            Message.TEXT_PAYMENT(HARGA, TOTAL_HARGA, BULAN),
            disable_web_page_preview=True,
            reply_markup=buttons,
        )
    except Exception:
        pass


@CMD.CALLBACK("^confirm")
async def confirm_payment(client, callback_query):
    await callback_query.answer()
    amount = int(callback_query.data.split()[1])
    month = callback_query.data.split()[2]
    user_id = callback_query.from_user.id
    full = f"{callback_query.from_user.first_name}"
    await callback_query.message.delete()

    # Batas waktu pembuatan QR baru
    current_time = time.time()
    if user_id in last_generated_time:
        elapsed_time = current_time - last_generated_time[user_id]
        if elapsed_time < 1800:
            remaining_time = 1800 - elapsed_time
            minutes = int(remaining_time // 60)
            seconds = int(remaining_time % 60)
            return await client.send_message(
                user_id,
                f"⚠️ Tunggu {minutes} menit {seconds} detik sebelum membuat QRIS baru."
            )

    try:
        wait = await client.send_message(user_id, "<b>Tunggu sebentar sedang menyiapkan metode pembayaran anda!!</b>")

        # Payload Maelyn API
        url = "https://api.maelyn.sbs/api/saweria/create/payment"
        headers = {
            "Content-Type": "application/json",
            "mg-apikey": API_MAELYN,
        }
        payload = {
            "user_id": SAWERIA_USERID,
            "amount": amount,
            "name": full,
            "email": SAWERIA_EMAIL,
            "msg": f"Payment for {full}",
        }
        
        r = await Tools.post_json(url, headers=headers, payload=payload)

     #   r = await Tools.fetch.post(url, headers=headers, json=payload)

        # Cek status HTTP dan content
        if r.status_code != 200 or not r.content:
            await client.send_message(user_id, "<b>Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.</b>")
            await client.send_message(OWNER_ID, f"⚠️ Payment error for user {full} ({user_id})\nStatus code: {r.status_code}\nContent: {r.text}")
            return await wait.delete()

        # Try parse JSON
        try:
            response_json = r.json()
        except Exception:
            await client.send_message(user_id, "<b>Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.</b>")
            await client.send_message(OWNER_ID, f"⚠️ Payment error for user {full} ({user_id})\nInvalid JSON:\n{r.text}")
            return await wait.delete()

        data = response_json.get("result")
        if not data:
            await client.send_message(user_id, "<b>Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.</b>")
            await client.send_message(OWNER_ID, f"⚠️ Payment error for user {full} ({user_id})\nEmpty result in JSON")
            return await wait.delete()

        hasil_result = data.get("data")
        hasil_amount = hasil_result["amount_raw"]
        hasil_qr = hasil_result["qr_string"]
        hasil_expired_str = hasil_result["expired_at"]
        hasil_expired = datetime.strptime(hasil_expired_str, "%d/%m/%Y %H:%M:%S")
        hasil_idpayment = hasil_result["id"]

        # Buat QR image
        qris_path = f"qris_{user_id}_{hasil_amount}.png"
        Tools.create_qrscan(hasil_qr, str(hasil_amount), qris_path)

        # Simpan state payment
        get_data = await dB.get_var(client.me.id, "PAYMENT") or []
        get_data.append(hasil_idpayment)
        await dB.set_var(client.me.id, "PAYMENT", get_data)
        progres = {"idpay": hasil_idpayment, "userid": user_id, "month": month}
        state.set(hasil_idpayment, "USER_PAYMENT", progres)

        # Kirim QR ke user
        msg = f"""
<b>📃「 Waiting Payment 」</b>

<blockquote expandable><b><i>Item: `{full}`
Price: `{Message.format_rupiah(amount)}`
Total Payment: `{Message.format_rupiah(hasil_amount)}`
Expiration Time: `{hasil_expired}`

Please scan the QRIS above to complete the payment.
If you encounter any issues, contact <a href='tg://user?id={OWNER_ID}'>ADMIN</a>
Type `.cancelpay` to cancel the transaction.</i></b></blockquote>

<blockquote>© Auto Payment @{client.me.username}</blockquote>
"""
        await client.send_photo(user_id, qris_path, caption=msg)
        await wait.delete()

    except Exception as e:
        await client.send_message(user_id, "<b>Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.</b>")
        logger.error(f"ERROR: {traceback.format_exc()}")
        logger.error(f"ERROR: {sys.exc_info()[-1].tb_lineno}")
        await client.send_message(OWNER_ID, f"⚠️ Payment exception for user {full} ({user_id})\n{e}")
        await wait.delete()
