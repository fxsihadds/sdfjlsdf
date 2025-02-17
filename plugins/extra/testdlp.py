# under devolpement
import os
import time
from random import randint
import yt_dlp
import logging
import asyncio
import time
import math
from bot import LOGGER
from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.c_video import get_file_size, get_video_duration, thumbnail_video
from helpers.timemanager import get_or_create_event_loop
from helpers.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from userc import user, LOGGER
from config import Config


class Translation(object):
    DISPLAY_PROGRESS = """[{0}{1}] {2}%
<i>📁 {3}</i>

<b>🔹Finished ✅:</b> <i>{4} of {5}</i>
<b>🔹Speed 🚀:</b> <i>{6}/s</i>
<b>🔹Time left 🕒:</b> <i>{7}</i>"""


# Create a ThreadPoolExecutor
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop = asyncio.get_event_loop()


@Client.on_message(filters.command("link"))
async def register_command(client: Client, message: Message):
    dl_path = f"your_download/{message.chat.id}/{randint(1, 20)}"
    urls = message.text.split("/link", 1)[1].strip()
    if not urls:
        await message.reply("<b>⎚ Use <code>/link</code> Url To Download Your File</b>")
    else:

        await handle_user_request(urls, message, dl_path)
        await client.delete_messages(chat_id=message.chat.id, message_ids=[message.id])


async def handle_user_request(urls, name, message, dl_path):
    await asyncio.gather(
        loop.run_in_executor(None, download_and_upload, urls, name, message, dl_path)
    )


def download_and_upload(urls, name, message, dl_path):
    asyncio.run(download_file(urls, name, message, dl_path))
    asyncio.run(upload_files(dl_path, message))


def progress_callback(progress, status):
    display_message = ""
    if progress["status"] == "downloading":
        now = time.time()
        diff = now - start_time
        downloaded = progress.get("downloaded_bytes")
        file_name = progress.get("filename")
        total_length = progress.get("total_bytes")
        if round(diff % 5.00) == 0 or downloaded == total_length:
            percentage = downloaded * 100 / total_length
            speed = downloaded / diff
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total_length - downloaded) / speed) * 1000
            estimated_total_time = elapsed_time + time_to_completion
            try:
                current_message = (
                    "<b>Downloading to my server... 📥</b>\n"
                    + Translation.DISPLAY_PROGRESS.format(
                        "".join(["●" for i in range(math.floor(percentage / 5))]),
                        "".join(["○" for i in range(20 - math.floor(percentage / 5))]),
                        round(percentage, 2),
                        file_name.split("/")[-1],
                        humanbytes(downloaded),
                        humanbytes(total_length),
                        humanbytes(speed),
                        (
                            TimeFormatter(time_to_completion)
                            if time_to_completion != ""
                            else "0 s"
                        ),
                    )
                )
                if current_message != display_message:
                    status.edit_text(current_message)
                    display_message = current_message
            except Exception as e:
                print("Error updating message:", e)


async def download_file(urls, name, message, output_dir="."):
    global start_time, display_message
    start_time = time.time()
    display_message = ""
    status = await message.reply("<b>⎚ `Downloading...`</b>")
    if "bongobd" in urls:
        ydl_opts = {
            "outtmpl": os.path.join(output_dir, f"{name}.mp4"),
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",  # Convert video format
                    "preferedformat": "mp4",  # Convert to mp4
                }
            ],
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
                "Referer": "https://bongobd.com/",
            },
        }
    else:
        ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "format": "best",
            "progress_hooks": [lambda p: progress_callback(p, status)],
            "cookiefile": "helpers/cookie.txt",
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # status = await message.reply("<b>⎚ `Downloading...`</b>")
        try:
            # Run blocking call in a separate thread
            await asyncio.to_thread(ydl.extract_info, urls)
            await status.delete()
        except yt_dlp.utils.DownloadError as e:
            LOGGER.error(e)
            await message.reply(str("Something Went Wrong"))
            await status.delete()


async def upload_files(dl_path, message):
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    dldirs = [i async for i in absolute_paths(dl_path)]

    for files in dldirs:
        success = await send_media(files, message)
        if success:
            await asyncio.sleep(1)
            os.remove(files)
        else:
            # await message.reply("<b>Error Uploading The File</b>")
            print("Maybe File handle Error")
            os.remove(files)


async def absolute_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


async def send_media(file_name, update):
    try:
        if os.path.isfile(file_name):
            start_time = time.time()
            caption = file_name if "/" not in file_name else file_name.split("/")[-1]
            captionss = os.path.basename(file_name)
            progress_argss = "<b>⎚ Uploading File...</b>"
            info_msg = await update.reply("<b>⎚ `Uploading...`</b>")
            size = get_file_size(file_name)
            if size:
                durations = get_video_duration(file_name)
                thumbs = thumbnail_video(file_name)
                if file_name.lower().endswith(
                    (
                        ".mkv",
                        ".mp4",
                        ".avi",
                        ".mov",
                        ".wmv",
                        ".flv",
                        ".webm",
                        ".m4v",
                        ".mpeg",
                        ".3gp",
                        ".ogg",
                    )
                ):
                    if Config.IS_PREMIUM:
                        await user.send_video(
                            chat_id=update.chat.id,
                            video=file_name,
                            caption=captionss,
                            thumb=thumbs,
                            duration=durations,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                progress_argss,
                                info_msg,
                                captionss,
                                start_time,
                            ),
                        )
                    else:
                        await update.reply_video(
                            file_name,
                            caption=captionss,
                            thumb=thumbs,
                            duration=durations,
                            quote=True,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                progress_argss,
                                info_msg,
                                captionss,
                                start_time,
                            ),
                        )
                        os.remove(thumbs)
                elif file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    await update.reply_photo(
                        file_name,
                        caption=captionss,
                        quote=True,
                        progress=progress_for_pyrogram,
                        progress_args=(progress_argss, info_msg, captionss, start_time),
                    )
                elif file_name.lower().endswith(".mp3"):
                    await update.reply_audio(
                        file_name,
                        caption=captionss,
                        quote=True,
                        progress=progress_for_pyrogram,
                        progress_args=(progress_argss, info_msg, captionss, start_time),
                    )
                else:
                    if Config.IS_PREMIUM:
                        await user.send_document(
                            chat_id=update.chat.id,
                            document=file_name,
                            caption=captionss,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                progress_argss,
                                info_msg,
                                captionss,
                                start_time,
                            ),
                        )
                    else:

                        await update.reply_document(
                            file_name,
                            caption=captionss,
                            quote=True,
                            progress=progress_for_pyrogram,
                            progress_args=(
                                progress_argss,
                                info_msg,
                                captionss,
                                start_time,
                            ),
                        )

                await info_msg.delete()

                return True
            else:
                await info_msg.edit("<b>Your File is To Big!</b>")
        else:
            logging.error(f"File not found: {file_name}")
    except Exception as e:
        logging.error(f"Error sending media: {str(e)}")
        return False
