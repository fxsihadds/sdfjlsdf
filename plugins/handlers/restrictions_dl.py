from pyrogram import filters, Client
from pyrogram.types import Message
from userc import user
from pyrogram.errors import (
    PeerIdInvalid,
    ChannelIdInvalid,
    ChannelInvalid,
    InviteHashInvalid
)

from helpers.help_uploadbot import (
    getChatMsgID,
    fileSizeLimit,
    get_parsed_msg,
    processMediaGroup,
)
import time, os
from helpers.help_uploadbot import send_media
from helpers.display_progress import progress_for_pyrogram


@Client.on_message(filters.command("dl", ['/', '.']) & filters.private)
async def download_media(bot, message: Message):
    if len(message.command) < 2:
        await message.reply("Provide a post URL after the /dl command.")
        return

    post_url = message.command[1]

    try:
        chat_id, message_id = getChatMsgID(post_url)

        # Fetch the chat message
        chat_message = await user.get_messages(chat_id, message_id)

        # Check file size for media
        if chat_message.document or chat_message.video or chat_message.audio:
            file_size = (
                chat_message.document.file_size
                if chat_message.document
                else (
                    chat_message.video.file_size
                    if chat_message.video
                    else chat_message.audio.file_size
                )
            )
            print(file_size)

            if not await fileSizeLimit(file_size, message, "download"):
                return

        # Parse caption and text
        parsed_caption = await get_parsed_msg(
            chat_message.caption or "", chat_message.caption_entities
        )
        print(parsed_caption)
        parsed_text = await get_parsed_msg(
            chat_message.text or "", chat_message.entities
        )

        # Check if the message has media or document
        if chat_message.media or chat_message.document:
            start_time = time.time()  # Corrected to use time.time()
            progress_message = await message.reply("Scraping...")
            file_name = (
                chat_message.document.file_name
                if chat_message.document
                else (
                    chat_message.video.file_name
                    if chat_message.video
                    else (
                        chat_message.audio.file_name
                        if chat_message.audio
                        else "Unknown"
                    )
                )
            )

            # Proceed with downloading the file
            media_path = await chat_message.download(
                progress=progress_for_pyrogram,
                progress_args=(
                    "<b>Downloading to my server... 📥</b>",
                    progress_message,
                    file_name,
                    start_time,
                ),
            )

            # Determine media type
            media_type = (
                "photo"
                if chat_message.photo
                else (
                    "video"
                    if chat_message.video
                    else "audio" if chat_message.audio else "document"
                )
            )
            await send_media(
                bot,
                message,
                media_path,
                media_type,
                parsed_caption,
                progress_message,
                file_name,
                start_time,
            )

            os.remove(media_path)
            await progress_message.delete()

        elif chat_message.text or chat_message.caption:
            await message.reply(parsed_text or parsed_caption)
        else:
            await message.reply("No media or text found in the post URL.")

    except (PeerIdInvalid, ChannelIdInvalid, ChannelInvalid):
        try:
            # Inform the user to send the invite link
            await message.reply(
                "Maybe this is a private channel!\nYou need to join via an invite link."
            )

            # Ask the user for the invite link
            response = await bot.ask(
                chat_id=message.from_user.id,
                text="Please send the invite link:",
                timeout=20,
                filters=filters.text
                & filters.regex(r"(https:\/\/t\.me\/(joinchat\/|\+)[a-zA-Z0-9_-]+)"),
            )

            # Join the channel using the invite link
            try:
                join_channel = await user.join_chat(response.text)
                await message.reply_text(
                    f"Successfully joined the chat: {join_channel.title}"
                )
            except InviteHashInvalid:
                await message.reply_text(
                    "The invite link is invalid. Please check and try again."
                )
        except TimeoutError:
            await message.reply_text("You didn't respond in time. Try again.")
        except Exception as e:
            await message.reply_text(f"Maybe Timeout Err: {e}")

    except Exception as e:
        error_message = f"Failed to download the media: {str(e)}"
        await message.reply(error_message)
