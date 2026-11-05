__MODULES__ = "Saweria"
__HELP__ = """<blockquote>Command Help **Saweria** </blockquote>
<blockquote expandable>--

    **Login ke Saweria**
        `{0}saweria login` (reply pesan berisi email dan username)
    **Buat pembayaran QRIS**
        `{0}saweria qris 5000 beli kopi`

 **Note**: Login dulu sebelum menggunakan perintah QRIS.</blockquote>
<b>   {1}</b>
"""

__CATEGORY__ = "Payment <emoji id=5287231198098117669>💳</emoji>"

import asyncio
import os
import traceback
from datetime import datetime
from uuid import uuid4

from config import config, OWNER_ID
from kelra.database import dB
from kelra.helpers import CMD, Emoji, Tools

transactions = {}


@CMD.UBOT("saweria")
async def saweria_handler(client, message):
    em = Emoji(client)
    await em.get()
    proses_ = await em.get_costum_text()
    proses = await message.reply(f"{em.proses}**{proses_[4]}**")

    args = ["login", "qris"]
    command = message.command

    if len(command) < 2 or command[1] not in args:
        return await proses.edit(f"{em.gagal}**Please give me valid query: `login`, `qris`**")

    # ─── LOGIN HANDLER ──────────────────────────────
    if command[1] == "login":
        if not message.reply_to_message:
            return await proses.edit(
                f"{em.gagal}**Usage:** `{message.text.split()[0]} login` (reply ke pesan yang berisi: email username)"
            )

        email, username = Tools.parse_text(message.reply_to_message)

        try:
            url = "https://api.maelyn.sbs/api/saweria/check/user"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "mg-apikey": config.API_MAELYN,
            }
            payload = {"username": username}

            r = await Tools.fetch.post(url, headers=headers, json=payload)
            if isinstance(r, str):
                return await proses.edit(f"{em.gagal}**Server error, coba lagi nanti.**")
            status = getattr(r, "status_code", 200)  # fallback status
            data_json = r if isinstance(r, dict) else {}

            if status != 200 or not data_json:
                return await proses.edit(f"{em.gagal}**Server error, coba lagi nanti.**")

            saweria_userid = data_json.get("result", {}).get("userId")
            if not saweria_userid:
                return await proses.edit(f"{em.gagal}**User ID tidak ditemukan.**")

        except Exception as e:
            await client.send_message(OWNER_ID, f"⚠️ Saweria login error:\n{traceback.format_exc()}")
            return await proses.edit(f"{em.gagal}**Login failed. Silahkan hubungi owner.**")

        data = {
            "saweria_userid": saweria_userid,
            "saweria_email": email,
            "saweria_username": username,
        }
        await dB.set_var(client.me.id, "SAWERIA_ACCOUNT", data)
        return await proses.edit(f"{em.sukses}**Berhasil login ke Saweria! User ID: `{saweria_userid}`**")

    # ─── QRIS PAYMENT HANDLER ───────────────────────────────
    elif command[1] == "qris":
        info = await dB.get_var(client.me.id, "SAWERIA_ACCOUNT")
        if not info:
            return await proses.edit(f"{em.gagal}**Login dulu pakai perintah `login`.**")

        if len(command) < 4:
            return await proses.edit(f"{em.gagal}**Usage:** `{message.text.split()[0]} qris 5000 beli kopi`**")

        try:
            amount = int(command[2])
        except ValueError:
            return await proses.edit(f"{em.gagal}**Amount harus angka!**")

        desc = " ".join(command[3:])
        uniq = str(uuid4())
        saweria_email = info["saweria_email"]
        saweria_userid = info["saweria_userid"]

        url = "https://api.maelyn.sbs/api/saweria/create/payment"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "mg-apikey": config.API_MAELYN,
        }
        payload = {
            "user_id": saweria_userid,
            "amount": amount,
            "name": client.me.first_name,
            "email": saweria_email,
            "msg": desc,
        }

        try:
            r = await Tools.fetch.post(url, headers=headers, json=payload)
            if isinstance(r, str) or not isinstance(r, dict):
                await client.send_message(OWNER_ID, f"⚠️ Payment create error for user {message.from_user.id}")
                return await proses.edit(f"{em.gagal}**Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.**")

            data = r.get("result", {}).get("data")
            if not data:
                await client.send_message(OWNER_ID, f"⚠️ Payment data empty for user {message.from_user.id}")
                return await proses.edit(f"{em.gagal}**Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.**")

        except Exception as e:
            await client.send_message(OWNER_ID, f"⚠️ Payment exception for user {message.from_user.id}\n{traceback.format_exc()}")
            return await proses.edit(f"{em.gagal}**Terjadi kesalahan saat membuat pembayaran. Silahkan hubungi owner.**")

        hasil_amount = data["amount_raw"]
        hasil_qr = data["qr_string"]
        hasil_expired_str = data["expired_at"]
        hasil_expired = datetime.strptime(hasil_expired_str, "%d/%m/%Y %H:%M:%S")
        hasil_idpayment = data["id"]

        qris_path = f"qris_{client.me.id}_{hasil_amount}.png"
        Tools.create_qrscan(hasil_qr, str(hasil_amount), qris_path)

        sent = await message.reply_photo(
            qris_path,
            caption=f"""
<b>📃「 Waiting Payment 」</b>

<blockquote expandable><b><i>{em.profil}Item: `{desc}`
{em.speed}Total Payment: `{Tools.format_rupiah(hasil_amount)}`
{em.warn}Expires At: `{hasil_expired}`

Scan QRIS di atas untuk membayar.</i></b></blockquote>

<blockquote>© Auto Payment @{client.me.username}</blockquote>
"""
        )

        if os.path.exists(qris_path):
            os.remove(qris_path)
        await proses.delete()

        transactions[uniq.split("-")[0]] = {
            "expire_time": hasil_expired,
            "message_id": sent.id,
            "done": False,
        }

        # ─── CEK PEMBAYARAN BERKALA ───────────────────────────────
        max_checks = 60
        count = 0
        while count < max_checks:
            count += 1
            await asyncio.sleep(5)
            trans = transactions.get(uniq.split("-")[0])
            if not trans or trans["done"]:
                break

            if datetime.now() > trans["expire_time"]:
                if not trans["done"]:
                    await client.send_message(message.chat.id, f"{em.gagal}<b><i>Payment canceled due to timeout.</i></b>")
                    await client.delete_messages(chat_id=message.chat.id, message_ids=trans["message_id"])
                    transactions.pop(uniq.split("-")[0], None)
                break

            try:
                check_url = "https://api.maelyn.sbs/api/saweria/check/payment"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "mg-apikey": config.API_MAELYN,
                }
                payload = {"user_id": saweria_userid, "payment_id": hasil_idpayment}

                r = await Tools.fetch.post(check_url, headers=headers, json=payload)
                is_paid = r.get("result") if isinstance(r, dict) else None

                if is_paid and not trans["done"]:
                    if is_paid.get("msg") == "BERHASIL":
                        trans["done"] = True
                        await message.reply(
                            f"""
<blockquote><b><i>{em.sukses}Payment received!

{em.profil}Item: `{desc}`
{em.speed}Total Paid: `{Tools.format_rupiah(hasil_amount)}`</i></b></blockquote>
"""
                        )
                        await client.delete_messages(chat_id=message.chat.id, message_ids=trans["message_id"])
                        transactions.pop(uniq.split("-")[0], None)
                        return

            except Exception as e:
                print(f"❌ Error checking payment: {e}")
                transactions.pop(uniq.split("-")[0], None)
                await message.reply(f"{em.gagal}**Error occurred:** `{str(e)}`")
                break
