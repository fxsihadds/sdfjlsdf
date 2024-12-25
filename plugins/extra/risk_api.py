from pyrogram import Client, filters
from pyrogram.types import Message
from helpers.video_meta_data import META


@Client.on_message(filters.command("/ext"))
async def sihad_new(bot: Client, cmd: Message):
    try:
        # user = cmd.text.split("/ext")[1]
        if cmd.reply_to_message.video or cmd.reply_to_message.document:
            file = await cmd.download(cmd.reply_to_message)
            v1 = META(file)
            result = v1.meta_data_extract()
            print(result)
    except ValueError:
        await cmd.reply_text("Use CMD")
