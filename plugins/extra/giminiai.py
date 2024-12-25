import os
import google.generativeai as genai
import PIL.Image
from pyrogram import Client, filters
from pyrogram.types import Message
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
GOOGLE_API_KEY = config['GOOGLE']['GOOGLE_API_KEY']


@Client.on_message(filters.command("gemi"))
async def gemini_ai(bot: Client, cmd: Message):
    global status
    images_path = "downloads"
    status = await cmd.reply_text("<b>⎚ `Generating...`</b>")
    user_redeem = cmd.text.split("/gemi", 1)[1].strip()
    if user_redeem:
        if cmd.reply_to_message and cmd.reply_to_message.text and user_redeem:
            await geminiai_text(bot, cmd, text=user_redeem + cmd.reply_to_message.text)
        else:
            await geminiai_text(bot, cmd, text=user_redeem)
    elif cmd.reply_to_message:
        if cmd.reply_to_message.document or cmd.reply_to_message.photo and user_redeem:
            download = await bot.download_media(cmd.reply_to_message.photo or cmd.reply_to_message.document)
            data = await gemini(bot=bot, cmd=cmd, image_path=user_redeem + images_path)
            os.remove(download)
        elif cmd.reply_to_message.document or cmd.reply_to_message.photo:
            download = await bot.download_media(cmd.reply_to_message.photo or cmd.reply_to_message.document)
            data = await gemini(bot=bot, cmd=cmd, image_path=images_path)
            os.remove(download)
        else:
            await status.edit_text("Please Provide Photos or Text")
    else:
        await status.edit_text("Please Provide Photos or Text")


# This Functions is for text generating
async def geminiai_text(bot, cmd, text):
    if GOOGLE_API_KEY is None:
        print('Api key is Not Found!')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(text)
    await status.edit_text(
        response.text
    )

# This  Functions for Images Proccessing!
async def gemini(bot, cmd, image_path):
    # Check if the API key is available
    if GOOGLE_API_KEY is None:
        print("API key not found. Please set the GOOGLE_API_KEY environment variable.")
        exit(1)
    # Configure the API key for Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    # Example: Generate text from text input
    # model = genai.GenerativeModel('gemini-pro')
    model = genai.GenerativeModel('gemini-pro-vision')
    for main_file in os.listdir(image_path):
        if main_file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            images_file = os.path.join(image_path, main_file)
            img = PIL.Image.open(images_file)
            # response = model.generate_content("Who is the greatest Person in The world?")
            response = model.generate_content(img)
            # print(response.text)  # Displaying text directly in the console
            await status.edit_text(
                response.text
            )
