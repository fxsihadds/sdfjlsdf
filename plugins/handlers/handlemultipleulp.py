from pyrogram import Client, filters
from pyrogram.types import Message
import os
import subprocess
from helpers.display_progress import progress_for_pyrogram
from time import perf_counter
import time
import chardet
from helpers.timemanager import run_sync_in_thread_running_loop
import wget


@Client.on_message(filters.command("ulpscr", ["/", "."]))
async def line_scraper(bot: Client, cmd: Message):
    if len(cmd.command) < 3:
        await cmd.reply_text("<b>Please provide a URL and a keyword.</b>")
        return

    url = cmd.command[1]
    find_str = cmd.command[2]
    status = await cmd.reply_text("<b>⎚ `Downloading The Text File...`</b>")

    try:
        user_folder = f"downloads/{cmd.from_user.id}"
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        file_path = os.path.join(user_folder, "downloaded_file.txt")
        await find_strings_from_txt(url, find_str, file_path, status, bot)
        os.remove(file_path)
    except Exception as e:
        await status.edit_text(f"<b>Error Bot: {e}</b>")
        if os.path.exists(file_path):
            os.remove(file_path)


@run_sync_in_thread_running_loop
def find_strings_from_txt(url, find_str, file_path, status, bot):
    status.edit_text("<b>⎚ `Extracting The Text File...`</b>")
    output_file = f"{find_str} ulp.txt"
    try:
        start_time = perf_counter()
        wget.download(url, file_path)
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
                    caption=f"Take {end_time-start_time:.3f} seconds",
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
                        caption=f"Take {end_time-start_time:.3f} seconds",
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
