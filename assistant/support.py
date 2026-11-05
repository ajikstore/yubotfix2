from pyrogram.helpers import kb

from config import OWNER_ID, SUDO_OWNERS
from kelra.database import dB, state
from kelra.helpers import CMD, ButtonUtils, no_commands
from kelra.logger import logger


async def pengguna_nanya(client, message):
    user_id = message.from_user.id
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    logs = await dB.get_var(client.me.id, "FORWARD_LOG")  # Fixed: Get logs from database
    log = int(logs) if logs else OWNER_ID
    try:
        button = kb([["❌ Batalkan"]], resize_keyboard=True, one_time_keyboard=True)
        pesan = await client.ask(
            user_id,
            f"✍️ Please write your question: {full_name}",
            reply_markup=button,
        )
        if pesan.text in no_commands:
            await pesan.delete()
            return await client.send_message(
                user_id,
                "Process has been cancelled.",
                reply_markup=ButtonUtils.start_menu(is_admin=False),
            )
    except Exception as error:
        logger.error(f"line 31 {str(error)}")
    buttons = kb(
        [[("👤 Akun"), ("💬 Jawab Pesan")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    text = f"💬 Your message has been sent: {full_name}"
    await pesan.forward(log)
    return await client.send_message(user_id, text)



@CMD.BOT("setlog")
async def _(client, message):
    if message.from_user.id not in SUDO_OWNERS:
        return
    await dB.set_var(client.me.id, "FORWARD_LOG", message.chat.id)
    return await message.reply(f"**Log forward diatur ke: `{message.chat.id}`**")


# @CMD.NO_CMD("QUESTION", bot)
async def _(client, message):
    if message.text in no_commands:
        return
    user_id = message.from_user.id
    logs = await dB.get_var(client.me.id, "FORWARD_LOG")
    log = int(logs) if logs else OWNER_ID
    forward = await client.forward_messages(chat_id=log, from_chat_id=message.chat.id, message_ids=message.id)
    state.set(forward.id, f"FORWARD_{forward.id}", user_id)


# @CMD.NO_CMD("ANSWER", bot)
async def _(client, message):
    if message.text in no_commands:
        return
    rep = message.reply_to_message
    if not rep:
        return
    user_id = state.get(rep.id, f"FORWARD_{rep.id}")
    if user_id:
        return await client.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.id)
