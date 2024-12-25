from pyrogram import Client, filters
from pyrogram.types import Message
import tempfile


@Client.on_message(filters.command("userlist", ["/", "."]))
async def userlist_cmd(client, message):
    with open(file="plugins/ExtraMod/users/admin.txt", mode="r+", encoding="utf-8") as admin:
        with open(file="plugins/ExtraMod/users/premium.txt", mode="r+", encoding="utf-8") as premium_file:
            premium_list = premium_file.readlines()
        main_admin = admin.readlines()

    if str(message.from_user.id)+'\n' in main_admin:
        # Create a temporary file to store the list of premium users
        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as temp_file:
            temp_file.writelines(premium_list)
            temp_file_path = temp_file.name

        try:
            await client.send_document(
                chat_id=message.chat.id,
                document=temp_file_path,
                caption="<b>Premium users</b>"
            )
        finally:
            # Clean up the temporary file
            temp_file.close()
    else:
        await message.reply("<b>You Are Not Fucking Admin🖕</b>")
