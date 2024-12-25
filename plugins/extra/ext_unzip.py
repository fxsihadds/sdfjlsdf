import os
from asyncio import get_running_loop
from functools import partial
from pyrogram.types import InlineKeyboardButton
import logging as LOGGER
from helpers.exzip_helper import ExtractZip
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message

LOGGER.basicConfig(format="%(asctime)s - %(message)s", level=LOGGER.INFO)


@Client.on_message(filters.command("unzip"))
async def unzip_files(bot: Client, cmd: Message):
    if cmd.reply_to_message:
        output = f"Unzip_{cmd.from_user.id}"
        document = cmd.reply_to_message.document

        if (
            document.mime_type == "application/zip"
            or document.mime_type == "application/x-rar-compressed"
        ):
            msg = await cmd.reply_text("<b>⎚ `Downloading the ZIP file...`</b>")
            zip_file = await bot.download_media(document)
            await msg.edit("<b>⎚ `Extracting the ZIP file...`</b>")
            zip = ExtractZip(path=zip_file, output=output, password=None)
            zip.cleanup_macos_artifacts()

            await cmd.reply_text("Ready For Upload")
            for root, dirs, f_name in os.walk(output):
                for filename in f_name:
                    file_path = os.path.join(root, filename)
                    try:
                        await bot.send_document(chat_id=cmd.chat.id, document=file_path)
                        print(f"Sent: {file_path}")
                    except Exception as e:
                        print(f"Failed to send {file_path}: {e}")
                        shutil.rmtree(output)

            shutil.rmtree(output)

        elif cmd.reply_to_message and cmd.text:
            pwd = cmd.text.split()[1]
            msg = await cmd.reply_text("<b>⎚ `Downloading the ZIP file...`</b>")
            zip_file = await bot.download_media(document)
            await msg.edit("<b>⎚ `Extracting the ZIP file...`</b>")
            zip = ExtractZip(path=zip_file, output=output, password=pwd)
            zip.cleanup_macos_artifacts()
            await msg.edit_text("Ready For Upload")
            for root, dirs, f_name in os.walk(output):
                for filename in f_name:
                    file_path = os.path.join(root, filename)
                    try:
                        await bot.send_document(chat_id=cmd.chat.id, document=file_path)
                        print(f"Sent: {file_path}")
                    except Exception as e:
                        print(f"Failed to send {file_path}: {e}")
                        shutil.rmtree(output)

            shutil.rmtree(output)

    else:
        await cmd.reply_text("Please Reply with ZipFile /unzip pwd")
