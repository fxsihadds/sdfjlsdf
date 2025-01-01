import requests
import json, os
from pyrogram import Client, filters
from pyrogram.types import Message

url = "https://aiapi-art.begamob.com/api/v1/generate_art"

headers = {
    "User-Agent": "VersionApp:34.4.1/AppId:com.chatbot.ai.aichat.openaibot.chat/Build:344100/VersionSDK:29/OS:Android/UserAgent:okhttp/5.0.0-alpha.3",
    "Accept-Encoding": "gzip",
    "authorization": "Bearer f4e3eba2a27a116edbc57622b835ee25",
    "timestamp": "1735674309846",
    "openai-organization": "org-TNpumOGtx3mOb6olZMTQS7zo",
    "content-type": "application/json; charset=UTF-8",
}


@Client.on_message(filters.command("genimg", ["/", "."]))
async def generate_image(_, cmd: Message):
    status = await cmd.reply_text("`Generating image...`")
    prompt_text = (
        cmd.text.split(maxsplit=1)[1]
        if len(cmd.text.split()) > 1
        else "A beautiful landscape painting"
    )

    payload = {
        "aspect_ratio": "1:1",
        "cfg": 7.5,
        "model_id": 34,
        "prompt": prompt_text,
        "style_id": 0,
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        data = response.json()
        binary_data = data.get("data", [])
        if binary_data:
            byte_data = bytes(
                (value + 256 if value < 0 else value) for value in binary_data
            )
            image_path = "output_image.jpg"
            with open(image_path, "wb") as img_file:
                img_file.write(byte_data)
            await cmd.reply_photo(
                photo=image_path, caption="Here is Your Generated Images!", quote=True
            )
            await status.delete()
            os.remove(image_path)
        else:
            await status.edit_text("`No image data found in the response.`")
    else:
        await status.edit_text(f"Error: {response.status_code} - {response.text}")
