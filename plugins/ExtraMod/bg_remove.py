"""from pyrogram import Client, filters
from pyrogram.types import Message
import os
from rembg import remove
from PIL import Image
import asyncio  # Import asyncio module

@Client.on_message(filters.command("remv", ['.', '/']))
async def remove_background(bot: Client, cmd: Message):
    status = await cmd.reply_text('<b>⎚ `Removing...`</b>')
    try:
        if cmd.reply_to_message and (cmd.reply_to_message.document or cmd.reply_to_message.photo):
            file_path = await bot.download_media(cmd.reply_to_message.document or cmd.reply_to_message.photo)
            file_dir = "downloads"
            for i in os.listdir(file_dir):
                if i.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
                    image_path = os.path.join(file_dir, i)
                    asyncio.create_task(bg_remove(bot, status, image_path))  # Run background removal function concurrently
                else:
                    os.remove(file_path)
                    await status.edit_text('<b>`Please Provide Photos! `</b>')
        else:
            await status.edit_text('<b>`Please Reply With Photo For Remove Background!`</b>')

    except Exception as e:
        await status.edit_text(f'<b>Error: {e}</b>')
        print(e)

# This is Functions for Remove Background from Photos
async def bg_remove(bot, status, file_path):
    try:
        input_image = Image.open(file_path)
        output_image = remove(input_image)
        file_name, file_extension = os.path.splitext(
            os.path.basename(file_path))
        save_path = f'{file_name}_no_bg.png'
        output_image.save(save_path)
        await bot.send_photo(
            chat_id=status.chat.id, 
            photo=save_path
            )
        os.remove(save_path)
        os.remove(file_path)
        await status.edit_text('<b>✅ Background Removed Successfully!</b>')

    except Exception as e:
        await status.edit_text(f'<b>Error: {e}</b>')"""

