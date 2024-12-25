from pyrogram import Client, filters
from helpers.timemanager import ratelimiters


@Client.on_message(filters.command("id", ["/", "."]))
@ratelimiters
async def userinfo_command(client: Client, message):
    if len(message.command) > 1:
        username = message.command[1]
        try:
            user = await client.get_users(username)
            reply_text = (
                f"<strong>User Information: </strong>\n"
                f"━━━━━━━━━━━\n"
                f"<b>User ID:</b> <code>{user.id}</code>\n"
                f"<b>Username:</b> <code>{user.username}</code>\n"
                f"<b>First Name:</b> <code>{user.first_name}</code>\n"
                f"<b>Last Name:</b> <code>{user.last_name}</code>\n"
                f"<b>DC ID:</b> <code>{user.dc_id}</code>\n"
                f"<b>Is Bot:</b> <code>{user.is_bot}</code>\n"
                f"<b>Language Code:</b> <code>{user.language_code}</code>\n"
                f"<b>Last Online Date:</b> <code>{user.last_online_date}</code>\n"
            )
            await message.reply_text(reply_text)
        except Exception as e:
            await message.reply_text(f"An error occurred while fetching user info: {e}")
    else:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        dc_id = message.from_user.dc_id
        is_bot = message.from_user.is_bot
        language_code = message.from_user.language_code
        last_online_date = message.from_user.last_online_date

        reply_text = (
            f"<strong>User Information: </strong>\n"
            f"━━━━━━━━━━━\n"
            f"<b>User ID:</b> <code>{user_id}</code>\n"
            f"<b>Username:</b> <code>{username}</code>\n"
            f"<b>First Name:</b> <code>{first_name}</code>\n"
            f"<b>Last Name:</b> <code>{last_name}</code>\n"
            f"<b>DC ID:</b> <code>{dc_id}</code>\n"
            f"<b>Is Bot:</b> <code>{is_bot}</code>\n"
            f"<b>Language Code:</b> <code>{language_code}</code>\n"
            f"<b>Last Online Date:</b> <code>{last_online_date}</code>\n"
        )
        await message.reply_text(reply_text)
