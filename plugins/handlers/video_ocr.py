from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
from helpers._ocr_helpers import sub_images
from bot import LOGGER


@Client.on_message(
    filters.command("vocr") | filters.group | filters.video | filters.regex(r"vocr")
)
async def video_ocr(bot: Client, cmd: Message):
    ocr_images_store = f"ocrdict{cmd.from_user.id}"
    try:
        if cmd.video:
            if cmd.video:
                buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝗦𝘂𝗯𝘁𝗶𝘁𝗹𝗲 𝗘𝘅𝘁𝗿𝗮𝗰𝘁✍", callback_data="extract"
                            ),
                            InlineKeyboardButton(
                                text="𝗘𝘅𝘁𝗿𝗮𝗰𝘁 𝗠𝗲𝘁𝗮𝗱𝗮𝘁𝗮✍", callback_data="metadata"
                            ),
                            InlineKeyboardButton(
                                text="𝗘𝘅𝘁𝗿𝗮𝗰𝘁 𝗔𝘂𝗱𝗶𝗼", callback_data="extaudio"
                            ),
                            InlineKeyboardButton(
                                text="Split Video", callback_data="spvideo"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="Trim Video", callback_data="trimvideo"
                            ),
                            InlineKeyboardButton(text="🤖", url="https://t.me/Fxsihad"),
                            InlineKeyboardButton(text="🚫", callback_data="closed"),
                        ],
                    ]
                )
                await cmd.reply_video(video=cmd.video.file_id, reply_markup=buttons)

                # download = await bot.download_media(cmd.reply_to_message.video)
                # await sub_images(bot, status, download, ocr_images_store)
                # os.remove(download)
            elif (
                cmd.reply_to_message.document
                and cmd.reply_to_message.document.file_name.endswith((".mp4", ".mkv"))
            ):
                status = await cmd.reply_text("<b>⎚ `Downloading...`</b>")
                download = await bot.download_media(cmd.reply_to_message.document)
                os.remove(download)
                await sub_images(
                    bot, status, download, ocr_images_store
                )  # Ensure to await here
            else:
                await status.edit_text(
                    "Please Reply With Mp4 and Mkv Other format Not Support at this moment"
                )
                return
        else:
            await status.edit_text("Please reply with hardsub Video!")
            return
    except Exception as err:
        LOGGER.error(err)
