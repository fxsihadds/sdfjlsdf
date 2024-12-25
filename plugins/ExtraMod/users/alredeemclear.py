from pyrogram import Client, filters
from pyrogram.types import Message
import aiofiles



@Client.on_message(filters.command("redclr"))
async def redeem_cmd(client, message):
    with open(file="plugins/ExtraMod/users/admin.txt", mode="r+", encoding="utf-8") as admin:
        admin_list = admin.readlines()
    if str(message.from_user.id)+'\n' in admin_list:
        async with aiofiles.open("plugins/ExtraMod/users/alredeem.txt", mode="w", encoding="utf-8") as remove_file:
            await remove_file.truncate(0)
        await message.reply_text("<b>Redeem Clear Successful<b>")

    else:
        await message.reply("<b>You Are Not Fucking Admin🖕</b>")
