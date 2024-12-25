import logging
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from helpers.display_progress import humanbytes

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
import os, requests, time

# from display_progress import humanbytes
from collections import defaultdict
from pyrogram import enums
from helpers.c_video import get_video_duration
from helpers.display_progress import progress_for_pyrogram

default_priority = 100
priority = {
    enums.MessageEntityType.BOLD: 1,
    enums.MessageEntityType.ITALIC: 2,
    enums.MessageEntityType.UNDERLINE: 3,
    enums.MessageEntityType.STRIKETHROUGH: 4,
    enums.MessageEntityType.SPOILER: 5,
    enums.MessageEntityType.CODE: 6,
    enums.MessageEntityType.PRE: 7,
    enums.MessageEntityType.TEXT_LINK: 8,
    enums.MessageEntityType.HASHTAG: 9,
}


def DetectFileSize(url):
    r = requests.get(url, allow_redirects=True, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    return total_size


async def get_parsed_msg(message_text, entities):
    if not entities:
        return message_text

    entity_dict = defaultdict(list)
    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length
        entity_dict[(start, end)].append(entity)

    last_end = 0
    result = []
    for (start, end), entities in sorted(entity_dict.items()):
        if start > last_end:
            result.append(message_text[last_end:start])
        formatted_text = message_text[start:end]
        entities.sort(
            key=lambda x: priority.get(x.type, default_priority), reverse=True
        )
        for entity in entities:
            if entity.type == enums.MessageEntityType.BOLD:
                formatted_text = f"**{formatted_text}**"
            elif entity.type == enums.MessageEntityType.ITALIC:
                formatted_text = f"__{formatted_text}__"
            elif entity.type == enums.MessageEntityType.UNDERLINE:
                formatted_text = f"--{formatted_text}--"
            elif entity.type == enums.MessageEntityType.STRIKETHROUGH:
                formatted_text = f"~~{formatted_text}~~"
            elif entity.type == enums.MessageEntityType.SPOILER:
                formatted_text = f"||{formatted_text}||"
            elif entity.type == enums.MessageEntityType.CODE:
                formatted_text = f"`{formatted_text}`"
            elif entity.type == enums.MessageEntityType.PRE:
                formatted_text = f"```{formatted_text}```"
            elif entity.type == enums.MessageEntityType.TEXT_LINK:
                formatted_text = f"[{formatted_text}]({entity.url})"
            elif entity.type == enums.MessageEntityType.HASHTAG:
                formatted_text = f"{formatted_text}"

        result.append(formatted_text)
        last_end = end

    if last_end < len(message_text):
        result.append(message_text[last_end:])

    return "".join(result)


# Helper function to handle media groups
async def processMediaGroup(user, chat_id, message_id, bot, message):
    media_group_messages = await user.get_media_group(chat_id, message_id)
    media_list = []

    for msg in media_group_messages:
        if msg.photo:
            media_list.append(
                InputMediaPhoto(
                    media=msg.photo.file_id,
                    caption=await get_parsed_msg(
                        msg.caption or "", msg.caption_entities
                    ),
                )
            )
        elif msg.video:
            media_list.append(
                InputMediaVideo(
                    media=msg.video.file_id,
                    caption=await get_parsed_msg(
                        msg.caption or "", msg.caption_entities
                    ),
                )
            )

    if media_list:
        await bot.send_media_group(chat_id=message.chat.id, media=media_list)
        return True
    return False


def getChatMsgID(url: str):
    """
    Extracts chat ID and message ID from a Telegram message URL.

    Args:
        url (str): The Telegram message URL.

    Returns:
        tuple: A tuple containing the chat ID (str or int) and the message ID (int).
    """
    parts = url.split("/")
    if "t.me/c/" in url:
        chat_id = int("-100" + parts[-2])
    else:
        chat_id = parts[-2]

    message_id = int(parts[-1])
    return chat_id, message_id


# Maximum file size limit to 2GB
MAX_FILE_SIZE = (
    2 * 1024 * 1024 * 1024
)  # If your telegram account is premium then use 4GB


def chkFileSize(file_size):
    return file_size <= MAX_FILE_SIZE


async def fileSizeLimit(file_size, message, action_type="download"):
    if not chkFileSize(file_size):
        await message.reply(
            f"The file size exceeds the {MAX_FILE_SIZE / (1024 * 1024 * 1024):.2f}GB limit and cannot be {action_type}ed."
        )
        return False
    return True


def DownLoadFile(url, file_name, chunk_size, client, ud_type, message_id, chat_id):
    if os.path.exists(file_name):
        os.remove(file_name)
    if not url:
        return file_name
    r = requests.get(url, allow_redirects=True, stream=True)
    # https://stackoverflow.com/a/47342052/4723940
    total_size = int(r.headers.get("content-length", 0))
    downloaded_size = 0
    with open(file_name, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
                downloaded_size += chunk_size
            if client is not None:
                if ((total_size // downloaded_size) % 5) == 0:
                    time.sleep(0.3)
                    try:
                        client.edit_message_text(
                            chat_id,
                            message_id,
                            text="{}: {} of {}".format(
                                ud_type,
                                humanbytes(downloaded_size),
                                humanbytes(total_size),
                            ),
                        )
                    except:
                        pass
    return file_name


async def send_media(
    bot, message, media_path, media_type, caption, progress_message, file_name, start_time
):
    file_size = os.path.getsize(media_path)

    if not await fileSizeLimit(file_size, message, "upload"):
        return

    

    progress_args = ("<b>⎚ Uploading File...</b>", progress_message, file_name,start_time)

    if media_type == "photo":
        await message.reply_photo(
            media_path,
            caption=caption or "",
            progress=progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "video":
        durations = get_video_duration(media_path)
        await message.reply_video(
            media_path,
            caption=caption or "",
            duration=durations,
            progress=progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "audio" or media_type == "audio":
        await message.reply_audio(
            media_path,
            caption=caption or "",
            progress=progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "document" or media_type == "document":
        await message.reply_document(
            media_path,
            caption=caption or "",
            progress=progress_for_pyrogram,
            progress_args=progress_args,
        )


"""async def progress_for_pyrogram(current, total, up_down, progress_message, start_time):
    elapsed_time = time.time() - start_time
    percentage = (current / total) * 100
    speed = current / elapsed_time if elapsed_time > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0

    await progress_message.edit_text(
        f"📥 {up_down} Progress:\n"
        f"✅ {percentage:.2f}%\n"
        f"📦 {current / 1024 / 1024:.2f} MB of {total / 1024 / 1024:.2f} MB\n"
        f"⚡ Speed: {speed / 1024:.2f} KB/s\n"
        f"⏳ ETA: {eta:.2f} seconds"
    )"""
