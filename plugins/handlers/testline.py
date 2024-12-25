from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import os
import subprocess
from helpers.display_progress import progress_for_pyrogram
from time import perf_counter
import time
from helpers.timemanager import (
    run_sync_in_thread_new_loop,
    run_sync_in_thread_running_loop,
)
import chardet
from bot import user, LOGGER


@Client.on_message(filters.document)
async def line_scraper(bot: Client, cmd: Message):
    if cmd.reply_to_message or cmd.document or cmd.reply_to_message.document:
        # status = await cmd.reply_text('<b>⎚ `Processing...`</b>')
        STATUS_ID = "<b>⎚ `Downloading The Text File...`</b>"
        document = cmd.document
        if document.mime_type == "text/plain":

            try:
                buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝗨lp-𝗘𝘅𝘁✍", callback_data="ulpextract"
                            ),
                            InlineKeyboardButton(
                                text="𝗖𝗼𝗻𝘃𝗲𝗿𝘁✍", callback_data="fmetadata"
                            ),
                            InlineKeyboardButton(
                                text="𝗘𝗫𝗧 𝗙𝗜𝗟𝗘", callback_data="fextaudio"
                            ),
                        ],
                        [
                            InlineKeyboardButton(text="🤖", url="https://t.me/Fxsihad"),
                            InlineKeyboardButton(text="🚫", callback_data="closed"),
                        ],
                    ]
                )
                await cmd.reply_document(
                    document=cmd.document.file_id, reply_markup=buttons
                )
                # await cmd.reply_to_message.download(file_name=file_path, progress=progress_for_pyrogram, progress_args=(STATUS_ID, status, file_name, start_time))
                # await cmd.reply_to_message.download(file_name=file_path, progress=progress_for_pyrogram, progress_args=(STATUS_ID, status, file_name, start_time))
                # await find_strings_from_txt(find_str, file_path, status, bot)
            except Exception as e:
                await cmd.reply(f"<b>Error Bot: {e}</b>")
        else:
            await cmd.reply("<b>Please send a text file with your finder string</b>")
    else:
        await cmd.reply_text("<b>Please send a text file for lines!</b>")


@run_sync_in_thread_running_loop
def find_strings_from_txt(find_str, file_path, status, bot):
    status.edit_text("<b>⎚ `Extracting The Text File...`</b>")
    output_file = f"{find_str} ulp.txt"
    try:
        start_time = perf_counter()
        # Using subprocess to run grep command with case insensitivity
        grep_process = subprocess.Popen(
            ["grep", "-i", find_str, file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )

        output_lines, errors = grep_process.communicate()
        if grep_process.returncode == 0:
            if output_lines:
                # Writing the output to a file
                with open(output_file, "w", encoding="utf-8") as new_file:
                    new_file.write(output_lines)
                end_time = perf_counter()
                bot.send_document(
                    status.chat.id,
                    document=output_file,
                    caption=f"Took {end_time-start_time:.3f} seconds",
                )
                status.delete()
                os.remove(file_path)
                os.remove(output_file)
            else:
                status.edit_text("Your Domain Or STR Not Found In Your Text File!")
                os.remove(file_path)
        else:
            status.edit_text(f"Error occurred Maybe Keyword Not Found: {errors}")
            os.remove(file_path)
    except (
        UnicodeDecodeError,
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        subprocess.SubprocessError,
    ):
        try:
            start_time = perf_counter()
            # Using subprocess to run grep command with case insensitivity
            with open(file_path, "rb") as file:
                raw = file.read(1048576)
                results = chardet.detect(raw)
                encodes = results["encoding"]
            grep_process = subprocess.Popen(
                ["grep", "-i", find_str, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding=encodes,
            )

            output_lines, errors = grep_process.communicate()
            if grep_process.returncode == 0:
                if output_lines:
                    # Writing the output to a file
                    with open(output_file, "w", encoding="utf-8") as new_file:
                        new_file.write(output_lines)

                    end_time = perf_counter()

                    bot.send_document(
                        status.chat.id,
                        document=output_file,
                        caption=f"Took {end_time-start_time:.3f} seconds",
                    )
                    status.delete()
                    os.remove(file_path)
                    os.remove(output_file)
                else:
                    status.edit_text("Your Domain Or STR Not Found In Your Text File!")
                    os.remove(file_path)
            else:
                status.edit_text(f"Error Occurred Maybe Keyword Not Found: {errors}")
                os.remove(file_path)
        except Exception as e:
            status.edit_text(f"Error Occurred: {errors}")
            os.remove(file_path)
