from pyrogram import Client, filters
from pyrogram.types import Message



@Client.on_message(filters.command("register", ["/", "."]))
async def register_command(client, message):
    with open(file="plugins/ExtraMod/users/admin.txt", mode="r+", encoding="utf-8") as admin:
        with open(file="plugins/ExtraMod/users/premium.txt", mode="r+", encoding="utf-8") as premium_existed:
            existed = premium_existed.readlines()
        main_admin = admin.readlines()

    if str(message.from_user.id) + '\n' in main_admin:
        try:
            premium_users = [int(user_id.strip()) for user_id in message.text.split(
                "/register")[1].split()]
        except IndexError:
            await message.reply("<b>⎚ Use <code>/register users ids</code></b>")
            return
        if not premium_users:
            await message.reply("<b>⎚ Use <code>/register users ids</code></b>")
            return
        elif str(premium_users[0]) + "\n" in existed:
            await message.reply(f'<b>⎚ This Fucking User Is Already in Premium</b>')
        else:
            await message.reply(f'<b>⎚ Premium User added successfully</b>')
            with open(file="plugins/ExtraMod/users/premium.txt", mode="a+", encoding="utf-8") as premium:
                for premium_user in premium_users:
                    premium.write(str(premium_user) + "\n")
    else:
        await message.reply("<b>You Are Not Fucking Admin🖕</b>")