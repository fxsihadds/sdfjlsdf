from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command("unregister", ["/", "."]))
async def unregister_command(client, message):
    with open(file="plugins/ExtraMod/users/admin.txt", mode="r+", encoding="utf-8") as admin:
        with open(file="plugins/ExtraMod/users/premium.txt", mode="r+", encoding="utf-8") as premium_file:
            premium_list = premium_file.readlines()
        main_admin = admin.readlines()

    if str(message.from_user.id) + '\n' in main_admin:
        try:
            user_to_remove = int(
                message.text.split("/unregister")[1].strip())
        except (IndexError, ValueError):
            await message.reply("<b>⎚ Use <code>/unregister user_id</code></b>")
            return

        if str(user_to_remove) + "\n" in premium_list:
            premium_list.remove(str(user_to_remove) + "\n")
            with open(file="plugins/ExtraMod/users/premium.txt", mode="w", encoding="utf-8") as premium_file:
                premium_file.writelines(premium_list)
            await message.reply(f'<b>⎚ User {user_to_remove} removed from Premium</b>')
        else:
            await message.reply(f'<b>⎚ User {user_to_remove} is not in Premium</b>')
    else:
        await message.reply("<b>You Are Not Fucking Admin🖕</b>")
