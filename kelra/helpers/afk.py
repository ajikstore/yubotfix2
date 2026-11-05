import asyncio

from ..database import dB
from .tools import Tools


class AFK_:
    @staticmethod
    async def set_afk(client, message, emo):
        try:
            rep = message.reply_to_message
            text = rep.text or rep.caption or ""
            entities = rep.entities or rep.caption_entities
            if rep.media:
                media = Tools.get_file_id(rep)
                extract = Tools.dump_entity(text, entities)
                value = {
                    "type": media["message_type"],
                    "file_id": media["file_id"],
                    "result": extract,
                }
            else:
                extract = Tools.dump_entity(text, entities)
                value = {"type": "text", "file_id": "", "result": extract}
            if value:
                await dB.set_var(client.me.id, "AFK", value)

            return await message.reply(f"{emo.sukses}**AFK status set to: [this]({rep.link})")
        except Exception as er:
            return await message.reply(f"{emo.gagal}**ERROR**: `{str(er)}`")

    @staticmethod
    async def get_afk(client, message, emo):
        try:
            data = await dB.get_var(client.me.id, "AFK")
            if not data:
                return
            type = data["type"]
            file_id = data["file_id"]

            if type == "text":
                entities = [Tools.convert_entity(asu) for asu in data["result"].get("entities", [])]
                return await message.reply(
                    data["result"].get("text"),
                    entities=entities,
                    reply_to_message_id=message.id,
                )
            elif type == "sticker":
                return await message.reply_sticker(
                    file_id,
                    reply_to_message_id=message.id,
                )
            elif type == "video_note":
                return await message.reply_video_note(file_id, reply_to_message_id=message.id)
            else:
                kwargs = {
                    "photo": message.reply_photo,
                    "voice": message.reply_voice,
                    "audio": message.reply_audio,
                    "video": message.reply_video,
                    "animation": message.reply_animation,
                    "document": message.reply_document,
                }

                if type in kwargs:
                    entities = [Tools.convert_entity(asu) for asu in data["result"].get("entities", [])]
                    return await kwargs[type](
                        file_id,
                        caption=data["result"].get("text"),
                        caption_entities=entities,
                        reply_to_message_id=message.id,
                    )
        except Exception as er:
            return await message.reply(f"{emo.gagal}**ERROR**: `{str(er)}`")

    @staticmethod
    async def unset_afk(client, message, emo):
        vars = await dB.get_var(client.me.id, "AFK")
        if vars:
            await dB.remove_var(client.me.id, "AFK")
            afk_text = f"<b>{emo.sukses}Back to Online!!</b>"
            try:
                ae = await message.reply(afk_text)
                await asyncio.sleep(3)
                return await ae.delete()
            except Exception:
                return
