import os
import json
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
}

# Function to upload text to Pastebin
async def upload_to_pastebin(message, extension=None):
    pastebin_url = "https://pasty.lus.pm/api/v1/pastes"
    data = {"content": message}
    try:
        response = requests.post(
            url=pastebin_url, data=json.dumps(data), headers=headers)
    except Exception as e:
        return {"error": str(e)}
    if response.ok:
        response_data = response.json()
        paste_url = (
            f"https://pasty.lus.pm/{response_data['id']}.{extension}"
            if extension
            else f"https://pasty.lus.pm/{response_data['id']}.txt"
        )
        return {
            "url": paste_url,
            "raw": f"https://pasty.lus.pm/{response_data['id']}/raw",
            "bin": "Pasty",
        }
    return {"error": "Unable to reach pasty.lus.pm"}

@Client.on_message(filters.command(["paste"]))
async def paste_command(client: Client, message: Message):
    text_to_paste = message.text
    if ' ' in message.text:
        text_to_paste = message.text.split(" ", 1)[1]
    elif message.reply_to_message:
        text_to_paste = message.reply_to_message.text
    else:
        await message.reply("<b>⎚ Please use <code>/paste text to upload to Pastebin</code></b>")
        return

    response_message = await message.reply_text("<b>⎚ `Uploading to Pastebin...`</b>")

    extension = "txt"
    paste_info = await upload_to_pastebin(text_to_paste, extension)
    paste_url = paste_info["url"]
    paste_raw_url = paste_info["raw"]

    pasted_message = f"""<b>
━━━━━━━━━━━
⎚ Online Text

⎚ Link : 
⎚  • [Click here]({paste_url})
━
⎚ Raw Link: 
⎚ • [Click here (Raw)]({paste_raw_url})

⎚ Status: Valid ✅
━━━━━━━━━━━
⎚ Created by <b>Unknown</b>
</b> 
"""
    await response_message.edit(pasted_message, disable_web_page_preview=True)
