"""import requests
import imgkit
from pyrogram import Client, filters


@Client.on_message(filters.command("screenshot"))
async def screenshot(client, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /screenshot <URL>")
        return

    url = message.command[1]

    try:
        response = requests.get(url)
        if response.status_code == 200:
            imgkit.from_url(url, 'screenshot.jpg')
            await message.reply_photo('screenshot.jpg')
        else:
            await message.reply_text("Failed to retrieve the webpage.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
"""