from pyrogram import Client, filters
from pyrogram.types import Message
import os
import shutil
import zipfile
import tempfile
import patoolib as unzip
import traceback


@Client.on_message(filters.command('unzips') & filters.private)
async def handle_file(bot: Client, cmd: Message):
    if cmd.reply_to_message and cmd.reply_to_message.document:
        pswd = cmd.text.split('/unzips')[1]
        document = cmd.reply_to_message.document
        try:
            if document.mime_type == 'application/zip':
                download_message = await cmd.reply_text("<b>⎚ `Downloading the ZIP file...`</b>")
                main_file = await bot.download_media(document)
                await download_message.edit("<b>⎚ `Extracting the ZIP file...`</b>")

                try:
                    with zipfile.ZipFile(main_file, 'r', allowZip64=True) as zip_ref:
                        unzip_dir = os.path.join(
                            tempfile.gettempdir(), 'unzipped')
                        os.makedirs(unzip_dir, exist_ok=True)
                        zip_ref.extractall(unzip_dir, pwd=bytes(pswd, 'utf-8'))
                        await download_message.edit("<b>⎚ `Sending the extracted files...`</b>")

                        for root, _, files in os.walk(unzip_dir):
                            for file_name in files:
                                file_path = os.path.join(root, file_name)
                                await bot.send_document(
                                    chat_id=cmd.chat.id,
                                    document=file_path
                                )
                    os.remove(main_file)
                    shutil.rmtree(unzip_dir)
                    await download_message.edit("<b>All files have been extracted and sent successfully.</b>")
                except zipfile.BadZipFile:
                    await download_message.edit("The file you sent is not a valid ZIP file.")
                    os.remove(main_file)
            else:
                download_message = await cmd.reply_text("<b>⎚ `Downloading the RAR file...`</b>")
                main_file = await bot.download_media(document)
                await download_message.edit("<b>⎚ `Extracting the RAR file...`</b>")
                try:
                    unzip_dir = os.path.join(tempfile.gettempdir(), 'unzipped')
                    os.makedirs(unzip_dir, exist_ok=True)
                    unzip.extract_archive(
                        main_file, outdir=unzip_dir, verbosity=1, interactive=True, password=pswd)
                    await download_message.edit("<b>⎚ `Sending the extracted files...`</b>")

                    for root, _, files in os.walk(unzip_dir):
                        for file_name in files:
                            file_path = os.path.join(root, file_name)
                            await bot.send_document(
                                chat_id=cmd.chat.id,
                                document=file_path
                            )

                    os.remove(main_file)
                    shutil.rmtree(unzip_dir)
                    await download_message.edit("<b>All files have been extracted and sent successfully.</b>")
                except Exception as e:
                    await download_message.edit("Error occurred during RAR extraction.")
                    traceback.print_exc()
                    os.remove(main_file)

        except Exception as e:
            await cmd.reply(f"<b>An error occurred: {e}</b>")
    else:
        await cmd.reply_text("<b>Please reply to a ZIP or RAR file.</b>")
