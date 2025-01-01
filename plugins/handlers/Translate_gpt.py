from pyrogram import Client, filters
from pyrogram.types import Message
import json
import requests
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InputMediaPhoto,
)


@Client.on_message(filters.command("gpt", ["/", "."]))
async def translate_text(client, cmd: Message):
    global text
    # Extract text from the command or replied message
    if cmd.reply_to_message and cmd.reply_to_message.text:
        text = cmd.reply_to_message.text
    elif len(cmd.text.split(maxsplit=1)) > 1:
        text = cmd.text.split(maxsplit=1)[1]
    else:
        await cmd.reply("`No text provided.`")
        return

    # Check for text length
    if len(text) > 5000:
        await cmd.reply("`Text is too long. Please provide shorter text.`")
        return

    # Perform translation
    translated_text = perform_translation(text)
    buttton = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("RE TRANSLATE", callback_data="gentr")],
        ]
    )
    await cmd.reply(
        translated_text,
        disable_web_page_preview=True,
        disable_notification=True,
        reply_markup=buttton,
    )


def perform_translation(text):
    url = "https://dali.novana.digital/translate-auto"
    payload = {"to": "Bengali", "text": text}
    headers = {
        "User-Agent": "Dart/3.2 (dart:io)",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer M92ii5PED6iRAxp2jRn2",
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            message = response_data[0].get("message", {})
            return message.get("content", "Translation result not found.")
        else:
            return f"Translation failed with status code {response.status_code}."
    except Exception as e:
        return f"An error occurred: {str(e)}"


async def Translate_text(_, callback_query):
    translated_text = perform_translation(text)
    buttton = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("RE TRANSLATE", callback_data="gentr")],
        ]
    )
    # await callback_query.edit_message_media(media=InputMediaPhoto(media=photo),reply_markup=keyboard)
    await callback_query.edit_message_caption(
        caption=translated_text, reply_markup=buttton
    )
