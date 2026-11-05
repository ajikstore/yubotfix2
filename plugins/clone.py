import os
import shutil
import tempfile
import random
from pathlib import Path

from kelra.helpers import CMD, Emoji

__MODULES__ = "Clone"
__HELP__ = """<blockquote>Command Help **Clone**</blockquote>

<blockquote expandable>    <u>**Clone someone's profile**</u>
        `{0}clone` [reply message/username/id]

    <u>**Return to your original profile**</u>
        `{0}unclone`

<b><u>**Note**: Use clone to copy someone's profile (name, bio, photo). Use unclone to restore your original profile.</u></blockquote></b>

<b>   {1}</b>
"""

# 🎆 Daftar efek emoji premium
BASIC_EFFECTS = [
    5046509860389126442,  # fireworks
    5104841245755180586,  # balloons
]

CLONED_USERS = {}
TEMP_DIR = None


def get_temp_dir():
    """Get or create temp directory for clone operations"""
    global TEMP_DIR
    if TEMP_DIR is None or not os.path.exists(TEMP_DIR):
        TEMP_DIR = tempfile.mkdtemp(prefix="clone_backup_")
    return TEMP_DIR


def cleanup_temp_files(user_id):
    """Clean up temporary files for specific user only"""
    temp_dir = get_temp_dir()
    pattern = f"backup_{user_id}_*"

    for file_path in Path(temp_dir).glob(pattern):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing temp file {file_path}: {e}")


def cleanup_all_temp():
    """Clean up all temporary files - ADMIN ONLY"""
    global TEMP_DIR
    if TEMP_DIR and os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            TEMP_DIR = None
        except Exception as e:
            print(f"Error cleaning up temp directory: {e}")


def extract_target_info(message):
    """Extract target user from message"""
    text = message.text.split()

    if message.reply_to_message:
        return message.reply_to_message.from_user
    elif len(text) > 1:
        return text[1]
    return None


async def backup_user_profile(client, user_id):
    """Backup current user profile data"""
    try:
        me = await client.get_me()
        backup_data = {"first_name": me.first_name, "last_name": me.last_name if me.last_name else "", "photos": [], "user_id": user_id}

        # Backup bio
        try:
            full = await client.get_chat(me.id)
            backup_data["bio"] = getattr(full, "bio", "")
        except Exception:
            backup_data["bio"] = ""

        # Backup profile photos
        try:
            temp_dir = get_temp_dir()
            photo_count = 0
            async for photo in client.get_chat_photos("me"):
                photo_path = await client.download_media(photo, file_name=os.path.join(temp_dir, f"backup_{user_id}_{photo_count}.jpg"))
                if photo_path:
                    backup_data["photos"].append(photo_path)
                    photo_count += 1
                    if photo_count >= 10:  # Limit backup photos
                        break
        except Exception as e:
            print(f"Error backing up photos: {str(e)}")

        return backup_data
    except Exception as e:
        print(f"Error in backup_user_profile: {str(e)}")
        return None


async def restore_user_profile(client, user_id):
    """Restore user's original profile"""
    try:
        if user_id not in CLONED_USERS:
            return False

        original = CLONED_USERS[user_id]

        # Delete current profile photos
        try:
            photos = []
            async for photo in client.get_chat_photos("me"):
                photos.append(photo.file_id)
            if photos:
                await client.delete_profile_photos(photos)
        except Exception as e:
            print(f"Error deleting photos: {str(e)}")

        # Restore profile info
        await client.update_profile(first_name=original["first_name"], last_name=original.get("last_name", ""), bio=original.get("bio", ""))

        # Restore profile photos
        if original.get("photos"):
            for photo_path in reversed(original["photos"]):
                try:
                    if os.path.exists(photo_path):
                        await client.set_profile_photo(photo=photo_path)
                except Exception as e:
                    print(f"Error setting photo {photo_path}: {str(e)}")

        # Clean up temp files for this user only
        cleanup_temp_files(user_id)
        del CLONED_USERS[user_id]

        return True
    except Exception as e:
        print(f"Error in restore_user_profile: {str(e)}")
        return False


async def clone_user_profile(client, target_user):
    """Clone target user's profile"""
    try:
        # Delete current profile photos
        try:
            photos = []
            async for photo in client.get_chat_photos("me"):
                photos.append(photo.file_id)
            if photos:
                await client.delete_profile_photos(photos)
        except Exception as e:
            print(f"Error deleting photos: {str(e)}")

        # Get target bio
        try:
            target_full = await client.get_chat(target_user.id)
            target_bio = getattr(target_full, "bio", "")
        except Exception:
            target_bio = ""

        # Update profile with target info
        await client.update_profile(first_name=target_user.first_name, last_name=target_user.last_name if target_user.last_name else "", bio=target_bio)

        # Clone profile photo
        try:
            temp_dir = get_temp_dir()
            async for photo in client.get_chat_photos(target_user.id):
                target_photo = await client.download_media(photo, file_name=os.path.join(temp_dir, f"clone_temp_{target_user.id}.jpg"))
                if target_photo:
                    await client.set_profile_photo(photo=target_photo)

                    # Clean up temp clone file immediately
                    try:
                        os.remove(target_photo)
                    except Exception:
                        pass
                break
        except Exception as e:
            print(f"Error cloning photo: {str(e)}")

        return True
    except Exception as e:
        print(f"Error in clone_user_profile: {str(e)}")
        return False


@CMD.UBOT("clone")
async def clone_handler(client, message):
    await handle_clone(client, message)


@CMD.UBOT("unclone")
async def unclone_handler(client, message):
    await handle_unclone(client, message)


async def handle_clone(client, message):
    em = Emoji(client)
    await em.get()

    proses_ = await em.get_costum_text()
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")

    user_id = message.from_user.id
    target_info = extract_target_info(message)

    if not target_info:
        return await msg.edit(
            f"{em.gagal}**Usage:**\n"
            "`clone` <reply message/username/id>\n"
            "`unclone` to restore original profile"
        )

    # Get target user
    try:
        if isinstance(target_info, str):
            target_user = await client.get_users(target_info)
        else:
            target_user = target_info
    except Exception:
        return await msg.edit(f"{em.gagal}**Invalid username/id provided.**")

    # Check if trying to clone bot owner
    try:
        from config import OWNER_ID
        if target_user.id == OWNER_ID:
            return await msg.edit(
                f"{em.gagal}**Cannot clone bot owner's profile.**\n"
                f"**Contact admin:** <a href=tg://openmessage?user_id={OWNER_ID}>admin</a>"
            )
    except ImportError:
        pass

    # If user already has a backup, restore first
    if user_id in CLONED_USERS:
        await msg.edit(f"{em.proses}**Restoring previous profile before cloning...**")
        await restore_user_profile(client, user_id)

    # Backup current profile before cloning
    backup_data = await backup_user_profile(client, user_id)
    if not backup_data:
        return await msg.edit(f"{em.gagal}**Failed to backup your profile. Please try again.**")

    CLONED_USERS[user_id] = backup_data

    # Clone target profile
    success = await clone_user_profile(client, target_user)
    await msg.delete()

    if success:
        target_name = f"{target_user.first_name} {target_user.last_name or ''}".strip()
        try:
            return await message.reply(
                f"{em.sukses}**Successfully cloned profile**\n"
                f"**Target:** <a href=tg://user?id={target_user.id}>{target_name}</a>\n"
                f"**Use** `unclone` **to restore your profile**",
                effect_id=random.choice(BASIC_EFFECTS),
            )
        except Exception:
            return await message.reply(
                f"{em.sukses}**Successfully cloned profile**\n"
                f"**Target:** <a href=tg://user?id={target_user.id}>{target_name}</a>\n"
                f"**Use** `unclone` **to restore your profile**",
            )
    else:
        cleanup_temp_files(user_id)
        if user_id in CLONED_USERS:
            del CLONED_USERS[user_id]

        try:
            return await message.reply(
                f"{em.gagal}**Failed to clone profile. Please try again.**",
                effect_id=random.choice(BASIC_EFFECTS),
            )
        except Exception:
            return await message.reply(
                f"{em.gagal}**Failed to clone profile. Please try again.**",
            )


async def handle_unclone(client, message):
    em = Emoji(client)
    await em.get()

    proses_ = await em.get_costum_text()
    msg = await message.reply(f"{em.proses}**{proses_[4]}**")

    user_id = message.from_user.id

    if user_id not in CLONED_USERS:
        return await msg.edit(
            f"{em.gagal}**No cloned profile found. Please clone a profile first.**"
        )

    success = await restore_user_profile(client, user_id)
    await msg.delete()

    if success:
        try:
            return await message.reply(
                f"{em.sukses}**Successfully restored your original profile.**",
                effect_id=random.choice(BASIC_EFFECTS),
            )
        except Exception:
            return await message.reply(
                f"{em.sukses}**Successfully restored your original profile.**",
            )
    else:
        try:
            return await message.reply(
                f"{em.gagal}**Failed to restore profile. Please try again.**",
                effect_id=random.choice(BASIC_EFFECTS),
            )
        except Exception:
            return await message.reply(
                f"{em.gagal}**Failed to restore profile. Please try again.**",
        )

# Auto cleanup on module unload (if supported by your framework)
def cleanup_on_exit():
    """Cleanup function to be called when module is unloaded"""
    cleanup_all_temp()
    CLONED_USERS.clear()
