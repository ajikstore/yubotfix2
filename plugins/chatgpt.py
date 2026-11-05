from config import API_BOTCHAX
from kelra.helpers import CMD, Emoji, Message, Tools

__MODULES__ = "Chatgpt"
__HELP__ = """<blockquote>Command Help **ChatGpt**</blockquote>

<blockquote expandable>
<u>**Chat with ChatGPT**</u>
`{0}ask` (prompt)

<u>**Stop the conversation**</u>
`{0}stop ask`
</blockquote>

<b>{1}</b>
"""
__CATEGORY__ = "Ai <emoji id=5237689785425877860>🤖</emoji>"

CONVERSATIONS = {}


@CMD.UBOT("ask")
async def ai_chat(client, message):
    em = Emoji(client)
    await em.get()

    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            f"<blockquote>{em.gagal} **Please reply to message text or give message!**</blockquote>"
        )

    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in CONVERSATIONS:
        CONVERSATIONS[user_id] = [
            {
                "role": "system",
                "content": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul, dan jangan gunakan bahasa inggris sebelum saya memulai duluan.",
            },
            {
                "role": "assistant",
                "content": "Kamu adalah asisten paling canggih yang berbahasa Indonesia gaul.",
            },
        ]

    question = client.get_text(message)

    while True:
        proses_ = await em.get_costum_text()
        pros = await message.reply(f"{em.proses}**{proses_[4]}**")

        try:
            CONVERSATIONS[user_id].append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            url = "https://api.botcahx.eu.org/api/search/openai-custom-v2"

            payload = {
                "apikey": API_BOTCHAX,
                "message": CONVERSATIONS[user_id],
            }

            response = await Tools.fetch.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()

                output = data.get("result") or data.get("message") or data.get("data")

                if not output:
                    await pros.edit(
                        f"<blockquote>{em.gagal}<code>{data}</code></blockquote>"
                    )
                    break

                CONVERSATIONS[user_id].append(
                    {
                        "role": "assistant",
                        "content": output,
                    }
                )

                if len(CONVERSATIONS[user_id]) > 20:
                    CONVERSATIONS[user_id] = (
                        CONVERSATIONS[user_id][:2]
                        + CONVERSATIONS[user_id][-18:]
                    )

                await pros.delete()

                if len(output) > 4096:
                    result = await Tools.paste(output)
                else:
                    result = output

                next_message = await client.ask(
                    chat_id=chat_id,
                    text=(
                        f"<blockquote>{em.sukses}"
                        f"<b>Question:</b>\n"
                        f"<blockquote>{question}</blockquote>\n\n"
                        f"<b>Answer:</b>\n"
                        f"<blockquote>{result}</blockquote>\n\n"
                        f"<b>Type <code>stop ask</code> to end the conversation.</b>"
                        f"</blockquote>"
                    ),
                    disable_web_page_preview=True,
                    timeout=300,
                    reply_to_message_id=Message.ReplyCheck(message),
                )

                if next_message.text.lower() == "stop ask":
                    del CONVERSATIONS[user_id]
                    await next_message.reply(
                        f"<blockquote>{em.sukses}Conversation ended.</blockquote>",
                        reply_to_message_id=Message.ReplyCheck(message),
                    )
                    break

                question = next_message.text

            else:
                await pros.edit(
                    f"<blockquote>{em.gagal}<b>API Error {response.status_code}</b>\n<code>{response.text}</code></blockquote>"
                )
                break

        except TimeoutError:
            if user_id in CONVERSATIONS:
                del CONVERSATIONS[user_id]

            await message.reply(
                f"<blockquote>{em.gagal}Conversation timed out after 5 minutes.</blockquote>",
                reply_to_message_id=Message.ReplyCheck(message),
            )
            break

        except Exception as er:
            if user_id in CONVERSATIONS:
                del CONVERSATIONS[user_id]

            await pros.edit(
                f"<blockquote>{em.gagal}<b>ERROR</b>\n<code>{er}</code></blockquote>"
            )
            break


@CMD.UBOT("clearai")
async def clear_ai(client, message):
    em = Emoji(client)
    await em.get()

    user_id = message.from_user.id

    if user_id in CONVERSATIONS:
        del CONVERSATIONS[user_id]
        await message.reply(
            f"<blockquote>{em.sukses}AI conversation history cleared.</blockquote>"
        )
    else:
        await message.reply(
            f"<blockquote>{em.gagal}No active AI conversation found.</blockquote>"
        )
