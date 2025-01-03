from pyrogram import Client, filters
from pyrogram.types import Message


def write_text(text):
    with open("temp.txt", "w+", encoding="utf-8") as temp_file:
        temp_file.write(text)
    return "temp.txt"


@Client.on_message(filters.command("txt", ["/", "."]))
async def text_cmd(bot: Client, cmd: Message):
    if cmd.reply_to_message and cmd.reply_to_message.text:
        text_to_write = cmd.reply_to_message.text
    elif cmd.text:
        text_to_write = cmd.text.split(maxsplit=1)[1] if len(cmd.text.split()) > 1 else ""
    else:
        await cmd.reply("<b>⎚ Please use <code>/txt text to Create txt File</code></b>")
        return
    if not text_to_write:
        return await cmd.reply("Please use text for Convert it, into txt file")

    status = await cmd.reply_text("<b>⎚ `Creating TxT file...`</b>")

    file_name = write_text(text_to_write)
    await bot.send_document(
        chat_id=cmd.chat.id,
        document=file_name,
    )
    await status.delete()
