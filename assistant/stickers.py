import os

from pyrogram import enums
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import (AddStickerToSet, CreateStickerSet,
                                             RemoveStickerFromSet)
from pyrogram.raw.types import (DocumentAttributeFilename, InputDocument,
                                InputMediaUploadedDocument,
                                InputStickerSetItem, InputStickerSetShortName)

from config import LOG_ERROR
from kelra import bot
from kelra.helpers import CMD, Sticker, Tools


@CMD.BOT("kang")
async def _(self: bot, message):
    prog_msg = await message.reply("Processing...")
    sticker_emojis = "🤔"
    sticker_emoji = message.command[1] if len(message.command) > 1 else sticker_emojis
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False
    reply = message.reply_to_message
    user = await self.resolve_peer(message.from_user.username or message.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                resize = True
            elif reply.document.mime_type in (
                enums.MessageMediaType.VIDEO,
                enums.MessageMediaType.ANIMATION,
            ):
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text("<blockquote>Stiker tidak memiliki nama.</blockquote>")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit_text()

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{message.from_user.id}_by_{self.me.username}"

        if (
            len(message.command) > 1
            and message.command[1].isdigit()
            and int(message.command[1]) > 0
        ):
            packnum = message.command.pop(1)
            packname = (
                f"{pack_prefix}{packnum}_{message.from_user.id}_by_{self.me.username}"
            )
        if len(message.command) > 1:
            sticker_emoji = (
                "".join(
                    set(Sticker.get_emoji_regex().findall("".join(message.command[1:])))
                )
                or sticker_emoji
            )
        filename = await self.download_media(message.reply_to_message)
        if not filename:
            await prog_msg.delete()
            return
    elif message.entities and len(message.entities) > 1:
        pack_prefix = "a"
        filename = "sticker.png"
        packname = f"c{message.from_user.id}_by_{self.me.username}"
        img_url = next(
            (
                message.text[y.offset : (y.offset + y.length)]
                for y in message.entities
                if y.type == "url"
            ),
            None,
        )

        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await Tools.fetch.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(message.command) > 2:
            if message.command[2].isdigit() and int(message.command[2]) > 0:
                packnum = message.command.pop(2)
                packname = f"a{packnum}_{message.from_user.id}_by_{self.me.username}"
            if len(message.command) > 2:
                sticker_emoji = (
                    "".join(
                        set(
                            Sticker.get_emoji_regex().findall(
                                "".join(message.command[2:])
                            )
                        )
                    )
                    or sticker_emoji
                )
            resize = True
    else:
        return await prog_msg.edit_text(
            "<blockquote>Ingin saya menebak stikernya? Harap tandai stiker.</blockquote>"
        )
    try:
        if resize:
            filename = Sticker.resize_image(filename)
        elif convert:
            filename = await Sticker.convert_video(filename)
            if filename is False:
                return await prog_msg.edit_text("Error")
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await self.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}_{packnum}_{message.from_user.id}_by_{self.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await self.save_file(filename)
        media = await self.invoke(
            SendMedia(
                peer=(await self.resolve_peer(LOG_ERROR)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=self.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {message.from_user.id}",
                random_id=self.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await prog_msg.edit_text("<blockquote>Menggunakan paket stiker yang ada...</blockquote>")
            await self.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text("<blockquote>Membuat paket stiker baru...</blockquote>")
            stkr_title = f"{message.from_user.first_name}"
            if animated:
                stkr_title += " AnimPack"
            elif videos:
                stkr_title += " VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                if animated:
                    await self.invoke(
                        CreateStickerSet(
                            user_id=user,
                            title=stkr_title,
                            short_name=packname,
                            tgs_stickers=[
                                InputStickerSetItem(
                                    document=InputDocument(
                                        id=stkr_file.id,
                                        access_hash=stkr_file.access_hash,
                                        file_reference=stkr_file.file_reference,
                                    ),
                                    emoji=sticker_emoji,
                                )
                            ]
                        )
                    )
                elif videos:
                    await self.invoke(
                        CreateStickerSet(
                            user_id=user,
                            title=stkr_title,
                            short_name=packname,
                            webm_stickers=[
                                InputStickerSetItem(
                                    document=InputDocument(
                                        id=stkr_file.id,
                                        access_hash=stkr_file.access_hash,
                                        file_reference=stkr_file.file_reference,
                                    ),
                                    emoji=sticker_emoji,
                                )
                            ]
                        )
                    )
                else:
                    await self.invoke(
                        CreateStickerSet(
                            user_id=user,
                            title=stkr_title,
                            short_name=packname,
                            stickers=[
                                InputStickerSetItem(
                                    document=InputDocument(
                                        id=stkr_file.id,
                                        access_hash=stkr_file.access_hash,
                                        file_reference=stkr_file.file_reference,
                                    ),
                                    emoji=sticker_emoji,
                                )
                            ]
                        )
                    )
            except PeerIdInvalid:
                return await prog_msg.edit_text(
                    "<blockquote>Tampaknya Anda belum pernah berinteraksi dengan saya dalam obrolan pribadi, Anda harus melakukannya dulu..</blockquote>"
                )
    except BadRequest:
        return await prog_msg.edit_text(
            "<blockquote>Paket Stiker Anda penuh jika paket Anda tidak dalam Tipe v1 /kang 1, jika tidak dalam Tipe v2 /kang 2 dan seterusnya.</blockquote>"
        )
    except Exception as all_e:
        return await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        await prog_msg.edit_text(
            f"<blockquote><b>Sticker Anda Berhasil Dibuat!</b>\n<b><a href=https://t.me/addstickers/{packname}>👀 Lihat Paket Sticker Disini</a></b>\n<b>Emoji:</b> {sticker_emoji}</blockquote>"
        )
        await self.delete_messages(chat_id=LOG_ERROR, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass
    return


@CMD.BOT("unkang")
async def _(self, message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        await message.reply("<blockquote>Harap balas ke stiker yang ingin dihapus.</blockquote>")
        return

    rep = message.reply_to_message.sticker

    try:
        sticker_id = rep.file_id
        decoded = FileId.decode(sticker_id)
        sticker = InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )
        await self.invoke(RemoveStickerFromSet(sticker=sticker))
        await message.reply("<blockquote>Stiker berhasil dihapus dari paket Anda.</blockquote>")
        return
    except Exception as e:
        await message.reply(
            f"<blockquote>Gagal menghapus stiker dari paket Anda.\n\nError: <code>{e}</code></blockquote>"
        )
        return
